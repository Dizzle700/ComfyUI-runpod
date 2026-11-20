import copy
from pathlib import Path
import random
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import comfy_batch_engine as engine


SAMPLE_WORKFLOW = {
    "1": {
        "class_type": "UNETLoader",
        "inputs": {"unet_name": "flux/krea2_turbo_fp8_scaled.safetensors"},
    },
    "2": {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": "masterpiece, detailed portrait of a red fox in snow"},
    },
    "3": {
        "class_type": "CLIPTextEncode",
        "inputs": {"negative": "blurry, low quality, bad anatomy"},
    },
    "4": {
        "class_type": "KSampler",
        "inputs": {"seed": 42, "steps": 8, "sampler_name": "euler"},
    },
    "5": {
        "class_type": "SaveImage",
        "inputs": {"filename_prefix": "ComfyUI"},
    },
}


class BatchEngineTests(unittest.TestCase):
    def test_detect_prompt_nodes_prefers_positive_clip_encode(self):
        nodes = engine.detect_prompt_nodes(SAMPLE_WORKFLOW)
        self.assertGreaterEqual(len(nodes), 3)
        self.assertEqual(nodes[0]["node_id"], "2")
        self.assertEqual(nodes[0]["input_key"], "text")
        self.assertTrue(nodes[0]["label"].startswith("⭐"))

    def test_extract_model_name_and_sanitize(self):
        self.assertEqual(engine.extract_model_name(SAMPLE_WORKFLOW), "krea2_turbo_fp8_scaled")
        self.assertEqual(engine.sanitize_folder_name("My Model: v2/beta"), "My_Model_v2beta")

    def test_randomize_seeds_and_apply_prefix(self):
        wf = copy.deepcopy(SAMPLE_WORKFLOW)
        changed = engine.randomize_workflow_seeds(wf, rng=random.Random(123))
        self.assertEqual(changed, 1)
        self.assertNotEqual(wf["4"]["inputs"]["seed"], 42)
        self.assertEqual(engine.apply_filename_prefix(wf, "my_batch"), 1)
        self.assertEqual(wf["5"]["inputs"]["filename_prefix"], "my_batch")

    def test_parse_prompts_text_skips_blank_lines(self):
        prompts = engine.parse_prompts_text("  first prompt \n\n  \nsecond prompt\n")
        self.assertEqual(prompts, ["first prompt", "second prompt"])

    def test_runner_validates_target_node_before_starting(self):
        runner = engine.BatchRunner(poll_interval=0.01)
        ok, msg = runner.start("http://127.0.0.1:8188", SAMPLE_WORKFLOW, "999", "text", ["hello"])
        self.assertFalse(ok)
        self.assertIn("999", msg)

    def test_runner_sequential_completes_and_captures_preview(self):
        with tempfile.TemporaryDirectory() as folder:
            out_dir = Path(folder)
            generated_file = out_dir / "batch_00001_.png"
            generated_file.write_bytes(b"\x89PNG\r\n\x1a\n")

            submitted_payloads = []

            def fake_http(url, payload=None, timeout=15):
                if url.endswith("/prompt"):
                    submitted_payloads.append(payload)
                    idx = len(submitted_payloads)
                    return 200, {"prompt_id": f"pid-{idx}"}
                if "/history/pid-" in url:
                    pid = url.rsplit("/", 1)[-1]
                    return 200, {
                        pid: {
                            "status": {"status_str": "success"},
                            "outputs": {
                                "5": {
                                    "images": [
                                        {"filename": "batch_00001_.png", "subfolder": "", "type": "output"}
                                    ]
                                }
                            },
                        }
                    }
                return 200, {"queue_running": [], "queue_pending": []}

            runner = engine.BatchRunner(poll_interval=0.01)
            with patch.object(engine, "_http_json", side_effect=fake_http):
                ok, _ = runner.start(
                    "http://127.0.0.1:8188/",
                    SAMPLE_WORKFLOW,
                    "2",
                    "text",
                    ["prompt one", "prompt two"],
                    sequential=True,
                    randomize_seeds=True,
                    filename_prefix="my_prefix",
                    output_dir=str(out_dir),
                )
                self.assertTrue(ok)
                deadline = time.time() + 5
                while runner.is_running() and time.time() < deadline:
                    time.sleep(0.02)

            snap = runner.snapshot()
            self.assertFalse(snap["running"])
            self.assertEqual(snap["succeeded"], 2)
            self.assertEqual(snap["failed"], 0)
            self.assertEqual(snap["last_image"], str(generated_file))
            self.assertEqual(snap["last_prompt"], "prompt two")
            self.assertEqual(len(submitted_payloads), 2)
            self.assertEqual(submitted_payloads[0]["prompt"]["2"]["inputs"]["text"], "prompt one")
            self.assertEqual(submitted_payloads[1]["prompt"]["2"]["inputs"]["text"], "prompt two")
            self.assertEqual(submitted_payloads[0]["prompt"]["5"]["inputs"]["filename_prefix"], "my_prefix")
            self.assertNotEqual(
                submitted_payloads[0]["prompt"]["4"]["inputs"]["seed"],
                submitted_payloads[1]["prompt"]["4"]["inputs"]["seed"],
            )

    def test_runner_burst_mode_queues_all_immediately(self):
        queued = []

        def fake_http(url, payload=None, timeout=15):
            if url.endswith("/prompt"):
                queued.append(payload["prompt"]["2"]["inputs"]["text"])
                return 200, {"prompt_id": f"pid-{len(queued)}"}
            raise AssertionError(f"Unexpected poll in burst mode: {url}")

        runner = engine.BatchRunner(poll_interval=0.01)
        with patch.object(engine, "_http_json", side_effect=fake_http):
            ok, _ = runner.start(
                "http://127.0.0.1:8188",
                SAMPLE_WORKFLOW,
                "2",
                "text",
                ["p1", "p2", "p3"],
                sequential=False,
            )
            self.assertTrue(ok)
            deadline = time.time() + 5
            while runner.is_running() and time.time() < deadline:
                time.sleep(0.02)

        snap = runner.snapshot()
        self.assertEqual(queued, ["p1", "p2", "p3"])
        self.assertEqual(snap["succeeded"], 3)

    def test_runner_aborts_after_consecutive_failures(self):
        calls = 0

        def fake_http(url, payload=None, timeout=15):
            nonlocal calls
            calls += 1
            raise OSError("connection refused")

        runner = engine.BatchRunner(poll_interval=0.01)
        with patch.object(engine, "_http_json", side_effect=fake_http):
            ok, _ = runner.start(
                "http://127.0.0.1:8188",
                SAMPLE_WORKFLOW,
                "2",
                "text",
                ["p1", "p2", "p3", "p4", "p5"],
                sequential=True,
            )
            self.assertTrue(ok)
            deadline = time.time() + 5
            while runner.is_running() and time.time() < deadline:
                time.sleep(0.02)

        snap = runner.snapshot()
        self.assertEqual(calls, engine.MAX_CONSECUTIVE_FAILURES)
        self.assertEqual(snap["failed"], engine.MAX_CONSECUTIVE_FAILURES)
        self.assertEqual(snap["succeeded"], 0)


if __name__ == "__main__":
    unittest.main()

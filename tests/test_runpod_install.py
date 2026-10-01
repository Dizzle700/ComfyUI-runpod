import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RunpodInstallTests(unittest.TestCase):
    """Exercise startup decisions without installing packages or using a GPU."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scripts = self.root / "scripts"
        self.scripts.mkdir()
        shutil.copy(ROOT / "comfy_install_runpod.sh", self.scripts)
        (self.scripts / "requirements.txt").write_text("gradio\n")
        self.comfy = self.root / "ComfyUI"
        self.manager = self.comfy / "custom_nodes" / "comfyui-manager"
        (self.comfy / ".git").mkdir(parents=True)
        (self.manager / ".git").mkdir(parents=True)
        (self.comfy / "requirements.txt").write_text("torch\n")
        (self.manager / "requirements.txt").write_text("requests\n")
        self.events = self.root / "events"
        self.stamp = self.comfy / ".runpod-setup.json"
        (self.scripts / "comfy_setup_cache.py").write_text(
            "import os, pathlib, sys\n"
            "stamp=pathlib.Path(os.environ['COMFY_DIR'])/'.runpod-setup.json'\n"
            "if sys.argv[1]=='check':\n"
            " sys.exit(0 if stamp.exists() and not os.environ.get('TEST_CACHE_MISS') else 1)\n"
            "stamp.write_text('{}')\n"
        )
        self.bin = self.root / "bin"
        self.bin.mkdir()
        python = self.bin / "python-test"
        python.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ $1 == -m && $2 == pip ]]; then\n"
            " case $3 in\n"
            "  --version) echo 'pip test'; exit 0;;\n"
            "  show) exit 1;;\n"
            "  install) echo pip-install >> \"$TEST_EVENTS\"; "
            "[[ ${TEST_FAIL_PIP:-0} != 1 ]]; exit $?;;\n"
            " esac\n"
            "fi\n"
            "if [[ $1 == - ]]; then\n"
            " source_text=$(cat)\n"
            " [[ $source_text != *importlib.metadata* ]] || echo 'torch==2.8'\n"
            " exit 0\n"
            "fi\n"
            "if [[ $1 == -c ]]; then exit 0; fi\n"
            "exec \"$TEST_REAL_PYTHON\" \"$@\"\n"
        )
        python.chmod(0o755)
        git = self.bin / "git"
        git.write_text(
            "#!/usr/bin/env bash\n"
            "echo git-\"$*\" >> \"$TEST_EVENTS\"\n"
            "if [[ $1 == clone ]]; then mkdir -p \"${@: -1}/.git\"; fi\n"
        )
        git.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update({
            "PATH": str(self.bin) + os.pathsep + self.env["PATH"],
            "PYTHON_EXE": str(python),
            "COMFY_DIR": str(self.comfy),
            "COMFY_UPDATE_ON_START": "0",
            "COMFY_FORCE_INSTALL": "0",
            "COMFY_MODEL_PACKAGES": "",
            "COMFY_TEMPLATE_IDS": "",
            "TEST_EVENTS": str(self.events),
            "TEST_REAL_PYTHON": shutil.which("python3"),
        })
        for name in (
            "PIP_CACHE_DIR", "TORCH_HOME", "HF_HOME", "HF_HUB_CACHE",
            "HUGGINGFACE_HUB_CACHE", "TRANSFORMERS_CACHE", "DIFFUSERS_CACHE", "HF_XET_CACHE",
        ):
            self.env[name] = str(self.root / "cache" / name)

    def run_installer(self, *args, expect_success=True):
        result = subprocess.run(
            ["bash", str(self.scripts / "comfy_install_runpod.sh"), "--no-start", *args],
            env=self.env, capture_output=True, text=True,
        )
        if expect_success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return self.events.read_text().splitlines() if self.events.exists() else []

    def test_first_install_then_warm_start_skips_network_and_pip(self):
        events = self.run_installer()
        self.assertEqual(events.count("pip-install"), 3)
        self.assertTrue(self.stamp.exists())
        self.events.unlink()
        events = self.run_installer()
        self.assertEqual(events, [])

    def test_update_pulls_both_repos_and_runs_pip(self):
        self.stamp.write_text("{}")
        events = self.run_installer("--update")
        self.assertEqual(sum("pull --ff-only" in event for event in events), 2)
        self.assertEqual(events.count("pip-install"), 3)

    def test_reinstall_uses_current_git_versions(self):
        self.stamp.write_text("{}")
        events = self.run_installer("--reinstall")
        self.assertEqual(events.count("pip-install"), 3)
        self.assertFalse(any(event.startswith("git-") for event in events))

    def test_missing_environment_runs_pip_despite_persistent_stamp(self):
        self.stamp.write_text("{}")
        self.env["TEST_CACHE_MISS"] = "1"
        self.assertEqual(self.run_installer().count("pip-install"), 3)

    def test_failed_install_removes_previous_stamp(self):
        self.stamp.write_text("{}")
        self.env["TEST_FAIL_PIP"] = "1"
        self.run_installer("--reinstall", expect_success=False)
        self.assertFalse(self.stamp.exists())

    def test_first_boot_clones_missing_repos(self):
        shutil.rmtree(self.comfy)
        events = self.run_installer()
        self.assertEqual(sum(event.startswith("git-clone ") for event in events), 2)
        self.assertTrue(self.stamp.exists())


if __name__ == "__main__":
    unittest.main()

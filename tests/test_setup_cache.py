import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("setup_cache", ROOT / "comfy_setup_cache.py")
cache = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cache)


class SetupCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.comfy = self.root / "ComfyUI"
        self.scripts = self.root / "scripts"
        self.manager = self.comfy / "custom_nodes" / "comfyui-manager"
        self.manager.mkdir(parents=True)
        self.scripts.mkdir()
        (self.comfy / "requirements.txt").write_text("numpy>=1.0\n")
        (self.manager / "requirements.txt").write_text("requests\n")
        (self.scripts / "requirements.txt").write_text("gradio>=5.5,<6\n")
        (self.scripts / "comfy_install_runpod.sh").write_text("# installer\n")
        (self.comfy / ".runpod-torch-constraints.txt").write_text("torch==2.8\n")
        self.stamp = self.comfy / ".runpod-setup.json"
        self.packages = {
            "torch": [{"version": "2.8", "location": "/usr/site-packages"}],
            "gradio": [{"version": "5.5", "location": "/usr/site-packages"}],
        }
        self.patches = [
            patch.object(cache, "repo_commit", return_value="saved-commit"),
            patch.object(cache, "installed_packages", side_effect=lambda: self.packages.copy()),
            patch.object(cache, "check_imports"),
        ]
        for item in self.patches:
            item.start()
        self.addCleanup(self.temp.cleanup)
        for item in self.patches:
            self.addCleanup(item.stop)

    def save(self):
        cache.save_cache(self.stamp, self.comfy, self.scripts)

    def ready(self):
        return cache.check_cache(self.stamp, self.comfy, self.scripts)[0]

    def test_first_start_installs(self):
        self.assertFalse(self.ready())

    def test_unchanged_installation_skips_pip(self):
        self.save()
        self.assertTrue(self.ready())

    def test_requirements_change_installs(self):
        self.save()
        (self.manager / "requirements.txt").write_text("requests\nnew-package\n")
        self.assertFalse(self.ready())

    def test_new_repo_commit_installs(self):
        self.save()
        with patch.object(cache, "repo_commit", return_value="updated-commit"):
            self.assertFalse(self.ready())

    def test_nested_requirements_change_installs(self):
        (self.manager / "requirements.txt").write_text("-r deps.txt\n")
        (self.manager / "deps.txt").write_text("requests\n")
        self.save()
        (self.manager / "deps.txt").write_text("requests\nnew-package\n")
        self.assertFalse(self.ready())

    def test_missing_package_in_new_container_installs(self):
        self.save()
        del self.packages["gradio"]
        self.assertFalse(self.ready())

    def test_changed_package_version_installs(self):
        self.save()
        self.packages["gradio"] = [{"version": "6.0", "location": "/usr/site-packages"}]
        self.assertFalse(self.ready())

    def test_new_custom_node_package_keeps_fast_start(self):
        self.save()
        self.packages["custom-node-dep"] = [{"version": "1", "location": "/usr/site-packages"}]
        self.assertTrue(self.ready())

    def test_changed_python_installs(self):
        self.save()
        with patch.object(cache, "python_environment", return_value={"version": "different"}):
            self.assertFalse(self.ready())

    def test_incompatible_hf_gradio_triggers_cleanup(self):
        self.save()
        self.packages["hf-gradio"] = [{"version": "1", "location": "/usr/site-packages"}]
        self.assertFalse(self.ready())

    def test_broken_import_despite_package_metadata_installs(self):
        self.save()
        with patch.object(cache, "check_imports", side_effect=RuntimeError("broken gradio")):
            self.assertFalse(self.ready())

    def test_corrupt_stamp_installs(self):
        self.stamp.write_text("interrupted JSON")
        self.assertFalse(self.ready())

    def test_incomplete_stamp_installs(self):
        self.save()
        saved = json.loads(self.stamp.read_text())
        del saved["packages"]
        self.stamp.write_text(json.dumps(saved))
        self.assertFalse(self.ready())

    def test_failed_import_never_marks_installation_ready(self):
        with patch.object(cache, "check_imports", side_effect=RuntimeError("broken gradio")):
            with self.assertRaises(RuntimeError):
                self.save()
        self.assertFalse(self.stamp.exists())


if __name__ == "__main__":
    unittest.main()

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StartupEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copy(ROOT / 'runpod_startup.sh', self.root)
        (self.root / 'comfy_template_startup.py').write_text('')
        (self.root / 'comfy_install_runpod.sh').write_text(
            "#!/bin/bash\npython3 - <<'PY'\n"
            "import json, os\nfrom pathlib import Path\n"
            "Path(os.environ['TEST_RESULT']).write_text(json.dumps({"
            "key: os.environ.get(key) for key in ['COMFY_TEMPLATE_IDS', 'COMFY_MODEL_PACKAGES']}))\nPY\n"
        )
        self.env = os.environ.copy()
        self.env.update({
            'COMFY_SECRET_FILE': str(self.root / 'nonexistent'),
            'PANEL_USER': 'test', 'PANEL_PASS': 'test',
            'RUNPOD_LOG_FILE': str(self.root / 'startup.log'),
            'TEST_RESULT': str(self.root / 'result.json'),
            'COMFY_TEMPLATE_IDS': '89,93,94', 'COMFY_MODEL_PACKAGES': '',
        })
        for key in ['XDG_CACHE_HOME', 'PIP_CACHE_DIR', 'TORCH_HOME', 'HF_HOME',
                    'HF_HUB_CACHE', 'HUGGINGFACE_HUB_CACHE', 'TRANSFORMERS_CACHE',
                    'DIFFUSERS_CACHE', 'HF_XET_CACHE']:
            self.env[key] = str(self.root / 'cache')

    def test_passes_template_and_package_environment_to_installer(self):
        self.env['COMFY_MODEL_PACKAGES'] = 'Krea'
        result = subprocess.run(['bash', str(self.root / 'runpod_startup.sh')],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((self.root / 'result.json').read_text()), {
            'COMFY_TEMPLATE_IDS': '89,93,94', 'COMFY_MODEL_PACKAGES': 'Krea',
        })

    def test_invalid_environment_fails_before_installation(self):
        self.env['COMFY_TEMPLATE_IDS'] = '89,bad'
        result = subprocess.run(['bash', str(self.root / 'runpod_startup.sh')],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'result.json').exists())


if __name__ == '__main__':
    unittest.main()

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('image_storage', ROOT / 'docker/prepare_storage.py')
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


class ImageStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.code, self.data = root / 'image', root / 'volume'
        self.code.mkdir()
        (self.code / 'main.py').write_text('baked source')

    def test_preserves_existing_data_and_links_download_destination(self):
        (self.code / 'models/loras').mkdir(parents=True)
        (self.data / 'output').mkdir(parents=True)
        output = self.data / 'output/result.png'
        output.write_bytes(b'existing output')
        storage.attach_storage(self.code, self.data)
        self.assertEqual(output.read_bytes(), b'existing output')
        self.assertTrue((self.data / 'models/loras').is_dir())
        (self.code / 'models/model.safetensors').write_bytes(b'model')
        self.assertEqual((self.data / 'models/model.safetensors').read_bytes(), b'model')
        self.assertEqual((self.code / 'main.py').read_text(), 'baked source')
        storage.attach_storage(self.code, self.data)
        self.assertEqual(output.read_bytes(), b'existing output')

    def test_baked_placeholder_does_not_replace_existing_model(self):
        (self.code / 'models').mkdir()
        (self.data / 'models').mkdir(parents=True)
        (self.code / 'models/model').write_bytes(b'baked placeholder')
        (self.data / 'models/model').write_bytes(b'existing model')
        storage.attach_storage(self.code, self.data)
        self.assertEqual((self.data / 'models/model').read_bytes(), b'existing model')

    def test_refuses_overlap_and_unexpected_existing_symlink(self):
        with self.assertRaises(ValueError):
            storage.attach_storage(self.code, self.code / 'data')
        (self.code / 'models').symlink_to(self.code)
        with self.assertRaises(ValueError):
            storage.attach_storage(self.code, self.data)


if __name__ == '__main__':
    unittest.main()

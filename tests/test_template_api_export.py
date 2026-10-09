import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import comfy_template_startup as templates


class TemplateApiExportTests(unittest.TestCase):
    def test_qwen_image_export_removes_frontend_note_only(self):
        selected = templates.load_templates([94])
        original = json.loads(selected[0][0]['api_json'])
        expected = {key: node for key, node in original.items()
                    if node.get('class_type') != 'MarkdownNote'}
        self.assertLess(len(expected), len(original))
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(templates, 'EXPORT_DIR', Path(folder)):
                _, manifest = templates.prepare(selected)
            self.assertEqual(json.loads(Path(manifest[0]['api_json']).read_text()), expected)
            self.assertNotIn('MarkdownNote', manifest[0]['node_types'])
            self.assertEqual(json.loads(Path(manifest[0]['workflow_json']).read_text()),
                             json.loads(selected[0][0]['workflow_json']))

    def test_preserves_required_custom_nodes(self):
        api = {'1': {'class_type': 'RequiredCustomNode', 'inputs': {}}}
        self.assertEqual(templates.strip_ui_notes(api), api)

    def test_rejects_execution_links_to_frontend_notes(self):
        api = {'1': {'class_type': 'MarkdownNote', 'inputs': {}},
               '2': {'class_type': 'OutputNode', 'inputs': {'image': ['1', 0]}}}
        with self.assertRaises(ValueError):
            templates.strip_ui_notes(api)


if __name__ == '__main__':
    unittest.main()

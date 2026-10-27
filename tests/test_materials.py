import json
import tempfile
import unittest
from pathlib import Path

try:
    from companion.materials import normalize_catalog, MaterialLibrary
except ImportError:
    normalize_catalog = MaterialLibrary = None


class MaterialTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(normalize_catalog, "尚未实现资料准入与检索")

    def test_catalogue_does_not_import_child_states_or_parent_hypotheses(self):
        source = {"books": [{"book_id": "bk-0001", "title": "纸飞机", "author": "未知", "owner": "test-a", "status": "unread", "transition_level": "text", "interest_hook": "她肯定喜欢", "source": "旧书架目录"}]}
        result = normalize_catalog(source)
        serialized = json.dumps(result, ensure_ascii=False)
        for forbidden in ("owner", "unread", "transition_level", "interest_hook", "她肯定喜欢"):
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(result["records"][0]["release_status"], "discover_only")
        self.assertEqual(result["records"][0]["edition_verified"], False)

    def test_bounded_search_respects_release_scope_and_no_plot_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "catalog.v3.json"
            path.write_text(json.dumps(normalize_catalog({"books": [{"book_id": "bk-0001", "title": "猫的故事", "author": "甲"}]})), encoding="utf-8")
            library = MaterialLibrary(path)
            found = library.search("猫", 1)
            self.assertEqual(found["matches"][0]["book_ref"], "bk-0001")
            self.assertIn("版本", found["matches"][0]["limits"])
            self.assertNotIn("gist", found["matches"][0])
            self.assertEqual(library.search("没有的书", 2)["matches"], [])

    def test_absent_catalogue_does_not_block_current_page_reading(self):
        result = MaterialLibrary(None).search("太空", 2)
        self.assertFalse(result["available"])
        self.assertIn("当前页", result["message"])


if __name__ == "__main__":
    unittest.main()

"""Regression tests for scripts/build_readme.py.

    python -m unittest discover -s scripts -p "test_*.py"
"""
import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_readme as br  # noqa: E402


class LookupValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = br.load_yaml("categories.yaml")["groups"]
        cls.papers = br.load_yaml("papers.yaml")
        cls.core = next(p for p in cls.papers if p.get("lookup"))

    def errors_for(self, mutate):
        papers = copy.deepcopy(self.papers)
        entry = next(p for p in papers if p["id"] == self.core["id"])
        mutate(entry)
        return br.validate(self.groups, papers)

    def test_current_data_is_valid(self):
        self.assertEqual(br.validate(self.groups, self.papers), [])

    def test_unknown_lookup_group_is_rejected(self):
        errors = self.errors_for(lambda p: p["lookup"].update(group=p["lookup"]["group"] + "p"))
        self.assertTrue(any("unknown lookup group" in e for e in errors), errors)

    def test_missing_lookup_field_is_rejected(self):
        errors = self.errors_for(lambda p: p["lookup"].pop("decoder"))
        self.assertTrue(any("missing `decoder`" in e for e in errors), errors)

    def test_bad_lookup_year_is_rejected(self):
        errors = self.errors_for(lambda p: p["lookup"].update(year="2023"))
        self.assertTrue(any("lookup year" in e for e in errors), errors)

    def test_every_lookup_record_is_rendered(self):
        doc = br.build_core_doc(self.papers)
        n_core = sum(1 for p in self.papers if p.get("lookup"))
        self.assertEqual(doc.count('<a id="system-'), n_core)


class Rendering(unittest.TestCase):
    def test_code_note_becomes_link_title(self):
        p = {"code": "owner/repo", "code_note": 'Partial "release"'}
        self.assertIn("\"Partial 'release'\")", br.code_badge(p))

    def test_dates_do_not_contain_hyphens(self):
        table = br.paper_table([{"id": "x", "title": "T", "paper": "https://example.org", "summary": "S.",
                                 "venue": "arXiv", "date": "2026-05", "category": "surveys"}])
        self.assertIn("| 2026.05 |", table)


if __name__ == "__main__":
    unittest.main()

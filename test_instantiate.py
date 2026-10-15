import tempfile
import unittest
from pathlib import Path

from instantiate import derive_mod_class, derive_mod_id, instantiate


class DeriveTest(unittest.TestCase):
    def test_mod_id_strips_dashes(self):
        self.assertEqual(derive_mod_id("dynamic-widgets"), "dynamicwidgets")
        self.assertEqual(derive_mod_id("widgets"), "widgets")

    def test_mod_class_is_pascal_case(self):
        self.assertEqual(derive_mod_class("dynamic-widgets"), "DynamicWidgets")
        self.assertEqual(derive_mod_class("widgets"), "Widgets")


class InstantiateTest(unittest.TestCase):
    def test_no_placeholders_remain_and_files_are_renamed(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "dynamic-widgets"
            instantiate(target, "dynamic-widgets", "Dynamic Widgets", "Widgets that do a thing.", jira_key="MINECRAFT-999")

            java_file = target / "src/main/java/io/github/brooswitminecraft/dynamicwidgets/DynamicWidgetsMod.java"
            self.assertTrue(java_file.is_file(), "mod class file was not renamed into place")
            self.assertIn("class DynamicWidgetsMod", java_file.read_text())
            self.assertIn('MODID = "dynamicwidgets"', java_file.read_text())

            self.assertEqual((target / "changelog.d/MINECRAFT-999.md").read_text().splitlines()[0], "bump: minor")

            for path in target.rglob("*"):
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue  # binary file, nothing to check
                self.assertNotIn("__MOD_", text, f"placeholder left in {path}")

    def test_refuses_non_empty_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "existing.txt").write_text("hi")
            with self.assertRaises(SystemExit):
                instantiate(target, "dynamic-widgets", "Dynamic Widgets", "desc")

    def test_rejects_non_kebab_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                instantiate(Path(tmp) / "x", "Dynamic_Widgets", "Dynamic Widgets", "desc")

    def test_tolerates_a_fresh_clones_git_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".git").mkdir()
            (target / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
            instantiate(target, "dynamic-widgets", "Dynamic Widgets", "desc")
            self.assertTrue((target / "build.gradle").is_file())
            self.assertTrue((target / ".git" / "HEAD").is_file(), ".git contents must survive instantiation")

    def test_still_refuses_other_content_alongside_git_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".git").mkdir()
            (target / "README.md").write_text("pre-existing, not from this template")
            with self.assertRaises(SystemExit):
                instantiate(target, "dynamic-widgets", "Dynamic Widgets", "desc")

    def test_rejects_too_short_derived_mod_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                instantiate(Path(tmp) / "x", "a", "A", "desc")

    def test_rejects_too_long_derived_mod_id(self):
        slug = "a" * 65
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                instantiate(Path(tmp) / "x", slug, "A", "desc")

    def test_accepts_boundary_length_mod_id(self):
        # 64 chars total, right at the documented limit.
        slug = "a" * 64
        with tempfile.TemporaryDirectory() as tmp:
            instantiate(Path(tmp) / "x", slug, "A", "desc")

    def test_rejects_double_quote_in_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                instantiate(Path(tmp) / "x", "dynamic-widgets", 'Dynamic "Widgets"', "desc")

    def test_rejects_triple_single_quote_in_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                instantiate(Path(tmp) / "x", "dynamic-widgets", "Dynamic Widgets", "it's ''' broken")


if __name__ == "__main__":
    unittest.main()

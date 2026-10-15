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
                if path.is_file() and path.suffix not in {".jar", ".png"}:
                    self.assertNotIn("__MOD_", path.read_text(encoding="utf-8"), f"placeholder left in {path}")

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


if __name__ == "__main__":
    unittest.main()

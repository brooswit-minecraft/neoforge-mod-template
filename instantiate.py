#!/usr/bin/env python3
"""Materialize a new NeoForge 1.21.1 mod repo from this template.

Usage:
    python3 instantiate.py <target-dir> --slug dynamic-widgets \
        --name "Dynamic Widgets" --description "Widgets that do a thing." \
        [--jira-key MINECRAFT-999]

<target-dir> should be an empty (or non-existent) directory, or a fresh
`git clone` of the new, empty GitHub repo (which contains only `.git` --
that's the one entry this script tolerates). Any other existing content is
refused. This script only writes files; it does not touch git or GitHub.

Placeholders replaced across every text file under template/:
    __MOD_SLUG__         kebab-case repo name, e.g. "dynamic-widgets"
    __MOD_ID__            derived: slug with dashes removed, e.g. "dynamicwidgets"
    __MOD_CLASS__         derived: PascalCase of slug, e.g. "DynamicWidgets"
    __MOD_NAME__          human display name, e.g. "Dynamic Widgets"
    __MOD_DESCRIPTION__   one-line mod description

__MOD_ID__ also appears in one directory name and one file name, which are
renamed, not just their contents rewritten.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parent / "template"

SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
# NeoForge's own mod_id constraint (see gradle.properties' mod_id comment):
# must fit [a-z][a-z0-9_]{1,63}, i.e. 2-64 characters total.
MOD_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


def derive_mod_id(slug):
    return slug.replace("-", "")


def derive_mod_class(slug):
    return "".join(word.capitalize() for word in slug.split("-"))


def replace_placeholders(text, placeholders):
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def instantiate(target_dir, slug, name, description, jira_key=None):
    if not SLUG_RE.match(slug):
        raise SystemExit(f"--slug must be kebab-case (e.g. dynamic-widgets), got: {slug!r}")

    mod_id = derive_mod_id(slug)
    if not MOD_ID_RE.match(mod_id):
        raise SystemExit(
            f"--slug {slug!r} derives mod_id {mod_id!r} ({len(mod_id)} chars), "
            "which must be 2-64 chars matching [a-z][a-z0-9_]{1,63} -- NeoForge's own mod_id constraint"
        )
    if '"' in name:
        raise SystemExit("--name must not contain a double-quote character (it is embedded in a quoted TOML string)")
    if "'''" in description:
        raise SystemExit("--description must not contain the sequence ''' (it is embedded in a triple-quoted TOML string)")

    mod_class = derive_mod_class(slug)
    placeholders = {
        "__MOD_SLUG__": slug,
        "__MOD_ID__": mod_id,
        "__MOD_CLASS__": mod_class,
        "__MOD_NAME__": name,
        "__MOD_DESCRIPTION__": description,
    }

    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    existing = [p for p in target_dir.iterdir() if p.name != ".git"]
    if existing:
        raise SystemExit(f"{target_dir} is not empty (beyond .git); instantiate into a fresh clone of the new repo")

    for src in TEMPLATE_DIR.rglob("*"):
        rel = src.relative_to(TEMPLATE_DIR)
        rel_str = replace_placeholders(str(rel), placeholders)
        dest = target_dir / rel_str
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        raw = src.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            dest.write_bytes(raw)
        else:
            dest.write_text(replace_placeholders(text, placeholders), encoding="utf-8")
        shutil.copymode(src, dest)

    if jira_key:
        fragment = target_dir / "changelog.d" / f"{jira_key}.md"
        fragment.write_text("bump: minor\n\n### Added\n- Initial scaffold.\n", encoding="utf-8")

    print(f"Instantiated {slug} (mod_id={mod_id}, class={mod_class}Mod) into {target_dir}")


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_dir")
    parser.add_argument("--slug", required=True, help="kebab-case repo/root-project name, e.g. dynamic-widgets")
    parser.add_argument("--name", required=True, help="human display name, e.g. 'Dynamic Widgets'")
    parser.add_argument("--description", required=True, help="one-line mod description")
    parser.add_argument("--jira-key", default=None, help="if set, seeds changelog.d/<jira-key>.md for this scaffold PR")
    args = parser.parse_args(argv[1:])
    instantiate(args.target_dir, args.slug, args.name, args.description, args.jira_key)


if __name__ == "__main__":
    main(sys.argv)

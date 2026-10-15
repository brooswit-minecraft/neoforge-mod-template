# neoforge-mod-template

Reusable boilerplate for a new `brooswit-minecraft` NeoForge 1.21.1 / Java 21
mod repo: Gradle build, CI, and the org's `changelog.d` + GitHub-release
conventions, copied verbatim from the sibling mods (`dynamic-despawn`,
`dynamic-backpacks`) that proved them out. This repo is not itself a mod —
`template/` is a skeleton with placeholders; `instantiate.py` fills them in
to produce a new mod repo's starting content.

## What's in `template/`

- Gradle build targeting NeoForge 1.21.1, loader floor `21.1.250`
  (`gradle.properties`, expanded into `neoforge.mods.toml`).
- `.github/workflows/ci.yml`: build + the org's reusable release gate
  (`brooswit-factory/release-gate/.github/workflows/gate.yml@v1`), pinned
  `@v1` — the only build gate, no local build/test policy.
- `.github/workflows/release.yml`: on push to `main`, tags and publishes a
  GitHub release from `changelog.d/` fragments. No Modrinth publishing (see
  "Extending" below if you need it).
- `changelog.d/README.md` + `CHANGELOG.md`: the per-PR fragment convention.
- A minimal `@Mod` class that registers and logs on load — no gameplay.
- Standard `LICENSE` (MIT), `README.md`, `.gitignore`.

Nothing in `template/` is meant to build as-is: its placeholders
(`__MOD_ID__`, `__MOD_NAME__`, `__MOD_SLUG__`, `__MOD_CLASS__`,
`__MOD_DESCRIPTION__`) aren't valid identifiers until `instantiate.py` fills
them in. This repo's own CI instead instantiates a sample mod and builds
*that*, as the regression test for the template mechanism.

## Instantiating a new mod repo

1. Confirm the repo name is free, then create the new (empty) GitHub repo,
   e.g. `gh repo create brooswit-minecraft/dynamic-widgets --public`, and
   clone it locally into an empty directory.
2. From a checkout of this template repo, run:

   ```sh
   python3 instantiate.py /path/to/dynamic-widgets \
     --slug dynamic-widgets \
     --name "Dynamic Widgets" \
     --description "Widgets that do a thing." \
     --jira-key MINECRAFT-999
   ```

   `--slug` is kebab-case and becomes the repo/root-project name. `mod_id`
   (`dynamicwidgets`) and the main class (`DynamicWidgetsMod`) are derived
   from it automatically — you don't pass them separately. `--jira-key` is
   optional; if given, it seeds `changelog.d/<jira-key>.md` for this
   scaffold PR (required because the PR touches `src/`), so the release gate
   doesn't trip on the scaffold.
3. `cd` into the new repo. If it had zero commits before this (a genuinely
   brand-new repo), seed `main` with an empty root commit first and say so
   in the PR description — see `dynamic-despawn`'s PR #1 for the pattern.
4. Commit, push a branch, open a PR, and let CI run — no local build/test
   per the org's policy (push, open the PR, read CI, fix forward).
5. Fill in the mod's real description in `src/main/java/.../*Mod.java`,
   `README.md`, and `neoforge.mods.toml` beyond what you passed to
   `--description` if needed, then build out gameplay logic.

## Required secrets

None. `release.yml` only uses the implicit `GITHUB_TOKEN`
(`${{ github.token }}`), and the release-gate reusable workflow needs no
repo secrets either. Nothing here needs copying from another repo.

## Extending: Modrinth publishing

This template deliberately does not include Modrinth publishing — it's
extra surface not every mod needs, and only one sibling (`dynamic-atmosphere`)
currently uses it. If a new mod needs it, copy `release.yml` and
`modrinth-draft-create.yml` from `dynamic-atmosphere` instead/in addition,
and set the `MODRINTH_TOKEN` repo secret (do not copy the token value
itself — get a fresh one or reuse the org's existing secret by name only).

## Running the tests in this repo

```sh
python3 -m unittest test_instantiate.py
python3 -m unittest discover -s template/scripts
```

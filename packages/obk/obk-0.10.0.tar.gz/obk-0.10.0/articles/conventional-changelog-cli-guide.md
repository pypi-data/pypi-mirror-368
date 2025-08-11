# Conventional Changelog CLI — Practical Guide

This is a hands-on guide for `conventional-changelog-cli` (the Node.js tool that generates a `CHANGELOG.md` from conventional commits).

* * *

## 1) What it does (and doesn’t)

* **Generates** changelog text from your git history (commits + tags).
    
* **Doesn’t** bump versions or create tags by itself (use `standard-version` if you want that automation).
    
* Works best when you follow a conventional commit style (e.g., Angular or Conventional Commits).
    

* * *

## 2) Install

```bash
# project-local (recommended)
npm i -D conventional-changelog-cli

# or globally
npm i -g conventional-changelog-cli
```

Verify:

```bash
npx conventional-changelog --help
```

* * *

## 3) Quick start (most common)

Initialize (creates a new `CHANGELOG.md` using your prior tags):

```bash
npx conventional-changelog -p angular -i CHANGELOG.md -s
```

* `-p angular` → preset. Common options: `angular`, `conventionalcommits`, `atom`, `ember`, `eslint`, `jquery`.
    
* `-i CHANGELOG.md` → input file. Will create it if missing.
    
* `-s` → “same file”: write back to the input file.
    

Update later (append new entries since the last tag):

```bash
npx conventional-changelog -p angular -i CHANGELOG.md -s
```

(The same command is repeatable; it only adds what’s new since your latest semver tag.)

* * *

## 4) Typical release flow

1. **Ensure commits are conventional** (see §5).
    
2. **Create a tag** that reflects the release version:
    
    ```bash
    git tag v1.4.0
    git push --tags
    ```
    
3. **Generate/update changelog**:
    
    ```bash
    npx conventional-changelog -p angular -i CHANGELOG.md -s
    ```
    
4. **Commit the changelog**:
    
    ```bash
    git add CHANGELOG.md
    git commit -m "docs(changelog): 1.4.0"
    git push
    ```
    

> Tip: If you prefer to generate notes **before** tagging, pass a range (see §8) or use `--commit-path` for partial histories.

* * *

## 5) Commit message format (Angular preset)

```
type(scope): short summary

body (optional)

BREAKING CHANGE: description (optional)
```

* Common **types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `build`, `ci`.
    
* Examples:
    
    * `feat(parser): add YAML parser`
        
    * `fix(api): handle 400 errors`
        
    * `feat!: drop Node 16 support` (the `!` marks a breaking change)
        
    * Include a footer line like: `BREAKING CHANGE: config file renamed to .obkrc`
        

The preset maps these to **CHANGELOG** sections like Features, Bug Fixes, and highlights breaking changes.

* * *

## 6) Useful CLI flags

* `-p, --preset <name>`: choose a preset (`angular`, `conventionalcommits`, …).
    
* `-r, --release-count <n>`: number of releases to generate (default 1).  
    Use `-r 0` to regenerate **all** releases from start.
    
* `-i, --infile <file>` and `-s, --same-file`: read/write the same file.
    
* `-k, --pkg <path>`: path to `package.json` (used for version detection if needed).
    
* `--commit-path <path>`: only consider commits that affect a subdirectory.
    
* `--append` / `--output-unreleased`: additional output behaviors.
    

* * *

## 7) Add npm scripts (so your team runs one command)

```json
{
  "scripts": {
    "changelog": "conventional-changelog -p angular -i CHANGELOG.md -s",
    "changelog:all": "conventional-changelog -p angular -i CHANGELOG.md -s -r 0"
  }
}
```

Then:

```bash
npm run changelog
```

* * *

## 8) Advanced: generate for a specific range

* Since a given tag:
    
    ```bash
    git describe --tags --abbrev=0   # prints last tag, e.g., v1.3.0
    npx conventional-changelog -p angular -i CHANGELOG.md -s --tag-prefix v --release-count 0
    ```
    
* Between two tags (useful for backfills):
    
    ```bash
    git log v1.2.0..v1.3.0 --oneline  # sanity check commits
    npx conventional-changelog -p angular -i CHANGELOG.md -s -r 0 \
      --lerna-package "" # (omit for single-package repos; see §10 for monorepos)
    ```
    

> Note: The CLI itself doesn’t expose a `--from`/`--to` pair; ranges are typically handled by tags + release counts, or by piping via programmatic APIs. In practice, `-r 0` + correct tag order covers most needs.

* * *

## 9) Configuration file (optional)

Create `.conventional-changelogrc` (JSON or YAML) in your repo root to avoid repeating flags:

```json
{
  "preset": "angular",
  "outputUnreleased": false,
  "releaseCount": 1
}
```

Then just run:

```bash
npx conventional-changelog -i CHANGELOG.md -s
```

You can also customize **sections**, **commit types**, or **note keywords** by switching to the programmatic API (or by using an extended preset).

* * *

## 10) Monorepos (lerna/pnpm workspaces)

* For a **single aggregated changelog** at the root, run the CLI at repo root (it will include all commits).
    
* For **per-package** changelogs, run the CLI in each package directory with `--commit-path packages/pkg-a` so only matching commits are considered:
    
    ```bash
    npx conventional-changelog -p angular -i packages/pkg-a/CHANGELOG.md -s --commit-path packages/pkg-a
    ```
    
* Tools like **changesets** or **lerna** can orchestrate this at scale. If you move to automated versioning, consider `changesets` or `standard-version` for the bump+tag+changelog workflow.
    

* * *

## 11) CI usage

* Run only on release/tag events, or on main before cutting a release:
    
    * Ensure tags are fetched: `git fetch --tags --force`
        
    * Generate: `npx conventional-changelog -p angular -i CHANGELOG.md -s`
        
    * Commit/push back (if desired) or attach the generated notes to a GitHub Release.
        
* Alternatively, generate locally and keep the changelog in the release PR.
    

* * *

## 12) Troubleshooting

**Changelog is empty**

* You don’t have semver **tags** (e.g., `v1.0.0`). Create and push one, then rerun.
    
* Commits don’t match the preset’s **types** or format. Fix future commits; for history, you can squash/reword or accept that earlier entries won’t be included.
    

**Wrong sections or missing breaking changes**

* Ensure commit messages use the preset’s **types** and include `BREAKING CHANGE:` footer or `!` after the type/scope.
    

**Monorepo: unrelated commits appear**

* Use `--commit-path` to limit which commits are considered for a package’s changelog.
    

**Need to regenerate everything**

* Use `-r 0` to rebuild all releases into the file.
    

* * *

## 13) “conventional-changelog” vs “standard-version”

* **conventional-changelog-cli**: only **writes the changelog** from existing commits/tags.
    
* **standard-version**: **bumps version**, **creates a tag**, and **updates the changelog** in one step. If you want a one-stop release command, consider:
    
    ```bash
    npm i -D standard-version
    npx standard-version --preset angular
    ```
    

* * *

## 14) Minimal checklist

*  Team commits follow the preset (e.g., Angular).
    
*  You use semver tags (`vX.Y.Z`) in git.
    
*  Add an npm script for the CLI.
    
*  Generate `CHANGELOG.md` on each release.
    
*  (Optional) Wire it into CI or a release script.
    

* * *

If you want, tell me:

* your current preset (Angular vs Conventional Commits),
    
* whether you tag before or after generating notes,
    
* single-repo vs monorepo,
    

…and I’ll tailor the exact commands and a ready-to-paste `package.json` script block for your setup.

* * *

**You:**

is this command represented `conventional-changelog -p angular -i CHANGELOG.md -s`?

* * *

**ChatGPT:**

Yes — that command is the **core usage** of `conventional-changelog-cli` in its most common form.

It breaks down like this:

| Flag / Arg | Meaning |
| --- | --- |
| `-p angular` | Use the **Angular preset** commit format (types like `feat`, `fix`, `docs`, etc.). |
| `-i CHANGELOG.md` | Input file for the changelog. If it doesn’t exist yet, it will be created. |
| `-s` | “Same file” — overwrite the file specified with `-i` instead of writing output to stdout. |

What it does:

* Looks at your **git tags** and **conventional commit messages**.
    
* Generates changelog text in **Angular preset style**.
    
* Writes or appends it into `CHANGELOG.md`.
    
* Only includes commits since the **most recent tag** (unless you use `-r 0` to regenerate all).
    

This is basically the “representative” single command you’d run for a typical project following Angular-style conventional commits.

If you want, I can show you the **full expanded equivalent** of that shorthand with long flags so it’s more explicit.

## Addendum — Only “Features” and “Fixes”, no tags, no links, and “none” placeholders

This setup:

* Keeps only **Features** (`feat`) and **Fixes** (`fix`) sections.
    
* **Removes tags** like `feat:` / `fix:` from bullets.
    
* **Removes all links** (commit, compare, issues, and any markdown links in text).
    
* Prints **“none”** under Features or Fixes if there are no commits of that type.
    
* Works for first run with **no tags** (adds a header stub).
    

### 1) `.conventional-changelogrc.js`

```js
// .conventional-changelogrc.js
const TYPE_PREFIX_RE =
  /^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(!:)?(\([^)]+\))?:\s*/i;
const MD_LINK_RE = /\[([^\]]*?)\]\((?:[^)]+)\)/g;

module.exports = {
  writerOpts: {
    // Never autolink issues/PRs
    linkReferences: false,

    // Render exactly the two sections we want, with "none" fallbacks
    mainTemplate: [
      '## {{#if version}}{{version}}{{else}}0.0.0{{/if}} ({{date}})',
      '',
      '#### Features',
      '{{#if features.length}}',
      '{{#each features}}* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}',
      '{{/each}}',
      '{{else}}* none',
      '{{/if}}',
      '',
      '#### Fixes',
      '{{#if fixes.length}}',
      '{{#each fixes}}* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}',
      '{{/each}}',
      '{{else}}* none',
      '{{/if}}',
      ''
    ].join('\n'),

    // Build the `features` and `fixes` arrays for the template
    finalizeContext: (context, writerOpts, commits) => {
      const features = [];
      const fixes = [];
      for (const c of commits) {
        if (c && c.type === 'Features') features.push(c);
        else if (c && c.type === 'Fixes') fixes.push(c);
      }
      context.features = features;
      context.fixes = fixes;
      return context;
    },

    // Keep only feat/fix; strip tag prefixes and any markdown links
    transform: (c) => {
      if (!c) return;
      const commit = { ...c, hash: null, references: [] };

      // map Angular types to our section names
      if (commit.type === 'feat') commit.type = 'Features';
      else if (commit.type === 'fix') commit.type = 'Fixes';
      else return; // drop every other type (docs/chore/ci/etc.)

      if (typeof commit.subject === 'string') {
        let s = commit.subject.replace(TYPE_PREFIX_RE, ''); // drop "feat:" / "fix(scope):"
        s = s.replace(MD_LINK_RE, '$1').trim();            // strip any [text](url)
        commit.subject = s;
      }

      // also scrub notes just in case (BREAKING CHANGE)
      if (Array.isArray(commit.notes)) {
        commit.notes = commit.notes.map(n => ({
          ...n,
          text: typeof n.text === 'string' ? n.text.replace(MD_LINK_RE, '$1') : n.text
        }));
      }
      return commit;
    }
  }
};
```

### 2) Script to run

Add/adjust your script so we still use the Angular parser but our custom writer:

```json
"scripts": {
  "changelog": "conventional-changelog -p angular -i CHANGELOG.md -s --config .conventional-changelogrc.js --no-link-compare"
}
```

### 3) Generate

```bash
npm run changelog
```

**Result format (example):**

```
## 0.10.0 (2025-08-11)

#### Features
* add dependency injection, agent task discovery, and codex automation features
…

#### Fixes
* none
```

This keeps your changelog laser-focused on what shipped (Features) and what got repaired (Fixes), with clean, link-free bullets.
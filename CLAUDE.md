# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

JackBot is a [Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot)-based wiki bot that performs automated formatting, linking, and maintenance tasks across multiple Wikimedia projects (Wikipedia, Wiktionary, Wikibooks, Wikiversity, Wikinews, Wikiquote, Wikisource, Wikivoyage, Commons).

The bot's core design principle: **parse wiki pages without a tree** — this tolerates malformed pages but requires care around nested templates and tags.

## Setup

```bash
# Clone with Pywikibot submodule
git clone https://github.com/JackPotte/JackBot.git
cd JackBot
devops/update_Pywikibot.sh   # initializes the core/ Pywikibot submodule

# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure authentication (copy and fill in credentials)
cp user-config.py.dist user-config.py
# Also create user-password.py with BotPassword credentials
```

The `core/` directory is the Pywikibot installation (a git submodule). Bot scripts are run via `core/pwb.py`.

## Running tests

```bash
python tests/fr_wiktionary_functions_test.py
```

There is currently only one test file, covering `fr_wiktionary_functions.py`. Tests use `unittest` and read sample files from a `samples/` directory (relative to the test file).

## Running scripts

All homemade scripts are invoked through `core/pwb.py`:

```bash
python core/pwb.py src/<script_name> [options]
```

Common CLI flags used across scripts:
- `-d` / `-debug` — enable debug output
- `-t` / `-test` — run on `User:JackBot/test`
- `-cat` — iterate pages from a category
- `-nocat` — iterate uncategorized pages
- `-p <PageName>` — process a single named page
- `-f <family>` / `-family:<family>` — target wiki family (wiktionary, wikipedia, wikibooks…)
- `-l <lang>` / `-lang:<lang>` — target language code

See `JackBot.sh` for the full list of active daily operations and commented-out examples of native Pywikibot script invocations.

## Code architecture

### Execution flow

Each top-level script in `src/` (e.g. `fr_wikipedia_format.py`) follows this pattern:
1. Imports shared helpers from `src/lib/` (via `sys.path.append`)
2. Instantiates a `PageProvider` with a `treat_page` callback and a site object
3. `PageProvider` fetches pages from a source (category, XML dump, recent changes, search, etc.) and calls `treat_page` for each
4. `treat_page` applies regex-based text transformations and calls `save_page` if the content changed

### Key shared modules (`src/lib/`)

| File | Purpose |
|---|---|
| `PageProvider.py` | Pywikibot middleware — iterates pages from all Wikimedia sources (category, XML dump, search, recent changes, user contributions, etc.) |
| `page_functions.py` | Core utilities: `get_global_variables()` for CLI arg parsing, `get_content_from_page()`, `save_page()`, `global_operations()`, section parsing helpers |
| `html2unicode.py` | Converts HTML entities to Unicode characters |
| `default_sort.py` | Handles `{{DEFAULTSORT}}` template logic |
| `hyperlynx.py` | Validates and marks broken hyperlinks |
| `templates_translator.py` | Translates citation templates (e.g. `{{Cite web}}` → `{{Lien web}}`) |
| `languages.py` | Language-related utilities |
| `template_functions.py` | Generic template manipulation helpers |

### Wiktionary-specific layer (`src/lib/` — wiktionary scripts)

The fr.wiktionary scripts are the most complex part of the codebase:
- `fr_wiktionary_format.py` — main formatting script
- `fr_wiktionary_functions.py` — transformation functions (the tested ones)
- `fr_wiktionary_templates.py` — template definitions
- `fr_wiktionary_create_inflexions.py` / `fr_wiktionary_import_inflexions.py` — generate/import inflected forms
- `fr_wiktionary_import_from_commons.py` — import audio files from Wikimedia Commons

### Deployment (Wikimedia Toolforge)

The `devops/` scripts manage deployment on [Toolforge](https://wikitech.wikimedia.org/wiki/Portal:Toolforge). The bot runs there via cron jobs. Key scripts:
- `toolforge_bootstrap_venv.sh` — creates the Python venv on Toolforge
- `toolforge_set_cronjobs.sh` — configures cron jobs
- `toolforge_start.sh` — starts the bot
- `WP.sh`, `WT.sh`, `WB.sh`, etc. — per-wiki shortcut launchers

## Code style

- Max line length: **150 characters**
- Python 3.7+ (configured in `.sourcery.yaml`)
- PEP 8 preferred but not strictly enforced
- `fr_wikiversity_format.py` is excluded from Sourcery analysis

---
description: Create a new prompt file from a template or plain text
argument-hint: "[<tmpl-name>|<tmpl-file>] [--data '<json>'] ['<user-prompt>']"
---
# /arx:prompt-new — Create New Prompt File

Create a rendered prompt file in `$ARX_WORK_DOCS`, optionally from a reusable template.

## Usage

```
/arx:prompt-new [<tmpl-name>|<tmpl-file-path>] [--data '<json-string>'] ['<user-command-prompt>']
```

Maps to:

```bash
arx prompt new [TEMPLATE] [PROMPT_TEXT] [--data JSON] [--name NAME] [--subdir DIR] [--dry-run] [-v]
```

## Parameters

| Arg / Option | Required | Description |
|---|---|---|
| `TEMPLATE` | no | Template name (resolved from `$ARX_AGENT_TOOLS/templates/` or `$AGENTRX_SOURCE/templates/`) or a direct file path |
| `PROMPT_TEXT` | no* | The user's intent/command text — available as `[[prompt]]` in the template |
| `--data` / `-D` | no | Inline JSON string merged into the render context |
| `--name` / `-n` | no | Base filename override (default: derived from first 3 words of PROMPT_TEXT) |
| `--subdir` | no | Output subdirectory under `$ARX_WORK_DOCS` (overrides template front-matter `subdir`) |
| `--dry-run` | no | Preview rendered output and target path without writing |
| `-v` | no | Verbose output |

\* At least one of TEMPLATE or PROMPT_TEXT must be given.

If TEMPLATE is given but doesn't resolve to a file, it is treated as PROMPT_TEXT (backward-compat).

## Processing Flow

```
Input args
    │
    ▼
1. Resolve template (name → search dirs → path)
    │
    ▼
2. Strip front matter → extract subdir / short_name / script
    │
    ▼
3. [optional] Run front-matter script → augment context
   (script receives context JSON on stdin; emits JSON on stdout)
    │
    ▼
4. ARX render: expand $ENV_VARs + substitute <ARX [[expr]] /> tags
   (PROMPT_TEXT available as [[prompt]])
    │
    ▼
5. [?] Write → $ARX_WORK_DOCS/{subdir}/{short_name}_{YY-MM-DD-H}.md
```

Mustache `{{...}}` block directives in the template body are **passed through unchanged** — structural evaluation is handled agent-side.

## Template Front Matter

```yaml
---
arx: template
subdir: vibes          # output subdir under ARX_WORK_DOCS  (default: vibes)
short_name: my_prompt  # base filename  (default: derived from prompt text)
script: ./_agents/scripts/agentrx/enrich.sh  # optional context script
---
# <ARX [[prompt]] />

Ticket: <ARX [[ticket | "none"]] />
```

## Output

Files are created as: `$ARX_WORK_DOCS/{subdir}/{short_name}_{YY-MM-DD-H}.md`

## Examples

```
/arx:prompt-new "Implement user authentication"
# → ARX_WORK_DOCS/vibes/implement_user_auth_26-02-22-14.md  (plain text)

/arx:prompt-new vibes "Refactor the payment module"
# → renders vibes template with [[prompt]] = "Refactor the payment module"

/arx:prompt-new ./templates/delta.md "Fix the cache bug" --data '{"ticket":"ENG-42"}'
# → renders delta template; [[ticket]] → "ENG-42"

/arx:prompt-new vibes "Debug login" --dry-run
# → preview only, no file written
```

## Implementation

When executing this command:

1. Resolve `TEMPLATE` → search `$ARX_AGENT_TOOLS/templates/`, `$AGENTRX_SOURCE/templates/`, or direct path; if not found treat arg as `PROMPT_TEXT`.
2. Parse front matter from template file (if any).
3. Build context: `--data` JSON < stdin JSON (stdin wins); add `"prompt": PROMPT_TEXT`.
4. If `script` key in front matter → run it, merge output JSON into context.
5. Render body through ARX renderer (`render_file` from `agentrx.render`).
6. Determine output path from `subdir` (front-matter → `--subdir` flag → default `vibes`) and `short_name`.
7. Write rendered body to `$ARX_WORK_DOCS/{subdir}/{short_name}_{timestamp}.md` (unless `--dry-run`).
8. Print the created file path.

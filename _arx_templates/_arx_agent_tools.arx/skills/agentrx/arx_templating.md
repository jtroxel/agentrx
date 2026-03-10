---
arx: skill
version: 1
description: ARX templating syntax reference for agents reading and writing template files
---
# ARX Templating Syntax

A minimal markdown-compatible templating syntax using `<ARX ... />` tags with mustache-inspired `[[...]]` expressions.

## Mustache Tags
Because CLI commands often use the same templates as a preprocessor, the syntax is designed to avoid conflicts with common mustache parsers by using `<ARX ... />` tags instead of `{{...}}`.
IMPORTANT - for all agents processing an ARX template...
When encountering a mustache syntax block: UNLESS the interpolation of the mustache block is *obvious* based off of input parameters, the block should be IGNORED (remmoved) in the outputted text.

## Front Matter

All ARX templates **must** include YAML front matter. This identifies the file as a template and provides default metadata.
### Example Front Matter
```yaml
arx: template
description: Brief description of template purpose
inputs:
  - name: tasks
    type: object
    default: { title: "Task Title", id: 123, completed: false, description: "Task description" }
  - name: parents
    type: array
    required: false
    default: []
```

## Template Detection

ARX templates can be identified by **either** method:

### 1. Front Matter Detection (Preferred)

Check for `arx: template` in YAML front matter:

```python
import re
import yaml

def is_arx_template(content: str) -> bool:
    match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)
    if match:
        fm = yaml.safe_load(match.group(1))
        return fm.get('arx') == 'template'
    return False
```

### 2. Tag Scanning (Fallback)

Scan for ARX tag patterns when front matter is missing:

```python
import re

ARX_PATTERN = re.compile(r'<ARX\s+.*?/>')

def has_arx_tags(content: str) -> bool:
    return bool(ARX_PATTERN.search(content))
```

### Detection Patterns

| Pattern | Matches |
|---------|---------|
| `<ARX\s+\[\[.+?\]\]\s*/>` | Variable tags |
| `<ARX\s+\[\[[#^*].+?\]\]:\s*/>` | Block openers |
| `<ARX\s+/:\s*/>` | Block closers |
| `<ARX\s+@".+?"\s*/>` | Includes |

### Combined Detection

```python
def detect_arx_template(content: str) -> dict:
    """Detect ARX template and return metadata."""
    result = {'is_template': False, 'method': None, 'front_matter': None}

    # Try front matter first
    fm_match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)
    if fm_match:
        fm = yaml.safe_load(fm_match.group(1))
        if fm.get('arx') == 'template':
            result['is_template'] = True
            result['method'] = 'front_matter'
            result['front_matter'] = fm
            return result

    # Fallback to tag scanning
    if ARX_PATTERN.search(content):
        result['is_template'] = True
        result['method'] = 'tag_scan'

    return result
```

---

## Data Sources

Templates accept data from:
- **YAML/JSON** - Inline or file-based context
- **ENV variables** - `[[env.VAR_NAME]]`
- **Workflow outputs** - Previous step results via `[[step.output]]`

---

## Variable Substitution

```html
<ARX [[variable]] />
<ARX [[user.name]] />
<ARX [[env.API_KEY]] />
<ARX [[items.0.title]] />
```

| Syntax | Description |
|--------|-------------|
| `[[var]]` | Simple variable |
| `[[obj.key]]` | Nested property (dot notation) |
| `[[arr.0]]` | Array index access |
| `[[env.NAME]]` | Environment variable |

**Default values:**
```html
<ARX [[user.name | "Guest"]] />
<ARX [[config.timeout | 30]] />
```

---

## Conditionals

### Boolean Check
```html
<ARX [[#enabled]] />          <!-- renders "true" or "false" -->
```

### Conditional Block
```html
<ARX [[#condition]]: />
  Content shown if truthy
<ARX /: />
```

### If/Else Block
```html
<ARX [[#user.admin]]: />
  Admin content here
<ARX [:] />
  Regular user content
<ARX /: />
```

### Negation
```html
<ARX [[^condition]]: />
  Content shown if falsy
<ARX /: />
```

| Sigil | Meaning |
|-------|---------|
| `#` | Truthy check |
| `^` | Falsy check (negation) |
| `[:] ` | Else branch |
| `/:` | End block |

---

## Loops

```html
<ARX [[*items]]: />
  Item: <ARX [[.]] />
<ARX /: />
```

### With Named Iterator
```html
<ARX [[*users as user]]: />
  Name: <ARX [[user.name]] />
  Email: <ARX [[user.email]] />
<ARX /: />
```

### With Index
```html
<ARX [[*tasks as task, idx]]: />
  <ARX [[idx]] />. <ARX [[task.title]] />
<ARX /: />
```

| Syntax | Description |
|--------|-------------|
| `[[*list]]:` | Iterate, current item is `[[.]]` |
| `[[*list as x]]:` | Iterate with named variable |
| `[[*list as x, i]]:` | Iterate with index |

---

## Includes

```html
<ARX @"path/to/file.md" />
<ARX @"_partials/header.md" />
```

### With Context
```html
<ARX @"template.md" { title: [[doc.title]], count: 5 } />
```

---

## Quick Reference

| Tag | Purpose | Example |
|-----|---------|---------|
| `<ARX [[x]] />` | Variable | `<ARX [[user.name]] />` |
| `<ARX [[x \| def]] />` | Default value | `<ARX [[name \| "Anonymous"]] />` |
| `<ARX [[#x]] />` | Boolean output | `<ARX [[#active]] />` |
| `<ARX [[#x]]: />` | If block start | `<ARX [[#logged_in]]: />` |
| `<ARX [[^x]]: />` | Unless block | `<ARX [[^errors]]: />` |
| `<ARX [:] />` | Else | |
| `<ARX /: />` | End block | |
| `<ARX [[*x]]: />` | Loop start | `<ARX [[*items]]: />` |
| `<ARX [[.]] />` | Current item | Inside loop |
| `<ARX @"file" />` | Include | `<ARX @"header.md" />` |

---

## Full Example

**Template File (`report_template.md`):**
```markdown
---
arx: template
version: 1
description: Generate a formatted report from structured data
inputs:
  - name: report
    type: object
    required: true
    description: Report data with title, date, sections
  - name: user
    type: object
    required: true
    description: Current user context
  - name: sections
    type: array
    required: false
    default: []
---
# <ARX [[report.title]] />

Author: <ARX [[user.name | "Unknown"]] />
Date: <ARX [[report.date]] />

<ARX [[#user.admin]]: />
*Administrative view enabled*
<ARX /: />

<ARX [[#sections]]: />
## Sections

<ARX [[*sections as sec, n]]: />
### <ARX [[n]] />. <ARX [[sec.heading]] />

<ARX [[sec.content]] />

<ARX [[#sec.items]]: />
<ARX [[*sec.items as item]]: />
- <ARX [[item]] />
<ARX /: />
<ARX /: />

<ARX /: />
<ARX [[^sections]]: />
*No sections available.*
<ARX /: />

---
<ARX @"_partials/footer.md" { year: 2026 } />
```

**Output:**
```markdown
# Monthly Summary

Author: Jane
Date: 2026-02-08

*Administrative view enabled*

## Sections

### 0. Overview

This month was productive.

- Completed A
- Started B

### 1. Metrics

All targets met.

---
[footer content]
```

---

## ARX Document Types

All AgentRx markdown files use front matter to declare their type:

| `arx` value | Purpose |
|-------------|---------|
| `template` | Renderable template with ARX tags |
| `context` | Static context document (no rendering) |
| `prompt` | Agent prompt definition |
| `skill` | Skill/command documentation |
| `config` | Configuration file |

**Example context document:**
```yaml
---
arx: context
description: Project coding standards
tags: [standards, guidelines]
---
# Coding Standards
...
```

**Example prompt:**
```yaml
---
arx: prompt
description: Code review prompt
model: claude-sonnet
inputs:
  - name: code
    type: string
    required: true
---
Review the following code...
<ARX [[code]] />
```

---

## Prompt Template Front Matter

Templates used with `arx prompt new` support additional front-matter fields:

| Field | Type | Default | Description |
|---|---|---|---|
| `subdir` | string | `vibes` | Output subdirectory under `$ARX_WORK_DOCS` |
| `short_name` | string | *(derived from prompt text)* | Base name for the output file |
| `script` | string | *(none)* | Path to a context-augmenting script (see below) |

### Context script protocol

When `script` is set, `arx prompt new` runs it as a subprocess:

- **stdin**: current context dict serialised as JSON
- **stdout**: JSON object — merged into context with highest priority
- **exit code 0**: success; non-zero aborts with an error

```yaml
---
arx: template
subdir: vibes
script: ./_agents/scripts/agentrx/enrich-context.sh
---
# <ARX [[prompt]] />
```

---

## CLI Usage

The `arx` CLI processes templates at two points:

### `arx prompt new [TEMPLATE] [PROMPT_TEXT] [--data JSON]`

Full render pipeline:

1. **Resolve template** — name searched in `$ARX_AGENT_TOOLS/templates/` then `$AGENTRX_SOURCE/templates/`; path accepted directly.
2. **Strip front matter** — metadata extracted; body is the render input.
3. **Run context script** — if `script` key present in front matter, subprocess called to augment context.
4. **ARX render** — `<ARX [[expr]] />` tags substituted; env vars expanded; unresolvable tags preserved.
5. **Write** — output to `$ARX_WORK_DOCS/{subdir}/{short_name}_{timestamp}.md`.

```bash
# Plain prompt (no template)
arx prompt new "Implement user authentication"

# From named template + inline data
arx prompt new vibes "Refactor the cache layer" --data '{"ticket":"ENG-99"}'

# From file path, dry-run preview
arx prompt new ./templates/delta.md "Fix the login bug" --dry-run

# The [[prompt]] tag in the template body is replaced by PROMPT_TEXT
```

### `arx prompt do [PROMPT_FILE] [--data JSON] [-D JSON]`

Renders an existing prompt file (already in `ARX_WORK_DOCS`) and sends it to stdout or a file:

```bash
arx prompt do my_prompt.md --data context.json
arx prompt do my_prompt.md -D '{"name":"Alice"}'
cat extra.json | arx prompt do my_prompt.md   # stdin highest priority
```

### Data priority (both commands)

`--data-file` < `--data` / `-D` inline JSON < `stdin`  (higher wins on key collision)

---

## Render Phases

ARX templates can be processed in two distinct phases: **`new`** (when creating a prompt
file with `arx prompt new`) and **`do`** (when rendering a saved prompt with `arx prompt do`).

Variable tags can be scoped to a phase using a `:phase` marker placed after `]]` and before `/>`:

| Syntax | Resolved during |
|---|---|
| `<ARX [[expr]] :new />` | `arx prompt new` only |
| `<ARX [[expr]] :do />` | `arx prompt do` only |
| `<ARX [[expr]] />` | Eager — any phase when data is present |

Phase-tagged tags that don't match the active phase are **preserved verbatim** so the
correct phase can still resolve them later.

### Example: dual-lifecycle template

```markdown
---
arx: template
subdir: vibes
---
# <ARX [[prompt]] :new />

Assigned to: <ARX [[user.name]] :do />
Ticket: <ARX [[ticket | "none"]] :new />
API key: <ARX [[env.API_KEY]] :do />
```

After `arx prompt new tmpl.md "Fix auth" --data '{"ticket":"ENG-42"}'`:

```markdown
# Fix auth
Assigned to: <ARX [[user.name]] :do />   ← preserved for do phase
Ticket: ENG-42
API key: <ARX [[env.API_KEY]] :do />     ← preserved for do phase
```

After `arx prompt do <saved-file> -D '{"user":{"name":"Alice"}}'`:

```markdown
# Fix auth
Assigned to: Alice
Ticket: ENG-42
API key: sk-...   ← resolved from environment
```

---

## Design Principles

1. **Terse** - Single `<ARX ... />` tag format
2. **Mustache-inspired** - `[[...]]` avoids conflicts with `{{...}}`
3. **Sigil-based** - `#` (if), `^` (unless), `*` (loop), `@` (include)
4. **Dot notation** - Nested access: `user.profile.name`
5. **Minimal closing** - All blocks end with `<ARX /: />`
6. **Front matter required** - All ARX documents declare type via `arx:` field


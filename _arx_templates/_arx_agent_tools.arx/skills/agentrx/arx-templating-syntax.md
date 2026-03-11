---
name: arx-templating-syntax
arx: context
version: 2
description: Detailed syntax reference for ARX Templating (Markdown-Native)
---

# ARX Templating Syntax Reference

ARX Templating is a Markdown-native syntax designed for interpolation by both **Programmatic Evaluators** (CLI/Scripts) and **Agentic Evaluators** (AI Agents).

## 1. Core Tag Structure
A tag always uses the following format:
```markdown
<ARX [[expression]] />
```

- **Outer Wrapper**: `<ARX ... />` (HTML-safe; ignored by Markdown parsers, legible to LLMs).
- **Inner Delimiters**: `[[ ... ]]` (Avoids collisions with standard `{{ }}` Mustache tags).

---

## 2. Expressions & Sigils

| Sigil | Type | Example | Description |
|-------|------|---------|-------------|
| *(none)* | **Variable** | `[[user.name]]` | Lookup value by key or dot-notation. |
| `#` | **If Block** | `[[#enabled]]:` | Renders if truthy; ends with `/:`. |
| `^` | **Unless** | `[[^errors]]:` | Renders if falsy; ends with `/:`. |
| `*` | **Loop** | `[[*items]]:` | Iterates; current item is `[[.]]`. |
| `@` | **Include** | `@"header.md"` | Inlines a file into the document. |
| `[:]` | **Else** | `[:]` | Logical branch within `#` or `^`. |
| `/:` | **End** | `/:` | Closes any logic block. |

---

## 3. Advanced Usage

### 3.1 Loops with Named Iterators
You can name the current item and index for better clarity:
```markdown
<ARX [[*tasks as task, i]]: />
  <ARX [[i]] />. <ARX [[task.title]] />
<ARX /: />
```

### 3.2 Escaping Control
- **`[[expr]]`**: Standard HTML-safe escaping (default).
- **`[[{expr}]]`**: Raw interpolation (no escaping). Use for snippets or Markdown blocks.

### 3.3 Default Values
```markdown
<ARX [[config.timeout | 30]] />
```

---

## 4. Evaluator Behavior (Implicit Resolution)

1.  **Strict Mode (CLI)**: If data for a tag is missing, the tool MUST preserve the tag verbatim (Punt).
2.  **Contextual Mode (AI)**: Agents should interpolate based on conversation context or placeholder intent.
3.  **Removal Rule**: Unresolved/non-obvious tags should be stripped by the *final* generator (the Agent) before the end-user sees them.

---
arx: skill
name: arx-render
description: Render ARX templates with context data
version: 1
tags: [templating, rendering, core]
inputs:
  - name: template
    type: string
    required: true
    description: Path to template file or inline template content
  - name: context
    type: object
    required: false
    description: Data context for rendering (YAML, JSON, or object)
  - name: output
    type: string
    required: false
    description: Output file path (defaults to stdout)
---

# Skill: arx-render

Render ARX templates by substituting variables, evaluating conditionals, iterating loops, and processing includes.

## Usage

```
/arx-render <template> [--context <file|inline>] [--output <file>]
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `template` | Yes | Template file path or `-` for stdin |
| `--context`, `-c` | No | Context data (YAML/JSON file or inline) |
| `--output`, `-o` | No | Output file (defaults to stdout) |
| `--env` | No | Include environment variables in context |
| `--strict` | No | Fail on undefined variables |

## Examples

```bash
# Render with YAML context file
/arx-render templates/report.md -c data.yaml

# Render with inline JSON context
/arx-render templates/email.md -c '{"user": {"name": "Jane"}}'

# Render to file with env vars
/arx-render templates/config.md -c settings.yaml --env -o output/config.md

# Pipe context from previous step
echo '{"items": [1,2,3]}' | /arx-render templates/list.md -c -
```

---

## Processing Steps

When this skill is invoked, follow these steps:

### 1. Load Template

```python
def load_template(path: str) -> tuple[dict, str]:
    """Load template, return (front_matter, body)."""
    content = read_file(path)

    # Parse front matter
    match = re.match(r'^---\n(.+?)\n---\n?(.*)', content, re.DOTALL)
    if match:
        front_matter = yaml.safe_load(match.group(1))
        body = match.group(2)
    else:
        front_matter = {}
        body = content

    return front_matter, body
```

### 2. Validate Template

```python
def validate_template(front_matter: dict, context: dict) -> list[str]:
    """Validate context against input schema. Return errors."""
    errors = []

    if front_matter.get('arx') != 'template':
        # Warn but continue - may be detected via tag scan
        pass

    for input_def in front_matter.get('inputs', []):
        name = input_def['name']
        required = input_def.get('required', False)

        if required and name not in context:
            errors.append(f"Missing required input: {name}")

    return errors
```

### 3. Build Context

```python
def build_context(
    context_input: dict,
    env: bool = False,
    front_matter: dict = None
) -> dict:
    """Build full rendering context."""
    ctx = {}

    # Apply defaults from front matter
    for input_def in (front_matter or {}).get('inputs', []):
        if 'default' in input_def:
            ctx[input_def['name']] = input_def['default']

    # Merge provided context
    ctx.update(context_input)

    # Add environment if requested
    if env:
        ctx['env'] = dict(os.environ)

    return ctx
```

### 4. Render Template

Process the template body by handling each ARX tag type:

#### Variable Substitution
```python
def render_variable(match: re.Match, ctx: dict) -> str:
    """Render [[variable]] or [[variable | default]]."""
    expr = match.group(1).strip()

    # Check for default value
    if ' | ' in expr:
        var_path, default = expr.split(' | ', 1)
        default = default.strip().strip('"\'')
    else:
        var_path = expr
        default = ''

    # Resolve dot notation
    value = resolve_path(ctx, var_path.strip())

    if value is None:
        return default
    return str(value)
```

#### Conditionals
```python
def render_conditional(block: str, ctx: dict, negate: bool = False) -> str:
    """Render [[#var]]: ... [[:]]: ... [/:] blocks."""
    # Parse condition variable
    condition = resolve_path(ctx, var_path)

    if negate:
        condition = not condition

    # Truthy check for objects/arrays
    if isinstance(condition, (list, dict)):
        condition = len(condition) > 0

    if condition:
        return render_body(if_block, ctx)
    elif else_block:
        return render_body(else_block, ctx)
    return ''
```

#### Loops
```python
def render_loop(block: str, ctx: dict) -> str:
    """Render [[*items]]: ... [/:] or [[*items as x, i]]: ... [/:] blocks."""
    output = []
    items = resolve_path(ctx, collection_path)

    if not items:
        return ''

    for idx, item in enumerate(items):
        loop_ctx = ctx.copy()
        loop_ctx['.'] = item  # Current item

        if iter_name:
            loop_ctx[iter_name] = item
        if index_name:
            loop_ctx[index_name] = idx

        output.append(render_body(loop_body, loop_ctx))

    return ''.join(output)
```

#### Includes
```python
def render_include(match: re.Match, ctx: dict, base_path: str) -> str:
    """Render @"file.md" or @"file.md" { key: val }."""
    include_path = resolve_include_path(match.group(1), base_path)

    # Parse inline context if present
    if inline_ctx_str:
        inline_ctx = parse_inline_context(inline_ctx_str, ctx)
        include_ctx = {**ctx, **inline_ctx}
    else:
        include_ctx = ctx

    # Recursively render included template
    fm, body = load_template(include_path)
    return render_body(body, include_ctx)
```

### 5. Output Result

```python
def output_result(rendered: str, output_path: str = None):
    """Write rendered content to file or stdout."""
    if output_path:
        write_file(output_path, rendered)
        return f"Rendered to: {output_path}"
    else:
        return rendered
```

---

## Tag Processing Order

Process tags in this order to handle nesting correctly:

1. **Includes** (`@"..."`) - Expand first to inline content
2. **Loops** (`[[*...]]`) - Outer to inner
3. **Conditionals** (`[[#...]]`, `[[^...]]`) - Outer to inner
4. **Variables** (`[[...]]`) - Last, after context is established

---

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing required input | Fail with error listing missing fields |
| Undefined variable | Empty string (or fail if `--strict`) |
| Include not found | Fail with path error |
| Malformed tag | Fail with line number and tag content |
| Unclosed block | Fail indicating expected `<ARX /: />` |

**Error format:**
```
ARX Error: <message>
  File: <path>
  Line: <number>
  Tag: <tag content>
```

---

## Regex Patterns

```python
# Match patterns for ARX tags
PATTERNS = {
    'variable': r'<ARX\s+\[\[([^\]#^*][^\]]*)\]\]\s*/>',
    'bool_out': r'<ARX\s+\[\[#([^\]]+)\]\]\s*/>',
    'if_open': r'<ARX\s+\[\[#([^\]]+)\]\]:\s*/>',
    'unless_open': r'<ARX\s+\[\[\^([^\]]+)\]\]:\s*/>',
    'else': r'<ARX\s+\[:\]\s*/>',
    'block_close': r'<ARX\s+/:\s*/>',
    'loop_open': r'<ARX\s+\[\[\*([^\]]+)\]\]:\s*/>',
    'include': r'<ARX\s+@"([^"]+)"(?:\s*\{([^}]+)\})?\s*/>',
    'current': r'<ARX\s+\[\[\.\]\]\s*/>',
}
```

---

## Agent Implementation Notes

When implementing this skill as an agent:

1. **Parse incrementally** - Process blocks from outermost to innermost
2. **Track scope** - Maintain variable scope stack for nested blocks
3. **Resolve paths safely** - Handle missing intermediate keys gracefully
4. **Preserve whitespace** - Maintain original formatting outside tags
5. **Report context** - On error, show surrounding template lines

### Minimal Render Loop

```python
def render(template_path: str, context: dict) -> str:
    # Load
    fm, body = load_template(template_path)

    # Validate
    errors = validate_template(fm, context)
    if errors:
        raise RenderError(errors)

    # Build context with defaults
    ctx = build_context(context, front_matter=fm)

    # Render
    return render_body(body, ctx)
```

---

## See Also

- [arx_templating.md](./arx_templating.md) - ARX syntax reference

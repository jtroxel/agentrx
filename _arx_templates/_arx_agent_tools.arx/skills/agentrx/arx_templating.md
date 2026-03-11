---
name: arx_templating
arx: skill
version: 2
description: ARX templating skill for agents reading and writing template files
---

# ARX Templating Skill

A minimal markdown-compatible templating syntax using `<ARX ... />` tags for automated workflows.

## Documentation
- [Syntax Reference](./arx-templating-syntax.md) - Full details on tags, sigils, and expressions.
- [Evaluator Logic](../../scripts/agentrx/arx_render.py) - Implementation of the "Implicit Resolution" pattern.

### Quick Start
To process a template locally with JSON data:
```bash
python3 ../../scripts/agentrx/arx_render.py template.md --data '{"user": "AI"}'
```

## Front Matter
Every ARX template should start with YAML front matter:
```yaml
arx: template
version: 2
description: Example template
```


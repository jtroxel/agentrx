# Prompt: design_and_document

Design and document a super simple markdown syntax for agent-based templating. The format should use terse HTML tags prefixed by `<ARX`. The syntax should support very basic control structures like if/then and for loops. Also variable substitution and include directives.
Inside the `<ARX` tags, the syntax should be similar to :mustache" templates, but should not confuse any mustache parsers since the tags are different. The goal is to have a simple way to create templates that can be rendered with data from the agent's context, without needing a full templating engine.

Templates could use additional text input (e.g.: yaml, json), ENV variables, or output data-structures from previous steps in the agent workflow as inputs for rendering.

**For Example (Only Suggested, use your judgement)**:
```html
<ARX [[variable]]" /> <!--simple variable substitution, supports dot notation for nested variables, e.g. [[user.name]] -->
<ARX [[# variable]] /> <!-- boolean variable, renders "true" or "false" -->
<ARX [[# variable]]: /> <!-- boolean start block" -- >
<ARX [[* variable]]: /> <!-- list or iterable, start block" -- >

```

Place documentation in a markdown file with examples of how to use the syntax, and a reference of the supported tags and their parameters. Location: `_agents/skills/agentrx/arx_templating.md`

---
*Created: 2026-02-08 08:00:00*

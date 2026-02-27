---
arx: command
name: prompt-do
description: Execute a prompt with optional data context
version: 1
argument-hint: [prompt-file] [--data <file>] [user-prompt-text]
---

# /arx:prompt-do - Execute Prompt with Data

Execute a prompt file with optional JSON data context. Can read data from a file or stdin.

## Usage

```bash
/arx:prompt-do [prompt-file] [options]

# Or via CLI
arx prompt-do [prompt-file] [options]

# With piped data
cat data.json | arx prompt-do

# With inline user prompt text
arx prompt-do my_prompt.md "What is the status of the project?"

```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `prompt-file` | No | N/A | Path to the prompt file to execute. |
| `user-prompt-text` | No | none | Inline prompt text to use instead of a prompt file. If both `prompt-file` and `user-prompt-text` are unset, the command errors. |
| `--data`, `-d` | No | none | Path to a JSON file with context data. When both `--data` and stdin are provided, they are merged (stdin takes precedence on key conflicts). |
| `--output`, `-o` | No | stdout | Write command output to the given file path instead of stdout. |
| `--dry-run` | No | false | Show the resolved execution plan (prompt file, merged data, output path) and exit without executing. |

## Examples

```bash
# Execute most recent prompt in ARX_PROMPTS
arx prompt-do

# Execute a specific prompt file
arx prompt-do my_prompt.md

# Provide inline prompt text instead of a file
arx prompt-do "Summarize the latest sprint status."

# Use a JSON data file for context
arx prompt-do my_prompt.md --data context.json

# Pipe JSON data from another command (stdin takes precedence)
curl -s https://api.example.com/data | arx prompt-do my_prompt.md

# Execute and append to history
arx prompt-do my_prompt.md --data context.json --history

# Write output to a file
arx prompt-do my_prompt.md --output result.txt

# Dry run to display resolved plan without running
arx prompt-do my_prompt.md --data context.json --dry-run
```

```bash
# Execute most recent prompt in ARX_PROMPTS
arx prompt-do

# Execute specific prompt file
arx prompt-do my_prompt_26-02-10-12.md

# Execute with JSON data file
arx prompt-do my_prompt.md --data context.json

# Pipe data from another command
cat api_response.json | arx prompt-do my_prompt.md

# Execute and log to history
arx prompt-do my_prompt.md --data context.json --history

# Dry run - show what would be executed
arx prompt-do my_prompt.md --data context.json --dry-run
```

## Data Input

Data can be provided in two ways:

### 1. File Input
```bash
arx prompt-do --data context.json
```

### 2. Stdin (Piped)
```bash
echo '{"user": "alice", "action": "create"}' | arx prompt-do

# Chain with other commands
curl -s https://api.example.com/data | arx prompt-do my_prompt.md
```

When both `--data` and stdin are provided, they are merged (stdin takes precedence for conflicting keys).

## Prompt File Selection

If no prompt file is specified:

1. Check `ARX_WORK_DOCS` environment variable for the project docs directory
2. Look in `$ARX_WORK_DOCS/vibes` for `.md` files
3. Use the most recent file by modification time

```bash
# Uses most recent prompt in $ARX_WORK_DOCS/vibes
export ARX_WORK_DOCS="docs/agentrx"
arx prompt-do --data context.json
```

## Git Commit Message
When done, set up a putative commit message with the prompt and brief summary of what was done.

## Implementation
`
When this command is executed:

1. Resolve prompt file path (explicit or most recent in ARX_PROMPTS)
2. Load data from:
   - `--data` file if specified
   - stdin if available and not a TTY
   - Merge both if present
3. Read and parse prompt file
4. If `--dry-run`, display execution plan and exit
5. Execute prompt (output to stdout or `--output` file)
6. If `--history`, append execution log to history directory
7. Return exit code 0 on success

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Prompt file not found |
| 2 | Data file not found or invalid JSON |
| 3 | ARX_PROMPTS directory not found |
| 4 | Write error (output or history) |

## See Also

- [prompt-new.md](./prompt-new.md) - Create new prompt files
- [arx_templating.md](../../skills/agentrx/arx_templating.md) - ARX template syntax
- [arx_render.md](../../skills/agentrx/arx_render.md) - Template rendering

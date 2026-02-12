---
arx: command
name: prompt-do
description: Execute a prompt with optional data context
version: 1
argument-hint: [prompt-file] [--data <file>] [--history]
---

# /agentrx:prompt-do - Execute Prompt with Data

Execute a prompt file with optional JSON data context. Can read data from a file or stdin.

## Usage

```bash
/agentrx:prompt-do [prompt-file] [options]

# Or via CLI
arx prompt-do [prompt-file] [options]

# With piped data
cat data.json | arx prompt-do
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `prompt-file` | No | Path to prompt file. If omitted, uses most recent in ARX_PROMPTS |
| `--data`, `-d` | No | Path to JSON data file for context |
| `--history`, `-H` | No | Append execution to history log |
| `--output`, `-o` | No | Output file path (default: stdout) |
| `--dry-run` | No | Show what would be executed without running |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ARX_PROMPTS` | `_project/docs/agentrx/vibes` | Directory containing prompt files |
| `ARX_HISTORY` | `$ARX_PROMPTS/history` | Directory for execution history logs |

## Examples

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

1. Check `ARX_PROMPTS` environment variable for directory
2. Find most recent `.md` file by modification time
3. Use that file as the prompt

```bash
# Uses most recent prompt in ARX_PROMPTS directory
export ARX_PROMPTS="_project/docs/agentrx/vibes"
arx prompt-do --data context.json
```

## History Logging

With `--history` flag, execution details are logged:

```
$ARX_HISTORY/
└── YYYY-MM-DD/
    └── prompt_name_HH-MM-SS.json
```

History entry format:
```json
{
  "timestamp": "2026-02-10T12:40:58Z",
  "prompt_file": "my_prompt_26-02-10-12.md",
  "data_source": "context.json",
  "data": { ... },
  "output_file": null
}
```

## Implementation

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

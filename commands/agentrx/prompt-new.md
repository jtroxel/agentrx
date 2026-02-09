---
description: Initialize trial worktrees for parallel development
argument-hint: <short_name> [out-dir]
---
# /agentrx:prompt-new - Create New Prompt File

Create a prompt markdown file from user input with automatic naming and timestamping.

## Usage
```
/agentrx:prompt:new "prompt content" [short_name] [out-dir]
```

## Parameters
- `prompt` (required): The user text describing the prompt
- `out-dir` (optional): Directory to place the file. Defaults to current directory

## File Naming 
Files are created with the format: `<short_name>_YY-MM-DD-h.md`

## Examples
```
/agentrx:agentrx:prompt:new "Create a REST API for user management" api
# Creates: create_mgmt_api_25-01-08-14.md

/agentrx:agentrx:prompt:new "Optimize database queries for better performance" --dir foo/vibes
# Creates: opt_db_queries_25-01-08-14.md in foo/vibes/

/agentrx:agentrx:prompt:new "Debug the authentication flow issue"
# Creates: debug_auth_flow_25-01-08-14.md
```

## Implementation
When this command is executed:

1. Parse the input parameters
2. If no short_name provided, derive it from the first 3 words of the prompt content (lowercase, alphanumeric only, joined with underscores)
3. Generate timestamp in YY-MM-DD-h format
4. Create filename as `{short_name}_{timestamp}.md`
5. Create the directory if it doesn't exist
6. Write markdown file with:
   - Header with prompt title
   - The prompt content
   - Timestamp footer
7. Return the created file path

## File Template
```markdown
# Prompt: {short_name}

{content}

---
*Created: YYYY-MM-DD HH:MM:SS*
```
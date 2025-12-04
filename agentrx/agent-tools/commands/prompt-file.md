# prompt-file

Read the specified file and treat its contents as a prompt for Claude Code.

## Usage
```
/prompt-file <file-path>
```

## Arguments
- `<file-path>` - Path to the file to read and use as a prompt

## Description
This command reads the contents of the specified file and executes it as if it were typed directly into Claude Code. This is useful for storing complex prompts or instructions in files and reusing them.

## Example
```
/prompt-file ./instructions.md
```

This would read the contents of `instructions.md` and execute it as a prompt.
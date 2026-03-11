---
name: arx-working_dir
description: Directory structure instructions for coding agents
---
# ARX Working Directory Structure
## Overview

The ARX working directory structure is designed to organize files and resources for work-in-process markdown documents and other resources used during agent & human collaboration.

## The Directory IS for
- deltas: *specs* for single iteration of a work-product (code or project docs), describing what is to be changed.
- sessions: coding-agent specific memories and logs of interactions
- vibes: starter prompts for a chat session or CLI invocation. And/or vibe chat sessions sumarized as repeatable instructions.

## What doesn't belong
- NOT A place for finalized or production-ready content
- NOT A place for official project documentation
- A place for curent, up-to-date artifacts or documents

## ALWAYS DO:
- Agents creating files here should always pick the most appropriate subdir for the type of content they are adding.
- Agents should always name files with the current date and an appropriate filename based on user input. E.g:
  - `24-06-12_my-work-product.md` # (User input: "let's finish the my-work-product")
  - `24-06-12_add-arx-templating.md` # (User input: "help me design a feature for adding ARX templating to markdown format docs")
  - `24-06-12_update-readme.md` # (User input: "update the README with new instructions")
- Agents should always prefer Markdown format for files in this directory. (or ARX Markdown template format, if applicable)
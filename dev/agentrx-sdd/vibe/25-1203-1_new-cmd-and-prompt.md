# Prompt: New `agentrx new` command and starter template
## Purpose
agentrx will provide a python project CLI for SDD.
For this prompt you will create the basic command and argument processing for `agentrx ...` commands and arguments. You'll also create a sample prompt "template" to provide AI coding agents with for creating a new prompt for the project.

## Goals
1. Create a `.env` file for with vars for the AGENTX_PROJECT_DIR (files that agentrx manages for a client project), AGENTX_DOCS_DIR (where final documentation for agentx-created features are saved).  For now: AGENTX_PROJECT_DIR=dev/agentrx-sdd and AGENTX_DOCS_DIR=dev/docs
2. Create the template for creating a new spec in agentrx/dot-project/sdd/new
3. Create the command to fill the template with text supplied to the `agentrx new` command, and save to AGENTX_PROJECT_DIR. Also use a filename with a condensed date and abbreviated change.
```bash
agentrx new [feature|capability] <user-text>
# Example:
agentrx new capability a service to manage user-defined, persistent "tags" for photos.
```
4. Create unit tests for the command.
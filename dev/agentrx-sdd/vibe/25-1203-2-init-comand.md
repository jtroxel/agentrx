# Spec: agentx `init` command v0.1
## SSD Atrtributes
Action: "Start"
Target: Feature

## Requirements
### 
### 1.0 Command CLI 
```bash
# copies agentrx/dot-project and subdirs to a .agentx-project (default) folder in $PWD. Idempotent, non-destructive
# Also creates a .agentx.env file, with vars for the AGENTX_PROJECT_DIR, AGENTX_DOCS_DIR
agentx init 
```

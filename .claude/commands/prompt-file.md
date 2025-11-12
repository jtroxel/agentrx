this is a claude code slash-command
# Prompt File Reader

Read and execute the markdown file specified as an argument as a prompt. This command allows you to reuse a prompt,
from the command line to simulate use by an agent or LLM.  

Usage: `/prompt-file {filename} {variables_json}`

Arguments:
- `{filename}`: Path to a markdown file to use as a prompt
- `{variables_json}`: Variables to be substituted in the prompt file as a json string.
  - Allow the json string to be passed as the 2nd argument OR as STDIN
  - If no variables are provided, the prompt file will be executed only substituted with default values defined in <!-- --> comment blocks

---

Please read the file `{{filename}}` and use its contents as a prompt. Execute the instructions contained in that file.

Variables defined in <!-- --> comment blocks are "default" values in the prompt file
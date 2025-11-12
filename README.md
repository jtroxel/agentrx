# AgentRX

AgentRX is a toolkit that provides templates and tools for authentic coding practices that can coexist with files in any project repository. It's designed to enhance your development workflow by providing a standardized set of prompts, commands, and utilities for working with AI agents like Claude.

## Overview

The core concept behind AgentRX is to create a portable, reusable collection of agent-oriented development tools that can be integrated into any project. These tools are designed to live alongside your project files, ideally as a `.agentrx` directory, providing consistent access to AI development patterns and workflows.

## Project Structure

```
agentrx/
├── agents/
│   └── prompts/           # Collection of reusable prompt templates
│       ├── agentrx_dev/   # Development-specific prompts
│       └── test_prompt_1.md
├── .claude/
│   ├── commands/          # Claude-specific commands and utilities
│   │   └── prompt-file.md # Prompt file execution command
│   └── settings.local.json
└── README.md             # This file
```

## Key Features

### Prompt Management
- **Reusable Prompts**: Store and organize prompt templates for common development tasks
- **Variable Substitution**: Support for dynamic variables in prompt templates
- **Development Workflows**: Specialized prompts for different development phases

### Claude Integration
- **Command System**: Custom commands specifically designed for Claude interactions
- **Prompt File Reader**: Execute markdown files as prompts with variable substitution
- **Settings Management**: Local configuration for Claude-specific settings

## Quick Start

### 1. Add AgentRX to Your Project (Recommended: Git Submodule)

```bash
# In your host project root directory
git submodule add https://github.com/jtroxel/agentrx .agentrx
git submodule update --init --recursive

# Commit the submodule addition
git add .gitmodules .agentrx
git commit -m "Add AgentRX as submodule"
```

### 2. Configure Your Host Project

Create a `.gitignore` entry for local customizations:

```bash
echo -e "\n# AgentRX local configurations\n.agentrx-local/\n*.local.*" >> .gitignore
```

### 3. Optional: Create Project-Specific Settings

```bash
# Create local settings directory (this won't be committed)
mkdir -p .agentrx-local/prompts
mkdir -p .agentrx-local/settings

# Copy and customize AgentRX settings if needed
cp .agentrx/claude/settings.json .agentrx-local/settings/claude.local.json
```

### 4. Validate Integration

```bash
# Test basic functionality
/prompt-file .agentrx/agents/prompts/test_prompt_1.md
# Should execute successfully

# Verify submodule status
git submodule status
# Should show clean .agentrx submodule

# Check command availability
ls .agentrx/.claude/commands/
# Should show available commands
```

### 5. Start Using AgentRX

```bash
# Execute an AgentRX prompt
/prompt-file .agentrx/agents/prompts/agentrx_dev/git_integration_01.md

# Execute with variables
/prompt-file .agentrx/agents/prompts/test_prompt_1.md '{"project_name": "my-app"}'

# Create project-specific prompts
echo "Deploy to {{environment}}" > .agentrx-local/prompts/deploy.md
/prompt-file .agentrx-local/prompts/deploy.md '{"environment": "staging"}'
```

## Installation Methods

### Git Submodule (Production - Recommended)
Best for production projects where you want version control over AgentRX updates:

```bash
cd your-project-root
git submodule add https://github.com/jtroxel/agentrx .agentrx

git submodule update --init --recursive
```

**Benefits:**
- Clean separation between host project and AgentRX files
- Version control over AgentRX updates
- Team members get consistent AgentRX version
- No modification of AgentRX source files

### Symbolic Link (Development)
For local development and testing:

```bash
# Clone AgentRX separately
git clone https://github.com/jtroxel/agentrx

# Create symbolic link in your project
ln -s /path/to/agentrx /path/to/your/project/.agentrx
```

### Direct Clone (Standalone)
For standalone use or experimentation:

```bash
git clone https://github.com/jtroxel/agentrx
cd agentrx
```

## Usage

### Prompt File Execution
Use the prompt file command to execute markdown files as prompts:

```bash
/prompt-file {filename} {variables_json}
```

**Arguments:**
- `{filename}`: Path to a markdown file to use as a prompt
- `{variables_json}`: Variables to be substituted in the prompt file as a JSON string

**Examples:**
```bash
# Execute a prompt file with no variables
/prompt-file agents/prompts/agentrx_dev/agentrx_readme01.md

# Execute with variables
/prompt-file agents/prompts/test_prompt_1.md '{"project_name": "my-app", "version": "1.0.0"}'
```

### Variable Substitution
Variables can be defined in prompt files using HTML comment blocks:
```markdown
<!-- variable_name: default_value -->
```

### Git Integration Patterns

#### Host Project Structure
When AgentRX is properly integrated, your host project maintains this clean separation:

```
your-project/
├── .agentrx/               # AgentRX submodule (never modify directly)
│   ├── agents/prompts/     # Standard AgentRX prompts
│   ├── claude/commands/    # Standard AgentRX commands
│   └── README.md           # AgentRX documentation
├── .agentrx-local/         # Project-specific customizations (gitignored)
│   ├── prompts/           # Your custom prompts
│   └── settings/          # Your local settings
├── .gitignore             # Excludes .agentrx-local/
├── .gitmodules            # Tracks AgentRX submodule
└── your-project-files...
```

#### Workflow for Managing Updates

**Updating AgentRX to Latest Version:**
```bash
# Navigate to AgentRX submodule
cd .agentrx
git pull origin main

# Return to host project and commit the update
cd ..
git add .agentrx
git commit -m "Update AgentRX to latest version"
```

**Creating Project-Specific Prompts:**
```bash
# Create custom prompts (these won't be committed to AgentRX)
echo "My custom prompt" > .agentrx-local/prompts/my-prompt.md

# Reference in your project documentation
echo "Custom AgentRX prompts: .agentrx-local/prompts/" >> CLAUDE.md
```

**Team Collaboration:**
```bash
# New team member setup
git clone your-project-repo
cd your-project
git submodule update --init --recursive  # Gets AgentRX automatically

# Everyone gets the same AgentRX version, no version conflicts
```

#### Integration Points

**1. Command Access:**
All AgentRX commands are available via `.agentrx/claude/commands/`

**2. Prompt Libraries:**
- Standard prompts: `.agentrx/agents/prompts/`
- Project-specific: `.agentrx-local/prompts/` (you create this)

**3. Settings Management:**
- Base settings: `.agentrx/claude/settings.json`
- Local overrides: `.agentrx-local/settings/claude.local.json`

**4. Documentation References:**
```markdown
# In your project's CLAUDE.md or README.md
## Available AgentRX Tools
- [Standard commands](.agentrx/claude/commands/)
- [Development prompts](.agentrx/agents/prompts/agentrx_dev/)
- [Project-specific prompts](.agentrx-local/prompts/)
```

## Integration Validation

After setting up AgentRX in your host project, verify the integration is working correctly:

### Health Check Commands
```bash
# Verify AgentRX submodule is properly initialized
git submodule status
# Should show: [commit-hash] .agentrx (tag or branch info)

# Check command availability
ls .agentrx/.claude/commands/
# Should show: prompt-file.md

# Test basic prompt execution
/prompt-file .agentrx/agents/prompts/test_prompt_1.md
# Should execute without errors

# Verify local customization structure (if created)
ls .agentrx-local/
# Should show: prompts/ settings/ (if you created them)
```

### Integration Status
```bash
# Check that .agentrx-local is properly gitignored
git status
# Should NOT show .agentrx-local/ files as untracked

# Verify submodule tracking
cat .gitmodules
# Should show .agentrx submodule configuration
```

## Troubleshooting

### Common Integration Issues

**Submodule not initialized**
```bash
# Symptom: .agentrx directory empty or missing
# Solution:
git submodule update --init --recursive
```

**Command not found: /prompt-file**
```bash
# Symptom: Command not recognized
# Check: Verify command file exists
ls .agentrx/.claude/commands/prompt-file.md
# If missing, submodule may not be properly initialized
```

**Local changes in AgentRX submodule**
```bash
# Symptom: git status shows modified .agentrx
# Solution: Reset submodule to clean state
cd .agentrx && git checkout . && cd ..
```

**Project-specific files appearing in AgentRX**
```bash
# Symptom: Custom prompts mixed with standard AgentRX files
# Solution: Move to .agentrx-local/ and ensure .gitignore excludes it
mkdir -p .agentrx-local/prompts
mv .agentrx/my-custom-prompt.md .agentrx-local/prompts/
echo ".agentrx-local/" >> .gitignore
```

## Development

### Prerequisites
- Python >= 3.13
- Git

### Setup
Pull the agentrx project into your Host project
```bash
# Clone the repository
git clone https://github.com/jtroxel/agentrx .agentrx
cd .agentrx
```

```bash
# Install in development mode (optional, if you plan to extend functionality)
pip install -e .
```

### Adding New Prompts
1. Create a new markdown file in `agents/prompts/`
2. Use HTML comments to define default variables if needed
3. Write your prompt content with variable placeholders: `{{variable_name}}`

### Adding New Commands
1. Create a new markdown file in `claude/commands/`
2. Follow the existing command format with usage instructions
3. Document the command purpose and arguments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your prompts, commands, or improvements
4. Submit a pull request with clear description of changes

## Use Cases

- **Consistent Development Workflows**: Standardize how you interact with AI agents across projects
- **Prompt Library**: Build and maintain a collection of proven prompt patterns
- **Team Collaboration**: Share agent workflows and templates across development teams
- **Project Templates**: Quickly bootstrap new projects with established AI development patterns

## Future Enhancements

- Enhanced variable substitution with environment variable support
- Plugin system for custom command extensions
- Integration templates for popular development frameworks
- Automated prompt testing and validation

## License

[Add your license information here]

## Support

[Add support information, issue reporting guidelines, or contact details here]

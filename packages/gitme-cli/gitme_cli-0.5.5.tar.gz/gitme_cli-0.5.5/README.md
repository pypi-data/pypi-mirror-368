
<div align="center">

## A git commit message generator that doesn't interrupt your vibe coding flow.

```bash
git add . && git commit -am "ugh... what did I do? what do I even say here?" && git push -u origin dev
```
### ⬇️ 
```bash
gitme -u <your-remote-branch>
```

</div>

![gitme-cli-generate](https://github.com/wangjing0/gitme/raw/main/images/gitcommit.png)

```bash
gitme show
```

![gitme-cli-show](https://github.com/wangjing0/gitme/raw/main/images/gitshow.png)

## Features

- Analyzes git diffs to generate contextually relevant commit messages
- Detects untracked files and prompts to add them
- Supports staged changes only or all modified files
- Direct commit and push to upstream branch with user confirmation on every step, extremely lightweight and fast.
- **Multiple AI Providers**: Choose between Anthropic or OpenAI, default is Anthropic
- Model options for both providers
- File changes and commit message history for logging, search and review at local
- Repository-specific message storage

## Installation

Install from PyPI:

```bash
pip install gitme-cli
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/wangjing0/gitme.git
```

Or develop locally:

```bash
git clone https://github.com/wangjing0/gitme.git
cd gitme
pip install -e .
```

### AI Provider Setup

Choose one or both providers:

**For Anthropic Claude (default):**
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

**For OpenAI GPT (Optional):**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Note:** All `gitme` commands must be run from within a git repository directory. If you're not in a git repository, you'll see an error message prompting you to run `git init`.

### Basic Usage

```bash
# Generate message for staged changes (default - uses Anthropic Claude)
gitme

# Generate message for all changes
gitme -a

# Generate message and commit
gitme -c

# Generate message and commit and push to remote branch
gitme -u dev
```

```bash
# Use OpenAI instead of Anthropic (default)
gitme -p openai

# Use OpenAI with specific model
gitme -p openai -m gpt-4o

# Use Anthropic with specific model
gitme -m claude-3-5-haiku-latest

# Combine with other options
gitme -p openai -c  # Use OpenAI and commit
```

### Untracked Files Handling

When you run `gitme`, it will automatically detect any untracked files in your repository and prompt you to add them to the staging area:

```bash
📁 Untracked files found:
    new_feature.py
    test_file.js
 Do you want to add these untracked files to the staging area? [y/N]:
```

- Choose **y** to add all untracked files to staging and include them in the commit message generation
- Choose **N** to proceed without the untracked files (they won't be included in the analysis)

### Message History

```bash
# Show previous messages (includes provider/model info)
gitme show

# Show last 5 messages
gitme show -n 5

# Show from all repositories
gitme show -r

# Clear history
gitme show --clear
```

**Enhanced Message History Display:**
```
[1] 2025-07-20 10:30:45
    💬 Message:
    Add user authentication feature
    
    - Modified auth.py
    - Updated config.json
    - Added login.html
    🤖 AI Provider: Anthropic (claude-3-5-haiku-latest)
    📝 Files changed: 3

[2] 2025-07-20 09:15:22
    💬 Message:
    Fix authentication bug
    
    - Fixed login validation
    🤖 AI Provider: Openai (gpt-4o-mini)
    📝 Files changed: 1
```

## Options

### Generate Options

- `-s, --staged`: Analyze only staged changes
- `-a, --all`: Analyze all changes (staged and unstaged)
- `-p, --provider`: Choose AI provider (`anthropic` or `openai`, default: anthropic)
- `-m, --model`: Model to use (provider-specific)
- `-c, --commit`: Create commit with generated message (uses `git commit -a -m "auto-generated message"`)

### Show Options

- `-n, --limit`: Number of messages to show
- `-r, --all-repos`: Show messages from all repositories
- `--clear`: Clear message history

### Available Models

**Anthropic Claude:**
- `claude-3-5-haiku-latest` (default)
- `claude-3-haiku-20240307`
- `claude-3-sonnet-20240229`

**OpenAI GPT:**
- `gpt-4o-mini` (default when using OpenAI)
- `gpt-4o`
- `gpt-4`

## Privacy & Security Notice

⚠️ **Important**: When using `gitme` or `gitme generate`, your code changes will be sent to the selected AI provider (Anthropic Claude or OpenAI GPT) for processing. The tool does NOT send your entire codebase - only the diff contents of changed files.

**Please exercise caution when using this tool:**
- Avoid using it with repositories containing sensitive information, credentials, or proprietary code
- Review your changes before running the command to ensure no sensitive data is included
- Consider using `.gitignore` to exclude sensitive files from git tracking
- Be aware that different providers have different data handling policies
- Both Anthropic and OpenAI have their own privacy policies and data retention practices

## Requirements

- Python 3.8+
- Git
- At least one AI provider API key:
  - Anthropic API key for Claude models
  - OpenAI API key for GPT models, `openai` Python package for OpenAI support


## New Release

```bash
chmod +x release.sh && ./release.sh <version>
```


## Roadmap

- [ ] Add a way to add custom prompt to the AI provider
- [ ] User feedback on the generated message and modify accordingly
- [ ] Local models with Ollama support

## Contributing

Contributions are welcome! Please feel free to submit a pull request. ❤️ @wangjing0 

## License

MIT
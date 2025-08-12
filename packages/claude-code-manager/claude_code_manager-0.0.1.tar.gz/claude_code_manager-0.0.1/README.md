# Claude Code Manager

<div align="center">

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)

A powerful CLI tool to orchestrate Claude Code runs from a Markdown TODO list, enabling automated task execution and pull request creation.

</div>

## 🚀 Features

- **Todo-Driven Development**: Parse TODO lists from GitHub-flavored markdown and execute each item
- **Automated Workflow**: Create branches, implement features, and submit pull requests automatically
- **Worktree Parallel Mode**: Execute multiple todo items simultaneously using Git worktrees
- **Hooks Integration**: Seamlessly integrates with Claude Code hooks for reliable task completion
- **Internationalization**: Support for multiple languages through simple configuration
- **Configurable**: Customize branch names, commit messages, PR titles and more

## 📋 Installation

```bash
# Install from PyPI (recommended)
uv tool install claude-code-manager

# Or with pip (inside your environment)
pip install -U claude-code-manager

# Run via uvx (no global install required)
uvx --from claude-code-manager claude-manager --version
# or simply (uvx will resolve the providing package)
uvx claude-manager run --input TODO.md

# Upgrade later
uv tool upgrade claude-code-manager
```

## 🚀 Quick Start

1. Create a markdown TODO.md list file:

```markdown
- [x] Completed item [#1](https://github.com/user/repo/pull/1)
- [ ] Add dark mode support
  - [ ] Create toggle component
  - [ ] Implement theme switching
- [ ] Fix pagination in user list
```

Note: Add TODO.md to your .gitignore so it isn't committed:

```gitignore
# Local planning checklist for claude-manager
TODO.md
```

2. Run Claude Code Manager:

```bash
claude-manager run
```

3. Each unchecked top-level item will be processed sequentially (or in parallel with `--worktree-parallel`):
   - A new branch will be created
   - Claude Code will implement the requested feature
   - Changes will be committed and pushed
   - A pull request will be created
   - The TODO list will be updated with a checkbox and PR link

## ⚙️ Configuration

You can configure Claude Code Manager using command-line options or a configuration file:

```bash
# Show all available options
claude-manager run --help

# Use a custom configuration file
claude-manager run --config my-config.toml

# Enable parallel execution using Git worktrees
claude-manager run -w -s 3
```

### Configuration File

Create a `.claude-manager.toml` file in your project root:

```toml
[claude_manager]
git_branch_prefix = "feature/"
git_commit_message_prefix = "feat: "
git_base_branch = "main"
github_pr_title_prefix = "Feature: "
github_pr_body_template = "Implements: {todo_item}"
```

### Internationalization

Claude Code Manager supports multiple languages through the `.claude-manager.i18n.toml` file:

```toml
[i18n.en]
processing = "Processing todo: {title}"
claude_not_found = "Claude CLI not found. Please install it first."

[i18n.ja]
processing = "Todoを処理中: {title}"
claude_not_found = "Claude CLIが見つかりません。先にインストールしてください。"
```

## 🧰 Advanced Usage

### Doctor Command

Validate your configuration and environment:

```bash
claude-manager run --doctor
```

### Custom Prompt Templates

You can customize how Claude Code is prompted:

```bash
claude-manager run --headless-prompt-template "Implement this feature: {title}\n\nDetails:\n{children_bullets}\n\nWhen finished, output: {done_token}"
```

### Git Worktree Parallel Mode

Process multiple todo items simultaneously:

```bash
claude-manager run -w -s 3
```

## 🤝 Contributing

Contributions are welcome!

## 📄 License

MIT

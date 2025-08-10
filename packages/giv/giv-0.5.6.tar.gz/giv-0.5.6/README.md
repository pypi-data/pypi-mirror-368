# giv - AI-Powered Git History Assistant

**giv** (pronounced "give") is a powerful CLI tool that transforms raw Git history into polished commit messages, summaries, changelogs, release notes, and announcements. This Python implementation provides cross-platform binary distribution with zero dependencies.

[![Build Status](https://img.shields.io/badge/build-passing-green)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ Key Features

- **🚀 Self-contained binaries** - No Python installation required
- **🤖 Multiple AI backends** - OpenAI, Anthropic, Ollama, and custom endpoints  
- **📝 Rich command suite** - Generate messages, summaries, changelogs, and release notes
- **🎯 Smart Git integration** - Support for revision ranges, pathspecs, and staged changes
- **⚙️ Flexible configuration** - Project and user-level settings with inheritance
- **🔧 Template system** - Customizable prompts for all output types

## 🚀 Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh
```

**Automated Releases:**
All binaries and PyPI packages are built and published automatically via GitHub Actions when a new version is pushed or released.
No manual build steps required for contributors—just bump the version, push, and create a release tag.
Release assets (binaries and PyPI packages) are attached to each GitHub release.

**Other Installation Methods:** [PyPI, install script, manual install, or build from source →](docs/installation.md)

## 🏁 Getting Started

```bash
# Initialize giv in your project
giv init

# Generate commit message for current changes
giv message

# Create changelog entry
giv changelog v1.0.0..HEAD

# Generate release notes
giv release-notes v1.2.0..HEAD
```

**Detailed Usage Guide:** [Command examples and advanced usage →](docs/app-spec.md)

## ⚙️ Basic Configuration

Set up your AI provider:

```bash
# Quick setup with environment variables (recommended)
export OPENAI_API_KEY="your-api-key"
export GIV_API_MODEL="gpt-4"

# Or configure via giv
giv config set api.url "https://api.openai.com/v1/chat/completions"
giv config set api.model "gpt-4"
```

**Complete Configuration Guide:** [All settings and providers →](docs/configuration.md)

## 🎨 Customization

```bash
# Initialize project templates
giv init

# Edit templates
nano .giv/templates/commit_message_prompt.md
nano .giv/templates/changelog_prompt.md

# Use custom template
giv message --prompt-file custom-prompt.md
```

**Template System:** [Customization and variables →](docs/app-spec.md#5-template-system)

## 📖 Documentation

- **[Installation Guide](docs/installation.md)** - All installation methods and troubleshooting
- **[Configuration](docs/configuration.md)** - Complete configuration reference
- **[App Specification](docs/app-spec.md)** - Commands, usage, and template system
- **[Build System](docs/build-system-review.md)** - Technical architecture
- **[Publishing Guide](docs/how-to-publish.md)** - Release process for contributors

## 🤖 Supported AI Providers

- **OpenAI** - GPT-4, GPT-3.5-turbo
- **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus
- **Local (Ollama)** - Llama 3.2, Code Llama, and more
- **Custom endpoints** - Any OpenAI-compatible API

**Provider Setup Examples:** [Configuration guide →](docs/configuration.md#configuration-examples)

## 🔧 Troubleshooting

### Linux Binary Compatibility Issues

If you encounter an error like `GLIBC_2.XX not found`, this means your system has an older version of GLIBC than required:

```bash
# Check your GLIBC version
ldd --version

# If you have GLIBC < 2.31, use one of these alternatives:
# 1. Install via pip (works on any Python 3.9+)
pip install giv

# 2. Use the install script which detects compatibility
curl -fsSL https://raw.githubusercontent.com/fwdslsh/giv/main/install.sh | sh

# 3. For very old systems, run from source
git clone https://github.com/fwdslsh/giv.git && cd giv && pip install .
```

**Supported Systems:**
- Linux: GLIBC 2.31+ (Ubuntu 20.04+, RHEL 8+, Debian 10+)
- macOS: 10.15+ (Catalina and newer)
- Windows: Windows 10 1909+ (November 2019 Update)

For other issues, check our [troubleshooting guide](docs/troubleshooting.md).

## 🔧 Development

```bash
git clone https://github.com/fwdslsh/giv.git
cd giv
poetry install
poetry run pytest
```

## 🛠️ Build & Release Automation

All builds and releases are handled by GitHub Actions:
- **Version bump:** Edit `pyproject.toml` and push to `main`.
- **Release:** Create a new release/tag on GitHub, and all binaries/packages are built and published automatically.
- **No manual build scripts required.**

**Development Details:** [Build system and contributing →](docs/build-system-review.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Quick Links

- [📥 Releases](https://github.com/fwdslsh/giv/releases) - Download binaries
- [🐛 Issues](https://github.com/fwdslsh/giv/issues) - Report bugs
- [💬 Discussions](https://github.com/fwdslsh/giv/discussions) - Community support
- [🗺️ Roadmap](docs/roadmap.md) - Planned features

---

*Transform your Git history into professional documentation with the power of AI.*
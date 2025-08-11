# Publishing Guide for Computer Split Screen MCP Server

This guide will walk you through the process of publishing the `computer-split-screen-mcp` package to PyPI so it can be used with the MCP configuration you specified.

## Prerequisites

1. **PyPI Account**: You need a PyPI account to publish packages
2. **Python Build Tools**: Install required build tools
3. **Git Repository**: Your code should be in a git repository

## Setup Steps

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Create PyPI Account

1. Go to [PyPI](https://pypi.org/account/register/)
2. Create an account
3. Verify your email
4. Enable two-factor authentication (recommended)

### 3. Configure PyPI Credentials

Create a `~/.pypirc` file:

```ini
[pypi]
username = __token__
password = pypi-<your-token-here>
```

Or use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-token-here>
```

## Publishing Process

### Option 1: Use the Publish Script (Recommended)

```bash
# Make sure you're in the project root directory
./scripts/publish.sh
```

The script will:
- Clean previous builds
- Build the package
- Ask if you want to publish
- Upload to PyPI if confirmed

### Option 2: Manual Publishing

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

### Option 3: Test Upload First

```bash
# Build the package
python -m build

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# If successful, upload to real PyPI
twine upload dist/*
```

## Post-Publishing

### 1. Verify Installation

```bash
# Install the published package
pip install computer-split-screen-mcp

# Test import
python -c "import computer_split_screen_mcp; print('Success!')"
```

### 2. Test MCP Integration

Configure your MCP client with:

```json
{
  "mcpServers": {
    "window-management": {
      "command": "uvx",
      "args": ["computer-split-screen-mcp"],
      "env": {}
    }
  }
}
```

### 3. Update Documentation

- Update any references to the package
- Share the PyPI link: https://pypi.org/project/computer-split-screen-mcp/

## Version Management

### Updating Version

1. Edit `pyproject.toml`
2. Update the `version` field
3. Follow semantic versioning (e.g., 0.1.0 → 0.1.1)

### Release Process

1. Update version in `pyproject.toml`
2. Commit changes: `git commit -am "Bump version to X.Y.Z"`
3. Tag release: `git tag vX.Y.Z`
4. Push: `git push && git push --tags`
5. Publish to PyPI

## Troubleshooting

### Common Issues

**Build Errors**
- Ensure all dependencies are in `pyproject.toml`
- Check Python version compatibility
- Verify package structure

**Upload Errors**
- Check PyPI credentials
- Ensure package name is unique
- Verify package format

**Import Errors After Publishing**
- Wait a few minutes for PyPI propagation
- Check package name spelling
- Verify installation: `pip list | grep computer-split-screen-mcp`

### Getting Help

- Check PyPI documentation: https://packaging.python.org/
- Review build logs for specific errors
- Ensure all required files are present

## Package Structure

Your package should have this structure:

```
computer-split-screen-mcp/
├── pyproject.toml
├── README.md
├── LICENSE
├── computer_split_screen_mcp/
│   ├── __init__.py
│   ├── window_manager.py
│   ├── server.py
│   └── __main__.py
├── tests/
├── examples/
└── scripts/
```

## Next Steps After Publishing

1. **Test the Package**: Install and test all functionality
2. **MCP Integration**: Test with your MCP client
3. **Documentation**: Update any project documentation
4. **Community**: Share on relevant forums/discussions
5. **Maintenance**: Monitor for issues and plan updates

## Security Notes

- Never commit PyPI credentials to git
- Use environment variables or `.pypirc` file
- Enable 2FA on your PyPI account
- Regularly rotate your PyPI token

---

**Congratulations!** 🎉 Once published, users can install your package with:

```bash
pip install computer-split-screen-mcp
```

And use it with the MCP configuration you specified!

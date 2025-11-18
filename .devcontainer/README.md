# Development Container

This directory contains the configuration for a VS Code development container that provides a consistent, isolated development environment for Garmin2ShotPattern.

## What's Included

- **Python 3.12** - Latest stable Python version
- **Zsh with Oh My Zsh** - Enhanced shell experience
- **Git** - Latest version for version control
- **Pre-installed Dependencies**:
  - All production dependencies from `requirements.txt`
  - All development dependencies from `requirements-dev.txt` (mypy, ruff)

## VS Code Extensions

The container automatically installs:
- Python extension with Pylance
- Ruff (linting and formatting)
- Mypy type checker

## Editor Settings

Pre-configured for optimal Python development:
- **Format on save** with Ruff
- **Auto-organize imports** on save
- **Type checking** with mypy (strict mode)
- **Linting** with Ruff
- Line length: 100 characters

## Using the Dev Container

### First Time Setup

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code
2. Open the project folder in VS Code
3. Click "Reopen in Container" when prompted, or:
   - Press `F1` or `Cmd+Shift+P`
   - Select "Dev Containers: Reopen in Container"
4. Wait for the container to build and start (first time takes a few minutes)

### Working in the Container

Once inside the container:
- All dependencies are pre-installed
- Python 3.12 is configured as the default interpreter
- Run commands directly: `python transform.py` or use the Makefile targets
- No need for virtual environments - the container is isolated

### Data Persistence

The `data/` directory is mounted from your local machine, so:
- ✅ Your CSV files persist between container rebuilds
- ✅ Generated config files are saved locally
- ✅ No data loss when stopping the container

### Rebuilding the Container

If you modify dependencies or devcontainer configuration:
1. Press `F1` or `Cmd+Shift+P`
2. Select "Dev Containers: Rebuild Container"

## Benefits

- **Consistency**: Same environment for all developers
- **Isolation**: No conflicts with local Python installations
- **Pre-configured**: All tools and settings ready to go
- **Reproducible**: Easy onboarding for new contributors
- **Cross-platform**: Works on macOS, Linux, and Windows

## Customization

### Adding Python Packages

Add packages to `requirements.txt` or `requirements-dev.txt`, then rebuild the container.

### Changing Python Version

Modify the `image` property in `devcontainer.json`:
```json
"image": "mcr.microsoft.com/devcontainers/python:1-3.11-bullseye"
```

## Troubleshooting

### Container won't start
- Check Docker is running
- Try "Dev Containers: Rebuild Container Without Cache"

### Dependencies not installed
- Rebuild the container
- Check `postCreateCommand` in devcontainer.json

### Python interpreter not found
- Reload VS Code window
- Check `python.defaultInterpreterPath` in devcontainer.json

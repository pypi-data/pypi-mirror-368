# Django Coolify

Easy Django deployment to Coolify with minimal configuration.

## Features

- Simple Django integration with Coolify
- Automatic Docker configuration generation
- Git-based deployments for public repositories
- SQLite support with persistent volumes
- Health check integration
- Environment variable management

## Installation

```bash
pip install django-coolify
```

## Quick Start

1. **Add to Django settings**:
   ```python
   # settings.py
   INSTALLED_APPS = [
       # ... your apps
       'django_coolify',
   ]
   ```

2. **Generate configuration**:
   ```bash
   python manage.py generate-config --interactive
   ```

3. **Setup infrastructure**:
   ```bash
   python manage.py setup-infra
   ```

4. **Deploy your application**:
   ```bash
   python manage.py deploy
   ```

## Commands

### `generate-config`

Generate a `coolify.json` configuration file for your project.

```bash
# Interactive mode (recommended for first setup)
python manage.py generate-config --interactive

# Command line mode
python manage.py generate-config \
    --coolify-url https://coolify.example.com \
    --api-token your-api-token \
    --project-name my-django-project \
    --app-name my-django-app \
    --git-repository https://github.com/username/repo \
    --git-branch main \
    --build-pack dockerfile
```

**Options:**
- `--coolify-url`: Your Coolify instance URL
- `--api-token`: Coolify API token (get from Keys & Tokens in Coolify dashboard)
- `--project-name`: Project name in Coolify
- `--app-name`: Application name in Coolify
- `--git-repository`: Git repository URL (auto-detected if not provided)
- `--git-branch`: Git branch to deploy (default: main)
- `--build-pack`: Build pack to use (dockerfile or nixpacks, default: dockerfile)
- `--domains`: Comma-separated list of domains
- `--force`: Overwrite existing configuration
- `--interactive`: Interactive configuration mode

### `setup-infra`

Create project and application in Coolify based on your configuration.

```bash
# Basic setup
python manage.py setup-infra

# List available servers
python manage.py setup-infra --list-servers

# Use specific server
python manage.py setup-infra --server-uuid <server-uuid>

# Force recreation of resources
python manage.py setup-infra --force
```

**Options:**
- `--server-uuid`: Specific server UUID to deploy to
- `--force`: Force recreation of existing resources
- `--list-servers`: List available servers and exit

### `deploy`

Deploy your application to Coolify.

```bash
# Standard deployment
python manage.py deploy

# Force rebuild (no cache)
python manage.py deploy --force

# Deploy specific branch
python manage.py deploy --branch feature-branch

# Deploy specific tag
python manage.py deploy --tag v1.0.0

# Skip git push (code already pushed)
python manage.py deploy --no-push
```

**Options:**
- `--force`: Force rebuild without cache
- `--no-push`: Skip git push (assume code is already pushed)
- `--branch`: Deploy specific branch (overrides config)
- `--tag`: Deploy specific tag instead of branch

## Configuration

The `coolify.json` file contains all the configuration for your deployment:

```json
{
  "coolify_url": "https://coolify.example.com",
  "api_token": "your-api-token",
  "project_name": "my-django-project",
  "project_uuid": "generated-after-setup",
  "app_name": "my-django-app",
  "app_uuid": "generated-after-setup",
  "server_uuid": "auto-selected-or-specified",
  "git_repository": "https://github.com/username/repo",
  "git_branch": "main",
  "build_pack": "dockerfile",
  "domains": "example.com,www.example.com",
  "environment_variables": {},
  "health_check_enabled": true,
  "health_check_path": "/health/"
}
```

## Docker Configuration

The package automatically generates Docker-related files if they don't exist:

- `Dockerfile`: Optimized for Django applications
- `requirements.txt`: Extracted from pyproject.toml or created with sensible defaults
- `.dockerignore`: Excludes unnecessary files from Docker context

## Health Checks

A health check endpoint is automatically added to your Django application at `/health/`. This endpoint returns a simple JSON response indicating the application status.

## Environment Variables

You can configure environment variables in the `coolify.json` file:

```json
{
  "environment_variables": {
    "DEBUG": "False",
    "ALLOWED_HOSTS": "example.com,www.example.com",
    "SECRET_KEY": "your-secret-key"
  }
}
```

## Getting Your Coolify API Token

1. Log in to your Coolify dashboard
2. Go to "Keys & Tokens" → "API tokens"
3. Click "Create New Token"
4. Give it a name and select appropriate permissions
5. Copy the token (you'll only see it once)

## Workflow

The typical workflow for using django-coolify:

1. **Initial Setup**: Run `generate-config --interactive` to create your configuration
2. **Infrastructure**: Run `setup-infra` to create the project and application in Coolify
3. **Development**: Make changes to your Django application
4. **Deployment**: Run `deploy` to push changes and deploy

## Requirements

- Python 3.12+
- Django 4.2+
- Git repository (public repositories supported)
- Coolify instance with API access

## Limitations

- Currently supports only public Git repositories
- Requires manual Coolify API token setup
- SQLite database with volume mounting (PostgreSQL support planned)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

# Django Coolify

Easy Django deployment to Coolify with minimal configuration and automated domain management.

## Features

- 🚀 **Simple Django integration** with Coolify
- 🐳 **Automatic Docker configuration** generation with uv support
- 🌐 **Smart domain management** with automatic port mapping
- 🔄 **Git-based deployments** for public repositories  
- 💾 **SQLite support** with persistent volumes
- 🔧 **Environment variable automation** including ALLOWED_HOSTS
- 📡 **Full Coolify API integration** for seamless deployment workflow
- ⚡ **Simplified configuration** with health checks disabled by default for easier setup

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

### `set_domain`

Set or update the domain for your application with automatic port mapping.

```bash
# Generate and set a new domain automatically
python manage.py set_domain

# Set a specific domain  
python manage.py set_domain --domain https://myapp.example.com:8000

# Force regenerate domain (overwrite existing)
python manage.py set_domain --force

# Generate domain with specific port
python manage.py set_domain --force  # Uses port from ports_exposes config
```

**Options:**
- `--domain`: Specific domain to set (include https:// prefix and port)
- `--force`: Force regeneration of domain (overwrite existing configuration)

**Features:**
- Automatically generates domains with port mapping (e.g., `:8000`)
- Updates Coolify application settings via API
- Saves domain to `coolify.json` configuration
- Configures `ALLOWED_HOSTS` environment variable in Django

## Configuration

Django Coolify uses a secure two-file configuration approach:

### 1. `coolify.json` - Non-sensitive configuration
Contains project settings that are safe to commit to version control:

```json
{
  "coolify_url": "https://coolify.example.com",
  "project_name": "my-django-project",
  "project_uuid": "generated-after-setup",
  "app_name": "my-django-app",
  "app_uuid": "generated-after-setup",
  "server_uuid": "auto-selected-or-specified",
  "git_repository": "https://github.com/username/repo",
  "git_branch": "main",
  "build_pack": "dockerfile",
  "domains": "https://app.example.com:8000",
  "ports_exposes": "8000",
  "environment_variables": {},
  "health_check_enabled": true,
  "health_check_path": "/django-coolify/health/"
}
```

### 2. `.env` - Sensitive configuration
Contains API tokens and secrets (automatically added to .gitignore):

```bash
# Coolify Configuration
COOLIFY_API_TOKEN="your-secret-api-token-here"
```

### Security Features

- 🔒 **API tokens stored securely** in `.env` file
- 📝 **Automatic .gitignore updates** to prevent accidental commits
- 🚫 **Excluded from Docker builds** via .dockerignore  
- ✅ **Safe public repository sharing** with coolify.json

**Note on Domains**: Domains are automatically generated with port mapping (e.g., `:8000`) to ensure proper routing to your Django application. You can specify multiple domains separated by commas, and include paths or specific ports as needed:
- `https://app.coolify.io:8000` - Maps to port 8000 inside the container
- `https://app.coolify.io,https://cloud.coolify.io/dashboard` - Multiple domains with paths
- `https://app.coolify.io/api/v3` - Domain with specific path

## Health Check Endpoint

Django Coolify automatically provides a `/django-coolify/health/` endpoint for application monitoring:

### Features
- 🏥 **Comprehensive health checks** - Database, Django, and Python status
- 📊 **JSON response format** with detailed status information  
- 🐳 **Docker integration** - Used by Docker HEALTHCHECK and Coolify monitoring
- 🔄 **Automatic configuration** - URLs are auto-configured during setup

### Example Response

```bash
curl http://localhost:8000/django-coolify/health/
```

```json
{
  "status": "healthy",
  "timestamp": "2025-08-11T22:30:00Z",
  "checks": {
    "database": "connected",
    "django": "ok (v5.2.5)",
    "python": "ok (v3.12.0)"
  },
  "application": {
    "name": "django-app",
    "debug": false,
    "django_version": "5.2.5", 
    "python_version": "3.12.0"
  }
}
```

### HTTP Status Codes
- **200 OK** - Application is healthy
- **503 Service Unavailable** - Application has issues (check `checks` field for details)

## Django Settings for Production

For successful deployment, ensure your Django settings are production-ready:

### Required Settings

```python
# settings.py

# Static files - Required for collectstatic
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # or os.path.join(BASE_DIR, 'staticfiles')

# Allow hosts - Configure for your domain
ALLOWED_HOSTS = ['*']  # For testing, or ['yourdomain.com', 'www.yourdomain.com']

# Optional: Health check endpoint (automatically added by django-coolify)
# No additional configuration needed
```

### Recommended Settings

```python
# For better security in production
import os

# Use environment variables for sensitive data
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-fallback-secret-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Database (SQLite with volume mount)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',  # Matches Docker volume
    }
}

# Logging (optional)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## Docker Configuration

The package automatically generates Docker-related files if they don't exist:

- `Dockerfile`: Optimized for Django applications
- `requirements.txt`: Extracted from pyproject.toml or created with sensible defaults
- `.dockerignore`: Excludes unnecessary files from Docker context

## Health Checks

A health check endpoint is automatically added to your Django application at `/django-coolify/health/`. This endpoint returns a simple JSON response indicating the application status.

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
- **Domain setting**: Auto-generated domains are saved to config and set as environment variables, but may need to be manually set in the Coolify UI due to API limitations

### Manual Domain Setup

If the domain doesn't appear in your Coolify application after running `setup_infra`, you can:

1. **Use the set_domain command**: `python manage.py set_domain`
2. **Manual setup in Coolify UI**:
   - Go to your application in Coolify dashboard
   - Navigate to Configuration > General > Domains  
   - Enter the domain from your `coolify.json` file
   - Click "Set Direction" and save

The domain is automatically saved to your `coolify.json` and set as an `ALLOWED_HOSTS` environment variable.

## Changelog

### v0.2.0 (Latest)
- ✨ **Smart domain management**: Automatic domain generation with proper port mapping
- 🔧 **Improved ALLOWED_HOSTS**: Correctly strips port numbers for Django configuration
- 🐳 **Enhanced Docker support**: Better uv integration and dependency management
- 📡 **Robust API integration**: Full CRUD operations with Coolify API
- 🎯 **Port mapping**: Automatic `:8000` port mapping for container routing
- 🔄 **Environment variables**: Better handling of existing vs new environment variables

### v0.1.x
- 🚀 Initial release with basic Coolify integration
- 🐳 Docker configuration generation  
- 📝 Management commands for deployment workflow

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

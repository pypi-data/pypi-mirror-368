"""
Utility functions for django-coolify
"""
import os
import shutil
from pathlib import Path
from typing import Optional


def auto_configure_django_settings(project_path: Optional[str] = None) -> bool:
    """
    Automatically configure Django settings for Coolify deployment
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        True if settings were modified, False otherwise
    """
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    # Find settings.py file
    settings_files = list(project_path.glob("*/settings.py"))
    if not settings_files:
        return False
    
    settings_file = settings_files[0]  # Take the first one found
    
    try:
        with open(settings_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        modified = False
        
        # Add STATIC_ROOT if not present
        if 'STATIC_ROOT' not in content:
            # Find STATIC_URL and add STATIC_ROOT after it
            for i, line in enumerate(lines):
                if line.strip().startswith("STATIC_URL"):
                    lines.insert(i + 1, "STATIC_ROOT = BASE_DIR / 'staticfiles'")
                    modified = True
                    break
        
        # Add dynamic ALLOWED_HOSTS configuration
        if 'os.getenv("ALLOWED_HOSTS")' not in content:
            # Add import os if not present - find the right place after imports
            if 'import os' not in content:
                # Find the line after the last import statement
                import_line_index = -1
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        import_line_index = i
                
                if import_line_index >= 0:
                    lines.insert(import_line_index + 1, 'import os')
                    modified = True
            
            # Find ALLOWED_HOSTS and modify it
            for i, line in enumerate(lines):
                if line.strip().startswith('ALLOWED_HOSTS'):
                    # Add environment variable support after ALLOWED_HOSTS definition
                    lines.insert(i + 1, '')
                    lines.insert(i + 2, '# Add dynamic allowed hosts from environment')
                    lines.insert(i + 3, 'if os.getenv("ALLOWED_HOSTS"):')
                    lines.insert(i + 4, '    ALLOWED_HOSTS.extend(os.getenv("ALLOWED_HOSTS").split(","))')
                    modified = True
                    break
        
        # Write back if modified
        if modified:
            with open(settings_file, 'w') as f:
                f.write('\n'.join(lines))
        
        return modified
        
    except Exception as e:
        print(f"Error configuring Django settings: {e}")
        return False


def generate_domain_name(app_name: str, coolify_url: str, port: int = 8000) -> str:
    """
    Generate a domain name for the application with port mapping
    
    Args:
        app_name: Application name
        coolify_url: Coolify instance URL
        port: Port to map the domain to (default: 8000 for Django)
        
    Returns:
        Generated domain name with https:// prefix and port mapping (required by Coolify API)
    """
    import urllib.parse
    
    # Parse the Coolify URL to get the base domain
    parsed_url = urllib.parse.urlparse(coolify_url)
    base_domain = parsed_url.netloc
    
    # Remove common prefixes from the base domain
    if base_domain.startswith('coolify.'):
        base_domain = base_domain[8:]  # Remove 'coolify.'
    elif base_domain.startswith('app.'):
        base_domain = base_domain[4:]   # Remove 'app.'
    elif base_domain.startswith('my.'):
        base_domain = base_domain[3:]   # Remove 'my.'
    
    # Generate domain: app-name.base-domain.com with port mapping
    app_slug = app_name.lower().replace('_', '-').replace(' ', '-')
    domain = f"{app_slug}.{base_domain}"
    
    # Coolify API requires https:// prefix and port mapping for internal routing
    return f"https://{domain}:{port}"


def create_dockerfile(project_path: Optional[str] = None) -> str:
    """
    Create a Dockerfile for Django application using uv
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        Path to created Dockerfile
    """
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    dockerfile_path = project_path / "Dockerfile"
    
    # Check if Dockerfile already exists
    if dockerfile_path.exists():
        return str(dockerfile_path)
    
    # Django Dockerfile template using uv
    dockerfile_content = '''# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE="{project_name}.settings"

# Set work directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        postgresql-client \\
        gettext \\
        curl \\
    && rm -rf /var/lib/apt/lists/* \\
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (uv installs to /root/.local/bin)
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files and clean them for production
COPY pyproject.toml uv.lock /app/

# Remove local development dependencies for production build
RUN sed -i '/^\\[tool\\.uv\\.sources\\]/,/^$/d' pyproject.toml

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy project
COPY . /app/

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Create volume for SQLite database (if using SQLite)
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD uv run python -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)" || exit 1

# Start server
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
'''
    
    # Try to detect project name
    project_name = "hello_django"  # default
    try:
        manage_py_path = project_path / "manage.py"
        if manage_py_path.exists():
            with open(manage_py_path, 'r') as f:
                content = f.read()
                # Look for DJANGO_SETTINGS_MODULE
                for line in content.split('\n'):
                    if 'DJANGO_SETTINGS_MODULE' in line and '"' in line:
                        settings_module = line.split('"')[1]
                        project_name = settings_module.split('.')[0]
                        break
    except:
        pass
    
    # Replace project name in template
    dockerfile_content = dockerfile_content.format(project_name=project_name)
    
    # Write Dockerfile
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)
    
    return str(dockerfile_path)


def create_requirements_txt(project_path: Optional[str] = None) -> str:
    """
    Create requirements.txt file if it doesn't exist
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        Path to requirements.txt file
    """
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    requirements_path = project_path / "requirements.txt"
    
    # Check if requirements.txt already exists
    if requirements_path.exists():
        return str(requirements_path)
    
    # Check for pyproject.toml and extract dependencies
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import tomllib
            with open(pyproject_path, 'rb') as f:
                pyproject_data = tomllib.load(f)
            
            dependencies = pyproject_data.get('project', {}).get('dependencies', [])
            
            if dependencies:
                with open(requirements_path, 'w') as f:
                    for dep in dependencies:
                        f.write(f"{dep}\\n")
                
                # Add production dependencies
                with open(requirements_path, 'a') as f:
                    f.write("\\n# Production dependencies\\n")
                    f.write("gunicorn>=21.0.0\\n")
                    f.write("whitenoise>=6.0.0\\n")
                    f.write("psycopg2-binary>=2.9.0\\n")
                
                return str(requirements_path)
        except ImportError:
            pass  # tomllib not available in older Python versions
        except Exception:
            pass  # Error reading pyproject.toml
    
    # Create basic requirements.txt
    basic_requirements = """Django>=4.2
gunicorn>=21.0.0
whitenoise>=6.0.0
psycopg2-binary>=2.9.0
"""
    
    with open(requirements_path, 'w') as f:
        f.write(basic_requirements)
    
    return str(requirements_path)


def create_dockerignore(project_path: Optional[str] = None) -> str:
    """
    Create .dockerignore file
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        Path to .dockerignore file
    """
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    dockerignore_path = project_path / ".dockerignore"
    
    # Check if .dockerignore already exists
    if dockerignore_path.exists():
        return str(dockerignore_path)
    
    dockerignore_content = """# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Requirements (we use uv/pyproject.toml)
requirements.txt
requirements-dev.txt

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Node.js (if using frontend tools)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Coolify
coolify.json
"""
    
    with open(dockerignore_path, 'w') as f:
        f.write(dockerignore_content)
    
    return str(dockerignore_path)


def ensure_docker_files(project_path: Optional[str] = None) -> dict:
    """
    Ensure all Docker-related files exist (using uv, no requirements.txt)
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        Dictionary with paths to created files
    """
    created_files = {}
    
    created_files['dockerfile'] = create_dockerfile(project_path)
    created_files['dockerignore'] = create_dockerignore(project_path)
    
    return created_files

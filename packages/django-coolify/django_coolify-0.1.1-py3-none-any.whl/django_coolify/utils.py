"""
Utility functions for django-coolify
"""
import os
import shutil
from pathlib import Path
from typing import Optional


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


def add_health_check_url(project_path: Optional[str] = None) -> bool:
    """
    Add a simple health check URL to Django project
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        True if health check was added, False if it already exists
    """
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    # Find the main URLs file
    urls_files = list(project_path.glob("*/urls.py"))
    main_urls_file = None
    
    for urls_file in urls_files:
        # Skip app-specific urls.py files, look for the main one
        with open(urls_file, 'r') as f:
            content = f.read()
            if 'admin' in content and 'path' in content:
                main_urls_file = urls_file
                break
    
    if not main_urls_file:
        return False
    
    # Check if health check already exists
    with open(main_urls_file, 'r') as f:
        content = f.read()
        if '/health/' in content:
            return False  # Already exists
    
    # Add health check import and URL
    try:
        lines = content.split('\\n')
        
        # Find imports section
        import_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('from django.urls'):
                import_index = i
                break
        
        # Add health check import
        if import_index >= 0:
            lines.insert(import_index + 1, 'from django.http import JsonResponse')
        
        # Find urlpatterns
        patterns_index = -1
        for i, line in enumerate(lines):
            if 'urlpatterns' in line:
                patterns_index = i
                break
        
        if patterns_index >= 0:
            # Find the closing bracket
            for i in range(patterns_index + 1, len(lines)):
                if lines[i].strip() == ']':
                    # Add health check URL before closing bracket
                    lines.insert(i, '    path("health/", lambda request: JsonResponse({"status": "ok"}), name="health"),')
                    break
        
        # Write back to file
        with open(main_urls_file, 'w') as f:
            f.write('\\n'.join(lines))
        
        return True
        
    except Exception:
        return False

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
    Uses the general-purpose AST-based settings modifier
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        True if settings were modified, False otherwise
    """
    # Define the modifications needed for Coolify deployment
    coolify_modifications = {
        'imports': ['os'],
        'settings': {
            'STATIC_ROOT': "BASE_DIR / 'staticfiles'"
        },
        'after_setting': {
            'ALLOWED_HOSTS': [
                '',
                '# Add dynamic allowed hosts from environment',
                'if os.getenv("ALLOWED_HOSTS"):',
                '    ALLOWED_HOSTS.extend(os.getenv("ALLOWED_HOSTS").split(","))'
            ]
        }
    }
    
    return modify_django_settings_ast(project_path, coolify_modifications)


def _analyze_django_settings(tree, source_code: str) -> dict:
    """
    Analyze Django settings.py using AST to find current configuration
    
    Args:
        tree: Parsed AST tree
        source_code: Original source code for line-based analysis
        
    Returns:
        Dictionary with analysis results
    """
    import ast
    
    analysis = {
        'has_os_import': False,
        'has_static_root': False,
        'has_dynamic_allowed_hosts': False,
        'last_import_line': -1,
        'static_url_line': -1,
        'allowed_hosts_line': -1,
        'settings_variables': {},  # Maps variable names to line numbers
        'imports': []  # List of imported modules
    }
    
    lines = source_code.split('\n')
    
    # Walk through AST to find imports and assignments
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                analysis['imports'].append(alias.name)
                if alias.name == 'os':
                    analysis['has_os_import'] = True
            analysis['last_import_line'] = node.lineno - 1  # Convert to 0-based
            
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                analysis['imports'].append(f"from {node.module}")
            analysis['last_import_line'] = node.lineno - 1  # Convert to 0-based
            
        elif isinstance(node, ast.Assign):
            # Check for variable assignments
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    analysis['settings_variables'][var_name] = node.lineno - 1
                    
                    if var_name == 'STATIC_ROOT':
                        analysis['has_static_root'] = True
                    elif var_name == 'STATIC_URL':
                        analysis['static_url_line'] = node.lineno - 1
                    elif var_name == 'ALLOWED_HOSTS':
                        analysis['allowed_hosts_line'] = node.lineno - 1
    
    # Check for dynamic ALLOWED_HOSTS pattern in source code
    if 'os.getenv("ALLOWED_HOSTS")' in source_code:
        analysis['has_dynamic_allowed_hosts'] = True
    
    return analysis


def modify_django_settings_ast(project_path: Optional[str] = None, modifications: dict = None) -> bool:
    """
    General-purpose AST-based Django settings modifier
    
    Args:
        project_path: Path to Django project root
        modifications: Dictionary defining what to modify:
            {
                'imports': ['os', 'sys'],  # Imports to ensure exist
                'settings': {
                    'STATIC_ROOT': "BASE_DIR / 'staticfiles'",  # Settings to add if missing
                    'DEBUG': 'False'  # Settings to add/update
                },
                'after_setting': {
                    'ALLOWED_HOSTS': [  # Code to add after specific settings
                        '',
                        '# Custom configuration',
                        'if os.getenv("ALLOWED_HOSTS"):',
                        '    ALLOWED_HOSTS.extend(os.getenv("ALLOWED_HOSTS").split(","))'
                    ]
                }
            }
        
    Returns:
        True if settings were modified, False otherwise
    """
    import ast
    
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    if not modifications:
        return False
    
    # Find settings.py file
    settings_files = list(project_path.glob("*/settings.py"))
    if not settings_files:
        return False
    
    settings_file = settings_files[0]
    
    try:
        with open(settings_file, 'r') as f:
            source_code = f.read()
        
        # Parse the source code into AST for analysis
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            print(f"Syntax error in {settings_file}: {e}")
            return False
        
        # Analyze current settings
        analysis = _analyze_django_settings(tree, source_code)
        
        lines = source_code.split('\n')
        modified = False
        line_offset = 0  # Track line insertions for subsequent modifications
        
        # 1. Add missing imports
        if 'imports' in modifications:
            for import_name in modifications['imports']:
                if import_name not in analysis['imports']:
                    insert_line = analysis['last_import_line'] + 1 + line_offset
                    lines.insert(insert_line, f'import {import_name}')
                    modified = True
                    line_offset += 1
        
        # 2. Add/update settings
        if 'settings' in modifications:
            for setting_name, setting_value in modifications['settings'].items():
                if setting_name not in analysis['settings_variables']:
                    # Add new setting at the end
                    lines.append(f'{setting_name} = {setting_value}')
                    modified = True
        
        # 3. Add code after specific settings
        if 'after_setting' in modifications:
            for setting_name, code_lines in modifications['after_setting'].items():
                if setting_name in analysis['settings_variables']:
                    # Check if the code is already present
                    code_exists = all(line.strip() in source_code for line in code_lines if line.strip())
                    if not code_exists:
                        insert_line = analysis['settings_variables'][setting_name] + 1 + line_offset
                        for i, code_line in enumerate(code_lines):
                            lines.insert(insert_line + i, code_line)
                        modified = True
                        line_offset += len(code_lines)
        
        # Write back if modified
        if modified:
            with open(settings_file, 'w') as f:
                f.write('\n'.join(lines))
        
        return modified
        
    except Exception as e:
        print(f"Error modifying Django settings: {e}")
        return False


def auto_configure_django_urls(project_path: Optional[str] = None) -> bool:
    """
    Automatically configure Django URLs to include django_coolify health endpoint
    Uses AST parsing for reliable Python code analysis with string-based modifications
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        True if URLs were modified, False otherwise
    """
    import ast
    
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    # Find the main urls.py file (usually in project_name/urls.py)
    urls_files = list(project_path.glob("*/urls.py"))
    if not urls_files:
        return False
    
    # Filter to find the main urls.py (typically contains admin.site.urls)
    main_urls_file = None
    for urls_file in urls_files:
        try:
            with open(urls_file, 'r') as f:
                content = f.read()
                if 'admin.site.urls' in content:
                    main_urls_file = urls_file
                    break
        except Exception:
            continue
    
    if not main_urls_file:
        main_urls_file = urls_files[0]  # Fallback to first found
    
    try:
        with open(main_urls_file, 'r') as f:
            source_code = f.read()
        
        # Parse the source code into AST for analysis
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            print(f"Syntax error in {main_urls_file}: {e}")
            return False
        
        # Check if django_coolify URLs are already included
        django_coolify_urls_exist = 'django_coolify.urls' in source_code
        
        # Analyze imports using AST
        has_include_import = False
        django_urls_import_info = None
        
        for node in tree.body:
            if (isinstance(node, ast.ImportFrom) and 
                node.module == 'django.urls'):
                
                # Store import information
                imported_names = [alias.name for alias in node.names]
                django_urls_import_info = {
                    'line': node.lineno,
                    'names': imported_names,
                    'has_include': 'include' in imported_names
                }
                
                if 'include' in imported_names:
                    has_include_import = True
                break
        
        # Use string manipulation for modifications (more reliable than AST reconstruction)
        lines = source_code.split('\n')
        modified = False
        
        # Fix import if needed
        if django_urls_import_info and not has_include_import:
            import_line_idx = django_urls_import_info['line'] - 1  # AST uses 1-based line numbers
            current_line = lines[import_line_idx]
            
            # Add include to the existing import
            if 'path' in current_line and 'include' not in current_line:
                lines[import_line_idx] = current_line.replace(
                    'from django.urls import path',
                    'from django.urls import path, include'
                )
                modified = True
            elif 'include' not in current_line:
                # Handle other cases
                lines[import_line_idx] = current_line.replace(
                    'from django.urls import',
                    'from django.urls import include,'
                )
                modified = True
        elif not django_urls_import_info:
            # No django.urls import found, add one
            insert_index = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if (line.startswith('from django.') or line.startswith('import django')):
                    insert_index = i + 1
                elif stripped == '' and insert_index > 0:
                    break
            
            lines.insert(insert_index, 'from django.urls import include')
            modified = True
        
        # Add django_coolify URLs if not present (using AST to find urlpatterns)
        if not django_coolify_urls_exist:
            # Find urlpatterns assignment using AST
            urlpatterns_line = None
            for node in tree.body:
                if (isinstance(node, ast.Assign) and 
                    len(node.targets) == 1 and 
                    isinstance(node.targets[0], ast.Name) and 
                    node.targets[0].id == 'urlpatterns'):
                    urlpatterns_line = node.lineno
                    break
            
            if urlpatterns_line:
                # Find the closing bracket of urlpatterns list
                start_line = urlpatterns_line - 1  # Convert to 0-based
                bracket_count = 0
                insert_line = None
                
                for i in range(start_line, len(lines)):
                    line = lines[i]
                    bracket_count += line.count('[') - line.count(']')
                    if bracket_count == 0 and ']' in line:
                        insert_line = i
                        break
                
                if insert_line is not None:
                    # Insert before the closing bracket
                    lines.insert(insert_line, "    path('django-coolify/', include('django_coolify.urls')),")
                    modified = True
        
        # Write back if modified
        if modified:
            with open(main_urls_file, 'w') as f:
                f.write('\n'.join(lines))
        
        return modified
        
    except Exception as e:
        print(f"Error configuring Django URLs: {e}")
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

# Health check using curl (more reliable than requests)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/django-coolify/health/ || exit 1

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

# Virtual environments and env files
.env
.env.*
*.env
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

# Development files
README.md
"""
    
    with open(dockerignore_path, 'w') as f:
        f.write(dockerignore_content)
    
    return str(dockerignore_path)


def ensure_gitignore_entries(project_path: Optional[str] = None) -> bool:
    """
    Ensure sensitive files are in .gitignore
    
    Args:
        project_path: Path to Django project root
        
    Returns:
        True if .gitignore was modified, False otherwise
    """
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    gitignore_path = project_path / ".gitignore"
    
    # Entries to ensure are in .gitignore
    required_entries = [
        ".env",
        "*.env",
        ".env.local", 
        ".env.*.local"
    ]
    
    existing_entries = set()
    if gitignore_path.exists():
        try:
            with open(gitignore_path, 'r') as f:
                existing_entries = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        except Exception:
            pass
    
    # Find missing entries
    missing_entries = [entry for entry in required_entries if entry not in existing_entries]
    
    if missing_entries:
        try:
            with open(gitignore_path, 'a') as f:
                if gitignore_path.exists():
                    f.write('\n')
                f.write('# Environment variables (added by django-coolify)\n')
                for entry in missing_entries:
                    f.write(f'{entry}\n')
            return True
        except Exception as e:
            print(f"Warning: Could not update .gitignore: {e}")
    
    return False


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

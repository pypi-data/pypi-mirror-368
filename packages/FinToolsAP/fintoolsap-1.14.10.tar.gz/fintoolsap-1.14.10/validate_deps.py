#!/usr/bin/env python3
"""
Dependency Validation Script for FinToolsAP

This script validates the dependencies in pyproject.toml by:
1. Checking syntax correctness
2. Verifying all dependencies are available on PyPI
3. Checking for potential version conflicts
4. Identifying unused dependencies
5. Finding missing dependencies
"""

import ast
import sys
import subprocess
import toml
import requests
from pathlib import Path

def check_pyproject_syntax(pyproject_path):
    """Check if pyproject.toml is syntactically correct"""
    try:
        with open(pyproject_path, 'r') as f:
            data = toml.load(f)
        print("✅ pyproject.toml syntax is valid")
        return data
    except Exception as e:
        print(f"❌ pyproject.toml syntax error: {e}")
        return None

def parse_requirement(req_string):
    """Parse a requirement string to extract package name and version constraints"""
    import re
    
    # Remove whitespace
    req_string = req_string.strip()
    
    # Extract package name (everything before version specifiers)
    match = re.match(r'^([a-zA-Z0-9_-]+)', req_string)
    if not match:
        return None, None
    
    package_name = match.group(1)
    version_spec = req_string[len(package_name):].strip()
    
    return package_name, version_spec

def check_package_exists(package_name):
    """Check if a package exists on PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        return response.status_code == 200
    except:
        return False

def find_imports_in_code(src_path):
    """Find all import statements in Python files"""
    imports = set()
    
    for py_file in Path(src_path).rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except Exception as e:
            print(f"Warning: Could not parse {py_file}: {e}")
    
    return imports

def get_standard_library_modules():
    """Get a list of standard library modules"""
    import sys
    stdlib_modules = set()
    
    # Common standard library modules
    common_stdlib = {
        'os', 'sys', 'json', 'csv', 'xml', 'html', 'http', 'urllib', 'email',
        'datetime', 'time', 'calendar', 'collections', 'heapq', 'bisect',
        'array', 'weakref', 'types', 'copy', 'pprint', 'reprlib', 'enum',
        'numbers', 'math', 'cmath', 'decimal', 'fractions', 'random', 'statistics',
        'itertools', 'functools', 'operator', 'pathlib', 'os.path', 'fileinput',
        'stat', 'filecmp', 'tempfile', 'glob', 'fnmatch', 'linecache', 'shutil',
        'pickle', 'copyreg', 'shelve', 'marshal', 'dbm', 'sqlite3', 'zlib',
        'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile', 'hashlib', 'hmac', 'secrets',
        'io', 'stringio', 'textwrap', 're', 'difflib', 'unicodedata', 'readline',
        'rlcompleter', 'subprocess', 'threading', 'multiprocessing', 'concurrent',
        'queue', 'asyncio', 'socket', 'ssl', 'select', 'selectors', 'signal',
        'mmap', 'logging', 'traceback', 'warnings', 'contextlib', 'abc',
        'atexit', 'tracemalloc', 'gc', 'inspect', 'site', 'importlib', 'zipimport',
        'pkgutil', 'modulefinder', 'runpy', 'typing', 'pydoc', 'doctest',
        'unittest', 'test', 'lib2to3', 'venv', 'dataclasses'
    }
    
    return common_stdlib

def map_import_to_package():
    """Map import names to PyPI package names"""
    mapping = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'scipy': 'scipy',
        'matplotlib': 'matplotlib',
        'sklearn': 'scikit-learn',
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'yaml': 'PyYAML',
        'dateutil': 'python-dateutil',
        'polars': 'polars',
        'tqdm': 'tqdm',
        'sqlalchemy': 'sqlalchemy',
        'wrds': 'wrds',
        'connectorx': 'connectorx',
        'statsmodels': 'statsmodels',
        'seaborn': 'seaborn',
        'linearmodels': 'linearmodels',
        'bottleneck': 'bottleneck',
        'knockknock': 'knockknock',
        'pyarrow': 'pyarrow',
        'twine': 'twine',
        'build': 'build',
        'pdoc': 'pdoc',
        'tracemalloc': None,  # Standard library
        'pathlib': None,  # Standard library in Python 3.4+
    }
    return mapping

def validate_dependencies():
    """Main validation function"""
    print("🔍 Validating FinToolsAP dependencies...")
    print("=" * 50)
    
    # Load pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False
    
    data = check_pyproject_syntax(pyproject_path)
    if not data:
        return False
    
    # Get dependencies
    dependencies = data.get('project', {}).get('dependencies', [])
    print(f"📦 Found {len(dependencies)} dependencies in pyproject.toml")
    
    # Parse dependencies
    parsed_deps = {}
    issues = []
    
    for dep in dependencies:
        package_name, version_spec = parse_requirement(dep)
        if package_name:
            parsed_deps[package_name] = version_spec
        else:
            issues.append(f"Could not parse requirement: {dep}")
    
    # Check if packages exist on PyPI
    print("\n🌐 Checking if packages exist on PyPI...")
    missing_packages = []
    for package_name in parsed_deps:
        if not check_package_exists(package_name):
            missing_packages.append(package_name)
            print(f"❌ {package_name} not found on PyPI")
        else:
            print(f"✅ {package_name}")
    
    # Find imports in source code
    print("\n🔍 Analyzing imports in source code...")
    src_path = Path("src/FinToolsAP")
    if src_path.exists():
        imports = find_imports_in_code(src_path)
        stdlib_modules = get_standard_library_modules()
        import_to_package = map_import_to_package()
        
        # Filter out standard library imports and internal imports
        external_imports = set()
        for imp in imports:
            if imp not in stdlib_modules and not imp.startswith('_') and imp != 'FinToolsAP':
                if imp in import_to_package:
                    if import_to_package[imp]:  # Not None (stdlib)
                        external_imports.add(import_to_package[imp])
                else:
                    external_imports.add(imp)
        
        print(f"Found {len(external_imports)} external imports: {sorted(external_imports)}")
        
        # Check for missing dependencies
        declared_packages = set(parsed_deps.keys())
        missing_deps = external_imports - declared_packages
        unused_deps = declared_packages - external_imports
        
        if missing_deps:
            print(f"\n⚠️  Potentially missing dependencies: {sorted(missing_deps)}")
        
        if unused_deps:
            print(f"\n⚠️  Potentially unused dependencies: {sorted(unused_deps)}")
            # Note: Some packages might be development dependencies
            dev_packages = {'twine', 'build', 'pdoc'}
            unused_runtime = unused_deps - dev_packages
            if unused_runtime:
                print(f"⚠️  Unused runtime dependencies: {sorted(unused_runtime)}")
    
    # Check for problematic dependency specifications
    print("\n🔧 Checking dependency specifications...")
    problematic_specs = []
    
    for package_name, version_spec in parsed_deps.items():
        if not version_spec:
            problematic_specs.append(f"{package_name}: No version constraint (could cause instability)")
        elif version_spec.startswith('=='):
            problematic_specs.append(f"{package_name}: Exact version pin (may cause conflicts)")
    
    # Specific issues found in your dependencies
    specific_issues = []
    
    # Check pathlib issue
    if 'pathlib' in parsed_deps:
        specific_issues.append("pathlib: This is part of the standard library since Python 3.4+. Should be removed from dependencies.")
    
    # Report results
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if not issues and not missing_packages and not specific_issues:
        print("✅ All dependencies are correctly specified!")
    else:
        if issues:
            print("\n❌ PARSING ISSUES:")
            for issue in issues:
                print(f"   • {issue}")
        
        if missing_packages:
            print("\n❌ MISSING PACKAGES:")
            for pkg in missing_packages:
                print(f"   • {pkg}")
        
        if specific_issues:
            print("\n⚠️  SPECIFIC ISSUES:")
            for issue in specific_issues:
                print(f"   • {issue}")
        
        if problematic_specs:
            print("\n⚠️  POTENTIAL ISSUES:")
            for issue in problematic_specs:
                print(f"   • {issue}")
    
    return len(issues) == 0 and len(missing_packages) == 0

if __name__ == "__main__":
    success = validate_dependencies()
    sys.exit(0 if success else 1)

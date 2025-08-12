"""Import to package name mappings.

This module contains mappings from Python import names to their
corresponding PyPI package names.
"""

from typing import Optional

from .utils import is_standard_library

# Common import name to package name mappings
IMPORT_TO_PACKAGE = {
    # Image processing
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "skimage": "scikit-image",
    # Scientific computing
    "sklearn": "scikit-learn",
    "scipy": "scipy",
    "numpy": "numpy",
    "pandas": "pandas",
    # Web frameworks
    "flask": "Flask",
    "django": "Django",
    "fastapi": "fastapi",
    # Database
    "MySQLdb": "mysqlclient",
    "psycopg2": "psycopg2-binary",
    "pymongo": "pymongo",
    "redis": "redis",
    "sqlalchemy": "SQLAlchemy",
    # Data formats
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "openpyxl": "openpyxl",
    "docx": "python-docx",
    "PyPDF2": "PyPDF2",
    # Testing
    "pytest": "pytest",
    "nose": "nose",
    "mock": "mock",
    # Other common mappings
    "dotenv": "python-dotenv",
    "jwt": "PyJWT",
    "cryptography": "cryptography",
    "requests": "requests",
    "click": "click",
    "tqdm": "tqdm",
    "colorama": "colorama",
    "dateutil": "python-dateutil",
}


def resolve_package_name(import_name: str) -> Optional[str]:
    """Resolve import name to PyPI package name.

    Args:
        import_name: Name used in import statement.

    Returns:
        PyPI package name, or None if it's a standard library module.
    """

    # Check if it's a standard library module
    if is_standard_library(import_name):
        return None

    # Filter out reqtracker itself to avoid self-reference
    if import_name == "reqtracker":
        return None

    # Filter out namespace packages that are part of other packages
    if import_name in {"mpl_toolkits"}:
        return None

    # Check our mapping
    return IMPORT_TO_PACKAGE.get(import_name, import_name)

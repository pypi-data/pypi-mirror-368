"""
Copyright (C) 2025, Jabez Winston C

Docuver - Document Version Control Tool

A meta tool for version control of Office documents (docx, xlsx, odt, ods, odp).
Converts binary Office files to/from extracted folder representations for proper versioning.

Author  : Jabez Winston C <jabezwinston@gmail.com>
License : MIT
Date    : 10 Aug 2025

"""

from .version import VERSION

__version__ = VERSION
__author__ = 'Jabez Winston C'
__email__ = 'jabezwinston@gmail.com'
__license__ = 'MIT'

from .core import Docuver, DocuverError
from .cli import main

__all__ = ['Docuver', 'DocuverError', 'main']

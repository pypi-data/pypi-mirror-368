"""
Django API Explorer

A powerful command-line tool and web interface for discovering, documenting, and testing API endpoints in Django projects.
"""

__version__ = "1.0.4"
__author__ = "Vikas Gole"
__email__ = "vikasgole089@gmail.com"

# Import main components to make them available at package level
from .cli import main

__all__ = ["main"]

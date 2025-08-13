"""
ImageNet Classes Package

A Python package for managing and retrieving ImageNet-1k mappings among integer class IDs, string class IDs, and human-readable class names.
"""

from .class_loader import ClassDictionary

__version__ = "0.1.1"
__author__ = "Illia Volkov, Nikita Kisel"
__email__ = "kiselnik@fel.cvut.cz"

__all__ = ["ClassDictionary"]

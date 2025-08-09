"""Strangeworks Qiskit SDK"""
import importlib.metadata

from .backend import StrangeworksBackend  # noqa: F401
from .job import StrangeworksQuantumJob  # noqa: F401

__version__ = importlib.metadata.version("strangeworks-azure")

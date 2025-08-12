"""
Robin Logistics Environment

A professional logistics optimization environment for hackathons and competitions.
"""

__version__ = "2.1.0"
__author__ = "Robin"
__email__ = "mario.salama@beltoneholding.com"
__description__ = "A professional logistics optimization environment for hackathons and competitions"

from .environment import LogisticsEnvironment
from .solvers import test_solver, nearest_neighbor_solver, advanced_solver

__all__ = [
    "LogisticsEnvironment",
    "test_solver", 
    "nearest_neighbor_solver",
    "advanced_solver"
]
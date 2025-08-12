"""
NUVA SDK - Unified Vaccine Nomenclature

A Python SDK for working with the Unified Vaccine Nomenclature (NUVA),
designed to aggregate vaccination histories from both digital and physical sources.
"""

from .nuva import Nuva, Repository, NuvaRepositories, NuvaQueries

__version__ = "1.0.0"
__all__ = ["Nuva", "Repository", "NuvaRepositories", "NuvaQueries"]

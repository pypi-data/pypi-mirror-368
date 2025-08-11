"""
Volume-based routines for estimating atom counts in supported nanoparticles.

Functions
---------
calculate_volumes(element: str, r: float, theta: float, facet: tuple) -> tuple
    Calculate volume of the interfacial region (excluding the perimeter region),
    perimeter region, and the entire nanoparticle
    using:
        1. contact angle (theta)
        2. footprint/interfacial radius (r) in Angstrom
        3. chemical symbol of the nanoparticle's atoms (element)
        4. facet of nanoparticle oriented to support (facet)

calculate_by_volume(element: str, r: float, theta: float, facet: tuple) -> tuple
    Main function to do all calculations through the 'volume' method
"""

from typing import Tuple, List
import numpy as np
import warnings
from NanoparticleAtomCounter.count_utilities import (
    volume_to_atoms,
    area_to_atoms,
    calculate_atomic_density,
    calculate_total_volume,
    calculate_surface_area,
    calculate_constants,
)

# warnings.filterwarnings(action="ignore")


def calculate_volumes(
    element: str,
    footprint_radius: float,
    theta: float = None,
    interface_facet: Tuple[int, int, int] = None,
) -> Tuple[float, float, float]:
    """
    Calculate volume of the interfacial region (excluding the perimeter region),
    perimeter region, and the entire nanoparticle

    Requires:
        element (str):              atomic symbol for atom type in the nanoparticle
        theta (float):              contact angle. degrees
        footprint_radius (float):   NP footprint radius. In Ang
        interface_facet (Tuple[int,int,int]): facet facing the support

    Returns:
        interface_volume, perimeter_volume, total_volume     all in A^3
    """
    # R: radius from spherical cap center,
    # r: footprint radius (i.e. radius of bottom of spherical segment),
    # x: radius of top of spherical segment, z: height of spherical segment,
    # x2: x but excluding the perimeter having thickness == z1,
    # r2: r but excluding the perimeter having thickness == z1,
    # h:
    # if θ>90: distance from sphere center vertically down to top of spherical segment
    # if θ<90: distance from sphere center vertically up to bottom of interface
    # if θ==90: zero
    # z1: atomic diameter
    # z: interplanar spacing at the interface, i.e. this is the height of the interface
    if theta in [0, 180]:
        raise ValueError(f"Contact angle of {theta} not allowed")
    elif theta > 180 or theta < 0:
        raise ValueError(f"Supplied {theta} is > 180 or < 0. Not allowed")

    r = footprint_radius  # to make things clear
    if r <= 0:
        raise ValueError(f"r ({r}) Ang supplied is <= 0. Invalid")
    if r < 5:
        warnings.warn(
            f"""Small value of r ({r}) Ang supplied; a spherical cap
        approximation may be tenuous""",
            category=UserWarning,
        )

    _, z, z1 = calculate_constants(element=element, facet=interface_facet)

    R = r / np.sin(np.radians(theta))
    # r2 = radial spacing
    r2 = np.clip(
        r - z1, 0, None
    )  # no reliable formula for radial spacing. assumed to be = atomic diameter
    # clip so it doesn't become negative for extremely small footprint radii
    ##Find h and x
    if theta > 90:
        h = np.sqrt(R**2 - r**2) - z  # thus spake pythagoras
        x = np.sqrt(R**2 - h**2)  # eqn 1
        dome_height = h + z + R
        x2 = np.sqrt(
            (2 * h * z) + (z**2) + (r2**2)
        )  # from eqn1, noting that R^2 = (h+z)^2 + r^2 and then substituting r2 for r
    else:
        h = np.clip(np.sqrt(R**2 - r**2), 0, None)  # clip so h==0 if theta == 90
        dome_height = R + h
        x = np.sqrt(R**2 - ((h + z) ** 2))  # eqn 2
        x2 = np.sqrt(
            (h**2) - ((h + z) ** 2) + (r2**2)
        )  # can have invalid values; see below notes


    # Formula from https://en.wikipedia.org/wiki/Spherical_segment
    segment_volume = np.pi * z * ((3 * (r**2 + x**2)) + z**2) / 6
    interface_volume = np.pi * z * ((3 * (r2**2 + x2**2)) + z**2) / 6
    total_volume = calculate_total_volume(r, theta)

    # if x2 was negative, then it means for the given combination of r and theta, if you shave off z from r
    # then too much will be shaved off from the top of the spherical segment that its radius (x2) becomes negative
    # this implies that we can't have any non-perimeter atoms for such a system
    # for a given r, will be more likely for smaller theta
    # for a given theta, will be more likely for smaller r
    if np.isnan(interface_volume):
        warnings.warn(
            f"""footprint radius ({r}) and-or θ ({theta}) too small.
        There is no non-perimeter for the given combination of r and θ""",
            category=RuntimeWarning,
        )
        interface_volume = 0

    perimeter_volume = segment_volume - interface_volume

    return interface_volume, perimeter_volume, total_volume


def calculate_by_volume(
    element: str,
    footprint_radius: float,
    theta: float = None,
    interface_facet: Tuple[int, int, int] = None,
    surface_facet: Tuple[int, int, int] = None,
) -> Tuple[int, int, int, int]:
    """
    Main function to do all calculations through the 'volume' method

    Units: A^3

    Requires:
        element (str):              atomic symbol for atom type in the nanoparticle
        theta (float):              contact angle. degrees
        footprint_radius (float):   NP footprint radius. In Ang
        interface_facet (Tuple[int,int,int]): facet facing the support
        surface_facet (Tuple[int,int,int]): facet facing vacuum

    Returns:
        perimeter_atoms, interfacial_atoms, surface_atoms, all_atoms
    """

    interfacial_volume, perimeter_volume, total_volume = calculate_volumes(
        element=element,
        footprint_radius=footprint_radius,
        theta=theta,
        interface_facet=interface_facet,
    )

    interfacial_atoms, perimeter_atoms, total_atoms = [
        volume_to_atoms(
            volume=i,
            element=element,
            molar_volume=None,
        )
        for i in [interfacial_volume, perimeter_volume, total_volume]
    ]

    surface_area = calculate_surface_area(
        element=element,
        footprint_radius=footprint_radius,
        theta=theta,
        interface_facet=interface_facet,
    )

    surface_atoms = area_to_atoms(
        area=surface_area, element=element, facet=surface_facet
    )

    return perimeter_atoms, interfacial_atoms, surface_atoms, total_atoms

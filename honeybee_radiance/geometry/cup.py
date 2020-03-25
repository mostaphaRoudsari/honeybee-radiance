"""Radiance Cup.

http://radsite.lbl.gov/radiance/refer/ray.html#Cup
"""
from .cone import Cone


class Cup(Cone):
    """Radiance Cup.

    A cup is an inverted cone (i.e., has an inward surface normal).

    A cone is a megaphone-shaped object. It is truncated by two planes perpendicular to
    its axis, and one of its ends may come to a point. It is given as two axis endpoints,
    and the starting and ending radii:

    .. code-block:: shell

        mod cup id
        0
        0
        8
                x0      y0      z0
                x1      y1      z1
                r0      r1

    Args:
        name: Geometry name as a string. Do not use white space or special
            character.
        center_pt_start: Cup start center point as (x, y, z) (Default: (0, 0 ,0)).
        radius_start: Cup start radius as a number (Default: 10).
        center_pt_end: Cup end center point as (x, y, z) (Default: (0, 0 ,10)).
        radius_end: Cup end radius as a number (Default: 0).
        modifier: Geometry modifier (Default: "void").
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])


    Properties:
        * name
        * center_pt_start
        * radius_start
        * center_pt_end
        * radius_end
        * values
        * modifier
        * dependencies
    """
    __slots__ = ()

    pass
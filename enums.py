"""
ShotPattern club identifier enums.

This module defines the valid club identifiers used by the ShotPattern application.
These values represent the standardized club naming convention for golf club tracking.
"""

from enum import Enum


class ShotPatternClub(Enum):
    """
    Enum representing all valid ShotPattern club identifiers.

    Each value corresponds to a specific club type that can be tracked
    in the ShotPattern application.
    """

    # Driver
    Dr = "Dr"
    Dr2 = "Dr2"

    # Woods
    W2 = "2W"
    W3 = "3W"
    W4 = "4W"
    W5 = "5W"
    W6 = "6W"
    W7 = "7W"
    W8 = "8W"
    W9 = "9W"
    W10 = "10W"
    W11 = "11W"
    W12 = "12W"
    W13 = "13W"
    W14 = "14W"
    W15 = "15W"

    # Hybrids
    Hy1 = "1Hy"
    Hy2 = "2Hy"
    Hy3 = "3Hy"
    Hy4 = "4Hy"
    Hy5 = "5Hy"
    Hy6 = "6Hy"
    Hy7 = "7Hy"
    Hy8 = "8Hy"
    Hy9 = "9Hy"
    Hy10 = "10Hy"
    Hy11 = "11Hy"
    Hy12 = "12Hy"
    Hy13 = "13Hy"
    Hy14 = "14Hy"
    Hy15 = "15Hy"

    # Irons
    I1 = "1i"
    I2 = "2i"
    I3 = "3i"
    I4 = "4i"
    I5 = "5i"
    I6 = "6i"
    I7 = "7i"
    I8 = "8i"
    I9 = "9i"
    I10 = "10i"
    I11 = "11i"

    # Standard Wedges
    PW = "PW"
    GW = "GW"
    SW = "SW"
    LW = "LW"

    # Degree-specific Wedges (48° to 64°)
    W48 = "48°"
    W49 = "49°"
    W50 = "50°"
    W51 = "51°"
    W52 = "52°"
    W53 = "53°"
    W54 = "54°"
    W55 = "55°"
    W56 = "56°"
    W57 = "57°"
    W58 = "58°"
    W59 = "59°"
    W60 = "60°"
    W61 = "61°"
    W62 = "62°"
    W63 = "63°"
    W64 = "64°"

    # Putter
    Putter = "Putter"

    def __str__(self):
        """Return the string representation of the club."""
        return self.value

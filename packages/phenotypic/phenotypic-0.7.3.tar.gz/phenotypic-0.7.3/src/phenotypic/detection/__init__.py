"""
The detection module contains classes for detecting objects in images.

"""

from ._otsu_detector import OtsuDetector
from ._triangle_detector import TriangleDetector
from ._watershed_detector import WatershedDetector

__all__ = ["OtsuDetector", "TriangleDetector", "WatershedDetector"]
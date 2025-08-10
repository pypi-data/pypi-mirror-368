from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from phenotypic import GridImage

from phenotypic.abstract import MapModifier
from phenotypic.abstract import GridOperation
from phenotypic.util.exceptions_ import GridImageInputError
from phenotypic.util.funcs_ import validate_operation_integrity


class GridMapModifier(MapModifier, GridOperation):

    @validate_operation_integrity('image.array', 'image.matrix', 'image.enh_matrix')
    def apply(self, image: GridImage, inplace: bool = False) -> GridImage:
        from phenotypic import GridImage
        if not isinstance(image, GridImage): raise GridImageInputError()
        output = super().apply(image=image, inplace=inplace)
        return output

    def _operate(self, image: GridImage) -> GridImage:
        return image

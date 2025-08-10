from __future__ import annotations
from typing import Callable, TYPE_CHECKING
import skia

if TYPE_CHECKING:
    from ..nodes import Node
    from ..models import SizeValue

class SizeResolver:

    def __init__(self, node: Node):
        self._node = node
        self._intrinsic_bounds: skia.Rect | None = None
    
    def resolve_width(self) -> int:
        if self._node._forced_size[0] is not None:
            forced_width, _ = self._node._forced_size
            spacing = self._get_horizontal_spacing()
            return max(0, forced_width - spacing)

        width = self._node.computed_styles.width.get()
        if not width:
            return self._node.compute_intrinsic_width()

        spacing = self._get_horizontal_spacing()
        box_width = self._get_axis_size(
            width,
            lambda: self._node.compute_intrinsic_width() + spacing,
            lambda: self._get_background_value("width"),
            lambda: self._get_container_value("width")
        )
        return max(0, box_width - spacing)

    def resolve_height(self) -> int:
        if self._node._forced_size[1] is not None:
            _, forced_height = self._node._forced_size
            spacing = self._get_vertical_spacing()
            return max(0, forced_height - spacing)

        height = self._node.computed_styles.height.get()
        if not height:
            return self._node.compute_intrinsic_height()

        spacing = self._get_vertical_spacing()
        box_height = self._get_axis_size(
            height,
            lambda: self._node.compute_intrinsic_height() + spacing,
            lambda: self._get_background_value("height"),
            lambda: self._get_container_value("height")
        )

        return max(0, box_height - spacing)
    
    def _get_horizontal_spacing(self) -> float:
        padding = self._node.computed_styles.padding.get()
        border = self._node.computed_styles.border.get()
        border_width = border.width if border else 0
        return padding.left + padding.right + (border_width * 2)
    
    def _get_vertical_spacing(self) -> float:
        padding = self._node.computed_styles.padding.get()
        border = self._node.computed_styles.border.get()
        border_width = border.width if border else 0
        return padding.top + padding.bottom + (border_width * 2)

    def _get_background_value(self, axis: str) -> float:
        background_image = self._node.computed_styles.background_image.get()
        if not background_image:
            raise ValueError("Cannot use 'fit-background-image' on an element without a background image.")

        image = background_image.get_skia_image()
        if not image:
            raise ValueError(f"Background image for node could not be loaded: {background_image.path}")

        return getattr(image, axis)()

    def _get_container_value(self, axis: str) -> float:
        parent = self._node.parent
        if not parent:
            raise ValueError("Cannot use 'percent' size on a root element without a parent.")

        parent_size = getattr(parent.computed_styles, axis).get()
        if not parent_size or parent_size.mode == 'fit-content' or parent_size.mode == 'auto':
            raise ValueError("Cannot use 'percent' size if parent element has 'fit-content' size.")

        if axis == 'width':
            return parent.content_width
        elif axis == 'height':
            return parent.content_height
        
        raise ValueError(f"Unknown axis: {axis}")

    def _get_axis_size(
            self,
            value: 'SizeValue',
            get_content_value: Callable[[], float],
            get_background_value: Callable[[], float],
            get_container_value: Callable[[], float]
    ) -> float:
        if value.mode == 'absolute':
            return value.value
        if value.mode == 'percent':
            return get_container_value() * (value.value / 100.0)
        if value.mode == 'fit-content' or value.mode == 'auto':
            return get_content_value()
        if value.mode == 'fit-background-image':
            return get_background_value()
        raise ValueError(f"Unsupported size mode: {value.mode}")

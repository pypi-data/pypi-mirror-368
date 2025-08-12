import numpy as np
from .. config.constants import constants
from .brush_preview import create_brush_mask


class BrushController:
    def __init__(self, brush):
        self._brush_mask_cache = {}
        self.brush = brush

    def apply_brush_operation(self, master_layer, source_layer, dest_layer, mask_layer, view_pos, image_viewer):
        if master_layer is None or source_layer is None:
            return False
        if dest_layer is None:
            dest_layer = master_layer
        scene_pos = image_viewer.mapToScene(view_pos)
        x_center = int(round(scene_pos.x()))
        y_center = int(round(scene_pos.y()))
        radius = int(round(self.brush.size // 2))
        h, w = master_layer.shape[:2]
        x_start, x_end = max(0, x_center - radius), min(w, x_center + radius + 1)
        y_start, y_end = max(0, y_center - radius), min(h, y_center + radius + 1)
        if x_start >= x_end or y_start >= y_end:
            return 0, 0, 0, 0
        mask = self.get_brush_mask(radius)
        if mask is None:
            return 0, 0, 0, 0
        master_area = master_layer[y_start:y_end, x_start:x_end]
        source_area = source_layer[y_start:y_end, x_start:x_end]
        dest_area = dest_layer[y_start:y_end, x_start:x_end]
        mask_layer_area = mask_layer[y_start:y_end, x_start:x_end]
        mask_area = mask[y_start - (y_center - radius):y_end - (y_center - radius), x_start - (x_center - radius):x_end - (x_center - radius)]
        mask_layer_area[:] = np.clip(mask_layer_area + mask_area * self.brush.flow / 100.0, 0.0, 1.0)  # np.maximum(mask_layer_area, mask_area)
        self.apply_mask(master_area, source_area, mask_layer_area, dest_area)
        return x_start, y_start, x_end, y_end

    def get_brush_mask(self, radius):
        mask_key = (radius, self.brush.hardness)
        if mask_key not in self._brush_mask_cache.keys():
            full_mask = create_brush_mask(size=radius * 2 + 1, hardness_percent=self.brush.hardness,
                                          opacity_percent=self.brush.opacity)
            self._brush_mask_cache[mask_key] = full_mask
        return self._brush_mask_cache[mask_key]

    def apply_mask(self, master_area, source_area, mask_area, dest_area):
        opacity_factor = float(self.brush.opacity) / 100.0
        effective_mask = np.clip(mask_area * opacity_factor, 0, 1)
        dtype = master_area.dtype
        max_px_value = constants.MAX_UINT16 if dtype == np.uint16 else constants.MAX_UINT8
        if master_area.ndim == 3:
            dest_area[:] = np.clip(master_area * (1 - effective_mask[..., np.newaxis]) + source_area * # noqa
                                   effective_mask[..., np.newaxis], 0, max_px_value).astype(dtype)
        else:
            dest_area[:] = np.clip(master_area * (1 - effective_mask) + source_area * effective_mask, 0, max_px_value).astype(dtype)

    def clear_cache(self):
        self._brush_mask_cache.clear()

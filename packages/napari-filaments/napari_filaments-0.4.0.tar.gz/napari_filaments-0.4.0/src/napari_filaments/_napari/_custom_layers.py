from __future__ import annotations

import numpy as np
from magicgui import register_type
from magicgui.widgets.bases import CategoricalWidget
from napari.layers import Shapes
from napari.utils._magicgui import find_viewer_ancestor
from psygnal import Signal

from napari_filaments._consts import ROI_ID


class FilamentsLayer(Shapes):
    _type_string = "shapes"

    data_added = Signal(np.ndarray)
    data_removed = Signal(dict[int, np.ndarray])
    draw_finished = Signal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_properties = {ROI_ID: 0}

    def add(self, data, *, shape_type="rectangle", **kwargs):
        next_id = self.nshapes
        props = self.current_properties
        props[ROI_ID] = next_id
        self.current_properties = props
        out = super().add(data, shape_type=shape_type, **kwargs)
        self.data_added.emit()
        return out

    def remove_selected(self):
        selected = list(self.selected_data)
        info = {i: self.data[i].copy() for i in selected}
        out = super().remove_selected()
        self.data_removed.emit(info)
        self._relabel()
        return out

    def _finish_drawing(self, event=None):
        was_creating = self._is_creating
        out = super()._finish_drawing(event)
        if was_creating:
            # NOTE: Emit here. Before calling super class method, the last data
            # may have a duplicated vertex.
            self.draw_finished.emit(self)
        return out

    def _relabel(self):
        """Relabel ROI IDs."""
        feat = self.features
        feat[ROI_ID] = np.arange(self.nshapes)
        self.features = feat
        return None


def get_filaments_layer(gui: CategoricalWidget) -> list[FilamentsLayer]:
    """Return a list of FilamentsLayer instances in the current viewer."""
    viewer = find_viewer_ancestor(gui)
    if not viewer:
        return []
    return [x for x in viewer.layers if isinstance(x, FilamentsLayer)]


register_type(FilamentsLayer, choices=get_filaments_layer)

from __future__ import annotations

from typing import TYPE_CHECKING

import napari

if TYPE_CHECKING:  # pragma: no cover
    from napari_filaments._napari._widget import FilamentAnalyzer


def start(viewer: napari.Viewer | None = None) -> FilamentAnalyzer:
    """Lauch viewer with a FilamentAnalyzer widget docked in it."""
    from napari_filaments._napari._widget import FilamentAnalyzer

    if viewer is None:
        viewer = napari.Viewer()
    ui = FilamentAnalyzer()
    viewer.window.add_dock_widget(ui)
    return ui

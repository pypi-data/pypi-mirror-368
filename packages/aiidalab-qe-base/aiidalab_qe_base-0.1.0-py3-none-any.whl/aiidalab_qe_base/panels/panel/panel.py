import typing as t

import ipywidgets as ipw
from aiidalab_widgets_base import LoadingWidget

from .model import PanelModel

PM = t.TypeVar("PM", bound=PanelModel)


class Panel(ipw.VBox, t.Generic[PM]):
    """Base class for all panels."""

    rendered = False
    loading_message = "Loading {identifier} panel"

    def __init__(self, model: PM, **kwargs):
        loading_message = self.loading_message.format(identifier=model.identifier)
        loading_message = loading_message.replace("_", " ")
        self.loading_message = LoadingWidget(loading_message)
        super().__init__(children=[self.loading_message], **kwargs)
        self._model = model

    def render(self):
        raise NotImplementedError()

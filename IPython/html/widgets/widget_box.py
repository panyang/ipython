"""Box class.  

Represents a container that can be used to group other widgets.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from .widget import DOMWidget, Widget, register
from IPython.utils.traitlets import Unicode, Tuple, TraitError, Int, CaselessStrEnum
from .deprecated import DeprecatedClass

def _widget_to_json(x):
    if isinstance(x, dict):
        return {k: _widget_to_json(v) for k, v in x.items()}
    elif isinstance(x, (list, tuple)):
        return [_widget_to_json(v) for v in x]
    elif isinstance(x, Widget):
        return "IPY_MODEL_" + x.model_id
    else:
        return x

def _json_to_widget(x):
    if isinstance(x, dict):
        return {k: _json_to_widget(v) for k, v in x.items()}
    elif isinstance(x, (list, tuple)):
        return [_json_to_widget(v) for v in x]
    elif isinstance(x, string_types) and x.startswith('IPY_MODEL_') and x[10:] in Widget.widgets:
        return Widget.widgets[x[10:]]
    else:
        return x

widget_serialization = {
    'from_json': _json_to_widget,
    'to_json': _widget_to_json
}


@register('IPython.Box')
class Box(DOMWidget):
    """Displays multiple widgets in a group."""
    _model_name = Unicode('BoxModel', sync=True)
    _view_name = Unicode('BoxView', sync=True)

    # Child widgets in the container.
    # Using a tuple here to force reassignment to update the list.
    # When a proper notifying-list trait exists, that is what should be used here.
    children = Tuple(sync=True, **widget_serialization)
    
    _overflow_values = ['visible', 'hidden', 'scroll', 'auto', 'initial', 'inherit', '']
    overflow_x = CaselessStrEnum(
        values=_overflow_values, 
        default_value='', sync=True, help="""Specifies what
        happens to content that is too large for the rendered region.""")
    overflow_y = CaselessStrEnum(
        values=_overflow_values, 
        default_value='', sync=True, help="""Specifies what
        happens to content that is too large for the rendered region.""")

    box_style = CaselessStrEnum(
        values=['success', 'info', 'warning', 'danger', ''], 
        default_value='', allow_none=True, sync=True, help="""Use a
        predefined styling for the box.""")

    def __init__(self, children = (), **kwargs):
        kwargs['children'] = children
        super(Box, self).__init__(**kwargs)
        self.on_displayed(Box._fire_children_displayed)

    def _fire_children_displayed(self):
        for child in self.children:
            child._handle_displayed()


@register('IPython.FlexBox')
class FlexBox(Box):
    """Displays multiple widgets using the flexible box model."""
    _view_name = Unicode('FlexBoxView', sync=True)
    orientation = CaselessStrEnum(values=['vertical', 'horizontal'], default_value='vertical', sync=True)
    flex = Int(0, sync=True, help="""Specify the flexible-ness of the model.""")
    def _flex_changed(self, name, old, new):
        new = min(max(0, new), 2)
        if self.flex != new:
            self.flex = new

    _locations = ['start', 'center', 'end', 'baseline', 'stretch']
    pack = CaselessStrEnum(
        values=_locations, 
        default_value='start', sync=True)
    align = CaselessStrEnum(
        values=_locations, 
        default_value='start', sync=True)


def VBox(*pargs, **kwargs):
    """Displays multiple widgets vertically using the flexible box model."""
    kwargs['orientation'] = 'vertical'
    return FlexBox(*pargs, **kwargs)

def HBox(*pargs, **kwargs):
    """Displays multiple widgets horizontally using the flexible box model."""
    kwargs['orientation'] = 'horizontal'
    return FlexBox(*pargs, **kwargs)


# Remove in IPython 4.0
ContainerWidget = DeprecatedClass(Box, 'ContainerWidget')

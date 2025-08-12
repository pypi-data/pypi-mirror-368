# NOTE: _ Avoids subsequent import overides
import param

from .core import ObjectInterface as _Interface
from .elements import *


class LineObject(_Interface):

    _LABELS_ = {"line": ""}
    line = param.ClassSelector(default=LineElement(), class_=LineElement)


class ShapeObject(_Interface):

    _LABELS_ = {"line": "Line", "fill": "Fill"}

    line = param.ClassSelector(default=LineElement(), class_=LineElement)
    fill = param.ClassSelector(default=FillElement(), class_=FillElement)


class ImageObject(_Interface):

    _LABELS_ = {"image": "Image"}

    image = param.ClassSelector(default=ImageElement(), class_=ImageElement)



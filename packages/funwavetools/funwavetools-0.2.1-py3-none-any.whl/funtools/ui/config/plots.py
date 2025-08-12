# NOTE: _ Avoids subsequent import overides
import param

from .core import PlotInterface as _Interface
from .core import SimplePlotInterface as _SimpleInterface
from .objects import *


class ShapePlot(_SimpleInterface):
    plot = param.ClassSelector(default=ShapeObject(), class_=ShapeObject)


class ImagePlot(_SimpleInterface):
    plot = param.ClassSelector(default=ImageObject(), class_=ImageObject)

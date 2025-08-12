"""
Standard collection of user interface widgets.

"""

import holoviews as hv
import panel as pn
import param
from panel.viewable import Viewer

from .colormaps import colormap_dict, colormap_names


# FUTURE: Remove ABC from LinkedParameter and merge?
class ColorMapSelector(Viewer):

    _cmaps = colormap_dict()
    
    provider = param.Selector(default='bokeh', objects=_cmaps.keys())
    category = param.Selector(default='Standard', objects=_cmaps['bokeh'].keys())   
    cmap_name = param.Selector(default='Viridis', objects =_cmaps['bokeh']['Standard'].keys())

    #palette = param.List()
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        cmaps = self._cmaps[self.provider][self.category]
 
        self._cmap_sel = pn.widgets.ColorMap(options={})
        #self._cmap_sel = pn.widgets.ColorMap.from_param(self.param['palette'])


        #self._palette = pn.widgets.LiteralInput(name='Array Input ', type=list)
        self._update()
 
        self._panel = pn.WidgetBox(self.param['provider'], self.param['category'], self._cmap_sel)
        #, self._palette)


    def __panel__(self):
        return self._panel

    @param.depends('provider', 'category', 'cmap_name', watch=True)
    def _update(self):

        cats = list(self._cmaps[self.provider].keys())
        self.param['category'].objects = cats
        if self.category not in cats:
            self.category = cats[0]

        cmaps = list(self._cmaps[self.provider][self.category].keys())
    
        self.param['cmap_name'].objects = cmaps
        #if self.cmap_name not in cmaps:
        self.cmap_name = cmaps[0]

        cmaps = self._cmaps[self.provider][self.category]

        self._cmap_sel.options = cmaps
        self._cmap_sel.value_name = str(self.cmap_name)


      #  print(type(cmaps[self.cmap_name]))
        #import numpy as np
        #self._palette.value = cmaps[self.cmap_name]

    @classmethod
    def from_param(cls, p, **kwargs):
        self = cls(**kwargs)
        return self 

    def jslink(self, target, **kwargs):
        self._cmap_sel.jslink(target, **kwargs)

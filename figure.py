from . import plotfuncs as pfs
from .base import PlotFactory, CatRecObject, KWS, PlotFunc
from .axis import SetFactory, CatSet, axes, Axes


class Figure(SetFactory):
    _default_params = dict(
                           PlotFactory._default_params, 
                           __inerit__ = {'figure', 'axes',
        'picker', 'edgecolor', 'clip_on', 'clip_box', 'transform',
        'canvas', 'facecolor', 'lod', 'size_inches', 'contains', 'clip_path', 'figwidth',
        'snap', 'agg_filter', 'figheight', 'tight_layout', 'rasterized',
        'path_effects', 'sketch_params', 'frameon', 'animated', 'dpi', 
        'style', 'version', 'fname', 'papertype', 'suptitle', 'bgcolor','figure_bgcolor'}
                           )
    _set = pfs.figure
    adjust = pfs.adjust
    save = pfs.savefig
    savefig = save
    draw = pfs.draw
    clear = pfs.fclear
    show = pfs.show
    colorbar = pfs.colorbar
    suptitle = pfs.suptitle

    def get_mpl_axes(self):
        return pfs.get_axes(self.get("axes",None), self.get("figure",None))

    def get_mpl_figure(self):
        return pfs.get_figure(self.get("figure",None), self.get("axes",None))
 

    @property
    def a(self):
        return self.get_mpl_axes()

    @property
    def f(self):
        return self.get_mpl_figure()

    @staticmethod
    def finit(self,*args, **kwargs):
        if len(args)>0:
            kwargs["figure"] = args[0]
        if len(args)>1:
            kwargs["axes"] = args[1]
        elif len(args)>2:
            raise ValueError("plots take no more than 2 positional arguments")
        self.set(**kwargs)        

    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)
        self._set()
        self.adjust()
        if self.suptitle.get("suptitle") is not None:
            self.suptitle()        

figure = Figure()


class FigAxes(SetFactory):
    _default_params = dict(
                           PlotFactory._default_params, 
                           __inerit__ = set(list(Axes._default_params["__inerit__"])+list(Figure._default_params["__inerit__"]))
                           )
    figure = figure.derive(__inerit__=None) 
    axes   = axes.derive(__inerit__=None)
    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)
        self.figure()
        self.axes()

fa = FigAxes()        








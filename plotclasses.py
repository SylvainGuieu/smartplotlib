from __future__ import division, absolute_import, print_function

from .recursive import alias, KWS
from .base import Plot
from . import plotfuncs as pfs
from .plotfuncs import _BaseFigAxes
from .figaxes import axes, figure

"""
Define the main plot classes and their plotfuncs
All the other more sofiticated Plots are added later
"""


class XYPlot(Plot, _BaseFigAxes):
    """ Plot for y vs x kind of data """
    axes = axes
    figure = figure

    plot = pfs.plot
    step = pfs.step
    errorbar = pfs.errorbar
    scatter = pfs.scatter

    ## fit and statistic
    xhist = pfs.hist.derive(orientation="vertical",   data=alias("x"))
    yhist = pfs.hist.derive(orientation="horizontal", data=alias("y"))

    vlines = pfs.vlines
    hlines = pfs.hlines

    ##
    # put the default in axvline and axhline, they have
    # nothing to do with data but axes
    axvline = pfs.axvline.derive(ymin=0, ymax=1.0)
    axhline = pfs.axhline.derive(xmin=0, xmax=1.0)

    bar  = pfs.bar
    fill = pfs.fill

    fill_betweeny = pfs.fill_betweeny
    fill_betweenx = pfs.fill_betweenx

    annotates = pfs.annotates

    @staticmethod
    def finit(plot,*args,**kwargs):
        """ """
        plot.update(kwargs.pop(KWS,{}), **kwargs)
        x, y = plot.parseargs(args, "x","y",
                              x=None, y=None
                             )
        if y is None: # x is y
            if x is None:
                raise ValueError("missing y data")
            y = x
            x = alias("x", lambda p,k :np.arange(np.asarray(p["y"]).shape[0]))
        else:
            if x is None:
                x = alias("x", lambda p,k :np.arange(np.asarray(p["y"]).shape[0]))
        plot.update(x=x, y=y)


class DataPlot(Plot, _BaseFigAxes):
    """ plot that derive from a data set """
    axes = axes
    figure = figure

    hist = pfs.hist

    fill_between = pfs.fill_between
    @staticmethod
    def finit(plot, data, **kwargs):
        plot.update(kwargs.pop(KWS,{}), **kwargs)
        data, = plot.parseargs([data], "data")
        plot["data"] = data



class DataXYPlot(XYPlot, DataPlot):
    """ plot that contain both Data and x/y
    They are usefull for dataplot wich can be called again
    """
    axes = axes
    figure = figure

    hist = pfs.hist
    @staticmethod
    def finit(plot,**kwargs):
        plot.update(kwargs.pop(KWS,{}), **kwargs)


def colors_or_z(p,k):
    return p[k] if k in p else p["z"]
class XYZPlot(Plot, _BaseFigAxes):
    """ plot for 3 dimentional data """
    axes = axes
    figure = figure
    imshow = pfs.imshow.derive(img=alias("colors"), colors=alias("Z"))
    pcolor = pfs.pcolor
    pcolormesh = pfs.pcolormesh
    pcolorfast = pfs.pcolorfast
    contour = pfs.contour
    contourf = pfs.contourf
    colorbar = pfs.colorbar



class ImgPlot(Plot, _BaseFigAxes):
    """ plot used for image """
    axes = axes
    figure = figure
    imshow = pfs.imshow
    hist = pfs.hist.derive(data=alias("img", lambda p,k: np.asarray(p[k]).flatten()))
    colorbar = pfs.colorbar

    @staticmethod
    def finit(plot, img, **kwargs):
        plot.update(kwargs.pop(KWS,{}), **kwargs)
        img, = plot.parseargs([img], "img")
        plot["img"] = img


class ScalarPlot(Plot, _BaseFigAxes):
    axes = axes
    figure = figure
    axline = pfs.axline
    axspan = pfs.axspan
    lines = pfs.lines
    text = pfs.text
    annotate = pfs.annotate

    @staticmethod
    def finit(plot,**kwargs):
        plot.update(kwargs.pop(KWS,{}), **kwargs)

xyplot = XYPlot()
dataplot = DataPlot()
dataxyplot = DataXYPlot()
xyzplot = XYZPlot()
imgplot = ImgPlot()
scalarplot = ScalarPlot()
















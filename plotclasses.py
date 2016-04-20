from __future__ import division, absolute_import, print_function

from .recursive import alias, KWS
from .base import PlotFactory, rproperty
from . import plotfuncs as pfs

from .figaxes import subplot, plots, axes, figure, fa

import numpy as np


class _BaseFigAxes(object):
    """ just a colection of usefull axes/figure
        for other plots.
    """

    subplot = subplot
    axes = axes
    plots = plots
    figure = figure

    aclear = pfs.aclear
    fclear = pfs.fclear
    cla = pfs.aclear
    clf = pfs.fclear
        

    def fa(self, **kwargs):
        self.axes(**kwargs)
        self.figure(**kwargs)

    #axes = axes
    #fset = fset
    show = pfs.show
    draw = pfs.draw
    legend = pfs.legend
    grid = pfs.grid
    savefig = pfs.savefig

    @rproperty
    def grids(self):
        """ axes.grids plot setter """
        return self.axes.grids

    @rproperty
    def xlabel(self):
        """ axes.x.label plot setter """
        return self.axes.x.label   
    
    @rproperty
    def ylabel(self):
        """ axes.y.label plot setter """
        return self.axes.y.label

    @rproperty
    def labels(self):
        """ axes.labels plot setter """
        return self.axes.labels          
    
    @rproperty
    def xaxis(self):
        """ axes.x plot setter """
        return self.axes.x

    @rproperty
    def yaxis(self):
        """ axes.y plot setter """
        return self.axes.y

    @rproperty
    def ticks(self):
        """ axes.ticks plot setter """
        return self.ticks
    
    @rproperty
    def xticks(self):
        """ axes.x.ticks plot setter """
        return self.axes.x.ticks    

    @rproperty
    def yticks(self):
        """ axes.y.ticks plot setter """
        return self.axes.y.ticks        

    def get_axes(self):
        """ Return the matplotlib axes linked """
        return pfs.get_axes(self.get("axes", None), self.get("figure", None))
    def get_figure(self):
        """ Return the matplotlib figure linked """
        return pfs.get_figure(self.get("figure", None), self.get("axes", None))
    @property
    def a(self):
        return self.get_axes()
    @property
    def f(self):
        return self.get_figure()



"""
Define the main plot classes and their plotfuncs
All the other more sofiticated Plots are added later
"""




def _k2edge(plot,k):
    """convert array plot[k] to bar edge (remove the last)"""
    return np.asarray(plot[k])[:-1]
def _k2width(plot,k):
    """convert array plot[k] to bar width np.diff()"""
    return np.diff(plot[k])

def _make_array(value):
    if not isinstance(value, np.ndarray):
        return np.asarray(value)
    return value

class _subxy(object):
    def __init__(self, _xyplot=None):
        self.xyplot = _xyplot

    def __get__(self, xyplot, cl=None):
        if xyplot is None:
            return self
        new = self.__class__(xyplot)
        return new

    def __getitem__(self, item):
        xyplot = self.xyplot
        try:
            y = xyplot["y"]
        except KeyError:
            raise TypeError("missing y data, cannot extract sub-data")

        y = _make_array(y)[item]
        is_scalar = not hasattr(y, "__iter__")
        if is_scalar:
            new = scalarplot.derive(value=y)
        else:
            new = xyplot.derive(y=y)


        try:
            x = xyplot["x"]
        except KeyError:
            pass
        else:
            if x is not None:
                if is_scalar:
                    new["index"] = _make_array(x)[item]
                else:
                    new["x"] = _make_array(x)[item]

        try:
            xerr = xyplot["xerr"]
        except KeyError:
            pass
        else:
            if not is_scalar and (xerr is not None) and hasattr(xerr, "__iter__"):
                new["xerr"] = _make_array(xerr)[item]

        try:
            yerr = xyplot["yerr"]
        except KeyError:
            pass
        else:
            if yerr is not None and hasattr(yerr, "__iter__"):
                if is_scalar:
                    new["err"] = _make_array(yerr)[item]
                else:
                    new["yerr"] = _make_array(yerr)[item]
            elif yerr is not None:
                new["yerr"] = _make_array(yerr)

        return new

    def __getslice__(self, start, end):
        return self.__getitem__(slice(start, end))

class XYFit(PlotFactory, _BaseFigAxes):
    """ a PlotColection of fit factory for x vs y type of data 

        PlotFactory Methods:
        |------------|------------|-------------------------------------------------|
        |   method   |  Factory   |                     comment                     |
        |------------|------------|-------------------------------------------------|
        | polynome   | XYPlot     | polynome fitting capability from x/y data       |
        | linear     | XYPlot     | polynome fit with dim=1                         |
        | inverse    | XYPlot     | fit y = (a*x +b)                                |

    """
    pass

class XYPlot(PlotFactory, _BaseFigAxes):
    """ PlotFactory. Return a new instance of xyplot ready to plot 2d x/y data

    call signature:
        xyplot(y)
        xyplot(x,y)
        xyplot(x,y, yerr, xerr, **kwargs)

    All arguments can inerite from a parent Plot object if any.

    All args can be keyword arguments or assigned parameter as obj['x'] = array(..)

    Use .info attribute to print a state of this curent PlotFactory object
    Args:
        x (array-like) : the x absis data
        y (array-like) : y-axis data
        yerr (Optional[array-like]) : error on y-data, can be scalar or None.
        xerr (Optional[array-like]) : error on x-data, can be scalar or None.

        params (Optional[dict]) : A dictionary of any parameters for child plots
            or child plots function (FuncPlot)
        go (Optional[list of string]) : Action taken after the ready-instance created
            see the .go method help

        **kwargs : Any other parameters that will ramp-up the hierarchy of childs

    Returns:
        xyplot : New ready instance of xyplot.

    Machined Parameters:
        x (array-like) : if not present x = np.arange(len(y))

        All other are set as they are

    PlotFunc Methods:
      The ones using "x" "y" like:
        |---------------|--------------------------------------------------------------|
        |     method    |                            action                            |
        |---------------|--------------------------------------------------------------|
        | plot          | plot line point etc...                                       |
        | errorbar      | errobar plotting                                             |
        | scatter       | scattered points plot                                        |
        | step          | plot line has step                                           |
        | fill          | polygone fill                                                |
        | xhist         | histogram on x axis of x data                                |
        | yhist         | histogram on y axis of y data                                |
        | vlines        | verticl lines where by default ymin=0 and ymax=alias("y")    |
        | hlines        | horozontal lines where by default xmin=0 and xmax=alias("x") |
        | axvline       | Use only the x data                                          |
        |               | (axes ymin and ymax are 0 and 1 by default)                  |
        | axhline       | Use only the y data                                          |
        |               | (axes xmin and xmax are 0 and 1 by default)                  |
        | bar2x         | plot bars horizontaly edges are y[:-1], width are diff(y)    |
        |               | and height are x. align="center" by default                  |
        | bar2y         | plot bars verticaly edges are x[:-1], width are diff(x)      |
        |               | and height are y. align="center" by default                  |
        | bar           | is bar2y                                                     |
        | annotates     | annotate x/y points                                          |
        | fill_betweeny | fill between y lines. Use 'y' bydefault for the first line   |
        | fill_betweenx | fill between x lines. Use 'x' bydefault for the first line   |
        | fill_between  | is fill_betweeny                                             |
        | fillstep      | plot a polygone that envelop data if it was ploted with bars |
        |---------------|--------------------------------------------------------------|


      Not related to "x", "y" data, for conveniant use:
{conveniant}

    PlotFactory Methods:
        |------------|------------|-------------------------------------------------|
        |   method   |  Factory   |                     comment                     |
        |------------|------------|-------------------------------------------------|
        | polyfit    | XYPlot     | polynome fitting capability from x/y data       |
        | linearfit  | XYPlot     | same as polyfit with ["dim"] = 1                |
        | ybinedstat | XYPlot     | make plot-ready binned statistic of y data.     |
        |            |            | this is the samething than .ydata.binedstat     |
        | ydata      | DataPlot   | a dataplot factory where data=alias("y")        |
        | xdata      | DataPlot   | a dataplot factory where data=alias("y")        |
        | cohere     | XYPlot     | coherence plot factory on 'x' vs 'y' by default |
        | csd        | XYPlot     | Cross Spectral Density  plot factory on         |
        |            |            | 'x' vs 'y' by default                           |
        | histogram2 | XYZPlot    | histogram2d Factory from 'x' and 'y'            |
        |            |            |                                                 |
        |            |            |                                                 |
        | ystat      | ScalarPlot | scalar statistic plot factory  on y-data        |
        |            |            | (e.i mean, median, etc). same as ydata.stat     |
        | xstat      | ScalarPlot | scalar statistic plot factory  on x-data        |
        |            |            | (e.i mean, median, etc).same as ydata.stat      |
        |------------|------------|-------------------------------------------------|
        | xmedian    | ScalarPlot | xstat with fstat="median"                       |
        | ymedian    | ScalarPlot | ystat with fstat="median"                       |
        | xmean      | ScalarPlot | xstat with fstat="mean"                         |
        | ymean      | ScalarPlot | ystat with fstat="mean"                         |
        | xmin       | ScalarPlot | xstat with fstat="min"                          |
        | ymin       | ScalarPlot | ystat with fstat="min"                          |
        | xmax       | ScalarPlot | xstat with fstat="max"                          |
        | ymax       | ScalarPlot | ystat with fstat="max"                          |
        | xstd       | ScalarPlot | xstat with fstat="std"                          |
        | ystd       | ScalarPlot | ystat with fstat="std"                          |
        |------------|------------|-------------------------------------------------|
        | subplot    | SubPlot    | return the subplot factory with all the default |
        |            |            | of thi xyplot                                   |
        | plots      | Plots      | return a plots factory (plots linked to figure) |
        |            |            | with all default taken from that xyxplot        |
        | fits       | PlotCollec | containe fit plot factory                       |
        |------------|------------|-------------------------------------------------|


    Others usefull methods:
{useful}

    And Attributes:
{usefulattr}

    See the doc of PlotFactory for other methods shared by PlotFactoty objects

    """
    sub = _subxy()
    fits = XYFit()
    

    plot = pfs.plot
    step = pfs.step
    errorbar = pfs.errorbar
    scatter = pfs.scatter

    ## fit and statistic
    xhist = pfs.hist.derive(orientation="vertical",   data=alias("x"))
    yhist = pfs.hist.derive(orientation="horizontal", data=alias("y"))

    vlines = pfs.vlines.derive(ymin=0, ymax=alias("y"))
    hlines = pfs.hlines.derive(xmin=0, xmax=alias("x"))

    ##
    # put the default in axvline and axhline, they have
    # nothing to do with data but axes
    axvline = pfs.axvline.derive(ymin=0, ymax=1.0)
    axhline = pfs.axhline.derive(xmin=0, xmax=1.0)

    bar2y  = pfs.bar.derive(edge=alias("x", _k2edge, "-> x[:-1]"),
                            width=alias("x", _k2width, "-> diff(x)"),
                            height=alias("y", _k2edge, "-> y[:-1]"),
                            align="center"
                          )
    bar2x  = pfs.bar.derive(edge=alias("y", _k2edge, "-> y[:-1]"),
                            width=alias("y", _k2width, "-> diff(y)"),
                            height=alias("x", _k2edge, "-> x[:-1]"),
                            align="center", direction="x"
                          )
    bar = bar2y

    fillstep = pfs.fillstep
    fill = pfs.fill

    fill_betweeny = pfs.fill_betweeny.derive(y1=alias("y"))
    fill_betweenx = pfs.fill_betweenx.derive(x1=alias("x"))
    fill_between = fill_betweeny

    annotates = pfs.annotates

    @staticmethod
    def finit(plot, *args,**kwargs):
        """ """
        plot.update(kwargs.pop(KWS,{}), **kwargs)
        x, y = plot.parseargs(args, "x","y",
                              x=None, y=None
                             )
        if y is None: # with one arg, x is y
            if x is not None:
                y, x = x, None
        
        if x is None:
            x = alias("x", lambda p,k :np.arange(np.asarray(p["y"]).shape[0]), "-> arange(len(y))")
        plot.update(x=x, y=y)




class _subdata(object):
    def __init__(self, _dataplot=None):
        self.dataplot = _dataplot

    def __get__(self, dataplot, cl=None):
        if dataplot is None:
            return self
        new = self.__class__(dataplot)
        return new

    def __getitem__(self, item):
        dataplot = self.dataplot
        try:
            data = dataplot["data"]
        except KeyError:
            raise TypeError("missing 'data', cannot extract sub-data")

        data = _make_array(data)[item]
        is_scalar = not hasattr(data, "__iter__")
        if is_scalar:
            new = scalarplot.derive(value=data)
        else:
            new = dataplot.derive(data=data)


        try:
            x = dataplot["indexes"]
        except KeyError:
            pass
        else:
            if is_scalar:
                new["index"] = _make_array(x)[item]
            else:
                new["indexes"] = _make_array(x)[item]

        try:
            weights = dataplot["weights"]
        except KeyError:
            pass
        else:
            if not is_scalar and (weights is not None) and hasattr(weights, "__iter__"):
                new["weights"] = _make_array(weights)[item]

        return new

    def __getslice__(self, start, end):
        return self.__getitem__(slice(start, end))






class DataPlot(PlotFactory, _BaseFigAxes):
    """ PlotFactory for single array like data

    Contain a colection of PlotFunc and PlotFactory to represend
    the data and its statistic.

    Use .info attribute to print a state of this curent PlotFactory object

    Args:
        data (array-like) : the (mostly 1-d) data
        indexes (Optiona[array]) : optional array of data indexes, can be used for
            binedstat or stat factories.
        params (Optional[dict]) : A dictionary of any parameters for child plots
            or child plots function (FuncPlot)
        go (Optional[list of string]) : Action taken after the ready-instance created
            see the .go method help

        **kwargs : Any other parameters that will ramp-up the hierarchy of childs

    Returns:
        dataplot factory : a new instance of self

    Machined Parameters:
        None, all are set as they are

     PlotFunc Methods:
        |--------|-------------------------|
        | method |          action         |
        |--------|-------------------------|
        | hist   | plot histogram directly |
        |--------|-------------------------|

     Not related to "x", "y" data, for conveniant use:
{conveniant}

     PlotFactory Methods:
        |--------------------|------------|-------------------------------------------------|
        |       method       |  Factory   |                     comment                     |
        |--------------------|------------|-------------------------------------------------|
        | histogram          | DataPlot   | Histogram factory on *data*                     |
        | binedstat          | DataPlot   | binned statistic (mean, max, etc) on *data*     |
        | stat               | ScalarPlot | A scalar factory tha contain full data          |
        |                    |            | statistics.                                     |
        | distribfit         | XYPlot     | Fit the data distribution (e.g. with            |
        |                    |            | 'normal'). Usefull to plot on top of histograms |
        | mean, median, min  | ScalarPlot | inerit from stat with the right fstat param     |
        | max, std           |            |                                                 |
        |                    |            | arange(len(data)) else                          |
        | specgram           | ImgPlot    | a specgram factory (produce image)              |
        | psd                | XYPlot     | power spectral density factory                  |
        | angle_spectrum     | XYPlot     | Angle spectrum factory from *data* see doc      |
        | magnitude_spectrum | XYPlot     | Magnitude Spectrum factory ..                   |
        | phase_spectrum     | XYPlot     | Phase Spectrum factory                          |
        |--------------------|------------|-------------------------------------------------|
        | subplot            | SubPlot    | return the subplot factory with all the default |
        |                    |            | of thi xyplot                                   |
        | plots              | Plots      | return a plots factory (plots linked to figure) |
        |                    |            | with all default taken from that xyxplot        |
        |                    |            |                                                 |
        |--------------------|------------|-------------------------------------------------|

    Others usefull methods:
{useful}

    And Attributes:
{usefulattr}

    """
    sub = _subdata()
    subplot = subplot
    plots = plots
    lines = pfs.lines
    vlines = pfs.vlines.derive(x=alias("data"))
    hlines = pfs.vlines.derive(y=alias("data"))

    hist = pfs.hist


    @staticmethod
    def finit(plot, data, **kwargs):
        plot.update(kwargs.pop(KWS,{}), **kwargs)
        data, = plot.parseargs([data], "data")
        plot["data"] = data



def colors_or_z(p,k):
    return p[k] if k in p else p["z"]
class XYZPlot(PlotFactory, _BaseFigAxes):
    """ plot for 3 dimentional data """

    imshow = pfs.imshow.derive(img=alias("colors"), colors=alias("Z"))
    pcolor = pfs.pcolor
    pcolormesh = pfs.pcolormesh
    pcolorfast = pfs.pcolorfast
    contour = pfs.contour
    contourf = pfs.contourf
    colorbar = pfs.colorbar


class _subimg(object):
    def __init__(self, _imgplot=None):
        self.imgplot = _imgplot

    def __get__(self, imgplot, cl=None):
        if imgplot is None:
            return self

        new = self.__class__(imgplot)
        return new

    def __getitem__(self, item):
        imgplot = self.imgplot
        try:
            img = imgplot["img"]
        except KeyError:
            raise TypeError("'img' is not defined, cannot extract sub-image")

        img = img[item]
        if not hasattr(img, "__iter__"): # this is a scalar
            return scalarplot(img)
        if len(img.shape)<2: # this is a vector
            return xyplot( np.arange(len(img)), img )
        if self.imgplot:
            return self.imgplot.derive(img=img)
        return imgplot(img=img)

    def __getslice__(self, start, end):
        return self.__getitem__(slice(start, end))



class ImgPlot(PlotFactory, _BaseFigAxes):
    """ plot used for image """


    imshow = pfs.imshow
    hist = pfs.hist.derive(data=alias("img", lambda p,k: np.asarray(p[k]).flatten(), "-> img.flatten()"))
    colorbar = pfs.colorbar

    sub = _subimg()
    @staticmethod
    def finit(plot, img, **kwargs):
        plot.update(kwargs.pop(KWS,{}), **kwargs)
        img, = plot.parseargs([img], "img")
        plot["img"] = img


class ScalarPlot(PlotFactory, _BaseFigAxes):

    axline = pfs.axline
    ##
    # here ymin and ymax has nothing to do with the data
    # change it to 0,1 by default
    axvline = pfs.axvline.derive(x=alias("value"),ymin=0,ymax=1)
    axhline = pfs.axhline.derive(y=alias("value"),xmin=0,xmax=1)

    vlines = pfs.vlines.derive(x=alias("value", lambda p,k:np.asarray(p[k]), "-> array(value)"))
    hlines = pfs.vlines.derive(y=alias("value", lambda p,k:np.asarray(p[k]), "-> array(value)"))
    lines  = pfs.vlines.derive(data=alias("value", lambda p,k:np.asarray(p[k]), "-> array(value)"))

    axspan  = pfs.axspan.derive(value1=alias("previous"), value2=alias("value"))
    axvspan = pfs.axvspan.derive(xmin=alias("previous"),   xmax=alias("value"))
    axhspan = pfs.axvspan.derive(ymin=alias("previous"),   ymax=alias("value"))

    text  = pfs.text.derive(text=alias("value", lambda p,k: str(p[k]), "-> str(value)"))


    annotate = pfs.annotate

    @staticmethod
    def finit(plot, *args,  **kwargs):
        plot.update(kwargs.pop(KWS,{}), **kwargs)
        value = plot.parseargs(args, "value")
        plot["value"] = value

conveniant = """
        |--------|-------------------------------------------------|
        | method |                      action                     |
        |--------|-------------------------------------------------|
        | axes   | set all valid axes parameters to the axes plot. |
        |        | Like "xlabel", "ylabel", grid, title etc ...                |
        | figure | set all figure parameters                       |
        | aclear | clear the axes                                  |
        | fclear | clear the figure                                |
        | legend | plot the axes legend                            |
        | show   | figure.show()                                   |
        | draw   | figure.canvas.draw()                            |
        | grids  | axes.grids setting                             |
        |--------|-------------------------------------------------|
"""
useful = """
      |   method   |     return     |                       comment                       |
      |------------|----------------|-----------------------------------------------------|
      | update     | None           | update parameters of the factory                    |
      | derive     | (Self class)   | A new factory instance where defaults are           |
      |            |                | in self                                             |
      | go         | dict (results) | execute a list actions from list of strings         |
      |            |                | e.g. .go("axes", "legend", "show")                  |
      | get        | any object     | As for dict get a parameter value                   |
      | pop        | any object     | As for dict pop a parameter                         |
      | clear      | None           | clear the local parameters                          |
      | setdefault | None           | As for dict set a default parameter                 |
      | iter       | (self class)   | Iter on iterables and return new instances of self  |
      | iteraxes   | (self class)   | Same has iter but buil *axes* params for each new   |
      | iterfigure | (self class)   | Same has iter but buil *figure* params for each new |
      | itercall   | (self class)   | Iter on iterables and return new()                  |
      | get_axes   | plt.Axes       | return the matplotlib Axes instance obect           |
      | get_figure | plt.Figure     | return the matplotlib Figure instance obect         |
      |            |                |                                                     |
"""

usefulattr = """
      | attribute |    return   |                   comment                   |
      |-----------|-------------|---------------------------------------------|
      | info      | None        | Print a state of the Factory object         |
      | all       | dict        | return a dictionary with all parameters set |
      |           |             | the locals and the inerited.                |
      | locals    | dict        | the local parameter dictionary              |
      | example   | string/None | If any return an string example ready for   |
      |           |             | print or exec                               |
      | axes      | plt.Axes    | the matplotlib Axes instance obect          |
      | figure    | plt.Figure  | the matplotlib Figure instance obect        |
      |-----------|-------------|---------------------------------------------|

"""





xyplot = XYPlot()
xyplot.finit.__doc__ = XYPlot.__doc__.format(conveniant=conveniant,
                                             useful=useful, usefulattr=usefulattr
                                             )
xyplot.__doc__ = xyplot.finit.__doc__
xyplot["_example_"] = ("xyplot", None)

dataplot = DataPlot()
dataplot["_example_"] = ("histogram", None)


xyzplot = XYZPlot()
imgplot = ImgPlot()
scalarplot = ScalarPlot()
















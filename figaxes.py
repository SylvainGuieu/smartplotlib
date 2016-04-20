from __future__ import division, absolute_import, print_function
from .axis import Axes, axes
from .figure import Figure, figure, fa

from . import plotfuncs as pfs

import matplotlib.pyplot as plt

from .base import PlotFactory, PlotFunc
from .recursive import cycle, lcycle, KWS
from . import styler

def _make_(idt=" "*4):
    blacklist = ["figure", "axes", "_axis", "_axes", "tables", "line2d", "spine"]    
    keys =  pfs.__dict__.keys()
    keys.sort()   
    for k in keys:
        f = pfs.__dict__[k]
        if k in blacklist: continue
        if isinstance(f, (PlotFunc, PlotFactory)):
            print(idt+"%s = pfs.%s"%(k,k))    

class BasePlot(PlotFactory):
    def get_axes(self):
        return pfs.get_axes(self.get("axes",None), self.get("figure",None))

    def get_figure(self):
        return pfs.get_figure(self.get("figure",None), self.get("axes",None))
        
    def derive(self, *args, **kwargs):
        new = super(BasePlot, self).derive(*args, **kwargs)
        new.reset() # reset all cycles to 0
        return new

    def clearparams(self):
        return self.locals.clear()
    ### _make_ build the following 

    adjust = pfs.adjust
    annotate = pfs.annotate
    annotates = pfs.annotates
    annotations = pfs.annotations
    arrow = pfs.arrow
    artist = pfs.artist
    
    axhline = pfs.axhline
    axhspan = pfs.axhspan
    
    axline = pfs.axline
    axspan = pfs.axspan
    axvline = pfs.axvline
    axvspan = pfs.axvspan
    bar = pfs.bar
    boxplot = pfs.boxplot
    bxp = pfs.bxp
    
    clf = pfs.clf
    collections = pfs.collections
    colorbar = pfs.colorbar
    contour = pfs.contour
    contourf = pfs.contourf
    contours = pfs.contours
    draw = pfs.draw
    errorbar = pfs.errorbar
    eventplot = pfs.eventplot
    fancyarrows = pfs.fancyarrows
    fclear = pfs.fclear
    fill = pfs.fill
    fill_between = pfs.fill_between
    fill_betweenx = pfs.fill_betweenx
    fill_betweeny = pfs.fill_betweeny
    fillstep = pfs.fillstep
    fset = pfs.fset    
    hexbin = pfs.hexbin
    hist = pfs.hist
    hist2d = pfs.hist2d
    histx2x = pfs.histx2x
    histx2y = pfs.histx2y
    histy2x = pfs.histy2x
    histy2y = pfs.histy2y
    hlines = pfs.hlines
    imshow = pfs.imshow
    legend = pfs.legend
    linecollections = pfs.linecollections
    lines = pfs.lines
    
    matshow = pfs.matshow
    patches = pfs.patches
    pcolor = pfs.pcolor
    pcolorfast = pfs.pcolorfast
    pcolormesh = pfs.pcolormesh
    pie = pfs.pie
    plot = pfs.plot
    plot_date = pfs.plot_date
    plotfunc = pfs.plotfunc
    polycollections = pfs.polycollections
    polygon = pfs.polygon
    quadmeshes = pfs.quadmeshes
    rectangle = pfs.rectangle
    savefig = pfs.savefig
    scatter = pfs.scatter
    semilogx = pfs.semilogx
    semilogy = pfs.semilogy
        
    stackplot = pfs.stackplot
    stem = pfs.stem
    step = pfs.step
    streamplot = pfs.streamplot
    table = pfs.table
    text = pfs.text
    texts = pfs.texts
    vlines = pfs.vlines

        


class SubPlot(Axes,BasePlot):
    """ PlotFactory. Return a new instance of this axes instance with updated parameters

    signatures:
    subplot()
    subplot(axes)  or axes(axes=axes)
    subplot(axes, "xlabel") or axes(axes=axes, xlabel="xlabel")
    subplot(axes, "xlabel", "ylabel") or  ...
    subplot(axes, "xlabel", "ylabel", "title")
    subplot(axes, "xlabel", "ylabel", "title", ["set","show","draw"])


    All args can be keyword arguments or assigned parameter as obj['color'] = "red"

    Use .info attribute to print a up-to-date state of this object.

    Note: contrary to matplotlib subplot(111) will not create a subplot on curent figure
        but will create a new instance of axes where the default axes is 111 on
        the curent figure (unless figure is set).
        However subplot(111, anchor=True) will have the same effect than matplotlib plt.axes(111)


    subplot like other PlotFactory object allow to create easely several instances with
    variable parameters, all iterable excecept tuple are cycled in iter method,
    iteraxes,  iter on axes and kind of replace the mathplotlib subplots function.
    See examples bellow.

    Note that subplot(111, xlabel="x", ylabel="y") will not store the labels on the
    axes (to keep the template capability), it will do it when the method .axes() is called.
        >>> myplot = subplot(111, xlabel="x", ylabel="y") # just store default labels
        >>> myplot.axes() # write labels on the defined axis
       can be also shorten in one:
        >>> myplot = subplot(111, xlabel="x", ylabel="y", go=["axes"]) # see go bellow


    Args:
      Full list is infinite, but here are some specific to smmartplotlib

        axes: Define witch axes to use. Can accept several formes:
            None/False (default) : curent axes is used for any subplot
            string : look for axes with that name raise ValueError if not found
            (ncol,nrow,i) : axes i'th in a ncol by nrow grid (see matplotlib.figure.add_subplot)
            (N,i)         : ncol, nrow are created so ncol*nrow>=N and the grid is
                            as square as possible. e.i N=10 is a 4x3 grid
            matplotlib.Axes object : use that axes
            subplot instance : use axes defined by its instance
            int : look for the i'th axes in the plot raise ValueError if not found
                But as there is little chance that anybody wants more than 100
                axes, int>100 is interpreted as : cri = (c,r,i) e.g 221 = (2,2,1)
                first axes on a 2x2 grid.
            (string, axes) : look for axes with name string if not found
                                use axes to find the plot axes
                                and then name it with string
            (axes, string) : here axes is one of the above and string is the the
                figure name/id. That it. ((2,2,1), "Mybestplots") will be enchor
                to the top axes of figure "Mybestplots".  This allows also to share axes
                limits of figure to another : sharex=((2,2,1), "Mybestplots") is understood

        xlabel (string) : x axis label
        ylabel (string) : y axis label
        title  (string) : axes top title

        figure (Optional[None/int/string]): determine witch figure to use. Can be
            None (default): use curent figure
            int : figure number (create one if needed)
            string : figure name (create one if needed)

            So  axes(axes=(2,2,1), figure="myplot") will be stuck on the "myplot" figure
            but axes(axes=(2,2,1), figure=None) will be the first axes of a 2x2
            grid of the curent figure (None is default)

        anchor (bool) : if True, run the anchor method on the axes instance.
            anchor is not stored as parameters. Equivalent to do:
                mysublpot.axes(axes=mysubplot.axes)

        go (string list) : actions to take after init, see .go method doc

        params (dict) : dictionary of parameters where keys can be a path to
            a targeted object e.g : {"xyplot.line|color": "red", "hist|bins":10, "xlabel":"x"} etc..

        **kwargs :  any other parameters which will be parsed to inerited childs
            instances of  PlotFactory or PlotFunc objects
            e.g. : subplot(color="blue") make a new instance of subplot where the default
            color is blue for any PlotFactory/PlotFunc used from the instance
            try: subplot(color="blue").errorbar.info

    Returns:
        subplot (PlotFactory): New ready instance of subplot.

    Altered Parameters:
        axes (matplotlib.Axes) : if anchor is True the 'axes' parameter become
            the matplolib axes.
        anchor (bool) : never saved as a parameter

        All other parameters are copied as they are.




    PlotFactory/PlotFunc Methods:
        TODO list of methods



    Examples:

     Simple make a subplot and plot directly with stored data:

         >>> a = subplot(111, xlabel="x", ylabel="y")
         >>> a.aclear() # clear the axes alias of cla()
         >>> a.axes() # set the labels
         >>> a.plot([1,2,3,4],[1,2,3,4])
         The one-line version would be :
         >>> subplot(111, xlabel="x", ylabel="y", x=[1,2,3,4], y=[1,2,3,4]).go("aclear","axes","plot")

     You can define the go action so it will be executed automaticaly, if you
         do so you must use the derive() method instead of calling the object.
         >>> my_velocity_plot = subplot.derive( xlabel="time", ylabel="velocity",
                                                       go=["aclear", "axes", "plot"]
                                                     )
         Than use my_velocity_plot where ever you want, of course x and y must
         be keywords.

         >>> my_velocity_plot( x=[1,2,3,4], y=[1,4,9,16], title="Data sample #1")
           NB: this example makes more sens with xyplot instead of subplot instance:
               >>> my_velocity_plot = subplot.xyplot.derive( .... )
              Then x, y can be parsed as positional argument since the my_velocity_plot
              is a xyplot instance and not a axes instance.
               >>> my_velocity_plot([1,2,3,4], [1,4,9,16], title="Data sample #1")

     Iter on parameter:

        >>> measure, model = subplot.iter(2, fmt=["k+","r-"],
                                           ylabel="velocity", xlabel="time")

        Then, one can re-use 'measure' and 'model' blindly
        >>> measure.plot(x, y) #plot with fmt "k+"
        >>> model.plot(x, y)   #plot with fmt "r-"

        The iteraxes kind of replace the mathplotlib subplots :
        >>> axs = list(subplot.iteraxes(2,2, xlabel=["x label1", "x label2"]))
        >>> len(axs)
        4
        >>> [a["axes"] for  a in axs]
        [(2, 2, 1), (2, 2, 2), (2, 2, 3), (2, 2, 4)]
        >>> [a["xlabel"] for  a in axs]
        ['x label1', 'x label2', 'x label1', 'x label2']

      You can plot 4 axes in one single line:
        >>> import numpy as np
        >>> _ = [a.go("axes","plot") for a in axes.iteraxes(2,2, y=np.random.rand(4,100),
                                                    x=[np.arange(100)],
                                                    color=list("rb")
                                                 )]

    """

    aclear = pfs.aclear
    axes = axes
    def set(self, *args, **kwargs):
        posvar = ["xlabel","ylabel","title"]
        largs = len(args)
        for i,k in enumerate(posvar):
            if largs>i:
                if k in kwargs:
                    raise TypeError("keyword argument '%s' repeated"%k)
                kwargs[k] = args[i]
            else:
                break
        self.update(dict(kwargs.pop(KWS,{}), **kwargs))
        self.axes()
        return self
        

    def anchor(self):
        """ anchor the matplolib axes to this subplot instance

        myaxes.anchor()
        is equivalent to:
        myaxes["axes"] = myaxes.get_axes()

        Returns:
            None

        Raises:
            TypeError : if this is the original subplot object

        """
        if self is subplot:
            raise TypeError("cannot anchor axes on the original subplot object")
        self["axes"] = self.get_axes()

    @staticmethod
    def finit(plot, *args, **kwargs):

        largs = len(args)
        posvar =["axes","xlabel","ylabel","title", "go"]
        if largs>len(posvar):
            raise ValueError("axes take no more than %d positional arguments"%len(posvar))

        for i,k in enumerate(posvar):
            if largs>i:
                if k in kwargs:
                    raise TypeError("keyword argument '%s' repeated"%k)
                kwargs[k] = args[i]
            else:
                break
        anchor = kwargs.get("anchor", False)
        plot.update(dict(kwargs.pop(KWS,{}), **kwargs))
        if anchor:
            plot.anchor()

        plot.goifgo()
    finit.__func__.__doc__ = __doc__
#axes["color"] = cycle(u"bgrcmyk")
subplot = SubPlot()

subplot["-"] = ["axes"]
subplot["-init"] = ["aclear", "axes"]
subplot["-end"]  = ["legend", "draw"]

pfs.plot_axes_classes += (SubPlot,)



class Plots(Figure,BasePlot):
    """
    plots would be the equivalent of figure. A colection of subplots, func, Plot object
    in the context of a figure.
    TODO : doc Plots
    """
    clear = pfs.fclear
    figure = figure
    axes   = axes

    @staticmethod
    def finit(plot, *args, **kwargs):
        if len(args)>0:
            kwargs["figure"] = args[0]
        if len(args)>1:
            kwargs["axes"] = args[1]
        elif len(args)>2:
            raise ValueError("plots take no more than 2 positional arguments")
        plot.update(dict(kwargs.pop(KWS,{}), **kwargs))

    def anchor(self):
        """ anchor the matplolib figure to this Plots instance

        myaxes.anchor()
        is equivalent to:
        myfig["figure"] = myfig.get_figure()

        Returns:
            None

        Raises:
            TypeError : if this is the original figure object

        """
        if self is plots:
            raise TypeError("cannot anchor figure on the original plots object")
        self["figure"] = self.get_figure()    

plots = Plots()

styler.pfs.update(plots=Plots,subplot=subplot)







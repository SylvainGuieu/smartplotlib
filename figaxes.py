from __future__ import division, absolute_import, print_function

from . import plotfuncs as pfs

import matplotlib.pyplot as plt

from .base import Plot, PlotFunc
from .recursive import cycle, lcycle, KWS


class null:
    """ a null value because sometime None is embigous """
    pass

class BasePlot(Plot):
    def get_axes(self):
        return pfs.get_axes(self.get("axes",None), self.get("figure",None))

    def get_figure(self):
        return pfs.get_figure(self.get("figure",None), self.get("axes",None))

    axes = pfs.aset
    figure = pfs.fset

    @property
    def _axes(self):
        return self.get_axes()

    @property
    def _figure(self):
        return self.get_figure()

    def derive(self, *args, **kwargs):
        new = super(BasePlot, self).derive(*args, **kwargs)
        new.reset() # reset all cycles to 0
        return new

    def clearparams(self):
        return self.locals.clear()


class AllPlot(BasePlot):
    pass
for k,p  in pfs.__dict__.iteritems():
    if isinstance(p, PlotFunc):
        setattr(AllPlot,k,p)


class Axes(AllPlot):
    """ Plot. Return a new instance of this axes instance with updated parameters

    signatures:
    axes()
    axes(axes)  or axes(axes=axes)
    axes(axes, "xlabel") or axes(axes=axes, xlabel="xlabel")
    axes(axes, "xlabel", "ylabel") or  ...
    axes(axes, "xlabel", "ylabel", "title")
    axes(axes, "xlabel", "ylabel", "title", ["set","show","draw"])


    All args can be keyword arguments or assigned parameter as obj['color'] = "red"

    Use .info attribute to print a up-to-date state of this object.

    Note: contrary to matplotlib axes(111) will not create an axes on curent figure
        but will create a new instance of axes where the default axes is 111 on
        the curent figure (unless figure is set).
        However axes(111, anchor=True) will have the same effect than matplotlib plt.axes(111)


    axes like other Plot object allow to create easely several instances with
    variable parameters, all iterable excecp tuple are cycled in iter method,
    iteraxes,  iter on axes and kind of replace the mathplotlib subplots function.
    See examples bellow.




    Args:
      Full list is infinite, but here are some specific to smmartplotlib

        axes: Define witch axes to use. Can take accept several formes:
            None/False (default) : curent axes is used for any subplot
            string : look for axes with that name raise ValueError if not found
            (ncol,nrow,i) : axes i'th in a ncol by nrow grid (see matplotlib.figure.add_subplot)
            (N,i)         : ncol, nrow are created so ncol*nrow>=N and the grid is
                            as square as possible. e.i N=10 is a 4x3 grid
            matplotlib.Axes object : use that axes
            axes instance : use axes defined by its instance
            int : look for the i'th axes in the plot raise ValueError if not found
                But as there is little chance that anybody wants more than 100
                axes, int>100 is interpreted as : cri = (c,r,i) e.g 221 = (2,2,1)
                first axes on a 2x2 grid.
            (string, axes) : look for axes with name string if not found
                                use axes to find the plot axes
                                and then name it with string

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

        anchor (bool) : if True run the anchor method on the axes instance.
            anchor is not stored as parameters

        go (string list) : actions to take after init, see .go method doc

        params (dict) : dictionary of parameters where keys can be a path to
            a targeted object e.g : {"xyplot.line|color": "red", "hist|bins":10}

        **kwargs :  any other parameters which will be parsed to inerited childs
            (new instances or child Plot/PlotFunc object)
            e.g. : axes(color="blue") make a new instance of axes where the default
            color is blue for any sub PlotFunc who is using them e.g.
            try axes(color="blue").errorbar.info

    Returns:
        axes(Plot): New ready instance of axes.

    Altered Parameters:
        axes (matplotlib.Axes) : if anchor is True the 'axes' parameter become
            the matplolib axes.
        anchor (bool) : never saved as a parameter

        All other are copied as they are

    Plot/PlotFunc Methods:
        TODO list of methods



    Examples:

     Simple make an axes and plot:

         >>> a = axes(111, xlabel="x", ylabel="y")
         >>> a.aclear()
         >>> a.aset() # set the labels
         >>> a.plot([1,2,3,4],[1,2,3,4])
         The on-line version would be :
         >>> axes(111, xlabel="x", ylabel="y", x=[1,2,3,4], y=[1,2,3,4]).go("aclear","aset","plot")

     You can define the go action so it will be executed automaticaly, if you
         do so you must use the derive() method instead of calling the object.
         >>> my_velocity_plot = axes.xyplot.derive( xlabel="time", ylabel="velocity",
                                            go=["aclear", "aset", "plot"]
                                            )
         Than use my_velocity_plot where ever you want, of course x and y must
         be untered as keywords.
         >>> my_velocity_plot( x=[1,2,3,4], y=[1,4,9,16], title="Data sample #1")
           NB: this example makes more sens with xyplot instead of axes instance:
               >>> my_velocity_plot = axes.xyplot.derive( .... )
              Then x, y can be parsed as positional argument since the my_velocity_plot
              is a xyplot instance and not a axes instance.
               >>> my_velocity_plot([1,2,3,4], [1,4,9,16], title="Data sample #1")


     Iter on parameter:

        >>> measure, model = axes.iter(2, fmt=["k+","r-"],
                                  ylabel="velocity", xlabel="time")

        Then, one can re-use measure and model blindly
        >>> measure.plot(x, y) #plot with fmt "k+"
        >>> model.plot(x, y)   #plot with fmt "r-"

        The iteraxes kind of replace the mathplotlib subplots :
        >>> axs = list(axes.iteraxes(2,2, xlabel=["x label1", "x label2"]))
        >>> len(axs)
        4
        >>> [a["axes"] for  a in axs]
        [(2, 2, 1), (2, 2, 2), (2, 2, 3), (2, 2, 4)]
        >>> [a["xlabel"] for  a in axs]
        ['x label1', 'x label2', 'x label1', 'x label2']

      You can plot 4 axes in one single line:
        >>> import numpy as np
        >>> _ = [a.go("aset","plot") for a in axes.iteraxes(2,2, y=np.random.rand(4,100),
                                                    x=[np.arange(100)],
                                                    color=list("rb")
                                                 )]

    """
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
        self.aset()
        return self

    @pfs.aclear.decorate("axes", "figure", ("plotinstance",".."))
    def aclear(axes=None, figure=None, plotinstance=None):
        """ clear the axes

        Parameters:
            figure : figure id or object get the first axes if axes is None
            axes   : axes object axes or number or tuple
        """
        # reset all the cycles of the axes plotinstance
        if plotinstance:
            plotinstance.reset()
        return pfs.get_axes(axes, figure).clear()

    clear = aclear

    def anchor(self):
        """ anchor the matplolib axes to this axes instance

        myaxes.anchor()
        is equivalent to:
        myaxes["axes"] = myaxes.get_axes()

        Returns:
            None

        Raises:
            TypeError : if this is the original axes object

        """
        if self is axes:
            raise TypeError("cannot anchor axes on the original axes object")
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
axes = Axes()

axes["-"] = ["aset"]
axes["-init"] = ["aclear", "aset"]
axes["-end"]  = ["legend", "draw"]

pfs.plot_axes_classes += (Axes,)



class Figure(AllPlot):
    set = pfs.fset
    clear = pfs.fclear
    @staticmethod
    def finit(plot, *args, **kwargs):
        if len(args)>0:
            kwargs["figure"] = args[0]
        if len(args)>1:
            kwargs["axes"] = args[1]
        elif len(args)>2:
            raise ValueError("figure take no more than 2 positional arguments")
        plot.update(dict(kwargs.pop(KWS,{}), **kwargs))

figure = Figure()










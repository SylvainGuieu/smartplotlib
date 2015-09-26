from __future__ import division, absolute_import, print_function

from .base import PlotFunc
from .recursive import popargs, KWS, extract_args, alias

import matplotlib.pyplot as plt
import numpy as np
import os # for savefig

__all__ = ["get_axes", "get_figure", "aset", "fset", "show", "fclear",
           "draw", "aclear", "grid", "plot", "lines", "errorbar", "scatter",
           "vlines", "axvline", "hlines", "axhline", "streamplot", "hist",
           "fill_between", "tables", "table", "texts", "text", "legend",
           "plot_axes_classes", "axhspan", "axvspan", "axspan", "bar", "step",
           "annotate", "annotates", "eventplot", "loglog", "semilogx", "semilogy"
           ]

AXES_PARAMS = "axes_params"

axes_param_names = ["sharex", "sharey"]

plotfunc = PlotFunc("axes", "figure")


artist = plotfunc.duplicate('clip_on', 'contains', 'label', 'animated',
                            'sketch_params', 'lod', 'snap',
                            'transform', 'alpha', 'rasterized', 'path_effects', 'agg_filter', 'zorder',
                            'clip_box', 'picker', 'clip_path', 'visible', 'url', 'gid'
                            )




def axesfunc(plotfunc, attrname):
    def axes_plot(*args, **kwargs):
        axes = get_axes_kw(kwargs)
        return getattr(axes, attrname)(*args, **kwargs)
    axes_plot.__doc__ = getattr(plt.Axes, attrname).__doc__
    setpfdoc(plotfunc, axes_plot.__doc__, attrname)
    return plotfunc.caller(axes_plot)

def figurefunc(plotfunc, attrname):
    def figure_plot(*args, **kwargs):
        figure = get_figure_kw(kwargs)
        return getattr(figure, attrname)(*args, **kwargs)
    figure_plot.__doc__ = getattr(plt.Figure, attrname).__doc__
    setpfdoc(plotfunc, figure_plot.__doc__, attrname)
    return plotfunc.caller(figure_plot)


def _make_func(name,derived="plotfunc", cls=plt.Axes,
               action="derive"
               ):
    func = getattr(cls, name)
    derive = "{name} = {derived}.{action}{args}".format(
                    name = name, derived=derived, action=action,
                    args=extract_args(func, 1)
                  )
    print(derive)
    decorate = "@{name}.caller\n".format(name=name)
    decorate += "def {name}(*args,**kwargs):\n".format(name=name)
    decorate += "    return get_axes_kw(kwargs).{name}(*args, **kwargs)\n".format(name=name)
    decorate += "setpfdoc({name}, plt.Axes.{name}.__doc__, '{name}')\n".format(name=name)
    print (decorate)
    return derive+"\n"+decorate+"\n"




def _keys(cls, idt=""):
    """ a developer function to help copying list of keyword """
    lens = len(idt)
    s = idt
    kw = []
    for sub in cls.__mro__:
        for k in sub.__dict__:
            if k[0:4]=="set_":
                ks = k[4:]
                if not ks in kw:
                    _s = "'%s', "%(ks)
                    lens+=len(_s)
                    s += _s
                    kw.append(ks)
                if lens>80:
                    s+="\n"+idt
                    lens=len(idt)
    print (s.rstrip().rstrip(","))

def _list_formater(lst, length=80, idt=""):
    lens = len(idt)
    out = []
    line = ""
    first = False
    for s in lst:
        if (len(s)+lens)>length:
            out.append(line+",")
            lens = len(idt)
            line = idt+s
        else:
            line += (", "*first)+s
            lens = len(line)
        first = True
    return "\n".join(out).rstrip(",")

def setpfdoc(pf, doc, name):
    doc = doc or "" #remove the None
    fmt = """ PlotFunc Wrapper of matplolib.{name} : {firstline}


default parameters can be assigned by func['param'] = value
or inerit from a parent PlotFactory obj. See PlotFunc and PlotFactory doc.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{doc}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PlotFunc : All the following args can be assigned by func['param'] = value
by func.update(param=value) or can inerit from parent PlotFactory :

{arglist}
     """
    pf.__doc__ = fmt.format(name=name,firstline=doc.split("\n",1)[0].strip(),
                            doc=doc, arglist=_list_formater(pf.args))


def colect_axes_kwargs(kwargs):
    """ colect all the axes_params need for its creation
    """
    return {}
    return {k:kwargs.pop(k) for k in axes_param_names if k in kwargs}

def _add_subplot(figure, coord, params):
    return figure.add_subplot(*coord, **params)


plot_axes_classes = []
def get_axes(axes, fig=None, params={}):
    """
     axesdef can be:
        None   : curent axes is used
        string : look for axes with that name raise ValueError is not found
        (ncol,nrow,i) : axes ith in a ncol by nrow grid (see matplotlib.figure.add_subplot)
        (N,i)         : ncol, nrow are created so ncol*nrow<N and the grid is
                        as square as possible. e.i N=10 is a 4x3 grid
        matplotlib.Axes object : use that axes
        axes instance : use axes defined there
        int : look for the i'th axes in the plot raise ValueError if not found

        params is a dictionary used only when an axes is created
    """
    if axes is None:
        figure = get_figure(fig)
        return figure.gca()

    if isinstance(axes, tuple(plot_axes_classes)):
        return get_axes(axes.get("axes",None), axes.get("figure",fig), params)


    if isinstance(axes, basestring):
        name = axes
        figure = get_figure(fig)
        for ax in (figure.axes or []):
            if getattr(ax, "id", None) == name:
                axes = ax
                break
        else:
            # raise an error if not found
            # however user as still possibility to send
            # a tuple of (name, axes) see below
            raise ValueError("Cannot find axes of name '%s' in this figure"%name)
        return axes

    if isinstance(axes, (tuple,list)):
        figure = get_figure(fig)
        coord = axes

        if len(coord)==2:
            if isinstance(coord[1], basestring):
                # if string the second is a figure
                axes, fig = coord
                # "3" must be 3
                try:
                    intfig = int(fig)
                except:
                    pass
                else:
                    fig = intfig
                return get_axes(axes, fig, params)

            if isinstance(coord[0], basestring):
                # this is a (name, axes) tuple
                # try to find the name if not found
                # find the axes and rename it
                name, axes = coord
                try:
                    axes = get_axes(name, fig)
                except TypeError:
                    axes = get_axes(axes, fig, params)
                    axes.id = name
                finally:
                    return axes
            if isinstance(coord[0], int):
                #########
                # If coord is a (N,i) tuple, build the (nx,ny,i) tuple automaticaly
                #########
                nx = int(plt.np.sqrt(coord[0]))
                ny = int(plt.np.ceil(coord[0]/float(nx)))
                coord = (nx,ny,coord[1])
            else:
                raise TypeError("invalid 2 tuple axes '%s'"%coord)
        elif len(coord)==1:
            #this is explicitaly a number (probably superior to 100)
            axes, = coord
            if not isinstance(axes,int):
                return get_axes(axes, fig, params)

            figure = get_figure(fig)
            num = axes
            ##
            # conserve the supid 1 has the 1st axes e.g. 0th
            # to avoide confusion
            num -= 1

            if num>=len(figure.axes):
                raise ValueError("cannot find the %dth axes, figure has only %d axes"%(num+1,len(figure.axes)))
            return figure.axes[num]


        if len(coord)!=3:
            raise TypeError("coord tuple must be of len 2 or 3 got %d"%len(coord))

        axes = _add_subplot(figure, coord, params)
        return axes

    if isinstance(axes, int):
        figure = get_figure(fig)
        num = axes
        ##
        # it is prety much unlikely that more than 100 axes is intanded
        # to be plot. so better to put the short cut 121 as (1,2,1)
        # user can still force axes number with (456,) which is the axes
        # number #456
        if num>100:
            if num>9981:
                raise ValueError("int acceed 9981 use (num,) to force to the num'th axes")
            coord = tuple(int(n) for n in str(num))
            return get_axes(coord, fig, params)
        ##
        # conserve the supid 1 has the 1st axes e.g. 0th
        # to avoide confusion
        num -= 1
        if num>=len(figure.axes):
            raise ValueError("cannot find the %dth axes, figure has only %d axes"%(num+1,len(figure.axes)))
        axes = figure.axes[num]

        return axes

    if isinstance(axes,(plt.Axes, plt.Subplot)):
        return axes

    raise TypeError("axes keyword must be a tuple, integer, None, string or Axes instance got a '%s'"%(type(axes)))


def get_figure(fig, axes=None):
    if isinstance(fig,plt.Figure):
        return fig
    if fig is None:
        if axes is None:
            return plt.gcf()
        return get_axes(axes).figure

    if isinstance(fig, (tuple,list)):
        tpl = fig
        if len(tpl)!=2:
            TypeError("Expecting a 2 tuple for figure got '%s'"%(tpl,))

        if isinstance(tpl[0], basestring):
            name, fig = tpl
            fig = figure(name)
        else:
            fig = get_figure(None, axes)

        if len(tpl)!=2:
            TypeError("Expecting a 2 tuple for figure got '%s'"%(tpl,))

        nrows, ncols = tpl
        gs = GridSpec(nrows, ncols)
        for i in range(nrows*ncols):
            fig.add_subplot(gs[i // ncols, i % ncols])
        return fig

    return plt.figure(fig)

def get_axes_kw(kwargs):
    return get_axes(kwargs.pop("axes", None),
                    kwargs.pop("figure",None),
                    colect_axes_kwargs(kwargs)
                    )

def get_figure_kw(kwargs):
    return get_figure(kwargs.pop("figure", None), kwargs.get("axes",None))



def update_form_rcparams(pf, name):
    """ update all default keyword of the root param NAME in the rcParameter """
    params = {}
    for path, value in plt.rcParams.iteritems():
        func, param = path.split(".",1)
        if func != name:
            continue
        if "." in param: # not a end point parameter
            continue
        params[param] = value
    pf.update(params)



###############################################################
#
#    Figure and Axes setupt
#
###############################################################

# Some keyword are not the same than in the plt.axes function
# than in the Axes.set_something , e.g. axisbg is axis_bgcolor
axes_short_kws = dict(axisbg="axis_bgcolor",frameon="frame_on")

aset = plotfunc.duplicate('figure', 'axes', "sharex", "sharey",
        'picker', 'adjustable', 'cursor_props', 'yscale', 'navigate', 'clip_box',
        'transform', 'xscale', 'aspect', 'axis_bgcolor', 'ylim', 'clip_on', 'xlim',
        'axis_on', 'title', 'contains', 'clip_path', 'axis_off', 'xticks', 'ylabel',
        'autoscalex_on', 'xlabel', 'rasterization_zorder', 'axes_locator', 'subplotspec',
        'agg_filter', 'axisbelow', 'frame_on', 'navigate_mode', 'snap', 'autoscaley_on',
        'autoscale_on', 'alpha', 'ybound', 'yticklabels', 'rasterized', 'xmargin',
        'path_effects', 'sketch_params', 'color_cycle', 'lod', 'zorder', 'xbound',
        'yticks', 'ymargin', 'position', 'animated', 'anchor', 'xticklabels',
        'axisgb', 'frameon', 'axis'
        )

@aset.caller
def aset(axes=None, figure=None, sharex=None, sharey=None, **kwargs):
    name = kwargs.pop("name", None)

    axes = get_axes(axes, figure, colect_axes_kwargs(kwargs))
    if sharey not in [None, False]:
        sharey = get_axes(sharey, figure)
        if sharey is not axes:
            axes._shared_y_axes.join(axes, sharey)
            if sharey._adjustable == 'box':
                sharey._adjustable = 'datalim'
            #warnings.warn(
            #    'shared axes: "adjustable" is being changed to "datalim"')
            axes._adjustable = 'datalim'

    if sharex not in [None, False]:
        sharex = get_axes(sharex, figure)
        if sharex is not axes:
            axes._shared_x_axes.join(axes, sharex)
            if sharex._adjustable == 'box':
                sharex._adjustable = 'datalim'
            #warnings.warn(
            #    'shared axes: "adjustable" is being changed to "datalim"')
            axes._adjustable = 'datalim'

    if name:
        axes.id = name

    for kshort, kreal in axes_short_kws.iteritems():
        if kshort in kwargs:
            kwargs[kreal] = kwargs.pop(kshort)

    axis = kwargs.pop("axis", None)

    if len(kwargs):
        axes.set(**kwargs)

    if axis:
        axes.axis(axis)

    return axes
setpfdoc(aset, plt.Axes.set.__doc__, "set")



fset = plotfunc.duplicate('figure', 'axes',
        'picker', 'edgecolor', 'clip_on', 'clip_box', 'transform',
        'canvas', 'facecolor', 'lod', 'size_inches', 'contains', 'clip_path', 'figwidth',
        'snap', 'agg_filter', 'figheight', 'alpha', 'tight_layout', 'rasterized',
        'path_effects', 'sketch_params', 'frameon', 'zorder', 'animated', 'dpi',
        "sp_left", "sp_bottom", "sp_right", "sp_top", "sp_wspace", "sp_hspace",
        "wspace", "hspace", "suptitle"
        )

@fset.caller
def fset(figure=None, axes=None, sp_left=None, sp_bottom=None, sp_right=None, sp_top=None,
         sp_wspace=None, sp_hspace=None, wspace=None, hspace=None, suptitle=None, **kwargs):
    fig = get_figure(figure, axes)

    if suptitle:
        fig.suptitle(suptitle)

    if len(kwargs):
        fig.set(**kwargs)
    fig.subplots_adjust(left=sp_left, bottom=sp_bottom, right=sp_right, top=sp_top,
                        wspace=wspace if sp_wspace is None else sp_wspace,
                        hspace=hspace if sp_hspace is None else sp_hspace
                        )

    return fig
setpfdoc(fset, plt.Figure.set.__doc__, "fset")

@plotfunc.decorate("left", "bottom", "right", "top", "wspace", "hspace")
def adjust(left=None, bottom=None, right=None, top=None,
           wspace=None, hspace=None, figure=None, axes=None):
    fig = get_figure(figure, axes)
    return fig.subplots_adjust(left=left, bottom=bottom, right=right,
                               top=top, wspace=wspace, hspace=hspace)



@plotfunc.decorate()
def show(figure=None, axes=None):
    """ show the figure

    Parameters:
        figure : figure id or object
        axes   : axes object axes.figure used if figure is None
    """
    return get_figure(figure, axes).show()

@plotfunc.decorate()
def fclear(figure=None, axes=None):
    """ clear the figure

    Parameters:
        figure : figure id or object
        axes   : axes object axes.figure used if figure is None
    """
    return get_figure(figure, axes).clear()
clf = fclear


@plotfunc.decorate()
def draw(figure=None, axes=None):
    """ draw the figure's canvas

    Parameters:
        figure : figure id or object
        axes   : axes object axes.figure used if figure is None
    """
    return get_figure(figure, axes).canvas.draw()

@plotfunc.decorate()
def aclear(axes=None, figure=None):
    """ clear the axes

    Parameters:
        figure : figure id or object get the first axes if axes is None
        axes   : axes object axes or number or tuple
    """
    return get_axes(axes, figure).clear()
cla = aclear

@plotfunc.decorate("b", "which", "axis")
def grid(*args, **kwargs):
    return get_axes_kw(kwargs).grid(*args, **kwargs)
setpfdoc(grid, plt.Axes.grid.__doc__, "grid")


colorbar = plotfunc.derive(0,
                           "mappable","cax", "ax", "use_gridspec",
                           "orientation","fraction", "pad", "shrink", "aspect",
                           "anchor", "panchor","extend","extendfrac",
                           "extendrect","spacing","ticks","format","drawedges",
                           "boundaries","values"
                           )
@colorbar.caller
def colorbar(*args, **kwargs):
    if not len(args):
        mappable = kwargs.pop("mappable", None)
    else:
        mappable = args[0]
        args = args[1:]

    if mappable is None:
        mappable = plt.gci()
        if mappable is None:
            raise RuntimeError('No mappable was found to use for colorbar '
                           'creation. First define a mappable such as '
                           'an image (with imshow) or a contour set ('
                           'with contourf).')
    args = (mappable,)+args
    ax = kwargs.pop("ax", None)
    if ax is not None:
        kwargs["ax"] = get_axes(ax, kwargs.get("figure",None))

    return get_figure_kw(kwargs).colorbar(*args, **kwargs)


savefig = plotfunc.derive(1,
           "fname", "dpi", "facecolor", "edgecolor",
           "orientation", "papertype", "format",
           "transparent", "bbox_inches", "pad_inches",
           "frameon", "version"
          )
@savefig.caller
def savefig(fname, *args, **kwargs):
    version = kwargs.pop("version", None)

    if not isinstance(fname, basestring):
        raise ValueError("fname must be a string got a '%s'"%type(fname))
    if version is not None:
        name, ext = os.path.splitext(fname)
        fname=name+version+ext

    return get_figure_kw(kwargs).savefig(fname, *args, **kwargs)


###############################################################
#
#    2D plots
#
###############################################################


line2d = plotfunc.duplicate('marker',
        'aa', 'mfc', 'dash_capstyle', 'figure', 'markeredgewidth', 'markevery', 'markerfacecoloralt',
        'markeredgecolor', 'linewidth', 'linestyle', 'mfcalt', 'solid_joinstyle',
        'markerfacecolor', 'axes', 'dash_joinstyle', 'fillstyle', 'lw', 'ls', 'solid_capstyle',
        'mec', 'markersize', 'mew', 'antialiased', 'path', 'color', 'c', 'drawstyle',
        'label', 'xydata', 'ms', 'pickradius', 'window_extent'
        )
setpfdoc(line2d, plt.Line2D.__doc__+"\n\n"+plt.Line2D.__init__.__doc__, "line2d")

##
# number of keyword triplet xi, yi, fmti accepted. where i included in range(1,Ntriplet+1)
_Ntriplet = 9
##
# build a triplet kw tuple
xyfmts = tuple(reduce(lambda l,i: l+["y%d"%i,"x%d"%i,"fmt%d"%i],range(1,_Ntriplet+1), [] ))

def _get_plot_args(args, kwargs, triplet=("x","y","fmt"), Ni=_Ntriplet):
    """ from args tuple and kwargs return a new args list and
    a modified kwargs
    """
    kx, ky, kfmt = triplet
    fmt_default = "-"
    x = None
    largs = len(args)
    if not largs:
        y = kwargs.pop(ky, None)
        x = kwargs.pop(kx, None)
        fmt = kwargs.pop(kfmt, fmt_default)
        if x is None and y is not None:
            x = np.arange(np.asarray(y).shape[0])
        if y is not None:
            args = (x,y,fmt)
    elif largs==1:
        # one unique argument is "y"
        y = args[0]
        x = kwargs.pop(kx, None)
        fmt = kwargs.pop(kfmt, fmt_default)
        if x is None:
             x = np.arange(np.asarray(y).shape[0])
        args = (x,y, fmt)
    elif largs==2:
        x, y = args
        fmt = kwargs.pop(kfmt, fmt_default)
        args = (x,y, fmt)
    else:
        if not isinstance(args[2], basestring):
            # if the third arg is not a string, that a new x
            args = args[0:2]+kwargs.pop(kfmt, fmt_default)+args[2:]


    for i in range(1,Ni+1):
        yi = kwargs.pop(ky+"%d"%i, None)
        if x is None and (yi is not None):
            x = np.arange( np.asarray(yi).shape[0] )

        if yi is not None:
            xi, fmti = kwargs.pop(kx+"%d"%i, x),kwargs.pop(kfmt+"%d"%i, fmt)
            args += (xi,yi,fmti)
        else:
            #remove any xi , fmti left
            kwargs.pop(kx+"%s"%i, None)
            kwargs.pop(kfmt+"%s"%i, None)
    return args, kwargs



@line2d.decorate(0, *(("x", "y", "fmt")+tuple(xyfmts)+("scalex", "scaley")))
def plot(*args, **kwargs):
    axes = get_axes_kw(kwargs)
    args, kwargs = _get_plot_args(args, kwargs)
    return axes.plot(*args, **kwargs)

setpfdoc(plot, plt.Axes.plot.__doc__, "plot")


errorbar = line2d.derive(2, "x", "y", "yerr", "xerr", "fmt",
                         "ecolor", "elinewidth",
                         "capsize", "capthick", "barsabove",
                         "lolims", "errorevery"
                        )
@errorbar.caller
def errorbar(x, y, *args, **kwargs):
    axes = get_axes_kw(kwargs)
    return axes.errorbar(x,y, *args, **kwargs)
setpfdoc(errorbar, plt.Axes.errorbar.__doc__, "errorbar")



@plot.decorate(0,*(("x", "y", "fmt")+tuple(xyfmts)+("scalex", "scaley", "where")))
def step(*args, **kwargs):
    args, kwargs = _get_plot_args(args, kwargs)
    axes = get_axes_kw(kwargs)
    return axes.step(*args, **kwargs)



@line2d.decorate(2, "xdates", "ydates", "fmt", "tz", "xdate", "ydate")
def plot_date(*args, **kwargs):
    axes = get_axes_kw(kwargs)
    return axes.plot_date(*args, **kwargs)
setpfdoc(plot_date, plt.Axes.plot_date.__doc__, "plot_date")

@plot.decorate("basex", "basey", "subsx", "subsy", "nonposx","nonposy")
def loglog(*args, **kwargs):
    args, kwargs = _get_plot_args(args, kwargs)
    axes = get_axes_kw(kwargs)
    return axes.loglog(*args, **kwargs)
setpfdoc(loglog, plt.Axes.loglog.__doc__, "loglog")

@plot.decorate("basex", "basey", "subsx", "subsy", "nonposx","nonposy")
def semilogx(*args, **kwargs):
    args, kwargs = _get_plot_args(args, kwargs)
    axes = get_axes_kw(kwargs)
    return axes.semilogx(*args, **kwargs)
setpfdoc(semilogx, plt.Axes.semilogx.__doc__, "semilogx")

@plot.decorate("basex", "basey", "subsx", "subsy", "nonposx","nonposy")
def semilogy(*args, **kwargs):
    args, kwargs = _get_plot_args(args, kwargs)
    axes = get_axes_kw(kwargs)
    return axes.semilogy(*args, **kwargs)
setpfdoc(semilogy, plt.Axes.semilogy.__doc__, "semilogy")

@plotfunc.decorate(0, "x", "y", "linefmt", "markerfmt", "basefmt", "bottom", 'label')
def stem(*args, **kwargs):
    if len(args)==1:
        y = args[0]
        x = kwargs.pop("x", None)
        if x is not None:
            args = (x,y)
    elif len(args)==2:
        kwargs.pop("x",None)
        kwargs.pop("y",None)

    return get_axes_kw(kwargs).stem(*args, **kwargs)
setpfdoc(stem, plt.Axes.stem.__doc__, "stem")


@line2d.decorate(2, "x", "y", "cmap", "norm", "vmin", "vmax",
                 "alpha", "linewidths", "verts")
def scatter(x, y, **kwargs):
    axes = get_axes_kw(kwargs)
    return axes.scatter(x, y, **kwargs)
setpfdoc(scatter, plt.Axes.scatter.__doc__, "scatter")


@line2d.decorate(3, "x", "ymin", "ymax")
def vlines(x, ymin, ymax,  **kwargs):
    return get_axes_kw(kwargs).vlines(x, ymin, ymax, **kwargs)
setpfdoc(vlines, plt.Axes.vlines.__doc__, "vlines")

@line2d.decorate(0, "x", "ymin", "ymax")
def axvline(*args,  **kwargs):
    args = list(args)
    x, = popargs(kwargs, args, "x", x=None)
    axes = get_axes_kw(kwargs)
    if hasattr(x, "__iter__"):
        return [axes.axvline(ix, *args, **kwargs) for ix in x]
    return axes.axvline(x, *args, **kwargs)
setpfdoc(axvline, plt.Axes.axvline.__doc__, "axvline")


@line2d.decorate(3, "y", "xmin", "xmax")
def hlines(y, xmin, xmax,  **kwargs):
    return get_axes_kw(kwargs).hlines(y, xmin, xmax, **kwargs)
setpfdoc(hlines, plt.Axes.hlines.__doc__, "hlines")


@line2d.decorate(3, "data", "min", "max", "direction")
def lines(data, _min, _max, direction="y", **kwargs):
    """execute hlines if direction=='y' or vlines if direction=="x"

    This is a PlotFunc wrapper, all parameters can be substitued form parents

    Args:
        lines(scalar,iterable): to plot on *direction* axes
        min (float) : the minimum value in data coordinate of the
            line in oposite of *direction*
        max (float) : the maximum value in data coordinate  of the
            line in oposite of *direction*
        direction (Optional[string,int]): if "y" or 0 (default) plot line(s) horizontaly with hlines
            if "x" or 1 plot line(s) verticaly with vlines
        **kwargs : all other kwargs for line2d

    See doc of vlines and hlines

    """
    if direction in ["y","Y",0]:
        return hlines(data, _min, _max, **kwargs)
    if direction in  ["x", "X", 1]:
        return vlines(data, _min, _max, **kwargs)
    raise ValueError("direction must be 'y' or 'x' , 1 or 0 got '%s'"%direction)

@line2d.decorate(0, "y", "xmin", "xmax")
def axhline(*args, **kwargs):
    args = list(args)
    y, = popargs(kwargs, args, "y", y=None)
    axes = get_axes_kw(kwargs)
    if hasattr(y, "__iter__"):
        return [axes.axhline(iy, *args, **kwargs) for iy in y]
    return axes.axhline(y, *args, **kwargs)
setpfdoc(axhline, plt.Axes.axhline.__doc__, "axhlines")

@line2d.decorate(0, "value", "axmin", "axmax", "direction")
def axline(value=0, axmin=0, axmax=1, direction="y", **kwargs):
    """execute axhline if direction=='y' or axvline if direction=="x"

    This is a PlotFunc wrapper, all parameters can be substitued form parents

    Args:
        data(Optional[scalar,iterable]): to plot on *direction* axes
        imin (Optional[float]) : the minimum value in axes coordinate (0 to 1) of the
            line in oposite of *direction*, default is 0
        imax (Optional[float]) : the maximum value in axes coordinate (0 to 1) of the
            line in oposite of *direction*, default is 1
        direction (Optional[string,int]): if "y" or 0 (default) plot line(s) horizontaly with axhline
            if "x" or 1 plot line(s) verticaly with axvline
        **kwargs : all other kwargs for line2d

    See doc of axvline and axhline

    """
    if direction in ["y","Y",0]:
        return axhline(value, axmin, axmax, **kwargs)
    if direction in  ["x", "X", 1]:
        return axvline(value, axmin, axmax, **kwargs)
    raise ValueError("direction must be 'y' or 'x' , 1 or 0 got '%s'"%direction)


@plotfunc.decorate(4, "x", "y", "vx", "vy", "density", "linewidth",
                 "color", "cmap", "norm", "arrowsize", "arrowstyle",
                 "minlength", "transform", "zorder")
def streamplot(x, y, u, v, **kwargs):
    axes = get_axes_kw(kwargs)
    return axes.streamplot(x,y, u, v, **kwargs)
setpfdoc(streamplot, plt.Axes.streamplot.__doc__, "streamplot")





###############################################################
#
#    patch plots
#
###############################################################

patches = plotfunc.duplicate(
        'aa', 'edgecolor', 'contains', 'clip_on', 'figure', 'color', 'clip_box',
        'joinstyle', 'clip_path', 'visible', 'linewidth', 'linestyle', 'fill', 'facecolor',
        'lod', 'axes', 'transform', 'label', 'lw', 'gid', 'ls', 'hatch', 'snap',
        'agg_filter', 'picker', 'fc', 'antialiased', 'ec', 'capstyle', 'alpha', 'rasterized',
        'path_effects', 'sketch_params', 'url', 'zorder', 'animated'
        )

#_keys(plt.Rectangle)
rectangle = plotfunc.duplicate(
    'xy', 'height', 'x', 'y', 'width', 'bounds', 'fill', 'fc', 'lw', 'ls', 'hatch', 'linewidth',
    'antialiased', 'aa', 'facecolor', 'edgecolor', 'joinstyle', 'linestyle', 'alpha',
    'ec', 'capstyle', 'color', 'clip_on', 'contains', 'label', 'animated', 'axes', 'sketch_params',
    'lod', 'snap', 'figure', 'transform', 'rasterized', 'path_effects', 'agg_filter',
    'zorder', 'clip_box', 'picker', 'clip_path', 'visible', 'url', 'gid'
   )

@patches.decorate(1, "data", "bins", "range", "normed", "weights", "cumulative",
                  "bottom", "histtype", "align", "orientation", "rwidth",
                  "log", "color", "label", "stacked")
def hist(*args, **kwargs):
    direction = kwargs.get("direction", "y")
    if direction in ["y","Y", 0]:
        kwargs["orientation"]="vertical"
    elif direction in ["x", "X", 1]:
        kwargs["orientation"]= "horizontal"
    else:
        raise ValueError("direction must be 'y' or 'x' (0 or 1) got '%s'"%direction)

    return get_axes_kw(kwargs).hist(*args, **kwargs)
setpfdoc(hist, plt.Axes.hist.__doc__, "hist")


histx2y = hist.derive(data=alias("x"),direction="y")
histy2x = hist.derive(data=alias("y"),direction="x")
histx2x = hist.derive(data=alias("x"),direction="x")
histy2y = hist.derive(data=alias("y"),direction="y")


@patches.decorate(2, 'indexes', 'data1', 'data2', 'where', 'interpolate', 'hold')
def fill_between(indexes, data1, data2=0,  **kwargs):
    d =  kwargs.get("direction", "y")
    axes = get_axes_kw(kwargs)
    if d in ['y','Y',0]:
        return axes.fill_between(indexes, data1, data2, **kwargs)
    elif d in ['x','X',1]:
        return axes.fill_betweenx(indexes, data1, data2, **kwargs)
    else:
        ValueError("direction must be 'y' or 'x' (0 or 1) got '%s'"%d)
setpfdoc(fill_between, plt.Axes.fill_between.__doc__, "fill_between")


@patches.decorate(2, 'x', 'y1', 'y2', 'where', 'interpolate', 'hold')
def fill_betweeny(*args, **kwargs):
    return get_axes_kw(kwargs).fill_between(*args, **kwargs)
setpfdoc(fill_between, plt.Axes.fill_between.__doc__, "fill_between")

@patches.decorate(2, 'y', 'x1', 'x2', 'where')
def fill_betweenx(*args, **kwargs):
    return get_axes_kw(kwargs).fill_betweenx(*args, **kwargs)
setpfdoc(fill_betweenx, plt.Axes.fill_betweenx.__doc__, "fill_between")


@rectangle.decorate(2, 'edge', 'height', 'width', 'base', 'rwidth', 'align', "direction", 'orientation')
def bar(edge, height, width=0.8, base=None, rwidth=1.0, offset=0.0,  **kwargs):
    """ PlotFunc. More general than the matplotlib bar function

    Compared to the  matplolib function the arg names has changed plus new ones:
        rwidth, offset, direction

    Args:
        edge (Array like): array of left (if direction="y")
            or bottom (if direction="x") corner of bars
        height (scalar/array): size of bar in direction of "direction"
        width (scalar/array) : (default 0.8) size of the bar in the oposote "direction"
        base (scalar/array) : bottom (if direction="x") left (if direction="y') of
            the bars

        align : if "center" the edge coordinates become the center of the bar

        rwidth (scalar/array): a relative width factor (default 1.0) the final width will be
            width*rwidth
        offset (scalar/array): offset of bars. final edges will be edges+offset
        direction ("y" or "x") : if "y" plot verticaly if "x" plot horizontaly
        orientation ("vertical" or "horizontal") : for compatibility raisons,
            used only if direction is not defined otherwhise it is ignored
    """
    kwargs.pop("xy", None)
    kwargs.pop("x", None)
    kwargs.pop("y", None)


    if "direction" in kwargs:
        kwargs.pop("orientation", None)

    d =  kwargs.pop("direction", "y")
    axes = get_axes_kw(kwargs)
    if d in ['y','Y',0]:
        func = axes.bar
    elif d in ['x','X',1]:
        func = axes.barh
    else:
        ValueError("direction must be 'y' or 'x' (0 or 1) got '%s'"%d)
    return func(edge+offset, height, width*rwidth, base, **kwargs)



def _fill_step_process(x0,y0, bottom):
    """ return a polygon that envelop what would have
    been ploted with bar( ..., align="center")
    """
    dim = len(x0)

    x = np.zeros(dim*2+2, np.float)
    y = np.zeros(dim*2+2, np.float)

    delta = np.diff(x0)/2.
    x[1:-3:2] = x0[:-1]-delta
    x[2:-2:2]  = x0[:-1]+delta
    y[1:-2:2] = y0
    y[2:-1:2]  = y0
    x[-3] = x0[-1]-delta[-1]
    x[-2] = x0[-1]+delta[-1]

    x[0] = x[1]
    x[-1] = x[-2]
    if bottom is not None:
        y[0] = bottom
        y[-1] = bottom
    else:
        y[0] = y0[0]
        y[-1] = y0[-1]
    return x, y


xymarker = sum((["x%d"%i,"Y%d"%i, "marker%d"%i] for i in range(1,10)), [])
@patches.decorate(2,"x","y", "marker", *xymarker)
def fill(*args, **kwargs):
    for i in range(1,10):
        x,y,m = (kwargs.pop("x%d"%i,None),
                 kwargs.pop("y%d"%i,None),
                 kwargs.pop("marker%d"%i, None))
        if (x,y,m) != (None,None,None):
            args+=(x,y,m)
    return get_axes_kw(kwargs).fill(*args, **kwargs)


fillstep = fill.derive(2, "x", "y", "marker", "bottom")
@fillstep.caller
def fillstep(x, y,**kwargs):
    bottom = kwargs.pop("bottom", None)
    x, y = _fill_step_process(np.asarray(x),
                              np.asarray(y),
                              bottom)

    return get_axes_kw(kwargs).fill(x, y, **kwargs)


###############################################################
#
#    3D plots
#
###############################################################



imshow = artist.derive(1, 'img', 'cmap', 'norm', 'aspect', 'interpolation', 'alpha',
                          'vmin', 'vmax', 'origin', 'extent', 'shape', 'filternorm',
                          'filterrad', 'imlim', 'resample', 'url'
                       )
@imshow.caller
def imshow(*args, **kwargs):
    return get_axes_kw(kwargs).imshow(*args,**kwargs)
setpfdoc(imshow, plt.Axes.imshow.__doc__, "imshow")

@imshow.decorate()
def matshow(*args, **kwargs):
    return get_axes_kw(kwargs).matshow(*args,**kwargs)
setpfdoc(matshow, plt.Axes.matshow.__doc__, "matshow")


tables = plotfunc.duplicate(
        'picker', 'axes', 'clip_on', 'figure', 'clip_box', 'clip_path', 'visible',
        'lod', 'contains', 'transform', 'label', 'gid', 'snap', 'agg_filter', 'fontsize',
        'alpha', 'rasterized', 'path_effects', 'sketch_params', 'url', 'zorder',
        'animated'
        )

table = tables.derive("cellText", "cellColours",
                 "cellLoc", "colWidths",
                 "rowLabels", "rowColours", "rowLoc",
                 "colLabels", "colColours", "colLoc",
                 "loc", "bbox")

@table.caller
def table(**kwargs):
    return get_axes_kw(kwargs).table(**kwargs)
setpfdoc(table, plt.Axes.table.__doc__, "table")


texts = plotfunc.duplicate(
        'picker', 'va', 'fontstyle', 'clip_on', 'figure', 'rotation_mode', 'color',
        'clip_box', 'clip_path', 'visible', 'verticalalignment', 'fontstretch', 'font_properties',
        'size', 'fontname', 'weight', 'linespacing', 'stretch', 'contains', 'transform',
        'label', 'fontvariant', 'fontproperties', 'gid', 'horizontalalignment', 'snap',
        'family', 'agg_filter', 'fontsize', 'variant', 'style', 'multialignment',
        'axes', 'backgroundcolor', 'alpha', 'rotation', 'ha', 'sketch_params', 'rasterized',
        'ma', 'name', 'path_effects', 'url', 'fontweight', 'lod', 'zorder', 'position',
        'animated', 'bbox'
        )
@texts.decorate(3, "x", "y", "text", "fontdict", "withdash")
def text(x, y, s, **kwargs):
    return get_axes_kw(kwargs).text(x, y, s, **kwargs)
setpfdoc(text, plt.Axes.text.__doc__, "text")





legend = plotfunc.derive(0, "loc", "bbox_to_anchor", "ncol", "prop", "fontsize",
                     "numpoints", "scatterpoints","scatteryoffsets","markerscale",
                     "frameon", "fancybox", "shadow", "framealpha",
                     "mode", "bbox_transform", "title", "borderpad", "labelspacing",
                     "handlelength", "handletextpad", "borderaxespad", "columnspacing",
                     "handler_map"
                     )

@legend.caller
def legend(*args, **kwargs):
    return get_axes_kw(kwargs).legend(*args, **kwargs)
setpfdoc(text, plt.Axes.legend.__doc__, "legend")







#################################################
#
# Others misc plots
#
#################################################
###
# contains y1, ...., to y99 positional arument

#_key(plt.Polygon)
polygon = plotfunc.derive('closed', 'xy', 'fill', 'fc', 'lw', 'ls', 'hatch', 'linewidth', 'antialiased', 'aa',
'facecolor', 'edgecolor', 'joinstyle', 'linestyle', 'alpha', 'ec', 'capstyle', 'color',
'clip_on', 'contains', 'label', 'animated', 'axes', 'sketch_params', 'lod', 'snap',
'figure', 'transform', 'rasterized', 'path_effects', 'agg_filter', 'zorder', 'clip_box',
'picker', 'clip_path', 'visible', 'url', 'gid')


@polygon.decorate(2, "xmin", "xmax", "ymin", "ymax")
def axvspan(xmin, xmax, ymin=0, ymax=1,**kwargs):
    get_axes_kw(kwargs).axvspan(xmin, xmax, ymin, ymax, **kwargs)

@polygon.decorate(2, "ymin", "ymax", "xmin", "xmax")
def axhspan(ymin, ymax, xmin=0, xmax=1,**kwargs):
    get_axes_kw(kwargs).axvspan(ymin, ymax, xmin, xmax, **kwargs)

@polygon.decorate(2, "ymin", "ymax", "xmin", "xmax")
def axspan(value1, value2, axmin=0, axmax=1, **kwargs):


    d =  kwargs.get("direction", "y")
    axes = get_axes_kw(kwargs)
    if d in ['y','Y',0]:
        func = axes.axhspan
    elif d in ['x','X',1]:
        func = axes.axvspan
    else:
        ValueError("direction must be 'y' or 'x' (0 or 1) got '%s'"%d)

    if not hasattr(lines1, "__iter__"):
        lines1 = [lines1]
    if not hasattr(lines2, "__iter__"):
        lines2 = [lines2]
    if len(lines1)!=len(lines2):
        raise ValueError("lines1 and lines2 must have the same length")

    return [func(l1,l2, axmin, axmax, **kwargs) for l1,l2 in zip(lines1, lines2)]









stackplot =fill_between.derive(2,"x","y",*("y%d"%i for i in range(1, 100)))
@stackplot.caller
def stackplot(*args, **kwargs):
    return get_axes_kw(kwargs).stackplot(*args, **kwargs)
setpfdoc(stackplot, plt.Axes.stackplot.__doc__, "stackplot")



#_keys(plt.Annotation, " "*4)
annotations = plotfunc.derive(
    'figure', 'clip_on', 'fontproperties', 'size', 'font_properties', 'x', 'y', 'va',
    'verticalalignment', 'fontvariant', 'weight', 'stretch', 'rotation', 'fontname',
    'fontstretch', 'multialignment', 'fontsize', 'clip_box', 'position', 'bbox',
    'variant', 'ha', 'style', 'backgroundcolor', 'clip_path', 'fontstyle', 'color',
    'rotation_mode', 'text', 'name', 'fontweight', 'linespacing', 'family', 'ma',
    'horizontalalignment', 'contains', 'label', 'animated', 'axes', 'sketch_params',
    'lod', 'snap', 'transform', 'alpha', 'rasterized', 'path_effects', 'agg_filter',
    'zorder', 'picker', 'visible', 'url', 'gid', 'annotation_clip'
    )

annotate = annotations.derive(2, "text", "xy", "xytext", "xycoords", "textcoords",
                   "arrowprops", "width", "frac", "headwidth", "shrink", "arrowstyle",
                   "connectionstyle", "relpos", "patchA", "patchB", "shrinkA",
                   "shrinkB", "mutation_scale", "mutation_aspect")
@annotate.caller
def annotate(*args, **kwargs):
    return get_axes_kw(kwargs).annotate(*args, **kwargs)
setpfdoc(annotate, plt.Axes.annotate.__doc__, "annotate")


annotates = annotate.derive(2, "x", "y", "texts", "dx", "dy")
@annotates.caller
def annotates(x, y, texts=None, dx=0.0, dy=0.0, **kwargs):
    """PlotFunc. Annotate from  x, y, texts arrays

    Args:
        x(array like): the x array coordinate. can be a scalar
        y(array like): the y array coordinate. can be a scalar
        texts(Optional[]): array of string labels. if None, the
            texts will be ["%d"%i for i in range(len(x))]
            Can be also a scalar string (repeated to the len(x))

        dx (Optional[float or sequence]): deltax coordinate for the texts default is 0.0
            if sequence, must of len of x
        dy (Optional[float or sequence]): deltay coordinate for the texts default is 0.0
           x, y, dx and dy overwrite the xy and xytext arg of annotate
           if sequence, must of len of y

        All other arguments are parsed to the annotate frunction.
        Please see the doc of annotate

    """
    if not hasattr(x, "__iter__"):
        x = [x]
    n = len(x)

    if not hasattr(y, "__iter__"):
        y = [y]*n
    elif len(y)!=n :
        raise ValueError("'x' and 'y' sequences must have the same length")

    if texts is None:
        texts = ["%d"%i for i in range(n)]
    elif not hasattr(texts, "__iter__"):
        texts = [texts]*n
    elif len(texts)!=n :
        raise ValueError("'texts' sequence must have the same length than 'x' and 'y'")
    kwargs.pop("xytext", None)
    kwargs.pop("xy", None)

    if not hasattr(dx, "__iter__"):
        dx = [dx]*n
    elif len(dx)!=n:
        raise ValueError("'dx' sequence must have the same length than 'x' and 'y'")


    if not hasattr(dy, "__iter__"):
        dy = [dy]*n
    elif len(dy)!=n:
        raise ValueError("'dy' sequence must have the same length than 'x' and 'y'")



    axes = get_axes_kw(kwargs)
    output = []
    for xi, yi, texti, dxi, dyi in zip(x,y,texts, dx, dy):
        output.append(axes.annotate(texti, (xi,yi), xytext=(xi+dxi, yi+dyi), **kwargs))
    return output
annotates["_example_"] = ("annotates", None)



collections = plotfunc.derive(
    'linestyles', 'offset_position', 'paths', 'offsets', 'lw', 'edgecolor', 'antialiaseds',
    'urls', 'facecolors', 'hatch', 'dashes', 'edgecolors', 'pickradius', 'antialiased',
    'facecolor', 'color', 'linewidths', 'linestyle', 'alpha', 'linewidth', 'clip_on',
    'contains', 'label', 'animated', 'axes', 'sketch_params', 'lod', 'snap', 'figure',
    'transform', 'rasterized', 'path_effects', 'agg_filter', 'zorder', 'clip_box',
    'picker', 'clip_path', 'visible', 'url', 'gid', 'clim', 'array', 'cmap', 'norm',
    'colorbar'
)


# from matplotlib import collections
# _keys(collections.LineCollection, " "*4)
linecollections = plotfunc.derive(
    'verts', 'segments', 'paths', 'color', 'linestyles', 'offset_position', 'offsets',
    'lw', 'edgecolor', 'antialiaseds', 'urls', 'facecolors', 'hatch', 'dashes', 'edgecolors',
    'pickradius', 'antialiased', 'facecolor', 'linewidths', 'linestyle', 'alpha',
    'linewidth', 'clip_on', 'contains', 'label', 'animated', 'axes', 'sketch_params',
    'lod', 'snap', 'figure', 'transform', 'rasterized', 'path_effects', 'agg_filter',
    'zorder', 'clip_box', 'picker', 'clip_path', 'visible', 'url', 'gid', 'clim',
    'array', 'cmap', 'norm', 'colorbar'
)

eventplot = linecollections.derive(1,
            "positions", "orientation", "lineoffsets",
            "linelengths", "linewidths", "colors",
            "linestyles"
            )
@eventplot.caller
def eventplot(*args, **kwargs):
    return get_axes_kw(kwargs).eventplot(*args, **kwargs)
setpfdoc(eventplot, plt.Axes.eventplot.__doc__, "eventplot")
eventplot["_example_"] = ("eventplot", None)



###
#(1,'x', 'explode', 'labels', 'colors','autopct', 'pctdistance',
# 'shadow','labeldistance', 'startangle', 'radius', 'counterclock',
# 'wedgeprops', 'textprops')
pie = plotfunc.derive(*extract_args(plt.Axes.pie.im_func, 1))
@pie.caller
def pie(*args, **kwargs):
    return get_axes_kw(kwargs).pie(*args, **kwargs)
setpfdoc(pie, plt.Axes.pie.__doc__, "pie")


boxplot = plotfunc.derive(*extract_args(plt.Axes.boxplot.im_func, 1))
@boxplot.caller
def boxplot(*args, **kwargs):
    return get_axes_kw(kwargs).boxplot(*args, **kwargs)
setpfdoc(boxplot, plt.Axes.boxplot.__doc__, "boxplot")

bxp = plotfunc.derive(*extract_args(plt.Axes.bxp.im_func, 1))
@bxp.caller
def bxp(*args, **kwargs):
    return get_axes_kw(kwargs).bxp(*args, **kwargs)
setpfdoc(bxp, plt.Axes.bxp.__doc__, "bxp")

# [:-1] to remove the True at the end
hexbin = collections.derive(*extract_args(plt.Axes.hexbin.im_func, 1)[:-1])
@hexbin.caller
def hexbin(*args, **kwargs):
    return get_axes_kw(kwargs).hexbin(*args, **kwargs)
setpfdoc(hexbin, plt.Axes.hexbin.__doc__, "hexbin")

#from matplotlib import patches
#_keys(patches.FancyArrow)
fancyarrows = plotfunc.derive(
    'closed', 'xy', 'fill', 'fc', 'lw', 'ls', 'hatch', 'linewidth', 'antialiased',
    'aa', 'facecolor', 'edgecolor', 'joinstyle', 'linestyle', 'alpha', 'ec', 'capstyle',
    'color', 'clip_on', 'contains', 'label', 'animated', 'axes', 'sketch_params',
    'lod', 'snap', 'figure', 'transform', 'rasterized', 'path_effects', 'agg_filter',
    'zorder', 'clip_box', 'picker', 'clip_path', 'visible', 'url', 'gid'
)

# extract_args( patches.FancyArrow.__init__, 1)
arrow = fancyarrows.derive(4, "x", "y", "vx", "vy", 'width', 'length_includes_head', 'head_width',
                           'head_length', 'shape', 'overhang', 'head_starts_at_zero')

@arrow.caller
def arrow(*args, **kwargs):
    return get_axes_kw(kwargs).arrow(*args, **kwargs)
setpfdoc(arrow, plt.Axes.arrow.__doc__, "arrow")

##
# from matplotlib import collections
# _keys(collections.PolyCollection, " "*4)
polycollections = plotfunc.derive(
    'verts',  'sizes', 'closed', 'paths', 'linestyles', 'offset_position', 'offsets', 'lw',
    'edgecolor', 'antialiaseds', 'urls', 'facecolors', 'hatch', 'dashes', 'edgecolors',
    'pickradius', 'antialiased', 'facecolor', 'color', 'linewidths', 'linestyle',
    'alpha', 'linewidth', 'clip_on', 'contains', 'label', 'animated', 'axes', 'sketch_params',
    'lod', 'snap', 'figure', 'transform', 'rasterized', 'path_effects', 'agg_filter',
    'zorder', 'clip_box', 'picker', 'clip_path', 'visible', 'url', 'gid', 'clim',
    'array', 'cmap', 'norm', 'colorbar'
                                  )
pcolor = polycollections.derive(0, "x", "y", "colors", "cmap", "norm", "vmin", "vmax",
                                "shading", "edgecolors", "alpha", "snap"
                                )

def _get_xyz_args(args, kwargs, x="x", y="y", z="colors"):

    largs = len(args)
    if not largs:
        colors = kwargs.pop(z, None)
        x = kwargs.pop(x,None)
        y = kwargs.pop(y, None)
        if x is None and y is None:
            pass
        elif x is None:
            raise ValueError("got '%s' but not '%s' "%(y,x))
        elif y is None:
            raise ValueError("got '%s' but not '%s' "%(x,y))
        else:
            args = (x,y,colors)
    elif largs==1:
        colors = args[0]
        colors = kwargs.pop(z, None)
        x = kwargs.pop(x,None)
        y = kwargs.pop(y, None)
        if x is None and y is None:
            pass
        elif x is None:
            raise ValueError("got '%s' but not '%s' "%(y,x))
        elif y is None:
            raise ValueError("got '%s' but not '%s' "%(x,y))
        else:
            args = (x,y,colors)

    elif largs>=3:
        colors = kwargs.pop(z, None)
        x = kwargs.pop(x,None)
        y = kwargs.pop(y, None)
    return args, kwargs

def _get_xyzv_args(args, kwargs):
    args, kwargs = _get_xyz_args(args, kwargs, "X", "Y", "Z")
    if len(args)>=4:
        kwargs.pop("contours", None)
    else:
        contours = kwargs.pop("contours", None)
        if contours is not None:
            args = args+(contours,)

    return args, kwargs


@pcolor.caller
def pcolor(*args, **kwargs):
    args, kwargs = _get_xyz_args(args, kwargs)
    return get_axes_kw(kwargs).pcolor(*args, **kwargs)
setpfdoc(pcolor, plt.Axes.pcolor.__doc__, "pcolor")

##
# _keys(collections.QuadMesh, " "*4)
# + extract_args(collections.QuadMesh.__init__, 1)
quadmeshes = plotfunc.derive(3,
    'meshWidth', 'meshHeight', 'coordinates', 'antialiased', 'shading'
    'paths', 'linestyles', 'offset_position', 'offsets', 'lw', 'edgecolor', 'antialiaseds',
    'urls', 'facecolors', 'hatch', 'dashes', 'edgecolors', 'pickradius',
    'facecolor', 'color', 'linewidths', 'linestyle', 'alpha', 'linewidth', 'clip_on',
    'contains', 'label', 'animated', 'axes', 'sketch_params', 'lod', 'snap', 'figure',
    'transform', 'rasterized', 'path_effects', 'agg_filter', 'zorder', 'clip_box',
    'picker', 'clip_path', 'visible', 'url', 'gid', 'clim', 'array', 'cmap', 'norm',
    'colorbar'
 )
pcolormesh = quadmeshes.derive(0, "x", "y", "colors", "cmap", "norm", "vmin", "vmax",
                                "shading", "edgecolors", "alpha")

@pcolormesh.caller
def pcolormesh(*args, **kwargs):
    args, kwargs = _get_xyz_args(args, kwargs)
    return get_axes_kw(kwargs).pcolormesh(*args, **kwargs)
setpfdoc(pcolormesh, plt.Axes.pcolormesh.__doc__, "pcolormesh")

pcolorfast = quadmeshes.derive(0, "x", "y", "colors", "cmap", "norm", "vmin", "vmax",
                                 "alpha")

@pcolorfast.caller
def pcolorfast(*args, **kwargs):
    args, kwargs = _get_xyz_args(args, kwargs)
    return get_axes_kw(kwargs).pcolorfast(*args, **kwargs)
setpfdoc(pcolorfast, plt.Axes.pcolorfast.__doc__, "pcolorfast")


contours = plotfunc.derive("X", "Y", "Z", "contours", "colors", "alpha", "cmap", "norm",
                           "vmin", "vmax", "levels", "origin", "extent","locator",
                           "extend","xunits", "yunits", "antialiased",
                           )
contour = contours.derive("X", "Y", "Z",  "contours", "colors", "linewidths","linestyles")

@contour.caller
def contour(*args, **kwargs):
    args, kwargs = _get_xyzv_args(args, kwargs)
    return get_axes_kw(kwargs).contour(*args, **kwargs)
setpfdoc(contour, plt.Axes.contour.__doc__, "contour")

contourf = contours.derive("X", "Y", "Z", "contours", "colors", "nchunk", "hatches")
@contourf.caller
def contourf(*args, **kwargs):
    args, kwargs = _get_xyzv_args(args, kwargs)
    return get_axes_kw(kwargs).contourf(*args, **kwargs)
setpfdoc(contourf, plt.Axes.contourf.__doc__, "contourf")

hist2d = pcolorfast.derive(2, "x", "y", "bins", "range", "normed", "weights",
                           "cmin", "cmax")

# remove the colors kwargs
a = list(hist2d.args);  a.remove("colors")
hist2d.args = tuple(a)
@hist2d.caller
def hist2d(*args, **kwargs):
    return get_axes_kw(kwargs).hist2d(*args, **kwargs)
setpfdoc(hist2d, plt.Axes.hist2d.__doc__, "hist2d")




class _BaseFigAxes(object):
    """ just a colection of usefull axes/figure
    for other plots
    """
    aclear = aclear
    fclear = fclear
    aset = aset
    fset = fset
    show = show
    draw = draw
    legend = legend
    grid = grid
    def get_axes(self):
        """ Return the matplotlib axes linked """
        return get_axes(self.get("axes", None), self.get("figure", None))
    def get_figure(self):
        """ Return the matplotlib figure linked """
        return get_figure(self.get("figure", None), self.get("axes", None))
    @property
    def axes(self):
        return self.get_axes()
    @property
    def figure(self):
        return self.get_figure()








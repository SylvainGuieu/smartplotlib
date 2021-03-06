from __future__ import division, absolute_import, print_function

from .base import PlotFunc, PlotFactory
from .recursive import popargs, KWS, extract_args, alias

import matplotlib.pyplot as plt
from matplotlib.axis import Axis as pltAxis
import numpy as np
import os # for savefig

__all__ = ["get_axes", "get_figure", "axes", "fset", "show", "fclear",
           "draw", "aclear", "grid", "plot", "lines", "errorbar", "scatter",
           "vlines", "axvline", "hlines", "axhline", "streamplot", "hist",
           "fill_between", "tables", "table", "texts", "text", "legend",
           "plot_axes_classes", "axhspan", "axvspan", "axspan", "bar", "step",
           "annotate", "annotates", "eventplot", "loglog", "semilogx", "semilogy",
           'hexbin', 'savefig', 'stackplot', 'quadmeshes', 'contourf', 'clf', 'cla',
           'collections', 'annotations', 'rectangle', 'plot_date', 'artist', 'bxp',
           'boxplot', 'adjust', 'pcolormesh', 'arrow', 'axline', 'fancyarrows',
           'line2d', 'contour', 'histx2y', 'histx2x', 'stem', 'patches', 'fill_betweeny',
           'fill_betweenx', 'plotfunc', 'histy2x', 'histy2y', 'imshow', 'pcolor', 'contours',
           'pie', 'linecollections', 'hist2d', 'colorbar', 'pcolorfast', 'polycollections',
           'fillstep', 'matshow', 'polygon', 'fill']


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
            fig = plt.figure(name)
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

def get_axis(axis="x", axes=None, figure=None):
    if isinstance(axis, pltAxis):
        return axis
    axes = get_axes(axes, figure)
    if axis in ["X", "x", "horizontal", 0]:
            return axes.xaxis
    if axis in ["Y", "y", "vertical" , 1]:
            return axes.yaxis
    raise TypeError("wrong axis parameter should be Axis instance, 'x' or 'y' got '%s'"%axis)

def get_axes_kw(kwargs):
    return get_axes(kwargs.pop("axes", None),
                    kwargs.pop("figure",None),
                    colect_axes_kwargs(kwargs)
                    )

def get_figure_kw(kwargs):
    return get_figure(kwargs.pop("figure", None), kwargs.get("axes",None))


def get_axis_kw(kwargs):
    return get_axis(kwargs.pop("axis", None),
                    kwargs.pop("axes", None),
                    kwargs.pop("figure",None))

def get_axis_kw2(axis, kwargs):
    return get_axis(axis,
                    kwargs.pop("axes", None),
                    kwargs.pop("figure",None))



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
axes_short_kws = dict(axisbg="axis_bgcolor",
                      bgcolor="axis_bgcolor",
                      facecolor="axis_bgcolor",
                      frameon="frame_on")

axes = plotfunc.duplicate('figure', 'axes', "sharex", "sharey",
        'picker', 'adjustable', 'cursor_props', 'yscale', 'navigate', 'clip_box',
        'transform', 'xscale', 'aspect', 'axis_bgcolor', 'ylim', 'clip_on', 'xlim',
        'axis_on', 'title', 'contains', 'clip_path', 'axis_off', 'xticks', 'ylabel',
        'autoscalex_on', 'xlabel', 'rasterization_zorder', 'axes_locator', 'subplotspec',
        'agg_filter', 'axisbelow', 'frame_on', 'navigate_mode', 'snap', 'autoscaley_on',
        'autoscale_on', 'alpha', 'ybound', 'yticklabels', 'rasterized', 'xmargin',
        'path_effects', 'sketch_params', 'color_cycle', 'lod', 'zorder', 'xbound',
        'yticks', 'ymargin', 'position', 'animated', 'anchor', 'xticklabels',
        'axis', *(axes_short_kws.keys())
        )

@axes.caller
def axes(axes=None, figure=None, sharex=None, sharey=None, **kwargs):
    name = kwargs.pop("name", None)
    axes = get_axes(axes, figure, colect_axes_kwargs(kwargs))

    if name:
        axes.id = name
    for short, real in axes_short_kws.iteritems():
        if short in kwargs:
            kwargs.setdefault(real,kwargs.pop(short))

    axes.set(**kwargs)
    return axes
setpfdoc(axes, plt.Axes.set.__doc__, "set")


axes2 = plotfunc.duplicate('figure', 'axes',
        'picker', 'adjustable', 'cursor_props',  'navigate', 'clip_box',
        'transform', 'aspect', 'axis_bgcolor', 'ylim', 'clip_on', 'xlim',
        'axis_on', 'title', 'contains', 'clip_path', 'axis_off', 'xticks', 'ylabel',
        'autoscalex_on', 'xlabel', 'rasterization_zorder', 'axes_locator', 'subplotspec',
        'agg_filter', 'axisbelow', 'frame_on', 'navigate_mode', 'snap', 'autoscaley_on',
        'autoscale_on', 'alpha', 'ybound', 'yticklabels', 'rasterized', 'xmargin',
        'path_effects', 'sketch_params', 'color_cycle', 'lod', 'zorder', 'xbound',
        'yticks', 'ymargin', 'position', 'animated', 'anchor', 'xticklabels',
        'axis', *(axes_short_kws.keys())
        )




###
# plotfunc to set axis
_axis = plotfunc.duplicate(
    'view_interval', 'default_intervals', 'ticks_position', 'label_position', 'data_interval',
    'tick_params', 'units', 'label_coords', 'scale', 'smart_bounds', 'major_locator',
    'minor_formatter', 'major_formatter', 'minor_locator', 'label_text', 'ticks',
    'pickradius', 'clip_path', 'ticklabels', 'clip_on', 'contains', 'label', 'animated',
    'axes', 'sketch_params', 'lod', 'snap', 'figure', 'transform', 'alpha', 'rasterized',
    'path_effects', 'agg_filter', 'zorder', 'clip_box', 'picker', 'visible', 'url',
    'gid'
    )

@_axis.decorate(1,"axis", axis="both")
def axis(axis,  **kwargs):
    """ Set default parameters to x, y or both axis """
    axes = kwargs.pop("axes", None)
    figure = kwargs.pop("figure", None)
    if axis in ["both"]:
        axes = get_axes(axes, figure)
        axes.xaxis.set(**kwargs)
        axes.yaxis.set(**kwargs)
        return
    get_axis(axis, axes, figure).set(**kwargs)

xaxis = _axis.derive(axis="x")
setpfdoc(xaxis, "Set parameters to the xaxis", "xaxis")
yaxis = _axis.derive(axis="y")
setpfdoc(yaxis, "Set any parameters to the yaxis", "yaxis")

tick = plotfunc.duplicate(
                           "axis", "reset", "which", "direction", "length", "width",
                           "color", "pad", "labelsize", "labelcolor", "colors", "zorder",
                           "bottom", "top", "left", "right",
                           "labelbottom","labeltop","labelleft","labelright"
                           )
@tick.caller
def tick(**kwargs):
    axes = get_axes_kw(kwargs)
    return axes.tick_params(**kwargs)
setpfdoc(tick, plt.Axes.tick_params.__doc__, "tick")


spine = plotfunc.duplicate(1, 'where',
    'bounds', 'patch_circle', 'position', 'patch_line', 'smart_bounds', 'color',
    'fill', 'fc', 'lw', 'ls', 'hatch', 'linewidth', 'antialiased', 'aa', 'facecolor',
    'edgecolor', 'joinstyle', 'linestyle', 'alpha', 'ec', 'capstyle', 'clip_on',
    'contains', 'label', 'animated', 'axes', 'sketch_params', 'lod', 'snap', 'figure',
    'transform', 'rasterized', 'path_effects', 'agg_filter', 'zorder', 'clip_box',
    'picker', 'clip_path', 'visible', 'url', 'gid'
                           )
@spine.caller
def spine(where=["top", "bottom", "left", "right"],
          *args, **kwargs):
    axes = get_axes_kw(kwargs)
    if isinstance (where, basestring):
        s = axes.spines[where]
        s.set(*args, **kwargs)
        return s
    else:
        output = []
        for w in where:
            s = axes.spines[w]
            s.set(*args, **kwargs)
            output.append(s)
        return output


figure_short_kws = dict(size='size_inches',
                        bgcolor='facecolor',
                        figure_bgcolor='facecolor'
                        )
figure = plotfunc.duplicate('figure', 'axes',
        'picker', 'edgecolor', 'clip_on', 'clip_box', 'transform',
        'canvas', 'facecolor', 'lod', 'size_inches', 'contains', 'clip_path', 'figwidth',
        'snap', 'agg_filter', 'figheight', 'alpha', 'tight_layout', 'rasterized',
        'path_effects', 'sketch_params', 'frameon', 'zorder', 'animated', 'dpi',
        *(figure_short_kws.keys())
        #"sp_left", "sp_bottom", "sp_right", "sp_top", "sp_wspace", "sp_hspace",
        #"wspace", "hspace",
        )


@figure.caller
def figure(figure=None, axes=None, **kwargs):
    fig = get_figure(figure, axes)

    for short, real in figure_short_kws.iteritems():
        if short in kwargs:
            kwargs.setdefault(real,kwargs.pop(short))

    if len(kwargs):
        fig.set(**kwargs)

    return fig
setpfdoc(figure, plt.Figure.set.__doc__, "figure")
_fset = figure

suptitle = plotfunc.duplicate(1, 'suptitle',('x',"__"),('y',"__"),'horizontalalignment', 'verticalalignment')
@suptitle.caller
def suptitle(*args,  **kwargs):
    fig = get_figure(kwargs.pop("figure",None),kwargs.pop("axes",None) )
    return fig.suptitle(*args,**kwargs)


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


@plotfunc.decorate(0, "scale", "base", "subs", "nonpos", "linthresh", "linscale", "axis")
def scale(scale="linear", **kwargs):
    axis = kwargs.pop("axis", "both")
    axes = get_axes_kw(kwargs)

    args = "base", "subs", "nonpos", "linthresh", "linscale"
    if axis in ("X","x",0,"both",None):
        d = {k+"x":kwargs[k] for k in args if k in kwargs}
        axes.set_xscale(scale, **d)
    if axis in ("Y","y",1,"both",None):
        d = {k+"y":kwargs[k] for k in args if k in kwargs}
        axes.set_yscale(scale, **d)


@plotfunc.decorate()
def aclear(axes=None, figure=None):
    """ clear the axes

    Parameters:
        figure : figure id or object get the first axes if axes is None
        axes   : axes object axes or number or tuple
    """
    return get_axes(axes, figure).clear()
cla = aclear




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
        # ax can be a list of figures
        if hasattr(ax, "__iter__") and not isinstance(ax, tuple):
            f = kwargs.get("figure",None)
            kwargs["ax"] = [get_axes(a,f) for a in ax]
        else:
            kwargs["ax"] = get_axes(ax, kwargs.get("figure",None))

    return get_figure_kw(kwargs).colorbar(*args, **kwargs)


savefig = plotfunc.derive(1,
           "fname", "dpi", "facecolor", "edgecolor",
           "orientation", "papertype", "format",
           "transparent", "bbox_inches", "pad_inches",
           "frameon", "version", "directory", "extention", 
           "verbose", "indexfile", "disabled"
          )
@savefig.caller
def savefig(fname, *args, **kwargs):
    if  kwargs.pop("disabled", False):
        return ''

    version   = kwargs.pop("version", None)
    directory = kwargs.pop("directory", None)
    extention = kwargs.pop("extention", None)
    verbose   = kwargs.pop("verbose", False)
    index = kwargs.pop("indexfile",None)


    if not isinstance(fname, basestring):
        raise ValueError("fname must be a string got a '%s'"%type(fname))
    direc, fname = os.path.split(fname)
    if not direc and directory:
        direc = directory

    name, ext = os.path.splitext(fname)
    ext.lstrip('.')
    if not ext in ['eps', 'jpeg', 'jpg', 'pdf', 'pgf', 'png', 'ps', 'raw', 'rgba', 'svg', 'svgz', 'tif', 'tiff']:
        if extention:
            ext = extention.lstrip(".")
        else:
            name += "."+ext # not a figure extention, put it back to name
            ext = None

    fname = os.path.join(direc, name+(version if version is not None else '')+("."+ext if ext else ''))   

    out = get_figure_kw(kwargs).savefig(fname, *args, **kwargs)
    if verbose:
        print("Figure saved at '%s'"%fname)

    if index:
        index.write("%s\n"%fname)    
    return out            
setpfdoc(savefig, plt.Figure.savefig.__doc__, "savefig")


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

@line2d.decorate(("state","grid"), "which", "axis")
def grid(state=None,  **kwargs):
    if state==None and not len(kwargs):
        state = False
    return get_axes_kw(kwargs).grid(state,   **kwargs)
setpfdoc(grid, plt.Axes.grid.__doc__, "grid")



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
setpfdoc(step, plt.Axes.step.__doc__, "step")


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


linestyle_lookup = {
    '-'  :  "solid",
    '--' : "dashed",
    '-.' :  "dashdot",
    ':'  :  "dotted"
}
bad_linestyles = ['.',',','o','v','^','<','>','1','2','3','4',
                   's','p','*','h','H','+','x','D','d','|','_'
                 ]
xymarker = sum((["x%d"%i,"Y%d"%i, "marker%d"%i] for i in range(1,10)), [])
@patches.decorate(2,"x","y", "marker", *xymarker)
def fill(*args, **kwargs):
    if "linestyle" in kwargs:
        # curiously matplotlib linestyle does not
        # accept linetyle = ":", change it.
        # if it is one of marker style remove it and
        # leave it to default.
        ls = kwargs.get("linestyle")
        if ls in bad_linestyles:
            kwargs.pop(linestyle)
        else:
            kwargs["linestyle"] = linestyle_lookup.get(ls,ls)

    for i in range(1,10):
        x,y,m = (kwargs.pop("x%d"%i,None),
                 kwargs.pop("y%d"%i,None),
                 kwargs.pop("marker%d"%i, None))
        if (x,y,m) != (None,None,None):
            args+=(x,y,m)
    return get_axes_kw(kwargs).fill(*args, **kwargs)
setpfdoc(fill, plt.Axes.fill.__doc__, "fill")

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
        'family', 'agg_filter', 'fontsize', 'variant', 'textstyle', 'multialignment',
        'axes', 'backgroundcolor', 'alpha', 'rotation', 'ha', 'sketch_params', 'rasterized',
        'ma', 'name', 'path_effects', 'url', 'fontweight', 'lod', 'zorder', 'position',
        'animated', 'bbox'
        )
@texts.decorate(3, "x", "y", "text", "fontdict", "withdash")
def text(x, y, s, **kwargs):
    return get_axes_kw(kwargs).text(x, y, s, **kwargs)
setpfdoc(text, plt.Axes.text.__doc__, "text")

@texts.decorate(1, "textobj")
def textset(textobj, **kwargs):
    """ PlotFunc. Set all parameters to a text object *textobj* """
    return textobj.set(**kwargs)

@texts.decorate(1, "textlist")
def textsset(textlist, **kwargs):
    """ PlotFunc. Set all parameters to a list of text object *textlist* """
    for textobj in textlist:
        textobj.set(**kwargs)

@texts.decorate(1, "axis", "which")
def ticklabels(axis, **kwargs):
    """ PlotFunc. Set all parameters to all tick labels of axis *axis* """
    if axis is "both":
        return ticklabels("x", **kwargs)+ticklabels("y", **kwargs)

    axis = get_axis_kw2(axis, kwargs)
    labels = axis.get_ticklabels(which=kwargs.pop("which"))

    if not len(kwargs):
        return labels
    for textobj in labels:
        textobj.set(**kwargs)
    return labels

@texts.decorate(("text","label"), "fontdict", "labelpad", "axis", "xlabel", "ylabel")
def label(text=None,  fontdict=None, labelpad=None,
          axis=None, xlabel=None, ylabel=None, **kwargs):
    """ PlotFunc. Set all parameters to all tick labels of axis *axis* """

    if axis in ("both", None):
        return [label("x", text, fontdict=fontdict,
                      labelpad=labelpad, xlabel=xlabel,
                      **kwargs),
                label("y", text, fontdict=fontdict,
                      labelpad=labelpad, ylabel=ylabel,
                      **kwargs)]
    if text is None:
        if axis in ("x", "X", 0):
            text = xlabel
        elif axis in ("y", "Y", 1):
            text = ylabel


    axis  = get_axis_kw2(axis, kwargs)
    if labelpad is not None:
        axis.labelpad = labelpad

    label = axis.label
    if fontdict is not None:
            axis.label.update(fontdict)
    axis.isDefault_label = False


    if text is not None:
        label.set_text(text)
    label.update(kwargs)
    return label

@texts.decorate(("text","title"), "fontdict", "loc", "title_offset")
def title(text=None,  fontdict=None, loc="center", title_offset=(0.0,0.0), **kwargs):
    if text is None:
        return None
    t =  get_axes_kw(kwargs).set_title(text, fontdict, loc, **kwargs)
    pos = t.get_position()
    t.set_position( (pos[0]+title_offset[0], pos[1]+title_offset[1]))
    return t

@label.decorate("xlabel", axis="x")
def xlabel(*args,**kwargs):
    return label(*args, **kwargs)

@label.decorate("ylabel", axis="y")
def ylabel(*args,**kwargs):
    return label(*args, **kwargs)


@line2d.decorate(1, "axis", "which", "where")
def ticklines(axis,**kwargs):
    if axis is "both":
        return ticklines("x", **kwargs)+ticklines("y", **kwargs)

    axis = get_axis_kw2(axis, kwargs)

    lines = axis.get_ticklines(kwargs.pop("which","major")=="minor")

    pos = kwargs.pop("where", None)
    if pos:
        if pos in ("default",):
            lines = lines[::2]
        elif pos in ("opposite",):
            lines = lines[1::2]
        elif axis.axis_name in ("X","x", 0):
            if pos in ["top", "t"]:
                lines = lines[1::2]
            elif pos in ["bottom", "b"]:
                lines = lines[::2]
            else:
                raise ValueError("with axis='x', where should be one of 'top', 'bottom', 'default', 'opposite', got '%s'"%pos)
        elif axis.axis_name in ("Y","y", 1):
            if pos in ["right", "r"]:
                lines = lines[1::2]
            elif pos in ["left", "l"]:
                lines = lines[::2]
            else:
                raise ValueError("with axis='y', where should be one of 'right', 'left', 'default', 'opposite', got '%s'"%pos)
        else:
            raise ValueError("where should be one of 'top', 'bottom', right', 'left', 'default', 'opposite', got '%s'"%pos)
    if not len(kwargs):
        return lines

    for l in lines:
        l.set(**kwargs)
    return lines

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
setpfdoc(legend, plt.Axes.legend.__doc__, "legend")







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
setpfdoc(axvspan, plt.Axes.axvspan.__doc__, "axvspan")

@polygon.decorate(2, "ymin", "ymax", "xmin", "xmax")
def axhspan(ymin, ymax, xmin=0, xmax=1,**kwargs):
    get_axes_kw(kwargs).axvspan(ymin, ymax, xmin, xmax, **kwargs)
setpfdoc(axhspan, plt.Axes.axhspan.__doc__, "axhspan")

@polygon.decorate(2, "ymin", "ymax", "xmin", "xmax")
def axspan(value1, value2, axmin=0, axmax=1, **kwargs):
    """ PlotFunc. This a nonymous version of axvspan/axhspan

    the plot direction if handled by the 'direction' parameter.
    if "y" -> axhspan if "x" -> axvspan.

    Args:
        value1 : first value in 'direction'
        value2 : second value in 'direction'
        axmin, axmax (Optional) : min and max in axes coordinate in the oposite
            'direction'

    """
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






# counter = 0
# class Tick(PlotFactory):
#     lines = ticklineset
#     labels = ticklabelset

#     _tickset = tickset
#     @staticmethod
#     def finit(p, **kwargs):
#         p.set(**kwargs)
#     def set(self, **kwargs):
#         global counter
#         print (counter)
#         counter += 1
#         self.update(kwargs.pop(KWS,{}), **kwargs)
#         self._tickset()
#         self.lines()
#         self.labels()

# tick = Tick()

# class XYTick(PlotFactory):
#     default = bottom
#     opposite = top
#     @staticmethod
#     def finit(p, **kwargs):
#         p.set(**kwargs)
#     def set(self, **kwargs):
#         self.update(kwargs.pop(KWS,{}), **kwargs)
#         self.default()
#         self.opposite()

# class XTick(XYTick):
#     top = tick.derive(where="top")
#     bottom = tick.derive(where="bottom")
#     default = bottom
#     opposite = top
# xtick = XTick(axis="x")

# class YTick(XYTick):
#     left = tick.derive(where="left")
#     right = tick.derive(where="right")
#     default = left
#     opposite = right
# ytick = YTick(axis="y")



# class SubTick(PlotFactory):
#     x = xtick
#     y = ytick
#     @staticmethod
#     def finit(p, **kwargs):
#         p.set(**kwargs)
#     def set(self, **kwargs):
#         self.update(kwargs.pop(KWS,{}), **kwargs)
#         self.x()
#         self.y()

# class Ticks(PlotFactory):
#     major = SubTick(which="major")
#     minor = SubTick(which="minor")
#     x = major.x
#     y = major.y

#     @staticmethod
#     def finit(p, **kwargs):
#         p.set(**kwargs)
#         #p.update(kwargs.pop(KWS,{}), **kwargs)

#     def set(self, **kwargs):
#         self.update(kwargs.pop(KWS,{}), **kwargs)
#         self.major()
#         self.minor()
# ticks = Ticks()

# class ATicks(PlotFactory):
#     major = SubTick(which="major")
#     minor = SubTick(which="minor")
#     x = major.x
#     y = major.y

#     @staticmethod
#     def finit(p, **kwargs):
#         p.set(**kwargs)
#         #p.update(kwargs.pop(KWS,{}), **kwargs)

#     def set(self, **kwargs):
#         self.update(kwargs.pop(KWS,{}), **kwargs)
#         self.major()
#         self.minor()


# def _special_prepare(special_def, kwargs):
#     specials = {}
#     for func, sk, kd in special_def:
#         kw = kwargs.pop(kd, {} )
#         ls = len(sk)
#         kw.update({k[ls:]:kwargs.pop(k) for k in kwargs.keys() if k[0:ls] == sk})
#         specials[func] = kw
#     return specials

# class Axis(PlotFactory):
#     axisset = axisset
#     ticklabel = ticklabelset
#     label = labelset
#     ticks = ticks
#     @staticmethod
#     def finit(p, **kwargs):
#         #p.update(kwargs.pop(KWS,{}), **kwargs)
#         p.set(**kwargs)
#     def set(self, **kwargs):
#         self.update(kwargs.pop(KWS,{}), **kwargs)

#         specials = _special_prepare(
#                 [(self.ticklabel, "tl_", "ticklabels"),
#                  (self.label, "l_", "labels"),
#                  (self.ticks, "t_", "ticks")
#                 ],
#             kwargs
#             )

#         self.axisset()
#         for func, kw in specials.iteritems():
#             func(axes=axes, **kw)

#     @property
#     def axis(self):
#         return get_axis(self.get("axis","x"),
#                  self.get("axes",None),
#                  self.get("figure",None)
#                  )
# axis = Axis()

# class XYAxis(PlotFactory):
#     x = axis.derive(axis="x")
#     y = axis.derive(axis="y")

#     @staticmethod
#     def finit(p, **kwargs):
#         p.set(**kwargs)
#         #p.update(kwargs.pop(KWS,{}), **kwargs)

#     def set(self, **kwargs):
#         self.update(kwargs.pop(KWS,{}), **kwargs)
#         self.x()
#         self.y()
# axis = XYAxis()
# xaxis = axis.x
# yaxis = axis.y


def fset(plots, *args, **kwargs):
    plots = plots.derive()
    specials = _special_prepare([(plots.adjust, "a_", "adjust")], kwargs)
    for func, sk, kd in special_def:
        kw = kwargs.pop(kd, {} )
        ls = len(sk)
        kw.update({k[ls:]:kwargs.pop(k) for k in kwargs.keys() if k[0:ls] == sk})
        specials[func] = kw


    plots.update(kwargs.pop(KWS, {}), **kwargs)
    plots._fset()
    fig = plots.figure
    suptitle = plots.get("suptitle", None)
    if suptitle:
        fig.suptitle(suptitle)



    for func, kw in specials.iteritems():
        func(axes=axes, **kw)







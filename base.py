from __future__ import division, absolute_import, print_function

from .recursive import RecObject, RecFunc
from .stack import stack
import inspect

class Plot(RecObject):
    _unlinked = tuple()#("go","_go_results")
    _default_params = {"go":None, "_go_results":None, "_example_":None}
    _example = None
    def goifgo(self):
        go = self.get("go",False)
        if go:
            if go is True:
                self["_go_results"] = self.go("-")
                return
            if hasattr(go,"__iteritems__"):
                self["_go_results"] = self.go(*go)
                return
            self["_go_results"] = self.go(go)
            return

    def _get_direction(self):
        d = self.get("direction","y")
        if d in ["y", "Y", 0]:
            return "x", "y"
        if d in ["x", "X", 1]:
            return "y", "x"
        raise ValueError("direction paramter must be one of 'y',0,'x',1  got '%s'"%d)

    @property
    def example(self):
        ex = self.get("_example_", None)
        if ex:
            return get_example(*ex)

    def __add__(self, right):
        if not isinstance( right, (Plot,PlotFunc,stack)):
            raise TypeError("can add a plot only to a plot, plotfunc or stack (not '%s') "%(type(right)))
        return stack([self, right])

class PlotFunc(RecFunc):
    @property
    def example(self):
        ex = self.get("_example_", None)
        if ex:
            return get_example(*ex)

    def __add__(self, right):
        if not isinstance( right, (Plot,PlotFunc,stack)):
            raise TypeError("can add a plotfunc only to a plot, plotfunc or stack (not '%s') "%(type(right)))
        return stack([self, right])


def get_example(name, module=None):
    if module is None:
        from . import examples as module
    else:
        try:
            import importlib
            base = __name__.split(".",1)[0]
            module = importlib.import_module(base+"."+module)
        except Exception as e:
            return """raise TypeError('cannot load example "%s", "%s"')"""%(name,e)

    try:
        func= getattr(module, name)
    except AttributeError:
        return """raise TypeError('cannot find example "%s"')"""%name

    source = inspect.getsource(func).replace("def %s"%name, "def %s_ex"%name)
    source += "\n"+"_ = %s_ex()"%name+"\n"
    return source




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

    if isinstance(axes, plot_axes_classes):
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
            TypeError("Expecting a 2 tuple for figure got '%s'"%tpl)

        if isinstance(tpl[0], basestring):
            name, fig = tpl
            fig = figure(name)
        else:
            fig = get_figure(None, axes)

        if len(tpl)!=2:
            TypeError("Expecting a 2 tuple for figure got '%s'"%tpl)

        nrows, ncols = tpl
        gs = GridSpec(nrows, ncols)
        for i in range(nrows*ncols):
            fig.add_subplot(gs[i // ncols, i % ncols])
        return fig

    return plt.figure(fig)


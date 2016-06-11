from . import plotfuncs as pfs
from .base import PlotFactory, CatRecObject, KWS, PlotFunc, rproperty
pltAxis = pfs.pltAxis

class SetFactory(PlotFactory):
    @staticmethod
    def finit(p, **kwargs):
        p.set(**kwargs)  

    def _axis_args(self, *lst):
        axis = self.get("axis",None)
        if axis is None:
            return None
        if isinstance(axis, pltAxis):
            ax = axis.axis_name                
        elif axis in ("x","X",0):
            ax = "x"
        elif axis in ("y","Y",1):
            ax = "y"    
        for p in lst:
            if (ax+p) in self:
                self[p] = self.get(ax+p)                    
        return ax        

class CatSet(CatRecObject):
    def __call__(self, *args, **kwargs):
        return [child(*args, **kwargs) for child in self]

    def __getattr__(self, attr):
        lst = [getattr(child,attr) for child in self ]
        if len(lst) and isinstance(lst[0], (PlotFactory, PlotFunc, CatRecObject)):
            return self.__class__(lst)
        return lst                    


class Tick(SetFactory):
    lines  = pfs.ticklines
    labels = pfs.ticklabels
    _set = pfs.tick
    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)
        self._set()        
        self.lines()
        self.labels()

class AnonymousTick(SetFactory):
    default  = Tick(where="default")
    opposite = Tick(where="opposite")

    @rproperty
    def lines(self):
        return CatSet(self["(default,opposite).lines"])

    @rproperty
    def labels(self):
        return CatSet(self["(default,opposite).labels"])
    
    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)
        self.default()
        self.opposite()

class XTick(AnonymousTick):
    @rproperty
    def bottom(self):
        return self.default
    @rproperty
    def top(self):
        return self.opposite  

class YTick(AnonymousTick):
    @rproperty
    def left(self):
        return self.default
    @rproperty
    def right(self):
        return self.opposite        

class XYTick(SetFactory):
    x = XTick(axis="x")
    y = YTick(axis="y")
    top = x.top
    bottom = x.bottom
    left  = y.left
    right = y.right
    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)                
        self.x()
        self.y()

class Ticks(SetFactory):
    major = AnonymousTick(which="major")
    minor = AnonymousTick(which="minor")

    
    @rproperty
    def lines(self):
        return CatSet(self["major.(default,opposite).lines"])       

    @rproperty
    def labels(self):
        return CatSet(self["major.(default,opposite).labels"])       

    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)
        self.major()
        self.minor()        
ticks = Ticks()

class Labels(SetFactory):
    x = pfs.xlabel
    y = pfs.ylabel
    def set(self, **kwargs):
        axis = kwargs.pop("axis", None)
        self.update(kwargs.pop(KWS,{}), **kwargs)

        if axis in ("X", "x", 0, None, "both"):
            self.x()
        if axis in ("Y", "y", 1, None, "both"):
            self.y()    
labels = Labels()


def _remove_args(pf, *removes):
    args = list(pf.args)
    for remove in removes:
        args.remove(remove)
    pf.args = tuple(args)     
    return pf

class AnonymousAxis(SetFactory):
    label = pfs.label
    ticks = ticks
    _set = _remove_args(pfs.axis.derive(), "label", "scale")

    major = ticks.major
    minor = ticks.minor
    scale = pfs.scale

    @rproperty
    def ticklines(self):
        return CatSet(self["ticks.major.(default,opposite).lines"])       

    @rproperty
    def ticklabels(self):
        return CatSet(self["ticks.major.(default,opposite).labels"])       

    def set(self, **kwargs):
        which = kwargs.pop("which", None)
        where = kwargs.pop("where", None)

        self.update(kwargs.pop(KWS,{}), **kwargs)
        axis  = self.get("axis", None)
        if where in ("top", "bottom"):
            if axis is None:
                axis = "x"
            elif  axis not in ("x", "X", 0):
                raise ValueError("incompatible keywords axis='%s' and where='%s'"%(axis, where))

        if where in ("right", "left"):
            if axis is None:
                axis = "y"
            elif  axis not in ("y", "Y", 1):
                raise ValueError("incompatible keywords axis='%s' and where='%s'"%(axis, where))


        ax = self._axis_args("label", "scale")            

        self._set()

        self.label()
        
        self.ticks()
        self.scale()        

xaxis = AnonymousAxis(axis="x")
yaxis = AnonymousAxis(axis="y")


class Axis(SetFactory):
    x = xaxis
    y = yaxis

    top    = x.ticks.major.default
    bottom = x.ticks.major.opposite
    left   = y.ticks.major.default
    right  = y.ticks.major.opposite

    xscale = x.scale
    yscale = y.scale

    @rproperty
    def majors(self):
        return CatSet(self["(x,y).ticks.major"])

    @rproperty
    def minors(self):
        return CatSet(self["(x,y).ticks.minor"])

    @rproperty
    def ticks(self):
        return CatSet(self["(x,y).ticks.major"])        

    @rproperty
    def ticklines(self):
        return CatSet(self["(x,y).ticks.major.(default,opposite).lines"])       

    @rproperty
    def ticklabels(self):
        return CatSet(self["(x,y).ticks.major.(default,opposite).labels"])       

    @rproperty
    def labels(self):
        return CatSet(self["(x,y).label"])
        
    @rproperty
    def tops(self):
        return CatSet(self["x.ticks.(major,minor).opposite"])

    @rproperty
    def bottoms(self):
        return CatSet(self["x.ticks.(major,minor).default"])

    @rproperty
    def rights(self):
        return CatSet(self["y.ticks.(major,minor).opposite"])

    @rproperty
    def lefts(self):
        return CatSet(self["y.ticks.(major,minor).default"])
    

    def set(self, **kwargs):
        which = kwargs.pop("which", None)
        where = kwargs.pop("where", None)
        axis  = kwargs.pop("axis", None)

        if where in ("top", "bottom"):
            if  axis not in ("x", "X", 0, None):
                raise ValueError("incompatible keywords axis='%s' and where='%s'"%(axis, where))

        if where in ("right", "left"):
            if  axis not in ("y", "Y", 1, None):
                raise ValueError("incompatible keywords axis='%s' and where='%s'"%(axis, where))


        self.update(kwargs.pop(KWS,{}), **kwargs)


        short_kws = ["label", "lim", "scale"]
        if axis in ("x", "X", 0, None, "both"):                                  
            self.x(which=which, where=where)
        if axis in ("y", "Y", 1, None, "both"):
            self.y(which=which, where=where)    

bothaxis = Axis()


class Grid(SetFactory):
    major = pfs.grid.derive(which="major")
    minor = pfs.grid.derive(which="minor")
    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)

        axis = self.get("axis",None)
        if axis in ("x", "X", 0):
            mg = ["xgrid"]
        elif axis in ("y", "Y", 0):
            mg = ["ygrid"]    
        else:
            mp = []    
        majorgrid = None
        for k in mg+["grid", "majorgrid", "state"]:
            majorgrid = self.get(k,None)
            if majorgrid is not None:
                break
        else:
            majorgrid = False

        if majorgrid:    
            self.major(True)
        if self.get("minorgrid", False):
            self.minor()


class Grids(SetFactory):
    x = Grid(axis="x")
    y = Grid(axis="y")
    @rproperty
    def majors(self):
        return self["(x,y).major"]
    @rproperty
    def minors(self):
        return self["(x,y).minor"]            
    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)
        self.x()
        self.y()

grids = Grids()

class Spines(SetFactory):
    top    = pfs.spine.derive(where="top")
    bottom = pfs.spine.derive(where="bottom")
    left   = pfs.spine.derive(where="left")
    right  = pfs.spine.derive(where="right")       
    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)
        self.top()
        self.bottom()
        self.left()
        self.right()
spines = Spines()


class Log(SetFactory):
    x = pfs.semilogx
    y = pfs.semilogy
    def set(self, **kwargs):
        self.update(kwargs.pop(KWS,{}), **kwargs)



class Axes(Axis):

    _default_params = dict(
                           PlotFactory._default_params, 
                           __inerit__ = {
        'figure', 'axes', "sharex", "sharey",     
        'picker', 'adjustable', 'cursor_props', 'yscale', 'navigate', 'clip_box',
        'transform', 'xscale', 'scale', 'aspect', 'axis_bgcolor','bgcolor', 'ylim', 'clip_on', 'xlim',
        'axis_on', 'title', 'title_offset','contains', 'clip_path', 'axis_off', 'xticks', 'ylabel',
        'autoscalex_on', 'xlabel', 'rasterization_zorder', 'axes_locator', 'subplotspec',
        'agg_filter', 'axisbelow', 'frame_on', 'navigate_mode', 'snap', 'autoscaley_on',
        'autoscale_on', 'ybound', 'yticklabels', 'rasterized', 'xmargin',
        'path_effects', 'sketch_params', 'color_cycle', 'lod', 'zorder', 'xbound',
        'yticks', 'ymargin', 'position', 'animated', 'anchor', 'xticklabels',
        'axisgb', 'frameon', 'axis', 'style', 'grid'
                           }
                           )

    _set = _remove_args(pfs.axes.derive(), "xlabel", "ylabel", "title")
    bothaxis = bothaxis
    #xaxis = axis.x
    #yaxis = axis.y

    spines = spines
    grids = grids
    clear = pfs.aclear
    cla = clear
    title = pfs.title

    @rproperty
    def xscale(self):
        return self.bothaxis.x.scale
    @rproperty
    def yscale(self):
        return self.bothaxis.y.scale        

    @rproperty
    def xlabel(self):
        return self.bothaxis.x.label

    @rproperty
    def ylabel(self):
        return self.bothaxis.y.label

    @rproperty
    def xaxis(self):
        return self.bothaxis.x

    @rproperty
    def yaxis(self):
        return self.bothaxis.y

    @rproperty
    def x(self):
        return self.bothaxis.x

    @rproperty
    def y(self):
        return self.bothaxis.y

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

    def set(self, *args, **kwargs):
        self.update(kwargs.pop(KWS, {}), **kwargs)
        sharex, sharey = self.parseargs(args,                                          
                                        "sharey", "sharey", 
                                        sharex=None, sharey=None                                        
                                      )
        ## in case labels were positional argument 




        axes = self.get_mpl_axes()
        #self._set(axes=axes) 

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

        self.bothaxis(axes=axes)
        #self.yaxis(axes=axes)
        self.spines(axes=axes)
        self.grids(axes=axes)
        self.title(axes=axes)

        lo = self.get("label_outer", None)
        if lo:
            axes.label_outer()   
        self._set(axes=axes)                                 

axes = Axes()


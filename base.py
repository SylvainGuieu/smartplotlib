from __future__ import division, absolute_import, print_function

from .recursive import (RecObject, RecFunc, CatRecObject, KWS, alias,
                        _value_formater, _list_formater, rproperty)
from .stack import stack

import inspect

param_docs = {
              "color" : "this is the color", 
              "linewidth" : "this is the line width"
            }

class _Style:
    def get_style_params(self, style):
        def gs(p,new):
            for k, v in new.get("__styles__", {}).get(style, {}).iteritems():
                p.setdefault(k,v)
        p = {}
        gs(p, self.locals)

        self._history.map(gs,p)
        args = getattr(self, "args", None)
        if args:
            return {k:v for k,v in p.iteritems() if k in args}
        return p

    def new_style(self, style, _kw_={}, **kwargs):
        if not "__styles__" in self.locals:
            self.locals["__styles__"] = {}
        self.locals["__styles__"][style] = kwargs
        for k,v in _kw_.iteritems():
            self.set_style_param(style, k, v)

    def set_style_param(self, style, path, value):
        obj, item = self.__getitempath__(path)

        if not len(item):
            if not isinstance(obj, (CatRecObject, PlotFunc, PlotFactory)):
                raise TypeError("End point object in '%s' is not a valid object. Usage: obj['a.b'] = {'p1':v1} or obj['a.b|p1'] = v1"%(
                               path if isinstance(path,basestring) else ".".join(path)
                               ))
            try:
                values = dict(value)
            except TypeError:
                raise TypeError("End point object in '%s' is a dict like, value must be a dict like object"%(
                                path if isinstance(path,basestring) else ".".join(path)
                                ))
            except ValueError:
                raise TypeError("End point object in %s' is a dict like, value must be a dict like object"%(
                                path if isinstance(path,basestring) else ".".join(path)
                                ))                               
            else:                
                return obj.new_style(style, values)        
                


        if obj is not self:
            return obj.set_style_param(style, item, value)
            #if not "__styles__" in obj.locals:
            #    obj.locals["__styles__"] = {}
            #styles = obj.locals["__styles__"]                
            #if style not in styles:
            #    styles[style] = {}                        
            #styles[style][item] = value
            #return
        # assume style exists in __style__  
        if not "__styles__" in self.locals:
            self.locals["__styles__"] = {}
        styles = self.locals["__styles__"]                
        if style not in styles:
            styles[style] = {}                
        self.locals["__styles__"][style][item] = value        
                

    def update_style(self, style, _kw_={}, **kwargs):
        kw = dict(_kw_, **kwargs)
        if not "__styles__" in self.locals:
            self.locals["__styles__"] = {}
        styles = self.locals["__styles__"]
        if not style in styles:
            styles[style] = {}
        styles[style].update(kw)

    @property
    def styleinfo(self):
        styles = self.get("__styles__", {})
        if not styles: return 
        prt(idt+"Styles:")
        for style, params in styles.iteritems():
            prt(idt*2+style+":")
            for k,value in params.iteritems():
                value = _value_formater(values)
                prt(idt*3+"|%s: %s"%(k,value))                   

    def _style2self(self):
        style = self.get("style", None)
        if not style: return 

        if isinstance(style, basestring):
            style = [s.strip() for s in ",".split(style)]
        for s in style[::-1]:    
            for p,v in self.get_style_params(s).iteritems():
                self.setdefault(p,v)  

    def get_styledict(self, style):

        if not style: return {}
        out = {}
        if isinstance(style, basestring):
            style = [s.strip() for s in style.split(",")]
        for s in style[::-1]:    
            for p,v in self.get_style_params(s).iteritems():
                out.setdefault(p,v)   
        return out   

    @property            
    def styledict(self):        
        style = self.get("style", None)
        return self.get_styledict(style) 

    @property
    def _info3(self):
        prt = print
        idt = " "*4
        prt()
        styles = self.get("__styles__", {})
        if styles:
            prt(idt+"Styles: ")
            prt("%s"%(_list_formater(styles.keys(), idt=idt*2)))


                
###
# update the CatRecObject with the style methods
def _cat_new_style(self, style, _kw_={}, **kwargs):
    for child in self:
        child.new_style(style, _kw_, **kwargs)
def _cat_update_style(self, style, _kw_={}, **kwargs):
    for child in self:
        child.update_style(style, _kw_, **kwargs)    

def _cat_set_style_param(self, style, path, value):
    for child in self:
        child.set_style_param(style, path, value)            



CatRecObject.new_style = _cat_new_style
CatRecObject.update_style = _cat_update_style
CatRecObject.set_style_param = _cat_set_style_param

class PlotFactory(RecObject, _Style):
    _unlinked = tuple() # ("go","_go_results")
    _default_params = {"go": None, "_go_results": None, 
        "_example_": None, "__inerit__":None}
    _example = None


    def __call__(self, *args, **kwargs):
        if self._initialized and self._stopped:
            raise TypeError("This RecObject instance can be initialized only ones")

        new = self.derive()
        # reset the root ids

        new._initialized = 1 # one -> in instance of beeing initialized
        if 'style' in kwargs:
            new['style'] = kwargs.pop("style", None)
        #new._style2self()
                
        _none_ = new.finit(new, *args, **kwargs)
        if _none_ is not None:
            raise TypeError("The init function should return None got type '%s'"%type(_none_))
        new._initialized = 2 # two -> init func finished
        return new

    def goifgo(self):
        go = self.get("go", False)
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
        d = self.get("direction", "y")
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
        if not isinstance( right, (PlotFactory, PlotFunc, stack)):
            raise TypeError("can add a plot only to a plot, plotfunc or stack (not '%s') "%(type(right)))
        return stack([self, right])

    def iteraxes(self, _ncol_, _nrow_=None, _n_=None, **kwargs):
        if _nrow_ is None:
            n = _ncol_
            axes = [(_ncol_,i) for i in range(1, n+1)]
        else:
            n = _nrow_*_ncol_ if _n_ is None else _n_
            axes = [(_ncol_, _nrow_, i) for i in range(1,n+1)]

        kwargs.setdefault("axes", axes)
        return self.iter(n, **kwargs)

    def iterfigure(self, *args, **kwargs):
        figs = list(range(*args))
        kwargs.setdefault("figure", figs)
        return self.iter(len(figs), **kwargs)

    def __make_doc__(self):
        doc = self.__doc__ or self.finit.__doc__
        if "{paramlist}" in doc:
            pass
    def __param_doc__(self,param):
        return param_docs.get(param,"")            
        
    
    def __colect_param_doc__(self, d, key="", inerit=None):
        cl = self.__class__
        selfinerit = cl._default_params.get("__inerit__", None)
        if selfinerit:
            if inerit is None:
                inerit = selfinerit
            else:
                inerit.extend(selfinerit)    

        for sub in cl.__mro__:
            for k,m in sub.__dict__.iteritems():
                if not isinstance(m, (PlotFactory,PlotFunc,rproperty,CatRecObject)):
                    continue
                m = getattr(self,k)
                if isinstance(m, CatRecObject):
                    for child in m:
                        child.__colect_param_doc__(d,k, inerit)    
                else:                    
                    m.__colect_param_doc__(d, k, inerit)


class PlotFunc(RecFunc, _Style):
    @property
    def example(self):
        ex = self.get("_example_", None)
        if ex:
            return get_example(*ex)

    def __add__(self, right):
        if not isinstance( right, (PlotFactory,PlotFunc,stack)):
            raise TypeError("can add a plotfunc only to a plot, plotfunc or stack (not '%s') "%(type(right)))
        return stack([self, right])

    def iteraxes(self, _ncol_, _nrow_=None, _n_=None, **kwargs):
        if _nrow_ is None:
            n = _ncol_
            axes = [(_ncol_,i) for i in range(1,n+1)]
        else:
            n = _nrow_*_ncol_ if _n_ is None else _n_
            axes = [(_ncol_, _nrow_, i) for i in range(1,n+1)]

        kwargs.setdefault("axes", axes)
        return self.iter(n, **kwargs)

    def iterfigure(self, *args, **kwargs):
        figs = list(range(*args))
        kwargs.setdefault("figure", figs)
        return self.iter(len(figs), **kwargs)

    def __prepare_call_args__(self, args, ikwargs):
        args = self.getargs(*args)
        kwargs = self.getkwargs(**ikwargs)
        for a,k in zip(args[self.nposargs:], self.kwargnames):
            if k in ikwargs:
                raise TypeError("got multiple values for keyword argument '%s'"%k)
            # remove the extra positional argument from the kwargs
            kwargs.pop(k,None)

        style = ikwargs.pop("style", self.get("style", None))
        argnames = self.args[:len(args)]
        for p,v in self.get_styledict(style).iteritems():
            if p not in argnames:
                kwargs.setdefault(p,v)     
            
        return args, kwargs


    def _s_call__(self, *args, **ikwargs):
        if not self.fcall:
            raise TypeError("Not callable")

        style = ikwargs.pop("style", self.get("style", None))

        args, kwargs = self.__prepare_call_args__(args, ikwargs)

        argnames = self.args[:len(args)]
        for p,v in self.get_styledict(style).iteritems():
            if p not in argnames:
                kwargs.setdefault(p,v) 
                

        output = self.fcall(*args, **kwargs)
        return output

    def set_style_param(self, style, item, value):
        if not "__styles__" in self.locals:
            self.locals["__styles__"] = {}
        styles = self.locals["__styles__"]                
        if style not in styles:
            styles[style] = {}                
        self.locals["__styles__"][style][item] = value              


    def __param_doc__(self,param):
        return param_docs.get(param,"")            
            

    def __colect_param_doc__(self, d, key="", inerit=None):
        for param in self.args:
            if inerit is None or param in inerit:
                if param in d:
                    d[param][1].append(key)
                else:                                
                    d[param] = (param,[key],self.__param_doc__(param))


    @property
    def _info4(self):
        prt = print
        idt = " "*4                                
        style = self.get("style", None)
        if not style: return 
        prt()
        prt(idt+"From Style: %s"%style)
        params = self.styledict
        kwargs = self.getkwargs()
        for k,value in params.iteritems():
            if k in kwargs: continue
            value = _value_formater(value)
            prt(idt*2+"|%s: %s"%(k,value)) 


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


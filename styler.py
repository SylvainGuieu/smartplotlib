from . import plotfuncs as pf
from .base import PlotFunc, PlotFactory
from .recursive import has_magic_lst, has_magic, lst_pattern, fnmatch
from . import axis as A
from . import figure as F

# adictionary containing all styles
style_definition = {}
class _dummy_:
    pass

#pfs = [pf]
#def _get_pfs(item):
#    return getattr(pfs, item)
#def _has_pfs(item):
#    return hasattr(pfs, item)

pfs = {k:f for k,f in pf.__dict__.iteritems() if isinstance(f,(PlotFunc, PlotFactory))}

# redefine some to be compatible with rcParams
pfs.update(
    images  = pf.imshow,
    lines   = pf.line2d,
    patches = pf.patches,
    texts  = pf.texts,
    axes   = A.axes,
    xaxis  = A.xaxis,
    yaxis  = A.yaxis,
    grids  = A.grids,
    spines = A.spines,
    labels = A.labels,
    ticks  = A.ticks,
    figures = F.figure
)

def _get_pfs(item):
    return pfs[item]
def _has_pfs(item):
    return item in pfs



def getfuncpath(pfs, path):
    if "." in path:
        path, item = path.split(".",1)
        if (not "." in item) and (not "|" in item):
            item = "."+item   
    elif "|" in path:        
        path, item = path.split("|",1)
    else:
        path, item = path, None    


    if (has_magic_lst(path)) or (has_magic(path)):
        if has_magic_lst(glob):
            patterns = lst_pattern(glob)
            matcher = lambda k: lst_match(k, patterns)
        else:    
            matcher = lambda k: fnmatch.fnmatch(k, glob)        
        for k,f in pfs.iteritems():            
            if matcher(k):
                ### must do a getattr here to get an instanced
                ### recobject 
                lst.append( f )         
        obj = CatRecObject(lst)    
    else:
        obj =  pfs[path]

     
    return obj, item

def new_style(style, _kw_={}, **kwargs):
    for k,v in kwargs.iteritems():
        pfs[k].new_style(style,v)
    
    for k,value in _kw_.iteritems():
        obj, item =getfuncpath(pfs, k)

        if item is None:
            try:
                values = dict(value)        
            except TypeError:
                raise TypeError("End point object in '%s' is a dict like, value must be a dict like object"%(
                                k
                                ))
            else:
                obj.new_style(style, values)
        else:
            obj.set_style_param(style, item, value)                                      


def _get_obj_params(obj, k):
    return obj["."+k]
    ks = k.split(".",1)
    if len(ks)>1:
        return getattr(obj, ks[0])[ks[1]]
        #return _go_to_params( getattr(obj, ks[0]), ks[1] )
    return getattr(obj, ks[0])   


def get_func(func):
    if isinstance(func, basestring):
        if "." in func:
            func, rest = func.split(".",1)
            if _has_pfs(func):
                f = _get_pfs(func)
                return _get_obj_params(f, rest)    
            raise TypeError("unknown function '%s' "%func)
        

        if _has_pfs(func):
            f = _get_pfs(func)
            return f
        raise TypeError("unknown function '%s' "%func)
    if not isinstance(f, PlotFunc):
        raise ValueError("not a PlotFunc object")
    return func



class FStyle(object):
    def __init__(self, func, params):
        self.func = get_func(func)
        self.params = params

    def populate(self, params):
        for p,v in self.params.iteritems():
            params.setdefault(p,v)

    def copy(self):
        return self.__class__(self.func, self.params)


    def isfunc(self, func):
        return self.func == func

    def __add__(self, right):
        if isinstance(right, FStyle):
            rparams = right.params
        elif isinstance(right, dict):
            rparams = right
        else:
            raise TypeError("cannot add FStyle object with '%s' object"%(type(right)))

        new = self.copy()
        new.populate(rparams)
        return new


class Style(object):
    def __init__(self, *args):
        styles = list(*args)
        for s in styles:
            if not isinstance(s, FStyle):
                raise TypeError("All items must be of FStyle instance")
        self.styles = styles

    def get(self, func, default=None):
        func = get_func(func)

        for s in self.styles:
            if s.isfunc(func):
                return s
        return default

    def populate(self, func, params):
        fs = self.get(func)
        if fs is not None:
            fs.populate(params)

    def add(self, func, **params):
        fs = self.get(func)
        if not fs:
            self.append( FStyle(func, params) )
            return
        fs.params.update(params)

    def append(self, s):
        if not isinstance(s, FStyle):
            TypeError("can only append a FStyle object got a '%' object"%(type(s)))
        return self.styles.append(s)

    def extend(self, styles):
        for s in styles:
            if not isinstance(s, FStyle):
                raise TypeError("All items must be of FStyle instance")
        return self.styles.extend(styles)

    def index(self, func):
        func = get_func(func)
        for i,s in enumerate(self.styles):
            if s.isfunc(func):
                return i
        raise ValueError("no style of given func found")





def _new_style(name, _kw_={}, **kwargs):
    for k,v in _kw_.iteritems():
        try:
            func, param = k.split("|", 1)
        except ValueError:
            ValueError("rcparams item style should be of form 'func.param' got '%s'"%k)

        if not func in kwargs:
            kwargs[func] = {}
        kwargs[func][param] = v

    for kfunc, params in kwargs.iteritems():
        f = get_func(kfunc)
        f.new_style(name, params)

def info_style(name):
    txt = [""]
    if isinstance(name, basestring):
        name = [name]
    for k, f in pfs.iteritems():
        _info_style(f, k, name, txt)
    return txt[0]    

def _info_style(f, kf, names, txt, idt=""):
    params = {}
    for name in names:
        params.update(f.locals.get("__styles__", {}).get(name, {}))
    nidt = " "*len(idt+kf)    

    tmp = ""
    found = False
    for p,v in params.iteritems():    
            tmp += "\n"+nidt+"|%s : "%p
            svalue = "{!r}".format(v)    
            svalue = svalue if len(svalue)<70 else svalue.split("\n",1)[0][0:70]+" ..."
            tmp += svalue
    if isinstance(f, PlotFactory):
        for sub in f.__class__.__mro__:
            for k, method in sub.__dict__.iteritems():
                if isinstance(method, (PlotFunc, PlotFactory)):
                    found = _info_style( getattr(f,k), k, names, [tmp], nidt)

    found = (len(params)>1) | found 
    if found:
        txt[0] += "\n"+idt+kf+tmp
    return found    

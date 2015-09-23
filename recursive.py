from __future__ import division, absolute_import, print_function

import weakref
import inspect

__all__ = ["RecObject", "RecFunc", "cycle", "lcycle", "loop", "fcycle",
           "popargs", "parseargs", "merge_args", "extract_args",
           "recobject", "alias"
          ]


ALLOW_FAST_KEYS = True

## cycle references
## for parent.child, child is stored inside parent in a diciotnary __recobjects__
## child hold also the parent: parent.child.parent is parent
## On solution is to use weakref, but it can cause not obious problems for the
## user.
## As far as I understood cycle references are not a problem if the finalizer
## __del__ is not defined. So let's not use it for now but keep both for easy switch
USE_WEAKREF = False

""" key name which will substitued to kwargs in the default finit of RecObject """
KWS = "params"

###
# used for .info formating
PSI = "+"
PSP = "."
INFMT = "{0:>6s}|{1}: {2}"

##########
# define type num code for LOOP/CYCLE object
CYCLE = 3
LCYCLE = 2
LOOP = 1
FCYCLE = 4



def newid(obj):
    """ id returned for a RecObject or RecFunc asked at __init__"""
    return id(obj)

def getparameters(opt, ids):
    """From a dictionary and a id tuple return the parameter dictionary

    The Dictionary is created if non existant
    """
    if not ids in opt:
        opt[ids] = {}
    return opt[ids]

def getparameters_r(opt, ids):
    """read only equivalent of getparameters.

    unlike getparameters if the dictionary does not exists return
    a new empty dictionary
    """
    if not ids in opt:
        return {}
    return opt[ids]


def getobj(obj, path, getattr=getattr):
    """ from a path of atribute 'a.b.c' return the end object 'c'"""
    for attr in path.split("."):
        obj = getattr(obj, attr)
    return obj

def relative_getobj(obj, path, getattr=getattr):
    """ from a path of atribute 'child.subchild.func' return the end object 'func'

    Args:
        path (string): path to the end object as it would be for normal python
            call. obj.relative_getobj(obj, 'a.b') is obj.a.b
            except that '..' is the relative parent (as python import)
            obj.relative_getobj(obj, '..a.b') is obj.parent.a.b

        getattr (Optional[method]): the getattr method

    Returns:
        obj : anything found at the end of the path

    Raises:
        TypeError: if the relative path is below root object

    """
    if not "." in path:
        return getattr(obj, path)

    paths = path.split(".")
    if paths[0:2] == ['','']: # remove the first blank e.i. first '.'
        paths = paths[2:]

    for attr in paths:
        if not attr:
            parent = getattr(obj, "parent", None)
            if parent is None:
                raise TypeError("relative path below root object")
            obj = parent
        else:
            obj = getattr(obj, attr)
    return obj

def getitempath(obj, path, getattr=getattr):
    """ from obj and a path return a target obj and an item

    Args:
        path (string or 2 tuple): gives the path/item pair
            if 2 tuple: (path (string), item (string) )
            if 1 tuple: (path (string),)  -> item=""
            if string : item  -> path=""

    Returns:
        obj : the object found from path
        item : the input item


    See Also:
        relative_getobj : for path specification
    """
    if isinstance(path, (tuple,list)):
        if len(path)>2:
            raise TypeError("If tuple, path size must not exceed 2, got a %d tuple"%len(path))
        if len(path)==1:
            path, = path
            item = ""
        else:
            path, item = path
    else:
        item = path
        path = ""

    if len(path):
        obj = relative_getobj(obj, path, getattr=getattr)
        #obj = getobj(obj, path, getattr=getattr)
    return obj, item

def getattrandinit(obj, attr):
    """get attribute and init it if a RecObject

    usefull to replace getattr in relative_getobj function
    Args:
        attr (string) : Attribute name

    Returns:
        obj: attribute object

    See also:
        relative_getobj

    """
    obj = getattr(obj, attr)
    if isinstance(obj, RecObject) and not obj.isinitialized:
        return obj()
    return obj


def _list_formater(lst, length=80, idt="", braket=-1):
    """ format a list of args """
    lens = len(idt)
    out = []
    line = idt
    first = False
    for i,s in enumerate(lst):
        if (len(s)+lens)>length:
            out.append(line+",")
            lens = len(idt)
            line = idt+"("*((braket>-1)*(braket==i))+s
        else:
            line += (", "*first)+"("*((braket>-1)*(braket==i))+s

            lens = len(line)
        first = True
    out.append(line+")"*(braket>-1))
    return "\n".join(out)


def _get_method_info(obj, output):

    output[0] = []
    for subs in obj.__class__.__mro__:
        for attr, method in subs.__dict__.iteritems():
            if isinstance(method, RecObject):
                output[attr] = {}
                _get_method_info(method, output[attr])

            elif isinstance(method, RecFunc):
                output[0].append(attr)


def _format_methods(obj, name="", idt=""):
    methods = {}

    s = []
    _get_method_info(obj, methods)
    return _format_methods_walker(methods, name, idt)

def _format_methods_walker(methods,  name="", idt=""):

    s = (idt+name+"\n"+_list_formater(methods[0], idt=idt+" "*4))

    methods.pop(0)
    for k,v in methods.iteritems():
        s += "\n"+_format_methods_walker(v, " "*len(name)+k, idt=idt)
    return s





def _build_args(args, substitutions=None):
    """ build args for RecFunc

    if firs arg is integer, that the number of positional arguments npos
    else it is 0

    the npos positional argument follow, None means that there is no keyword in
    the object to substitute the keyword argument.

    Then keywords argument are following, they must be string or a 2 tuple
    of (string, something) where something is the substitution key.

    If True is the last argument, it means that the RecFunc object will accept
    any other kwargs. Used when the fcall function has **kwargs

    """
    anyparams = False

    if not args:
        return 0, tuple(), {}, False

    if isinstance(args[0], int):
        # first argument is the number of positional arguments
        nposargs  = args[0]
        args = args[1:]
    #elif isinstance(args[0], tuple):
    #    nposargs = len(args[0])
    #    kwargs  = args[1:]
    #    args = args[0]+kwargs

    else:
        nposargs = 0

    #### look for True at the end
    try:
        args[nposargs:].index(True)
    except ValueError:
        anyparams = False
    else:
        if not args[-1] is True:
            raise TypeError("True or False should be at the end of args only")
        anyparams = True
        args = args[:-1]

    #### look for False at the end
    try:
        args[nposargs:].index(False)
    except ValueError:
        pass
    else:
        if not args[-1] is False:
            raise TypeError("True or False should be at the end of args only")
        args = args[:-1]


    # silently eliminate arg that appear more than ones
    # should I raise an exception ????



    if len(args)<nposargs:
        raise TypeError("expecting at least %d positional argument"%nposargs)

    args = list(args)

    substitutions = substitutions or {}
    for i, obj in enumerate(args):
        if isinstance(obj, tuple):
            if len(obj)>2 or not isinstance(obj[0], basestring):
                raise TypeError("Invalid tuple for arg/kwargs definition. Expecting (string, hashable) got %s"%(obj,))
            if obj[0] not in substitutions:
                substitutions[obj[0]] = obj[1]
            args[i] = obj[0]

        elif (i>=nposargs) and (not isinstance(obj, basestring)):
            raise TypeError("Expecting only string or a 2 tuple for kwargs got %s"%obj)


    keyargs = args[nposargs:]
    keyset = set(keyargs)
    if len(keyargs)!=len(keyset):

        for k in keyset:
            if keyargs.count(k)>1:
                break
        else:
            raise TypeError("Duplicate arguments")
        raise TypeError("Duplicate argument '%s'"%k)

    return nposargs, tuple(args), substitutions, anyparams



def _argsadd(args1,args2):
    return args1+tuple(a for a in args2 if not a in args1)

def merge_args(pf, iargs):
    """ merge  list of args for RecFunc

    If a number of positional argument is given (e.i. first args is int)
    it is returned as the new number of pos args else pf.nposargs is returned.
    If anyparams is given (last in args is boolean) it is returned as the
    new anyparams else pf.anyparams is returned.

    Args:
        recfunc (RecFunc): original recfunc object
        args (iterable): list of new arguments

    Returns:
        nposargs (int): number of positional argument
        args (tuple): tuple of arg names
        substitutions (dict): dictionary of key substitutions
        anyparams (bool): True if all parameters are accepted

    See Also:
        RecFunc
    """
    if not iargs:
        return pf.nposargs, pf.args, pf.substitutions, pf.anyparams


    posargsdefined = isinstance(iargs[0], int)

    subs = pf.substitutions

    nposargs, args, subs, anyparams = _build_args(iargs, subs)
    anyparamsdefined = iargs[nposargs:][-1] in [True,False]

    if not posargsdefined:
        if anyparamsdefined and (anyparams is False):
            return pf.nposargs, pf.args[:pf.nposargs]+args, subs, False
        else:
            return pf.nposargs, pf.args[:pf.nposargs]+_argsadd(args,pf.args[pf.nposargs:]), subs, anyparams
    else:
        if anyparamsdefined and (anyparams is False):
            return nposargs, args, subs, False
        else:
            return nposargs, _argsadd(args,pf.args[pf.nposargs:]), subs, anyparams

    raise TypeError("BUG !")



def extract_args(finit, remove=0):
    """ extract args of a function so they can be parsed directly to a RecFunc

    Args:
        finit (callable): a callable object (function) its signature is used to
            return a list of args parsable to a RecFunc object.
            the function must not be a built-in
        remove (Opional[int]) : default 0, the number of first args to remove
            in the output. usefull when want to remove the self like argument
            of bounded methods.
    Examples:

        >>> f =  lambda a,b,c=0,d=0: None
        >>> extract_args(f)
        (2, 'a', 'b', 'c', 'd')
        >>> RecFunc(*extract_args(f))

    """
    spec = inspect.getargspec(finit)
    npos = len(spec.args)-len(spec.defaults or [])
    args = (npos,)+tuple(spec.args)
    if spec.keywords is not None:
        args += (True,)
    if remove:
        args = (args[0]-remove,)+args[remove+1:]

    return args






def _go_walker(obj, func, output, sp):
    """ see doc of go attribute of RecObject """
    ##
    # understood syntax:
    # "subplot.attr1|-all"  work is plot.subplot.attr1["-all"] is a list of go string command
    # "subplot: attr1,attr2,attr3" -> "subplot.attr1", "subplot.attr2", "subplot.attr3"
    # "subplot: attr1|-all" -> subplot.attr1.go("-all")
    #

    if isinstance(func, basestring):
        if func[0]=="-":
            # no embiguity we want a keyword here
            func = "|"+func

        if ":" in func:
            if func.count(":")>1:
                raise TypeError("to many ':' in '%s' expecting one"%func)

            rootpath, paths = [s.strip() for s in func.split(":")]
            paths = [s.strip() for s in paths.split(",")]
            obj = relative_getobj(obj, rootpath, getattrandinit)

            _go(obj, paths, output, sp+"."+rootpath)
            return

        else:
            if not ("|" in func):

                obj = relative_getobj(obj, func, getattrandinit)
                if not isinstance(obj, RecObject):
                    obj = obj() # RecObject mare already initialized
                                # but not other object
                    output[sp+"."+func] = obj
                    return
                else:
                    ###
                    # if the end point is a plot RecObject,
                    # execute its "-" e.i. obj.go()
                    if "-" in obj:
                        return _go_walker(obj, "-", output, sp+"."+func)
                    else:
                        return

            else:
                if func.count("|")>1:
                    raise TypeError("to many '|' in '%s' expecting one"%func)

                path, item = [s.strip() for s in func.split("|",1)]
                if len(path):
                    obj = relative_getobj(obj, path, getattrandinit)

                if len(item):
                    return _go(obj, obj[item], output, sp+("."+path if path else ""))

                else:
                    if isinstance(obj, RecObject):
                        if "-" in obj:
                            return _go_walker(obj, "-", output, sp+"."+func)
                        else:
                            return
                    else:
                        output[sp+"."+func] = obj()
                        return

    elif isinstance(func, (tuple,list)):
        return _go(obj, func, output, sp)
    else:
        if sp:
            output[sp] = func()
        else:
            output[None] = output.get(None,[])+[func()]
        return

def _go(obj, funclist, output, sp=""):
    """ see doc of go attribute of RecObject """
    for func in funclist:
        _go_walker(obj, func, output, sp)


def _is_iterable(obj):
    """ Return the iterable int type """
    return isinstance(obj, loop)*LOOP or\
           isinstance(obj, lcycle)*LCYCLE or\
           isinstance(obj, cycle)*CYCLE or\
           isinstance(obj, fcycle)*FCYCLE

def _process_iterable(obj):
    """ private function ussed in iter methods of RecObject and RecFunc,
        decide what to do with obj:
            if an iterable : newobj=cycle(obj)
            if one of cycle, loop, lcycle, fcycle : newobj=obj
            else newobj=obj

        return check, newobj
        if check is false newobj is obj

    """
    if _is_iterable(obj):
        return False, obj
    if (not hasattr(obj,"__iter__")) or isinstance(obj,(tuple,dict)):
        return False, obj

    if inspect.isgenerator(obj):
        return True, loop(obj)
    return True, cycle(obj)

def parseargs(obj, args, *arg_names, **kwargs):
    """return args generator of an arg names list

    the i'th values of *arg_names[i] is taken from args if i<len(args)
    else from obj, else from **kwargs. If not found raise a TypeError
    positional argument are saved (by their name) in the object

    Args:
        obj (dict-like): obj with item capability as dictionary, RecObject,
            RecFunc, etc ...
        args (list/tuple): list of values
        *arg_names : argument name
        **kwargs : any default values

    Yields:
        value: The next value found in args, obj, or default
    Returns:
        generator

    Raises:
        TypeError : if cannot return one of the args

    Examples:
        def plot(x,y,color="black",marker="+"):
            pass

        def plot_from_params(params, *args):
            x, y, color, marker = parseargs(params, args, "x", "y",
                                            "color", "marker",
                                            color="red",marker="-")
            return plot(x, y, color, marker)

        >>> params = {"x":0, "y":0, "color":"blue"}
        >>> plot_from_params(params, np.arange(10), np.random.rand(10))


    See Also:
        popargs : same thing but pop argument from obj and args list

    """


    largs = len(args)
    for i,p in enumerate(arg_names):
        if i<largs:
            obj[p] = args[i]
            yield args[i]
            continue

        if p is None:
            raise TypeError("missing %dth argument"%(i+1))
        try:
            yield obj[p]
            continue
        except KeyError:
            pass

        try:
            yield kwargs[p]
        except KeyError:
            raise TypeError("missing %dth argument and cannot substitute by '%s' param"%(i+1,p))

def popargs(obj, args, *arg_names, **kwargs):
    """return args generator of an arg names list and pop argument

    the i'th values of *arg_names[i] is taken from args if i<len(args)
    else from obj, else from **kwargs. If not found raise a TypeError.

    argument are poped from obj or args.
    Args:
        obj (dict-like): obj with .pop method, dict, RecObject, RecFunc, etc ...

        args (list): list of values. Must have the .pop method
        *arg_names : argument name
        **kwargs : any default values

    Yields:
        value: The next value found in args, obj, or default
    Returns:
        generator

    Raises:
        TypeError : if cannot return one of the args

    Examples:
        def plot(x,y, *args, *kwargs):
            pass

        def plot_from_params(params, *args, **kwargs):
            params = dict(params, **kwargs)
            args = list(args) # must be a list

            x, y, scale = parseargs(params, args, "x", "y", "scale", scale=1.0)
            # do something with x,y and scale
            return plot(x, y*scale, *args, **kwargs)

        >>> params = {"x":0, "y":0, "color":"blue"}
        >>> plot_from_params(params, np.arange(10), np.random.rand(10))


    See Also:
        parseargs : same thing but pop argument from obj and args list

    """

    largs = len(args)
    offset = 0
    for i,p in enumerate(arg_names):
        if i<largs:
            value = args.pop(i-offset)
            offset += 1
            try:
                obj.pop(p)
            except KeyError:
                pass
            yield value
            continue

        if p is None:
            raise TypeError("missing %dth argument"%(i+1))
        try:
            yield obj.pop(p)
            continue
        except KeyError:
            pass

        try:
            yield kwargs[p]
        except KeyError:
            raise TypeError("missing %dth argument and cannot substitute by '%s' param"%(i+1,p))



def recobject(*args, **kwargs):
    """ recobject decorator and decorator factory

    decorator signature:
        @recobject
        def myrecobject(recobj, x, y):
            pass

        @recobject(color="red")
        def myrecobject(recobj, x, y):
            pass

        @recobject(parent,  color="red")
        def myrecobject(recobj, x, y):
            pass

    In the last forme, parent must be a RecObject from which the new recobject will
    inerit.

    Notes:
        @recobject(parent, **kargs)
        def myrec(recobj):
            pass

      is equivalent to

        @parent.decorate(**kwargs)
        def myrec(recobj):
            pass

      or

        myrec = parent.derive(**kwargs)
        @myrec.initier
        def myrec(recobj):
            pass


    See Also:
        RecObject : for a complete doc

    """
    if args:
        if len(args)>1:
            finit, rec = args
            if not isinstance(rec, RecObject):
                raise TypeError("second positional argument must be a RecObject got %s"%args[1])

            if not hasattr(finit,"__call__"):
                raise TypeError("finit must be callable")
            return rec.derive(**kwargs).initier(finit)

        if isinstance(args[0], (RecObject,RecFunc)):
            rec, = args
            return rec.derive(**kwargs).initier

        else:
            finit, = args
            if len(kwargs):
                raise TypeError("unexpecting kwargs when setting finit")
            if not hasattr(finit,"__call__"):
                raise TypeError("finit must be callable")
            return RecObject(finit, **kwargs)
    else:
        return RecObject(**kwargs).initier


def recfunc(*args, **kwargs):
    """ recfunc decorator and decorator factory

    decorator signature:
        @recfunc
        def myfunc(x, y, a=0, b=1):
            pass

        @recfunc(2, "x", "y", "a", "b", b=10)
        def myfunc(x, y, a=0, b=1):
            pass

        @recfunc(parent)
        def myfunc(x, y, a=0, b=1):
            pass

        @recfunc(parent,0)
        def myrecobject():
            pass
    """
    # ->>>>>> TODO:  THIS FUNCTION -<<<<<<<<<<<<
    if args:
        if len(args)>1:
            finit, rec = args
            if not isinstance(rec, RecObject):
                raise TypeError("second positional argument must be a RecObject got %s"%args[1])

            if not hasattr(finit,"__call__"):
                raise TypeError("finit must be callable")
            return rec.derive(**kwargs).initier(finit)

        if isinstance(args[0], (RecObject,RecFunc)):
            rec, = args
            return rec.derive(**kwargs).initier

        else:
            finit, = args
            if len(kwargs):
                raise TypeError("unexpecting kwargs when setting finit")
            if not hasattr(finit,"__call__"):
                raise TypeError("finit must be callable")
            return RecObject(finit, **kwargs)
    else:
        return RecObject(**kwargs).initier






class RecObject(object):
    """ RecObject object is a clolection of RecObject or RecFunc callable and
    with default keyword assignement.

    Can works as stand alone object or inside a hierarchy of RecObject
    If instanced from any other object than RecObject it is considered as
    the data object.

    As class does with the __init__ function, RecObject takes a function executed
    when a new instance of the recobj is created (when called recobj())

    RecObject can be used as a decorator as well.



    RecObject() instances accept item get and set as a dictionary. However the
        items can be in the local dictionary of the object or in the parent
        object (a RecObject).
        They are 2 forms of parent object:
            a bounded parent : parent.child
            an instance : child = parent()
            for both type parent can be found in child.parent and
            child.parentinstance respectively.
        If the item is not found in the local dictionary it is searched recursively
        in the parentinstance and parent. a KeyError is raised if not found
        Therefore:
            >>> parent["color"] = "red"
            >>> parent["marker"] = "+"
            >>> parent.child["marker"]  = "-"
            >>> parent.child["marker"]
            "-"
            >>> parent.child["color"]
            "red"

    Items assignement recobj["item"] = value  or recobj.update(item=value) are
    done on the recobj.locals dictionary.


    If a RecObject is attribute of an other object, an instance of the
    recobject is return, not the original. So a recobj can have different params
    for different instance of its parent class (Data in the eample below).
    Therefore:
        recobj = RecObject(param1="original value of param 1")
        class Data(object):
            recobj = recobj

        >>> Data.recobj is recobj
        True
        >>> data = Data()
        >>> data.recobj is recobj
        False
        >>> data.recobj is data.recobj
        True

        >>> data.recobj["param1"]
        "original value of param 1"
        >>> data.recobj["param1"] = "new value of param 1 for my data instance"
        >>> data.recobj["param1"]
        "new value of param 1 for my data instance"
        >>> recobj["param1"]
        "original value of param 1"

    The same thing is true if a child inerit from a parent RecObject:
        parent.child["param1"]  = "original .child[param1] value"
        data.parent.child["param1"] = "value of .child[param1] of the data instance"


    A call on the recobj create a new recobj instance and call the finit func
    with the newly created instance as first argument. As well any params
    modification made on the new instance or its child will not modify the original
    Therefore:
        >>> parent.child["param1"] = "original .child[param1] value"
        >>> newparent = parent()
        >>> newparent.child["param1"] = "new value for .child[param1]"
        >>> newparent.child["param1"]
        "new value for .child[param1]"
        >>> parent.child["param1"]
        "original .child[param1] value"


    RecObject usualy ends with a RecFunc which is a function that substitute
    its default args and params from its parent RecObjects.
    They are usefull to create templates. A good example is for plots
    functionalities, see below.


    Param assignement can take a 'path|param' string as item:
        >>> a["b.c.d|param1"] = abcd_value1
        is the same as
        >>> a.b.c.d["param1] = abcd_value1

    the update method can be used to change parameters as dict does except
    that a special key params is understood as a dictionary of parameters
        >>> a.update(param1=value2,
                     param2=value2,
                     params={"param3":value3,
                             "b.c.d|param1":abcd_value1}
                    )
    If one need to set 'params' as a parameter used a['params'] or include it
    in the params dictionary.



    Args:
        finit (Optional[callable]) : a callable that define the RecObject init
            function, called after each calls of the RecObject.
            Has __init__ for classes, finit will get a new RecObject as first
            argument followed by any type of signature and must return None
            The default finit just update new params, it is:
            def (newrecobj, **kwargs):
                newrecobj.update(kwargs.pop("params", {}), **kwargs)


        **params : any parameters to record in the newly created RecObject

    Returns:
        obj (RecObject): a RecObject instance


    Attributes:
        locals (dict) : The local parameters dictionary (read/write dict)
        all (dict) : Return a dictionary containing all parames/value pairs found
            in the hierachy structure. If modified tha all dictionary will have
            no effect on recobj params.
        parent : The parent object parent.child is child.parent
            however to avoid cycling referenced the parent is retrieved via a
            weak reference. Therefore if parent obj has been deleted child.parent
            return None and print a warning. If child has no parent, None is return.
        parentinstance : The parent if child = parent()



    Examples:

        Below is an example where RecObject is used to create plot template.
        Of course the gain in coding is not when defining new RecObject but when
        using them.

    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    #######
    # subclassing RecObject and defining its RecFunc
    #######
    import numpy as np
    class XYPlot(RecObject):
        @RecFunc(2, "x", "y", "color", "style")
        def line(x,y, **kwargs):
            #... plot some lines here ...
            return (x,y,kwargs)

        @RecFunc(2, "x", "y", "color", "marker")
        def point(x,y, **kwargs):
            #... plot some points here ...
            return x,y,kwargs

        @RecFunc("xlabel","ylabel", "title"):
        def setaxes(xlable="", ylbale="", title=""):
            #... do something with labels and titles
            return



    ## Example As a stand alone object:
    @XYPlot
    def xyplot(plot, x, y, **kwargs):
        plot.update(**kwargs)
        plot["x"] = np.asarry(x)
        plot["y"] = np.asarray(y)

    x = range(10)
    y = [v*v for i in x]
    xyplot(x,y, title="some plot title").line()


    ## XYPlot can be used in Other RecObject or inside any object considered
    ## as the data

    ## define a RecObject class that will contained all xyplots
    class PlotForData(RecObject):
        def finit(self, plot, **kwargs):
            ''' init a new instance of plot colection for my data  '''
            plot.update(kwargs.pop("params",{}), **kwargs)
            plot["title"] = "Data from "+plot.data.filename

        @XYPlot
        def velocity(plot, **kwargs):
            ''' the velocity versus time plot '''
            plot.update(kwargs.pop("params",{}), **kwargs)

            plot["y"] = plot.data.velocity
            plot["x"] = plot.data.time



        @XYPlot
        def xwoble(plot, **kwargs):
            ''' whoble in x direction versus time plot '''
            plot.update(kwargs.pop("params",{}), **kwargs)
            plot.init_parent()

            plot["y"] = plot.data.xposition
            plot["x"] = plot.data.time
            ## put a warning color for line if above>100
            if max(xposition)>100:
                plot.line["color"] = "red"


        # decorate create a new instance and send the initier function
        # to be used as decorator
        @xwoble.decorate(color="green") #ywoble ploted in green by default
        def ywoble(plot, **kwargs):
            plot.xwoble.finit(plot, **kwargs)
            plot["y"] = plot.data.yposition


    class Data(object):
        def __init__(self, filename):
            self.filename = filename

            self.velocity =  <... some data from file ...>
            self.xposition =  <... some data from file ...>
            self.yposition =  <... some data from file ...>
            self.time =  <... some data from file ...>

        plots = PlotForData(marker="*") # default marker is '*'



    >>> data = Data("path/to/data")

    >>> data.plots["marker"] = "+" # if not specified the default marker
                               # will be "+"
    # also one can use update
    # default color and style:
    >>> data.plots.update(color="blue", style="-.-")


    #red overwrite blue for velocity lines only
    >>> data.plots.velocity.line["color"] = "red"
    # also can use a string path
    >>> data.plots["velocity.line", "color"] = "red"


    >>> data.plots.velocity().line()
    >>> data.plots.xwoble().line()
    #or
    #will plot "xwoble" and  "ywoble" as defined in plots["-"] keyword
    # plus velocity.line
    >>> data.plots.go("xwoble:line,point", "velocity.line")

    # is equivalent to do:
    >>> data.plots().velocity().line()
    >>> data.plots().xwoble().point()
    >>> data.plots().xwoble().line()

    """
    _initialized = False
    _parent = None
    _default_params = {}
    """ _default_params are always set localy they can be copied from an
    instance but never from a parent. """

    _data = None
    def __init__(self, _init_=None, **params):

        if _init_ is not None:
            self.set_initier(_init_)

        self.ids = newid(self)
        self.rootids = []


        self._params  = {}
        self._params.update(self._default_params)

        self.locals.update(params.get(KWS,{}), **params)

        self.__recobjects__ = {}
        self._parentinstance = None
        self._parent = None

    @staticmethod
    def finit(plot, params={}, **kwargs):
        """ Initialize the plot object

        By default do nothing else than setting parameters to
        new object instance.
        Also parameters can be parsed from the params keyword
        special keyword which contain a dictionary of parameters.

        Args:
            params (Optional[dictionary]) : parameters in a dictionary.
                dictionary keys are parameter and can be a string path|param:
                 dict("parent.child1|color":"red")
        Returns:
            recobj (RecObject) : a new instance of RecObject

        See Also:
            RecObject
            RecFunc
        """
        plot.update(params, **kwargs)

    @property
    def locals(self):
        """ The local dictionary of parameters

        All modification of the locals dictionary will not affect
        parents but only the object itself.
        in other words:
         recobj.locals != recobj.parent.locals != recobj.parentinstance.locals

        """
        return self._params
        #return getparameters(self._params, self.ids)


    @property
    def all(self):
        """ Return the dictionary containing all the parameters in the hierarchy

        modifing the all dictionary will have no effect on the recobj or its
        parents.

        """
        params = self.locals.copy()
        if self.parentinstance:
            for k,v in self.parentinstance.all.iteritems():
                params.setdefault(k,v)

        if self.parent:
            for k,v in self.parent.all.iteritems():
                params.setdefault(k,v)

        return params



    def __call__(self, *args, **kwargs):
        if self._initialized:
            raise TypeError("RecObject instance already initialized")

        new = self.derive()
        # reset the root ids

        new._initialized = 1 # one -> in instance of beeing initialized
        parent = self.parent # hold a parent reference here
        _none_ = new.finit(new, *args, **kwargs)
        if _none_ is not None:
            raise TypeError("The init function should return None got type '%s'"%type(_none_))
        new._initialized = 2 # two -> init func finished
        return new

    def reset(self):
        """ reset all special iterable found in all

        special iterable are one of cycle(), lcycle(), fcycle() or loop()
        the reset  function will set the iterator at the begining if possible
        (that not the case for e.g. generators).

        """
        for k,v in self.all.iteritems():
            if _is_iterable(v):
                self[k] = iter(v)


    def iter(self, _start_or_n_=None, _stop_=None, **kwargs):
        """ iterator over obj duplicates with cycled params

        Call signature:
         recobj.iter(**kwargs)
         recobj.iter(n, **kwargs)
         recobj.iter(start,stop, **kwargs)


        Args:
            n ([int]) : number of iteration, if not present, The returned iterator
                will run until the shortest iterable parameter sequence or it will
                be of the length of the shortest loop() object
           -or-
           start, stop : the n start params are skiped


        Example:
            xyplot being a RecObject with a line attribute

            >>>  blue, green = xyplot.iter(2, color=["blue", "green"])
            >>> [p["color"] for p in xyplot.iter(5, color=["red", "blue"])]
            ["red", "blue", "red", "blue", "red"]
            >>> [p.line() for p in xyplot.iter(x=[np.arange(10)]
                                               y=[np.arange(10)**i for i in 4],
                                              color=["red", "blue"]
                                             ) ]

        Raises:
            TypeError : if n iterable is not given and none of the params are
                iterable.
        """

        if _stop_ is None:
            n = _start_or_n_
            start = 0
        else:
            start = _start_or_n_
            n = _stop_
        return self._iter(start, n, kwargs, False)


    def itercall(self, _start_or_n_=None, _stop_=None, **kwargs):
        """ Same has iter attribute but call all the sub instances

        The init func should be callable without arguments.

        >>> [p().line() for p in plot.iter(2)]
        equivalent to:
        >>> [p.line() for p in plot.itercall(2)]


        """
        if _stop_ is None:
            n = _start_or_n_
            start = 0
        else:
            start = _start_or_n_
            n = _stop_
        return self._iter(start, n, kwargs, True)



    def _iter(self, start, n, kwargs, call=False):
        kwargs = dict(kwargs.pop(KWS, {}), **kwargs)
        # transform all iterables to cycle un less they are loop or cycle

        for k,v in kwargs.iteritems():
            isit, objit = _process_iterable(v)
            if isit:
                kwargs[k] = objit

        iterables = {}
        scalars = {}
        nit = 0
        for k,v in kwargs.iteritems():
            isit = _is_iterable(v)
            if isit:
                iterables[k] = iter(v)
                nit += isit == LOOP
            else:
                scalars[k] = v


        if n is None and not nit:
            # if n is None transform all iterables to loop so the
            # cycle will stop at the shortest iterable
            if iterables:
                iterables = {k:loop(getattr(v, "obj", v)) for k,v in iterables.iteritems()}
            else:
                raise TypeError("Cannot determine the iteration size")

        if call:
            derive = self.__call__
        else:
            derive = self.derive

        return RecFuncIterator(derive, iterables, scalars, n, start)


    def set_initier(self,finit):
        """ set the finit function

        finit is called after each call with a new instance as first argument

        Args:
            finit (callable) : a callable funtion, must take at least one argument
                and must return None  (as the __init__ function of classes)

        Example:
            >>> xy = RecObject()
            def xyinit(obj, x, y, color="red", scale=1.0, **kwargs):
                obj["x"] = np.asarray(x)
                obj["y"] = np.asarray(y)*scale
                obj.update(color=color, **kwargs)
            >>> xy.set_initier(xyinit)

        Returns:
            None

        See Also:
            initier : same thing but return self
        """
        self.finit = finit
        if finit.__doc__:
            self.__doc__ = finit.__doc__

    def initier(self, finit):
        """ same than set_initier but return self

        can be used as decorator:
            xy = RecObject()
            @xy.initier
            def xy(x, y, color="red", scale=1.0, **kwargs):
                obj["x"] = np.asarray(x)
                obj["y"] = np.asarray(y)*scale
                obj.update(color=color, **kwargs)

        See Also Methods:
            decorate  : derive the object and send a initier decorator
            duplicate : duplicate the object and send a initier decorator
        """
        self.set_initier(finit)
        return self

####
# duplicate_dec droped for now, the name is confusing
####
    # def duplicate_dec(self, _finit_=None, **kwargs):

    #     """ duplicate the recobject and send a initier decorator

    #     Args:
    #         **params : Any parameters set into the duplicate

    #     Examples:
    #         If xyplot already is a RecObject

    #         class Data(object):
    #             def __init__(self):
    #                 ### replace by somthing clever
    #                 self.time = np.arange(100)
    #                 self.velocity = self.time*self.time

    #             @xyplot.duplicate_dec(ylabel="Velocity", xlabel="time")
    #             def velocity(plot, color="blue", **kwargs):
    #                 plot["x"] = plot.data.time
    #                 plot["y"] = plot.data.velocity
    #                 plot.update(color=color, **kwargs)

    #     Notes:
    #         @obj.duplicate_dec()
    #         def xy(obj):
    #             pass
    #         would be the equivalent of
    #         xy = obj.duplicate()
    #         @xy.initier
    #         def xy(obj):
    #             pass

    #         But python raise a syntax error things like @xy.duplicate().initier





    #     """
    #     # self is now a new object
    #     self = self.duplicate(**kwargs)
    #     if _finit_ is None:
    #         ## finit setting is pending return the _set_finit function
    #         ## to use initier as a decorator
    #         return self.initier
    #     self.set_initier(_finit_)
    #     return self

    def decorate(self, _finit_=None, **kwargs):
        """ derive the recobject and send a initier decorator

            **params : Any parameters set into the duplicate

        Examples:
            If xyplot already is a RecObject

            class Data(object):
                def __init__(self):
                    ### replace by somthing clever
                    self.time = np.arange(100)
                    self.velocity = self.time*self.time

                @xyplot.decorate(ylabel="Velocity", xlabel="time")
                def velocity(plot, color="blue", **kwargs):
                    plot["x"] = plot.data.time
                    plot["y"] = plot.data.velocity
                    plot.update(color=color, **kwargs)

        See Also Methods:
            derive  : obj.derive() create new linked instance of obj
            initier : obj.initier(finit), @obj.finit set the finit function
            duplicate : obj.duplicate() create a new independent recobj with
                obj.all parameters
        """
        self = self.derive(**kwargs)
        if _finit_ is None:
            ## finit setting is pending return the _set_finit function
            ## to use initier as a decorator
            return self.initier
        self.set_initier(_finit_)
        return self



    def duplicate(self, _init_=None, **params):
        """ new = old.duplicate() all parameters old become locals in new

        contrary to the derive method, the new object created is independent
        of the old.
        >>> new = old.duplicate()
        is
        >>> new = old.__class__(old.finit, **old.all)

        Any change on old will not affect new.

        Args :
            finit (Optional[callable]) : the finit function. see set_finit method
                help.
            params (Optional[dict]): a dictionary of parameters
            **params : Any parameters set on the new method. Overwrite the ones
                in params.



        """
        params = dict(self.all, **params)
        new = self.__class__(
                             **params
                            )
        if _init_:
            new.set_initier(_init_)
        else:
            new.set_initier(self.finit)
        return new

    def derive(self, **params):
        """ child = parent.derive() params not defined in child taken from parent


        child will inerit of parent parameters. Any parameter change in child
        will not affect parent, but a parameter change in parent will affect child if
        the parameter is not defined in child.


        Args :
            params : a dictionary of params to set
            **kwargs : Any other parameters to set (overwrite params)

        Examples :
            >>> parent = RecObject(color="red", marker="+")
            >>> parent["color"]
            "red"
            >>> child = parent.derive()
            >>> child["marker"] = "-.-"
            >>> child["color"]
            "red"
            >>> child["marker"]
            "-.-"
            >>> parent["marker"]
            "+"

            >>> parent["color"] = "green"
            >>> child["color"]
            "green"
            >>> del child["color]
            KeyError 'color'

        """
        new = self._derive(None)
        new.update(params.pop(KWS, {}), **params)
        return new

    def _derive(self, parent):
        new = self.__class__(self.finit)

        new._data = self._data
        #new.ids = self.ids
        new._parentinstance = self

        new.parent =  parent

        if self._default_params:
            # default paramters can inerit from an parentinstance
            # but never from a parent.
            # need to copy the instance value here to eraze
            # the default value made by init
            new.locals.update({k:self.locals[k] for k in self._default_params})


        __recobjects__ = {}
        for ids,psub in self.__recobjects__.iteritems():
            __recobjects__[ids] = psub._derive(new)

        new.__recobjects__ = __recobjects__
        return new



    def _new_instance(self, parent):
        """ private func. Return a new instance from a parent.

        The parent can be any user object or a RecObject.
        The only restriction is that the user object must accept
        __recobjects__ as an attribute

        """

        if self.isinitialized:
            raise Exception("not a root instance")


        if isinstance(parent, RecObject):
            recchilds = parent.__recobjects__
            if self.ids in recchilds:
                return recchilds[self.ids]

            if False: ##
                new = self.__class__(self.finit)
                new._data = parent._data
                new.ids  = self.ids
                new._params = {}
                new._parentinstance = self
                new.__recobjects__ = self.__recobjects__
                new.parent = parent
            else:
                new = self._derive(parent)

            #new._parent = parent
            #parent.__recobjects__[self.ids] = new
            recchilds[self.ids] = new

            return new

        else:
            data = parent
            if not hasattr(data, "__recobjects__"):
                data.__recobjects__ = {}

            if self.ids in data.__recobjects__:
                return data.__recobjects__[self.ids]

            if False:
                new = self.__class__(self.finit)

                new._data = weakref.ref(data)
                new.ids = self.ids
                new._parentinstance = self
                new._parent = self._parent
            else:
                new = self._derive(self._parent)
                new._data = weakref.ref(data)

            data.__recobjects__[self.ids] = new

        return new

    @property
    def data(self):
        """ if parent of any object, data is that parent object

        data is None otherwhise.
        the data is set by a weakref, if the data object has been deleted
        .data return None and a warning is printed. to avoid any unwanted
        warning use the hasdata attribute.


        """
        if self._data:
            data = self._data()
            if data is None:
                print("Warning Data object deleted")
            return data

    @property
    def hasdata(self):
        """ True if has data and data is not deleted (dead) """
        return self._data and (self._data() is not None)


    if USE_WEAKREF:
        @property
        def parent(self):
            """ parent RecObject if any or None

            parent.recobj is recobj.parent


            parent is set with a weakref, if the parent object is dead, None is
            return and a warning is printed. To avoid unwanted warning use
            hasparent attribute.

            """
            parent = self._parent
            if parent:
                if isinstance(parent, weakref.ref):
                    parent = parent()
                    if parent is None:
                        print("Warning Parent object deleted")
                return parent

        @parent.setter
        def parent(self, parent):
            if isinstance(parent, weakref.ref):
                self._parent = parent
            elif parent:
                self._parent = weakref.ref(parent)
    else:
        @property
        def parent(self):
            """ parent RecObject if any or None """
            return self._parent

        @parent.setter
        def parent(self, parent):
            self._parent = parent


    @property
    def hasparent(self):
        """ True if has parent and parent is not deleted (dead) """
        return self._parent and (self._parent() is not None)



    @property
    def parentinstance(self):
        """ parent instance if any or None

        if child = pi()  than   child.parentinstance is pi
        also:
        if child = pi.derive()  child.parentinstance is pi

        """
        return self._parentinstance

    #def __del__(self):
    #    print("freeing plot", self.ids)

    def __get__(self, data, cl=None):
        if data is None:
            return self
        return self._new_instance(data)



    #####
    #
    # FAST_KEY are obj["a.b.c|item"] form
    #######
    if ALLOW_FAST_KEYS:
        def __getitempath__(self, path, getattr=getattr):
            if isinstance(path, basestring):
                if not "|" in path:
                    if "." in path:
                        path = path.lstrip(".")
                        return getitempath(self, (path,), getattr=getattr)
                    return getitempath(self, path, getattr=getattr)

                spath = path.split("|")
                if len(spath)>2:
                    raise TypeError("to many '|' in '%s'"%path)
                path, item = [s.strip() for s in spath]
                path = path.lstrip(".")
                return getitempath(self, (path,item), getattr=getattr)

            return getitempath(self, path, getattr=getattr)
    else:
        def __getitempath__(self, path, getattr=getattr):
            return getitempath(self, path, getattr=getattr)


    def __setitem__(self, path, value):

        obj, item = self.__getitempath__(path)
        if not len(item):
            raise KeyError("Missing end point keyword in '%s'"%(
                           path if isinstance(path,basestring) else ".".join(path)
                           ))
        if obj is not self:
            obj[item] = value
            return

        self.locals[item] = value

    def _search(self, item, spath=""):
        """ search the item in locals, than in the parentinstance than
        in the parent.
        Raises:
            KeyError if not found
        """
        try:
            value = self.locals[item]
        except KeyError:
            pass
        else:
            return value, spath

        if self.parentinstance:
            try:
                value, spath = self.parentinstance._search(item, spath)
            except KeyError:
                pass
            else:
                return value, spath+PSI


        if self.parent:
            try:
                value, spath = self.parent._search(item, spath)
            except KeyError:
                pass
            else:
                return value, spath+PSP

        raise KeyError("'%s'"%item)

    def _return_value(self,value):
        if isinstance(value, alias):
            return value.get(self)
        return value

    def __getitem__(self, path):
        """ self['param'] -> return param if found
        self['a.b.c|param'] -> return self.a.b.c['param'] if found

        """
        obj, item = self.__getitempath__(path)

        ##
        # if path like 'a.b|key1'
        # obj is b and item is 'key1'
        if obj is not self:
            if not item:
                return obj
            return obj[item]
        ###
        # from here self[""] return self to allow explicite self["."]
        if not item:
            return self
        #####################################

        #####################################
        try:
            value, _ =  self._search(item)

        except KeyError:
            pass
        else:
            return self._return_value(value)

        raise KeyError("'%s'"%item)


    def __delitem__(self, path):
        """ del item in the locals
        del self['a.b.c|param'] is  del self.a.b.c['param']

        """
        obj, item = self.__getitempath__(path)
        if not len(item):
            raise KeyError("Missing end point keyword in '%s'"%(
                           path if isinstance(path,basestring) else ".".join(path)
                           ))

        if obj is not self:
            del obj[item]
            return

        if item in self._default_params:
            print ("Warning: '%s' deleted. Deleting a default parameter can be hurtful"%(item))
        del self.locals[item]

    def __eq__(self, right):
        return isinstance(right, RecObject) and self.ids==right.ids \
                               and self.rootids==right.rootids



    def __contains__(self, path):
        try:
            self[path]
        except KeyError:
            return False
        return True

    @property
    def root(self):
        """ original recobj instance if any

        a.derive().derive().derive().root is a
        """
        while self.parentinstance:
            self = self.parentinstance
        else:
            return None
        return self

    @property
    def isinitialized(self):
        """ True if the instance is initialized

        a = RecObject()
        a.isinitialized  is False
        a(args).isinitialized  is True
        """
        return self._initialized>0

    def update(self, __d__={}, **kwargs):
        """ update the local dictionary


        obj.update([E, ]**F) -> None.  Update obj from dict/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k in F: obj[k] = F[k]

        E can contain path:
            >>> obj.update( {'a.b.c|param1':value1 }, param2=value2)
          is equivalent to
            >>> obj['param2'] = value2
            >>> obj.a.b.c['param1'] = value1

        Args :
          params (Optional[dict]) : params dictionary
          **kwargs : other params

        Returns:
            None

        """
        # __d__ dictionary can contain keyword with path like e.g fit.line.color
        for k,v in __d__.iteritems():
            self[k] = v
        self.locals.update(**kwargs)

    def setdefault(self, param , value):
        """ set obj[param] = default to the locals dictionary if param not in obj

        recobj.setdefault(param, value) is recobj.locals.setdefault(item, value)

            >>> recobj.setdefault('a.b.c|param1', value1)
           is
            >>> recobj.a.b.c.detdefault('param1', value1)

        Args:
            param (string) : param name 'param1' or path 'a.b.c|param'

        Return:
            None
        """
        if not param in self:
            self[param] = value

    def clear(self):
        """ Clear the locals parameter dictionary

        A param can still exist after clearing if coming from parent instances

        >>> a = RecObject(color="red")
        >>> b = a.derive(marker="++")
        >>> b["color"]
        "red"
        >>> b["marker"]
        "++"
        >>> b.clear()
        >>> b["color"]
        "red"
        >>> b["marker"]
        KeyError : 'marker'
        >>> a.clear()
        >>> b['color']
        KeyError : 'color'

        """
        self.locals.clear()

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def gets(self, *keys):
        return {k:self[k] for k in keys if k in self}

    def getargs(self, *params, **kwargs):
        lst = []
        for p in params:
            try:
                lst.append(self[p])
            except KeyError:
                lst.append(kwargs[p])
        return tuple(lst)

    # def getcallargs(self, *args, **kwargs):
    #     allkwargs =  self.all
    #     largs = len(args)
    #     nsargs = len(self.args)
    #     args = list(args)
    #     for i,a in zip(args, self.args):
    #         allkwargs.pop(a, None)
    #         if a in kwargs:
    #             raise TypeError("got multiple values for keyword argument '%s'"%a)

    #     for i,a in enumerate(self.args[largs:self.nposargs], start=largs):

    #         try:
    #             value = self[a]
    #         except KeyError:
    #             raise ValueError("Missing %d'th positional argument cannot substitute wit '%s' parameter"%(i,a))
    #         else:
    #             args.append(value)

    #     allkwargs.update(kwargs)
    #     return tuple(args), allkwargs


    parseargs = parseargs
    popargs = popargs


    def pop(self, *args):
        largs = len(args)
        if (largs<1) or (largs>3):
            raise TypeError("pop expected 1 to 3 arguments, got %d"%largs)

        if largs>1:
            if largs ==2:
                path , default, extern = args+(False,)
            else:
                path , default, extern = args

            obj, item = self.__getitempath__(path)
            local = obj.locals
            if item in local:
                value = local[item]
                del local[item]
            else:
                if extern and path in self:
                    value = self[path]
                else:
                    value = default
            return value

        item, = args
        value = self[item]
        del self[item]
        return value

    def _get_value_info(self):
        all = self.all
        output = []
        for key in all:
            value, spath = self._search(key)
            if isinstance(value, alias):
                try:
                    linked_value = self[key]
                except:
                    value = "{!r}".format(value)+" -> ?"
                else:
                    value = "{!r}".format(value)+" -> {!r}".format(linked_value)
            else:
                value = "{!r}".format(value)
            value = value if len(value)<70 else value.split("\n",1)[0][0:70]+" ..."
            output.append( (
                             spath, key, value
                             )
                          )
        return output




    @property
    def info(self):
        print("{self.__class__.__name__} object ".format(self=self), end="")
        idt = " "*4
        if self.isinitialized:
            print(idt+"Initialized")
        else:
            print("")
        print()
        print (idt+"Initializer Function :")
        try:
            finfo = self.finit.func_name+inspect.formatargspec(*inspect.getargspec(self.finit))
        except:
            finfo = str(self.finit)
        print (idt+"    "+finfo)
        #print()
        #print ("Recursive Methods :")
        #print (_format_methods(self, "self"," "*4))

        print()
        print (idt+"Curent Values : ")
        infos = self._get_value_info()
        print("\n".join([idt+INFMT.format(*inf) for inf in infos]))
        print()



    def go(self, *funclist):
        if not len(funclist):
            if not "-" in self:
                return []
            funclist = ["|-"]
        output = {}
        _go(self, funclist, output, "")
        return output

class RecFunc(object):
    _default_params = {}
    def __init__(self, *args, **params):

        nposargs, args, kwargs, anyparams = _build_args(args)

        self.substitutions = kwargs

        self.args = args
        self.nposargs = nposargs
        self.anyparams = anyparams

        self._params = self._default_params.copy()

        self.fcall = None

        self.ids = newid(self)

        self.update(params)

        self._parent = None
        self._parentinstance = None


    @property
    def posargnames(self):
        return self.args[:self.nposargs]
    @property
    def kwargnames(self):
        return self.args[self.nposargs:]


    def set_caller(self, fcall):
        """ set in place the fcall function """
        self.fcall = fcall
        # for now just copy the doc, will see after what to
        # do
        if getattr(fcall, "__doc__", None):
            self.__doc__ = fcall.__doc__

    def caller(self, fcall):
        """ same as set_caller but return the object """
        self.set_caller(fcall)
        return self



    def _return_value(self, value):
        if isinstance(value, alias):
            return value.get(self)

        isit = _is_iterable(value)
        if not isit:
            return value
        return getattr(value, "cnext", value.next)()


    def autocaller(self, finit):
        if type(finit) is type:
            nposargs, args, kwargs = _build_args(extract_args(finit.__init__))
            nposargs -= 1
            args = args[1:]
        else:
            nposargs, args, kwargs = _build_args(extract_args(finit))
        self.nposargs = nposargs
        self.args = args
        self.substitutions = kwargs
        return self.caller(finit)


    def _s_decorate(self, *args, **kwargs):
        """ set the caller function, pos args and kwargs and return a duplicate

        caller can be used as a decorator:
        @pf.caller
        def newpf(x,y,color="red"):
            pass

        @pf.caller("x", "y", "color=")
        def newpf(x,y,color="red"):
            pass

        or as a object duplication
        newpf = pf.caller()
        newpf = pf.caller("x", "y", "color=")
        newpf = pf.caller(lambda x,y,color="red": None)
        etc ....
        """
        # check if first arg is callable and not string
        # is it is the case that the fcall function
        fcall = None

        if args and (not isinstance(args[0], (int,tuple,basestring))):
            if not hasattr(args[0], "__call__"):
                raise TypeError("The fcall function must be callable")
            fcall, args = args[0], args[1:]


        ##
        # duplicate the object. if fcall is None, the fcall setting
        # is pending, so return the caller function
        self = self.duplicate(*args, **kwargs)
        if fcall is None:
            return self.caller
        self.set_caller(fcall)
        return self

    def decorate(self, *args, **kwargs):
        fcall = None

        if args and (not isinstance(args[0], (int,tuple,basestring))):
            if not hasattr(args[0], "__call__"):
                raise TypeError("The fcall function must be callable")
            fcall, args = args[0], args[1:]

        ##
        # duplicate the object. if fcall is None, the fcall setting
        # is pending, so return the caller function
        self = self.derive(*args, **kwargs)
        if fcall is None:
            return self.caller
        self.set_caller(fcall)
        return self

    def _search(self, item, sitem, spath=""):

        try:
            value, spath = self._search_instance(item, sitem, spath)
        except KeyError:
            pass
        else:
            return value, spath

        if self.parent:
            try:
                value, spath = self.parent._search(sitem, spath)
            except KeyError:
                pass
            else:
                return value, spath+PSP

        raise KeyError("'%s,%s'"%(item,sitem))


    def _search_instance(self, item, sitem, spath=""):
        try:
            value = self.locals[item]
        except KeyError:
            pass
        else:
            return value, spath

        if self.parentinstance:
            try:
                value, spath = self.parentinstance._search_instance(item,sitem, spath)
            except KeyError:
                pass
            else:
                return value, spath+PSI
        raise KeyError("'%s,%s'"%(item,sitem))


    def __getitem__(self, item, sitem=None):

        if isinstance(item , tuple):
            if len(item)>1:
                raise TypeError("invalid item %s"%item)
            item, = item
            _return = lambda x:x
        else:
            _return = self._return_value


        if not isinstance(item , basestring):
            raise TypeError("RecFunc item must be string got %s"%type(item))

        if sitem is None:
            sitem = self.substitutions.get(item, item)

        if isinstance(sitem, (list)):
            for sit in sitem:
                try:
                    value = self.__getitem__(item, sit)
                except KeyError:
                    continue
                else:
                    return value
            raise KeyError("'%s'"%item)



        if "." in sitem:
            obj = relative_getobj(self, sitem)
            return obj

        # first look at locals
        try:
            value, _ = self._search(item, sitem)
        except KeyError:
            pass
        else:
            return _return(value)


        raise KeyError("'%s'"%item)


    @property
    def locals(self):
        return self._params


    def duplicate(self, *args, **kwargs):
        """ copy the plot func object

        any kwargs are added to the original kwargs
        The positional kwargs are unchange if not defined or set to
        null if the first argument is None

        pf = RecFunc("x", "y", color="color")

        # add 'marker' keyword but keep "x", and "y" as positional keyword substitution
        pf.duplicate( marker="marker")
        # redefine the positional arguments to "x", "y" and "z"
        pf.duplicate("x", "y", "z", marker="marker")
        # remove any positional argument:
        pf.duplicate(None, marker="marker")

        """


        new = self.__class__()

        (new.nposargs, new.args,
         new.substitutions, new.anyparams) = merge_args(self, args)


        new.fcall = self.fcall
        new.__doc__ = self.__doc__

        params = self.getrealkwargs(**kwargs)
        for a in self.posargnames:
            if a in self:
                params[a] = self[a]

        new.update(**params)

        new.set_caller(self.fcall)
        return new

    def _derive(self, parent):
        new = self.__class__()
        new.__doc__ = self.__doc__
        new.fcall = self.fcall

        #new.ids = self.ids # not good !!!
        new._parentinstance = self
        new.parent = parent
        new.nposargs = self.nposargs
        new.args = self.args
        new.substitutions = self.substitutions
        new.anyparams = self.anyparams

        if self._default_params:
            # default paramters can inerit from an parentinstance
            # but never from a parent.
            # need to copy the instance value here to eraze
            # the default value made by init
            new.locals.update({k:self.locals[k] for k in self._default_params})

        return new

    def derive(self, *args, **params):
        new = self._derive(None)

        (new.nposargs, new.args,
         new.substitutions, new.anyparams) = merge_args(self, args)

        new.update(**params)
        return new

    def _new_instance(self, parent):

        if not hasattr(parent, "__recobjects__"):
            parent.__recobjects__ = {}
        if self.ids in parent.__recobjects__:
            return parent.__recobjects__[self.ids]

        new = self.__class__()
        new.args = self.args
        new.nposargs   = self.nposargs
        new.substitutions = self.substitutions
        new.__doc__ = self.__doc__
        new.fcall = self.fcall

        new._parentinstance = self
        new.ids = self.ids

        if isinstance(parent, RecObject):
            new.parent= parent

        parent.__recobjects__[self.ids] = new
        return new


    if USE_WEAKREF:
        @property
        def parent(self):
            """ parent RecObject if any or None

            parent.recobj is recobj.parent


            parent is set with a weakref, if the parent object is dead, None is
            return and a warning is printed. To avoid unwanted warning use
            hasparent attribute.

            """
            parent = self._parent
            if parent:
                if isinstance(parent, weakref.ref):
                    parent = parent()
                    if parent is None:
                        print("Warning Parent object deleted")
                return parent

        @parent.setter
        def parent(self, parent):
            if isinstance(parent, weakref.ref):
                self._parent = parent
            elif parent:
                self._parent = weakref.ref(parent)
    else:
        @property
        def parent(self):
            """ parent RecObject if any or None """
            return self._parent

        @parent.setter
        def parent(self, parent):
            self._parent = parent



    @property
    def parentinstance(self):
        return self._parentinstance

    #def __del__(self):
    #    print("freeing ", self.ids)

    def __get__(self, parent, cl=None):
        if parent is None:
            return self
        return self._new_instance(parent)


    def __contains__(self, item):
        try:
            self[item]
        except KeyError:
            return False
        return True

    def __setitem__(self, item, value):
        self.locals[item] = value


    def __delitem__(self, item):
        del self.locals[item]


    def __call__(self, *args, **ikwargs):
        if not self.fcall:
            raise TypeError("Not callable")

        args = self.getargs(*args)
        kwargs = self.getkwargs(**ikwargs)
        for a,k in zip(args[self.nposargs:], self.kwargnames):
            if k in ikwargs:
                raise TypeError("got multiple values for keyword argument '%s'"%k)
            # remove the extra positional argument from the kwargs
            kwargs.pop(k,None)
        parent = self.parent # hold a parent reference here
        output = self.fcall(*args, **kwargs)
        return output

    def update(self, __d__={}, **kwargs):
        self.locals.update(__d__, **kwargs)

    def set(self, __d__={}, **kwargs):
        """ same as update but return the object """
        self.update(__d__, **kwargs)
        return self

    def setdefault(self, item , value):
        return self.locals.setdefault(item , value)

    def get(self, item, default=None):
        if item in self:
            return self[item]
        return default

    def add_prefix(self, prefix, arglist=True, first=False,
                   exclude=[]
                   ):
        if arglist is True:
            arglist = self.args
        substitutions = self.substitutions
        for arg in arglist:
            if arg in exclude:
                continue
            if arg in substitutions:
                sub = substitutions[arg]
                if isinstance(sub, list):
                    if first:
                        substitutions[arg] = [prefix+arg]+sub
                    else:
                        substitutions[arg] = sub+[prefix+arg]
                else:
                    if first:
                        substitutions[arg] = [prefix+arg, sub]
                    else:
                        substitutions[arg] = [sub, prefix+arg]
            else:
                if first:
                    substitutions[arg] = [prefix+arg, arg]
                else:
                    substitutions[arg] = [arg, prefix+arg]


    def pop(self, *args):
        largs = len(args)
        if (largs<1) or (largs>3):
            raise TypeError("pop expected at 1 to 3 arguments, got %d"%largs)

        if largs>1:
            if largs ==2:
                item , default, extern = args+(False,)
            else:
                item , default, extern = args

            local = self.locals
            if item in local:
                value = local[item]
                del local[item]
            else:
                if extern and item in self:
                    value = self[item]
                else:
                    value = default
            return value

        item, = args
        value = self[item]
        del self[item]
        return value

    def clear(self):
        self.locals.clear()


    @property
    def all(self):
        return self._getkwargs(False,{},self.args)

    @property
    def allreal(self):
        return self._getkwargs(True,{},self.args)


    def __iter__(self):
        return self.iter(n)

    def iter(self, _start_or_n_=None, _stop_=None, **kwargs):
        if _stop_ is None:
            n = _start_or_n_
            start = 0
        else:
            start = _start_or_n_
            n = _stop_

        # transform all iterables to cycle un less they are loop or cycle

        for k,v in kwargs.iteritems():
            isit, objit = _process_iterable(v)
            if isit:
                kwargs[k] = objit

        kwargs = self.getrealkwargs(**kwargs)

        for k in self.posargnames:
            try:
                kwargs[k] = self[k,]
            except KeyError:
                continue


        iterables = {}
        scalars = {}
        nit = 0
        for k,v in kwargs.iteritems():
            isit = _is_iterable(v)
            if isit:
                iterables[k] = iter(v)
                nit += isit == LOOP
            else:
                scalars[k] = v

        if n is None and not nit:
            # if n is None transform all iterables to loop so the
            # cycle will stop at the shortest iterable
            if iterables:
                iterables = {k:loop(getattr(v, "obj", v)) for k,v in iterables.iteritems()}
            else:
                raise TypeError("Cannot determine the iteration size")




        it = RecFuncIterator(self.duplicate, iterables, scalars, n, start)
        return it


    def _getargs(self, real , args):
        largs = len(args)
        lsargs = len(self.posargnames)

        if not real:
            args = [self._return_value(a) for a in args]
        else:
            args = list(args)

        if largs>=lsargs:
            return tuple(args)


        getitem = (lambda self,item: self[item,]) if real else (lambda self,item: self[item])

        for i,item in enumerate(self.posargnames[largs:]):
            if item is None:
                raise TypeError("Missing positional argument to execute, got %d"%largs)
            try:
                value = getitem(self,item)
            except KeyError:
                raise TypeError("Cannot substitute the %dth positional argument: '%s' is missing"%(i+largs+1,item))
            else:
                args.append(value)
        return tuple(args)

    parseargs = parseargs

    def getargs(self, *args):
        return self._getargs(False, args)

    def getrealargs(self, *args):
        return self._getargs(True, args)


    def _getkwargs(self, real, kwargs, arglist):
        if not self.anyparams:
            getitem = (lambda self,item: self[item,]) if real else (lambda self,item: self[item])
            if not real:
                kwargs = {k:self._return_value(value) for k, value in kwargs.iteritems()}

            for k in arglist:
                if k in kwargs:
                    continue
                try:
                    value = getitem(self,k)
                except KeyError:
                    pass
                else:
                    kwargs[k] = value
            return kwargs
        ################################################
        # All kwargs must be parsed
        ################################################
        params = self.locals.copy()
        if self.parentinstance:
            for k,v in self.parentinstance.all.iteritems():
                params.setdefault(k,v)
        if self.parent:
            for k,v in self.parent.all.iteritems():
                params.setdefault(k,v)
        if real:
            return params
        else:
            return {k:self._return_value(value) for k, value in params.iteritems()}


    def getkwargs(self, **kwargs):
        return self._getkwargs(False, kwargs,self.kwargnames)

    def getrealkwargs(self, **kwargs):
        return self._getkwargs(True, kwargs,self.kwargnames)

    def _get_value_info(self):
        all = self.all
        output = []
        for key in all:
            value, spath = self._search(key, self.substitutions.get(key,key))
            if isinstance(value, alias):
                try:
                    linked_value = self[key]
                except:
                    value = "{!r}".format(value)+" -> ?"
                else:
                    value = "{!r}".format(value)+" -> {!r}".format(linked_value)
            else:
                value = "{!r}".format(value)

            value = value if len(value)<70 else value.split("\n",1)[0][0:70]+" ..."
            output.append( (
                             spath,
                             key, value
                             )
                          )
        return output
    @property
    def info(self):
        print ("{self.__class__.__name__} function.".format(self=self))
        idt = " "*4
        print()
        print (idt+"Substitued Parameters :")
        print (_list_formater(self.args,70,idt+" "*4, self.nposargs))

        print()
        print (idt+"Function called :")
        try:
            finfo = self.fcall.func_name+inspect.formatargspec(*inspect.getargspec(self.fcall))
        except:
            finfo = str(self.fcall)


        print (idt+" "*4+finfo)
        try:
            fdoc = self.__doc__
        except:
            pass
        else:
            if fdoc:
                print(idt+"  "+" "*4+ fdoc.split("\n",1)[0].rstrip() )

        print()
        print (idt+"Curent Values : ")
        infos = self._get_value_info()
        if infos:
            print("\n".join([idt+INFMT.format(*inf) for inf in infos]))
        else:
            print(idt+" "*4+"None")
        print()


class RecFuncIterator(object):
    def __init__(self, duplicator, iterables, scalars, n=None, start=0):

        self.iterables = iterables
        self.scalars = scalars
        self.duplicator = duplicator

        self.count = 0
        self.n = n
        self.start = start

    def __iter__(self):
        #resete the iterables
        it = self.__class__(self.duplicator, self.iterables,
                            self.scalars, self.n, self.start)
        for i in range(it.start):
            it.skip()
        return it

    def skip(self):
        for it in self.iterables.itervalues():
            try:
                next(it)
            except StopIteration:
                break
        self.count += 1

    def next(self):
        if (self.n is not None) and (self.count>=self.n):
            raise StopIteration
        #pf = self.duplicator()

        nexts = {k:next(it) for k,it in self.iterables.iteritems()}
        #for k,it in self.iterables.iteritems():
        #    pf[k] = next(it)
        #pf.update(self.scalars)

        pf = self.duplicator(**dict(self.scalars, **nexts))

        self.count += 1
        return pf


class _loopbase_(object):
    def __str__(self):
        return "{name}({obj!r})".format(name=self.__class__.__name__,
                                    obj=self.obj
                                )
    def __repr__(self):
        return self.__str__()

class cycle(_loopbase_):
    def __init__(self, obj, cycles=100000):
        if inspect.isgenerator(obj):
            raise ValueError("cannot cycle on a generator object")
        self.obj = obj
        self.iterator = iter(obj)
        self.cycles = cycles
        self.cycle = 0

    def __iter__(self):
        return self.__class__(self.obj, self.cycles)

    def cnext(self):
        self.cycle = 0
        return next(self)

    def next(self):
        try:
            return next(self.iterator)
        except StopIteration:
            self.cycle += 1
            if self.cycle>self.cycles:
                raise StopIteration
            self.iterator = iter(self.obj)
            return next(self.iterator)


class fcycle(_loopbase_):
    def __init__(self, func, cycles=100000):
        if not hasattr(func, "__call__"):
            raise ValueError("func must be callable")

        self.func = func
        self.obj = func # for __str__ to works
        self.cycles = cycles
        self.cycle = 0

    def __iter__(self):
        return self.__class__(self.func, self.cycles)

    def cnext(self):
        self.cycle = 0
        return next(self)

    def next(self):
        if self.cycle>self.cycles:
            raise StopIteration
        self.cycle += 1
        return self.func()



class lcycle(_loopbase_):
    """
    lcycle is for RecFunc item object
    lcycle( iterable ) the first argument of the iterable is used
    in normal call of a RecFunc e.i. pf()  or pf[item]

    All other argument of the iterables are cycled when a iteration
    is made on the plot.

    example:
    pf = RecFunc("color")
    @pf.caller
    def pf(color=None):
        return color

    pf["color"] = lcycle(["black", "red", "blue", "green"])

    pf() # "black"
    pf() # "black"

    [p() for p in pf.iter(5)]
    # ['red', 'blue', 'green', 'red', 'blue']
    """
    def __init__(self, obj, cycles=100000):
        if inspect.isgenerator(obj):
            raise ValueError("cannot cycle on a generator object")

        self.obj = obj
        self.iterator = iter(obj)
        try:
            self.cvalue = next(self.iterator)
        except StopIteration:
            raise ValueError("The iterator must be iterable at least ones")

        self.cycles = cycles
        self.cycle = 0

    def __iter__(self):
        return self.__class__(self.obj, self.cycles)

    def cnext(self):
        return self.cvalue

    def next(self):
        try:
            return next(self.iterator)

        except StopIteration:
            self.cycle += 1
            if self.cycle>self.cycles:
                raise StopIteration
            self.iterator = iter(self.obj)
            # skip the first one
            next(self.iterator)
            return next(self.iterator)


class loop(_loopbase_):
    def __init__(self, obj):

        self.obj = obj
        self.iterator = iter(obj)

    def __iter__(self):
        return self.__class__(self.obj)

    def cnext(self):
        return self.next()

    def next(self):
        return  next(self.iterator)

class alias(object):
    def __init__(self, param, func=None):
        self.param = param
        self.func  = func
    def get(self, obj):
        if self.func:
            return self.func(obj,self.param)
        return obj[self.param]

    def __str__(self):
        if self.func:
            return "alias('%s', %s)"%(self.param, self.func)
        return "alias('%s')"%self.param

    def __repr__(self):
        return self.__str__()






loopers = {LOOP:loop, LCYCLE:lcycle, CYCLE:cycle, FCYCLE:fcycle}

def __test__():
    global p0, P0, ip0, acumulator1
    acumulator1 = 0
    def test(num, shouldbe, valis):
        s = "{0:4.1f} {1:>8} == {2:<8}    {3}".format(num, shouldbe,  valis, shouldbe==valis)
        print(s)

    class P0(RecObject):
        __doc__ = RecObject.__doc__
        @staticmethod
        def finit(plot, **kwargs):
            plot.update(kwargs)
            plot["zoro"] = 100

        class P00(RecObject):
            def finit(self, plot, **kwargs):
                plot.update(kwargs)
                #print("Init p00")
            class P000(RecObject):
                pass
            class P001(RecFunc):
                pass
            p000 = P000()
            p001 = P001()
        p00 = P00()
        p00["fmt"] = "b+"

    p0 = P0()
    p0["color"] = "red"

    test(1, p0["color"], "red")
    test(2, p0.p00["color"], "red")
    test(2.1, p0.p00["color"], "red")

    test(3, p0.p00.p001["color"], "red")
    test(3.1, p0.p00["fmt"], "b+")


    ip0 = p0()
    pp0 = P0()

    test(4, ip0["color"], "red")
    ip0["color"] = "blue"
    test(4, ip0["color"], "blue")
    test(5, p0["color"], "red")

    p0.p00["color"] = "violet"
    test(6.1, p0.p00["color"], "violet")
    test(6.2, p0().p00["color"], "violet")
    test(6.3, p0().p00()["color"], "violet")
    cp = p0().p00()
    cp["color"] = "blue"
    test(7, cp["color"], "blue")
    test(8, p0().p00()["color"], "violet")

    test(9, p0.p00.p001["color"], "violet")
    test(10, p0["color"], "red")

    p0.p00["fmt"] = "r-"
    test(11, p0.p00()["fmt"], "r-")
    test(11.2, p0.p00.p000()["fmt"], "r-")

    P0.P00.p000["style"] = "--"
    p0.p00.p000["style"] = "***"
    test(12, p0.p00.p000["style"], "***")
    test(13, ip0.p00.p000["style"], "--")

    test(15, p0().p00.p000["style"], "***")

    test(16, p0.p00.p000["style"], "***")
    test(17, pp0.p00.p000["style"], "--")

    test(18, p0().p00.p000["style"], "***")
    test(19, pp0().p00.p000["style"], "--")

    import gc

    def inc1():
        global acumulator1
        acumulator1 += 1
    gc.enable()
    for i in range(1000):
        tc = P0()
        wr = weakref.ref(tc , lambda wr : inc1())
        _ = tc.p00


    #_ = tc.p00
    #del _
    #del tc
    gc.collect()
    print(acumulator1)


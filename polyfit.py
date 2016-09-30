from __future__ import division, absolute_import, print_function
import numpy as np
from . import plotfuncs as pfs
from .plotclasses import (XYPlot, xyplot, XYFit)

from .recursive import KWS, alias
from .base import PlotFactory


class PolyFit(XYPlot):
    get_label = pfs.PlotFunc(0, "coeff","label_fmt", "label_x", "xlabel")
    @get_label.caller
    def get_label(coeff=None, label_fmt="%g", label_x=None, xlabel=None):
        """ PlotFunc. Return a string representation of the fitted polynome

        As it is a PlotFunc all args can inerit from the parent PolyFit
        Args:
            coeff (list of float) : polynome coefficient, highest first
            label_fmt (string) : python format with the '%' of coeeficients. Can also be
                a list of string with the same size than coeff
            label_x (Optional[string]) : the string representation of x data default is 'x'
                if label_x is None a short representation of xlabel (if present) is taken

        Return :
            text (string):  string representation of the polynome


        """
        if coeff is None: return None
        if label_x is None:
            label_x = "x"

        return polyfitcoef2text(coeff, label_fmt, label_x)

    def get_repr(self, dim):
        out = ""
        for i,c in zip(range(dim+1),list("abcdefghijklmnopqrstuvwxyz")):
            out += ("+" if i else "")+c+("x^%d"%i if i else "")
        return out

    @property
    def x(self):
        return self["x"] if self.isinitialized else None
    @property
    def y(self):
        return self["y"] if self.isinitialized else None
    @property
    def coeff(self):
        return self["coeff"] if self.isinitialized else None

    @property
    def label(self):
        return self.get_label()

                
    @staticmethod
    def finit(plot, *args, **kwargs):
        """ PlotFactory object where a polynomial fit is performed

        As all PlotFactory object, all parameters can inerit from a parent plot if any.

        Args:
          Used for the fit:

            x (array-like): origin x data
            y (array-like): y data to fit  y(x)~polynome(x)
            dim (Optional[int]) : polynome dimention, default is 1

            xrange (Optional[2tuple]) : (min, max) value of x, default is (None, None)
            yrange (Optional[2tuple]) : (min, max) value of y, default is (None, None)

          Processed for plot purpose:

            xmin (bool/float) : xmin of the fit plot.
                if True (default) that the min of the original x data
                if None or False that the min of the cliped x data (by xrange and yrange)
            xmax (bool/float) : see xmin

            npoints (Optional[int]): number of point to plot the fit regurlaly expaced
                between xmin and xmax.
                if None an automatic (depending of polynome dimention) is provided

            label (Optional[string/bool]):
                if string : the fit label, for legends
                if True : write automaticaly the polynome label with the get_label method
            label_fmt (Optional[string]) : is the polynome coeeficient format, default is "%g"
            label_x (Optional[string]) : the string representation of x data default is 'x' or
                try a shorten version of xlabel parameter (e.g "t [seconds]"->"t")

            go (list) : actions to perform after initialisation (see Plot help)
                e.g. go=["line"] plot the line directly

            **params : any other plot parameters (e.g. color, linestyle etc ...)

        Altered Parameters:
            x (array) : np.linspace(xmin,xmax, npoints)
            y (array) : polynome(x)
            coeff (list) : polynome coefficients
            xmin, xmax, npoints are updated if original is None
            ymin : set to 0
            ymax : set to y (for vlines)
            xerr, yerr : set to None

        Example:
            >>> import smartplotlib as splt
            >>> myfit = splt.polyfit.derive(dim=2, color="red", linestyle="--")
            >>> axes = splt.subplot()
            >>> x = np.arange(100);
            >>> yerr = np.random.rand(100)*2.0*x
            >>> y = x*x + yerr
            >>> axes.errorbar(x,y, yerr=yerr, linestyle="None")

            >>> myfit(x, y).plot()
            >>> myfit(x, y, xrange=(1,30), dim=1, color="green", xmax=100).plot()

        """
        plot.update(kwargs.get(KWS, {}), **kwargs)

        (x, y, dim, xrange, yrange,
         xerr, yerr, xmin,
         xmax, npoints, fin, fout, fcoeff) = plot.parseargs(args, "x", "y", "dim",
                                  "xrange", "yrange",
                                  "xerr", "yerr", "xmin",
                                  "xmax", "npoints", "fin", "fout", "fcoeff", 
                                  x=plot.locals.get("_x_", None), 
                                  y=plot.locals.get("_y_", None),
                                  dim=1, xrange=None, yrange=None,
                                  xerr=None, yerr=None,
                                  xmin=None, xmax=None,
                                  npoints=None,fin=None, fout=None, fcoeff=None
                                  )
        if y is None:
            raise ValueError("missing y data")
        if x is None:
            x = np.arange(len(y))    
        
        plot.update(_x_ = x, _y_ = y) #store the original data for a call back              

        xmin, xmax, npoints, (xc,yc,xerrc,yerrc) = polyfit_prepare(x, y,
                                                       dim=dim, xrange=xrange,
                                                       yrange=yrange, xmax=xmax,
                                                       xerr=xerr,yerr=yerr,
                                                       xmin=xmin, npoints=npoints
                                                      )

        if fin:
            xc, yc = fin(plot, xc, yc)

        polycoeff = _mpolyfit(np.array(xc),np.array(yc),dim)    

        if fcoeff:
            coeff = fcoeff(plot, polycoeff)
        else:
            coeff = list(polycoeff)    

        label = plot.get("label", None)

        if label is True:
            label_formater = plot.get("label_formater", None)
            if label_formater:
                plot["label"] = label_formater(plot,coeff)
            else:
                plot["label"] = plot.get_label(coeff)

        plot["coeff"] = coeff
        plot["polycoeff"] = polycoeff
        plot["xmin"] = xmin
        plot["xmax"] = xmax
        plot["npoints"] = npoints

        x = alias(
                  lambda p: np.linspace(p["xmin"],p["xmax"],p["npoints"]),
                  "-> linspace(xmin, xmax, npoints)"
                  )
        plot["x"] = x

        if fout:
            y = alias(lambda p: fout(p, p["x"], p['coeff']),
                   "-> y_fit(x)")
        else:    
            y = alias(lambda p: get_model(p["x"], p['coeff']),
                      "-> y_fit(x)")
        
        plot["y"] = y
        plot["ymin"] = 0
        plot["ymax"] = y

        plot.update(xerr=None, yerr=None)

        plot.goifgo()





#################################################################
#
# Polynome fitting engine
#
##################################################################


class NotEnoughData(ValueError):
    pass

def _cliptest(data, datarange=None):
    """ return boolean array, element are True if data in range """
    dmin, dmax = (None, None) if datarange is None else datarange
    test = np.ones(data.shape, dtype=np.bool)
    if issubclass(type(data),np.ma.MaskedArray):
        mask = data.mask
        test *= ~mask
    if dmin is not None:
        test *= data>=dmin
    if dmax is not None:
        test *= data<=dmax
    return test

def _cliptest_values(data_range, *args, **kwargs):
    """ return boolean array, element are True if all data are within range"""
    data, datarange = data_range
    test = _cliptest(data, datarange)
    for data, datarange in args:
        test *= _cliptest(data, datarange)
    return test

def clip(data_range, *args, **kwargs):
    """ clip several data arrays from a several range

    each input array (x1,x2,x3,...) has is pair of range (min,max) (r1,r2,r3,..)
    the returned arrays will be shorten to all element satifaying :
       test = x1>=r1[0] & x1<=r1[0] & x2>=r2[0] & x2<=r2[0] & ...


    Args:
        *args : each args must be a 2 tuple (data,(min,max)) where data is
            the array and min, max the clip ranges.
            min and max can be None in range -> no cut in this made.
        additional (Optional[list]) : a list of additional array that will be
            truncated without constrains on their data.

    Returns:
        *cliped : truncated arrays, the lenght of *cliped is len(args)+len(additional)

    Examples:

        x, y, xerr, yerr = clip( (x,(0,100)), (y,(None,10)), additional=[xerr, yerr])
    """
    additional = kwargs.pop("additional", [])
    if len(kwargs):
        raise KeyError("take only additional= as keyword argument")

    test = _cliptest_values(data_range, *args)
    out = [ data_range[0][test]  ]
    for data, dr in args:
        out.append( data[test])
    for data in additional:
        out.append( data[test] if data is not None else None)
    return tuple(out)

def _mpolyfit(x,y,dim):
    if dim==0: return y.mean()
    if len(x)<(dim+1):
        raise NotEnoughData("Not enought point to fit")

    xx = np.vstack([ pow(x,e) for e in np.arange(dim+1)[::-1]])
    w = np.linalg.lstsq( xx.T, y)
    return w[0]

def get_model(x, coef):
    """ get_model(x, coef) return polynome(x)

    where poynome is described by its coeficients.
    Args:
        x (array-like) : x data
        coef (list of float) : polynome coefficient (higher first)

    Returns:
        y (array):  polynome(x)

    Examples:
        >>> get_model(x, [4.5, 2.3, 4.5])
       is
        >>> 4.5*x**2 + 2.3*x + 4.5

    """
    y = np.zeros_like(np.asarray(x))
    y[:] = coef[-1]
    dim = len(coef)-1
    for i in range( dim):
        y += coef[i]*x**(dim-i)
    return y


def polyfit_prepare(ix,iy, dim=1, xrange=None, yrange=None,
            xerr=None, yerr=None,
            xmax=True, xmin=True, npoints=None
            ):
    """ Perform a polynomial fit on x/y return coeff and info to plot


    Args:
      Used for fits:
        x (array-like): origin x data
        y (array-like): y data to fit  y(x)~polynome(x)
        dim (Optional[int]) : polynome dimention, default is 1

        xrange (Optional[2tuple]) : (min, max) value of x, default is (None, None)
        yrange (Optional[2tuple]) : (min, max) value of y, default is (None, None)

      Processed for plot purpose:
        xerr (Optional[array]) : Not used for the fit (sorry) but truncated
            version is returned
        yerr (Optional[array]) : Not used for the fit (sorry) but truncated
            version is returned

        xmin (bool/float) : if float, this is just returned as it is,
            if True (default) that the min of the original x data
            if None or False that the min of the cliped x data (by xrange and yrange)
        xmax (bool/float) : see xmin

        npoints (Optional[int]): if provided returned has it is, else a number
            of points to plot the polynome corectly is returned (for dim=1, npoints=2)

    Returns:
        xmin : the xmin, for plot (see above)
        xmax : the xmax, for plot (see above)
        npoints : number of points to plot
        (x,y,xerr,yerr) : the cliped version of input data

    Raises:
        NotEnoughData : (subclass of ValueError) when there is not enough points
            to perform the fit (e.i. when only 2 points are available for dim=2)

    """

    ix = np.asarray(ix)
    iy = np.asarray(iy)

    if not hasattr(xerr, "__iter__"):
        if  not hasattr(yerr, "__iter__"):
            x,y = clip((ix,xrange),
                       (iy,yrange))
        else:
            x,y,yerr  = clip((ix,xrange),
                             (iy, yrange),
                             additional=[np.asarray(yerr)]
                             )
    elif not hasattr(yerr, "__iter__"):
        x,y, xerr = clip((ix,xrange),
                         (iy,yrange),
                         additional=[np.asarray(xerr)]
                         )
    else:
        x,y,xerr, yerr = clip((ix,xrange),
                              (iy,yrange),
                               additional=[np.asarray(xerr),
                                           np.asarray(yerr)]
                              )

    
    if npoints is None:
        npoints = 2 if dim<2 else 1000

    if xmin is True:
        xmin = ix.min()
    elif xmin in [None,False]:
        xmin = x.min()

    if xmax is True:
        xmax = ix.max()
    elif xmax in [None,False]:
        xmax = x.max()

    return xmin, xmax, npoints, (x, y, xerr, yerr)



def polyfitcoef2text(coef, fmt="%g", x="x"):
    """ return a string representation of a polynome described by its coefficients

    Args:
        coef (list of float) : polynome coefficient, higher first
        fmt (string) : python format with the '%' of coeeficients. Can also be
            a list of string with the same size than coeff
        x (Optional[string]) : the string representation of x data default is 'x'

    Return :
        text (string):  string representation of the polynome
    """
    out = ""
    dim = len(coef)
    if isinstance(fmt, basestring):
        fmt = [fmt]*dim

    for i,c in enumerate(coef):
        if (dim-1)==0:
            xs = ""
        elif (dim-1)==1:
            xs= x
        else:
            xs = "%s^%d"%(x,dim-1)
        out += ("%s"+fmt[i]+" %s ")%( "-" if c<0.0 else "+" if i else "", np.abs(c), xs )
        dim -= 1
    return out






###
# REcord classes 
# Two same versions, one is explicitely a linearfit
###
polyfit   = PolyFit(_example_=("polyfit", None))
linearfit = PolyFit(dim=1, npoints=2, _example_=("polyfit", None))

def inv_formater(plot, coeff):
    label_fmt, label_x, xlabel = plot.parseargs([], "label_fmt", "label_x", "xlabel", 
                                                 label_fmt="%g", label_x=None, xlabel=None
                                                )
    if label_x is None: 
        label_x = "x"
    return   "1/ ("+polyfitcoef2text(coeff, label_fmt, label_x)+")"

invfit = PolyFit( fin=lambda plot,x,y: (x, 1./y), 
                  fout=lambda plot,x,coeff:1./(get_model(x,coeff)), npoints=100, dim=1, 
                  label_formater = inv_formater
                  )
invfit.finit.__doc__ = """plotfactory fit y = 1/(a*x+ b).  see fitpoly for more options """

###########
def sqrt_formater(plot, coeff):
    label_fmt, label_x, xlabel = plot.parseargs([], "label_fmt", "label_x", "xlabel", 
                                                 label_fmt="%g", label_x=None, xlabel=None
                                                )
    if label_x is None: 
        label_x = "x"
    return   "sqrt("+polyfitcoef2text(coeff, label_fmt, label_x)+")"

sqrtfit = PolyFit( fin=lambda plot,x,y: (x, y**2), 
                  fout=lambda plot,x,coeff:np.sqrt(get_model(x,coeff)), npoints=100, dim=1, 
                  sqrt_formater = sqrt_formater
                  )
sqrtfit.finit.__doc__ = """plotfactory fit y = sqrt(a*x+ b).  see fitpoly for more options """





def expfcoeff(plot, coeff):
    origin = plot.get("origin", 0.0)

    if len(coeff)>2:
        raise ValueError("For expo fit dim should be 1 or 0")
    if len(coeff)==2:
        alpha, amp = [coeff[0], np.exp(coeff[1]+origin*coeff[0]) ]
    else:
        alpha, amp = [1.0, np.exp(coeff[0]+origin)]
    return alpha, amp

def expfout(plot, x, coeff):
    if len(coeff)>2:
        raise ValueError("For exp fit dim should be 1 or 0")
    origin = plot.get("origin", 0.0)
    return coeff[1]*np.exp(coeff[0]*(x-origin))
        
def exp_formater(plot, coeff):
    label_fmt, label_x, xlabel = plot.parseargs([], "label_fmt", "label_x", "xlabel", 
                                                 label_fmt="%g", label_x=None, xlabel=None
                                                )
    if label_x is None: 
        label_x = "x"
    origin = plot.get("origin", 0.0)

    coeff = [label_fmt%c for c in coeff]

    if origin:            
        return  "{1} Exp({0}*({x}-{origin}))".format(*coeff, origin=origin, x=label_x)    
    return "{1} Exp({0}*({x}))".format(*coeff, x=label_x)    
            

expfit = PolyFit( fin = lambda plot,x,y: (x, np.log(y)), 
                  fcoeff = expfcoeff,   
                  fout   =  expfout,
                  npoints=100, dim=1, 
                  label_formater = exp_formater
                  )


def gaussfcoeff(plot, coeff):
    if len(coeff)!=3:
        raise ValueError("For gauss fit dim should be 2")    
    sigma = 1./coeff[0]    
    xo = -0.5*sigma*coeff[1]
    A = np.exp( coeff[2] - xo*xo/sigma)
    return [sigma, x0, A]

def gaussfout(plot, x, coeff):
    if len(coeff)!=3:
        raise ValueError("For gauss fit dim should be 2")    
    sigma, xo, A = coeff    
    return A*np.exp((x-x0)**2/sigma)        

def gauss_formater(plot, coeff):
    label_fmt, label_x, xlabel = plot.parseargs([], "label_fmt", "label_x", "xlabel", 
                                                 label_fmt="%g", label_x=None, xlabel=None
                                                )
    if label_x is None: 
        label_x = "x"
    orgigin = plot.get("origin", 0.0)

    coeff = [label_fmt%c for c in coeff]



    return  "{2} Exp( ({x}-{1})^2 / {0} )".format(*coeff, x=label_x)                

gaussfit = PolyFit(
                  fin = lambda plot,x,y: (x, np.log(y)), 
                  fcoeff = gaussfcoeff,    
                  fout   =  gaussfout,
                  npoints=100, dim=2, 
                  label_formater = gauss_formater
                  )

###
# add instances to XYPlot
XYPlot.linearfit = linearfit
XYPlot.polyfit = polyfit

XYFit.inverse = invfit
XYFit.sqrtfit = sqrtfit
XYFit.linear = linearfit
XYFit.polynome = polyfit
XYFit.exp  = expfit
XYFit.gaussfit  = gaussfit


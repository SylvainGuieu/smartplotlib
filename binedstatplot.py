from __future__ import division, absolute_import, print_function

from . import plotfuncs as pfs
from .recursive import KWS, alias
from .base import Plot
import numpy as np
from .plotclasses import (DataPlot, xyplot, XYPlot, DataXYPlot,
                          dataxyplot
                          )

from .histogram import _makebinedstatplot

# scipy.stats is imported at the end


##
# define som basic stat functions
def _plur_std(value, m=None):
    m = np.mean(value) if m is None else m
    return m+np.std(value)

def _minus_std(value, m=None):
    m = np.mean(value) if m is None else m
    return m-np.std(value)

def _medplur_std(value, m=None):
    m = np.median(value) if m is None else m
    return m+np.std(value)

def _medminus_std(value, m=None):
    m = np.median(value) if m is None else m
    return m-np.std(value)

def _std(value):
    return np.std(value)


def _stdsmed(value):
    m = np.median(value)
    std = np.std(value)
    return [m, std]


# list of functions handled by binned_statistic
handled = ["std", "stdmean", "stdmed", "mean", "median", "count", "sum"]


# lookup table for other functions
fstat_lookup = {
                "+std":_plur_std,
                "-std":_minus_std,
                "mean+std":_plur_std,
                "mean-std":_minus_std,
                "med+std":_plur_std,
                "med-std":_minus_std
}
# lookup for relevant error computation
# of the statistics
fstat_err_lookup = {
                    "mean":   "std",
                    "median": "std",
                    "count": lambda v: sqrt(len(v))
                   }


def _statbin(x, values, fstat="mean", bins=10,
             range=None, binerror=False,
             centered=True, sigma=1.0):
    """ return the binned_statistic from scipy.stats
    return bins, stats, error

    stats can is a list of statistic, for instance if fsat="std"
    it is 2 stats [mean+std*sigma, mean-std*sigma]
    default sigma is one.

    """
    ## if already handled by binned_statistic or by this func do nothing
    # else look in lookup

    if isinstance(fstat, basestring) and (fstat not in handled):
        try:
            fstat = fstat_lookup[fstat]
        except KeyError:
            raise ValueError("'%s' is not a valid function name should be one of %s"%(fstat,
                             "'"+"', '".join(set(handled+fstat_lookup.keys()))+"'"
                             ))
    # if count bineerror does not make sens
    if (fstat is "count") and binerror:
      binerror = False

    stat, bins, _ = binned_statistic(x, values, fstat, bins, range)
    if fstat in fstat_err_lookup:
        # compute errors if we can
        stat_err, _, _ = binned_statistic(x, values, fstat_err_lookup[fstat], bins, range)
        stat_err *= sigma
        if binerror:
          # if binederror we need also the histogram
          N, _, _ = binned_statistic(x, values, "count", bins, range)
          stat_err = stat_err/np.sqrt(N)

    else:
      stat_err = None

    return bins, stat, stat_err

@dataxyplot.decorate(_example_=("binedstat",None))
def binedstat(plot, *args,**kwargs):
    """ initiate a plot for y axis bined statistic

    All parameters  can be substitued from the parent plot if any

    Parameters:
    -----------
      data  : the *Y* data on which ftat will be applied for each bins

      indexes  : the *X* data which will be binned default, if
        None it is np.arange(data.size)

      fstat : can be on of the following:
          "mean" (default), "median", "min", "max"
          "std" or "stdmean" -> two lines around the mean separated to +/-std*sigma
          "stdmed" -> two std lines arouond the median
          Or any user method that takes an array and return a scalar

      bins : int or sequence of scalars, optional
          If `bins` is an int, it defines the number of equal-width
          bins in the given range (10, by default). If `bins` is a sequence,
          it defines the bin edges, including the rightmost edge, allowing
          for non-uniform bin widths.

      min, max : the minimum and maximum for indexes. None is np.min() or np.max()

      sigma : sigma number for std lines and errorbars

      centered : if True the points are bin centered
            if False plot all the bin edges, the 2 first point will be the
            same then

      binerror : if False (default), errors are errors are std, the error
           on a single value in that bin.
           if True the error is the error of the bin, e.i.: std/sqrt(count)

      go : a go list to execute after creation (see Plot doc)
        example ["line", "fill"]

    Affected Plot Parameters:
    -----------------------
    if direction == "y" (default)
      "x"  : the bins x-coordinates
      "y"  : the statistic data.
      "y1" : the second statistic data if any.
      "yerr" : the statistic error if relevant
      "xerr" : set to None

    if direction == "x"
      "y"  : the bins x-coordinates
      "x"  : the statistic data.
      "x1" : the second statistic data if any.
      "xerr" : the statistic error if relevant
      "yerr" : set to None


    Attributes:
    ----------
     TODO list of attributes

     line() : plot the computed lines (all kwargs of plt.plot)

     errorbar() : plot error bars if relevant  (kwargs of plt.errorbar)

     fill() : fill between the two lines if relevant (e.g. if ftat='std')

    """

    plot.update(kwargs.pop(KWS,{}),**kwargs)

    (data, indexes,  fstat, bins,
     _min, _max, sigma, binerror
          ) = plot.parseargs(args,
                             "data", "indexes",
                             "fstat","bins",
                             "min", "max","sigma",
                             "binerror",
                             fstat=np.mean, bins=10,
                             min=None, max=None,
                             sigma=1.0,centered=True,
                             binerror=False
                           )


    di, dd = plot._get_direction()

    data = np.asarray(data).flatten()
    if indexes is None:
      indexes = np.arange(data.size)
    else:
      indexes = np.asarray(indexes)

    _range = (np.min(indexes) if _min is None else _min, np.max(indexes) if _max is None else _max)

    bins, stats, err= _statbin(indexes, data, fstat=fstat, bins=bins, range=_range,
                               binerror=binerror,
                               sigma=sigma
                               )

    _makebinedstatplot(plot, stats, bins, err)
    plot.update(data=data,indexes=indexes)
    plot.goifgo()
    return



try:
    from scipy.stats import binned_statistic
except:
    @statplot.decorate()
    def binedstat(plot, *args,**kwargs):
        raise TypeError("This function needs scipy.stats.binned_statistic")


#####
# add instances to relevant classes

DataPlot.binedstat = binedstat

ybinedstat = binedstat.derive(data=alias("y"), indexes=alias("x"), direction="y")
xbinedstat = binedstat.derive(data=alias("x"), indexes=alias("y"), direction="x",
                             _example_ = ("xbinedstat", None)
                             )

XYPlot.ybinedstat = ybinedstat
XYPlot.xbinedstat = xbinedstat





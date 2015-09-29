from __future__ import division, absolute_import, print_function

from . import plotfuncs as pfs
from .recursive import  KWS, alias
from .plotclasses import (DataPlot, DataXYPlot, ScalarPlot, scalarplot,
                          XYPlot, ImgPlot
                          )

import numpy as np



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

fstat_lookup = {"mean":np.mean,
                "median":np.median,
                "min":np.min,
                "max":np.max,
                "std":np.std,
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
                    "mean": np.std,
                    "median": np.std
                   }


def _compute_stat( value, fstat):
        if isinstance( fstat, basestring):
            try:
                fstat = fstat_lookup[fstat]
            except KeyError:
                raise ValueError("fstat '%s' not valid "%fstat)
        return fstat(value)





@scalarplot.decorate()
def stat(plot, *args, **kwargs):

        plot.update(kwargs.pop(KWS,{}),**kwargs)
        (data, fstat) = plot.parseargs(args, "data", "fstat",
                                       fstat="mean")

        di, dd = plot._get_direction()

        value = _compute_stat(data, fstat)
        #if isinstance(fstat, basestring) and fstat[:3]=="std":
        #    sigma = plot.get("sigma", 1.0)
        #    m,rms = value
        #    value = [m-rms*sigma, m+rms*sigma]


        plot["value"] = value
        #plot["lines"] = [value]
        #plot[dd] = alias("lines")

        last = plot.get("last",None)

        # save now the curent in last
        plot["last"] = value
        if last is not None:
            # the last in previous
            plot["previous"] = last

        indexes = plot.get("indexes", None)
        if indexes is not None:
            plot.update( min=np.min(indexes),
                         max=np.max(indexes)
                        )
            plot[dd+"min"] = alias("min")
            plot[dd+"max"] = alias("max")






ystat = stat.derive(data=alias("y"), indexes=alias("x"),
                    direction="y"
                   )
xstat = stat.derive(data=alias("x"), indexes=alias("y"),
                    direction="x"
                   )

median= stat.derive(fstat="median")
xmedian = xstat.derive(fstat="median")
ymedian = ystat.derive(fstat="median")

mean = stat.derive(fstat="mean")
xmean = xstat.derive(fstat="mean")
ymean = ystat.derive(fstat="mean")

min = stat.derive(fstat="min")
xmin = xstat.derive(fstat="min")
ymin = ystat.derive(fstat="min")

max = stat.derive(fstat="max")
xmax = xstat.derive(fstat="max")
ymax = ystat.derive(fstat="max")

std = stat.derive(fstat="std")
ystd = ystat.derive(fstat="std")
xstd = xstat.derive(fstat="std")


######
# add instances to XPlot and YPlot and _XYPlot
# duplicate to have both version of .xsomething .something in XPlots

XYPlot.ystat = ystat
XYPlot.xstat = xstat
XYPlot.xmedian = xmedian
XYPlot.ymedian = ymedian
XYPlot.xmean   = xmean
XYPlot.ymean   = ymean
XYPlot.xmin    = xmin
XYPlot.ymin    = ymin
XYPlot.xmax    = xmax
XYPlot.ymax    = ymax
XYPlot.ystd    = ystd
XYPlot.xstd    = xstd

DataPlot.stat   = stat
DataPlot.median = median
DataPlot.mean   = mean
DataPlot.min    = min
DataPlot.max    = max
DataPlot.std    = std

DataXYPlot.stat   = stat
DataXYPlot.median = median
DataXYPlot.mean   = mean
DataXYPlot.min    = min
DataXYPlot.max    = max
DataXYPlot.std    = std

ImgPlot.stat   = stat
ImgPlot.median = median
ImgPlot.mean   = mean
ImgPlot.min    = min
ImgPlot.max    = max
ImgPlot.std    = std







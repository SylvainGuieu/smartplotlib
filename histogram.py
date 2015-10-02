from __future__ import division, absolute_import, print_function
from .recursive import KWS, alias
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from .plotclasses import (DataPlot, dataplot, XYPlot, xyplot,
                          ImgPlot, XYZPlot, xyzplot
                         )

import numpy as np



import matplotlib.cbook as cbook
import six

histogram = xyplot.derive()

def _statbin(x, values, fstat="mean", bins=10,
             range=None, binerror=False,
             centered=True, sigma=1.0):
    """ return the binned_statistic from scipy.stats
    return bins, stats, error, count

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
          N, _, _ = binned_statistic(x, values, count, bins, range)
          stat_err = stat_err/np.sqrt(N)

    else:
      stat_err = None

    return bins, stat, stat_err, count




@histogram.initier
def histogram(plot, *args, **kwargs):
    plot.update(kwargs.pop(KWS,{}), **kwargs)

    (data, bins, bin_range, weights) = plot.parseargs(args,
             "data", "bins", "range",  "weights",
             bins=10, range=None,  weights=None)

 # NOTE: the range keyword overwrites the built-in func range !!!
    #       needs to be fixed in numpy                           !!!

    # Validate string inputs here so we don't have to clutter
    # subsequent code.

    density = plot.get("density", False)

    binsgiven = (hasattr(bins, "__iter__") or bin_range is not None)
    if not binsgiven:
        bin_range = (np.min(data), np.max(data))


    m, bins = np.histogram(data, bins, weights=weights, range=bin_range,
                           density=density
                          )
    if density:
        ## TODO: compute errorbars for density == True
        err = None
    else:
        err = np.sqrt(m)
    m = m.astype(float)  # causes problems later if it's an int

    plot["data"] = data # set the data, in case it was an alias for instance
    _makebinedstatplot(plot, m, bins, err)
    plot.goifgo()

def _makebinedstatplot(plot, m, bins, err):

    (cumulative, bottom,  align,
    orientation, rwidth, log,
    stacked, rsep, roffset, amplitude, count) = plot.parseargs([],
             "cumulative", "bottom",  "align",
             "orientation", "rwidth", "log",
              "stacked", "rsep", "roffset", "amplitude","count",
             bins=10, range=None,  weights=None,
             cumulative=False, bottom=None, align='mid',
             orientation='vertical', rwidth=1.0, log=False,
             stacked=False, rsep=None, roffset=0.0,
             amplitude=1,
             count=0
             )
    if rsep is None:
        rsep = rwidth

    if stacked:
        try:
            last = plot["last"]
        except KeyError:
            raise ValueError("cannot stack histogram, need the 'last' parameter")
        bottom = last
        m += last

    lasty = plot.get("lasty", None)

    #di index dd data can be "x", "y" or "y", "x"
    di, dd = plot._get_direction()

    totwidth = np.diff(bins)

    if rwidth is not None:
        dr = min(1.0, max(0.0, rwidth))
    else:
        dr = 1.0

    if not stacked:
        boffset = (rsep*count+roffset)*totwidth
    else:
        boffset = roffset*totwidth


    width = dr*totwidth


    realx = (bins[:-1]+bins[1:])/2.
    if align in ['mid', "center"]:
        xbins = realx
    elif align == 'right':
        xbins = (realx+(totwidth*(1.-dr))/2.)
    else:
        xbins = (realx-(totwidth*(1.-dr))/2.)

    if bottom is None:
        bottom = np.zeros(len(m), np.float)
    if stacked:
        height = m - bottom
    else:
        height = m

    #xbin = (bins[:-1]+bins[1:])/2.
    oxbins = xbins+boffset

    hist_plot = height*amplitude

    plot.update({di:oxbins, dd:hist_plot,
                 dd+"min":0, dd+"max":alias("y"),
                 dd+"err":err
                },
                hist=m, bins=bins,
                last=alias("y"),
                lasty=alias("y"),
                count=count+1,
               )
    plot.step.update(where="mid")


    plot.bar.update(align="center",
                    edge=oxbins,
                    height=hist_plot, width=width,
                    base=bottom, rwidth=1.0,
                    yerr=None, xerr=None
                   )
    plot.fillstep.update(x=realx)

    plot.fill_between.update(indexes=xbins,
                             data1=alias("y") if lasty is None else lasty,
                             data2=alias("y")
                            )


    #if di == "x":
    #    plot.update(left=alias("edge"), bottom=alias("base"),
    #                height=alias("length"))
    #else:
    #    plot.update(left=alias("base"), bottom=alias("left"),
    #                height=alias("length"))



    # these define the perimeter of the polygon
    x = np.zeros(4 * len(bins) - 3, np.float)
    y = np.zeros(4 * len(bins) - 3, np.float)

    x[0:2*len(bins)-1:2], x[1:2*len(bins)-1:2] = bins, bins[:-1]
    x[2*len(bins)-1:] = x[1:2*len(bins)-1][::-1]

    if bottom is None:
        bottom = np.zeros(len(bins)-1, np.float)

    y[1:2*len(bins)-1:2], y[2:2*len(bins):2] = bottom, bottom
    y[2*len(bins)-1:] = y[1:2*len(bins)-1][::-1]

    if log:
        # Setting a minimum of 0 results in problems for log plots
        if density or weights is not None:
            # For normed data, set to log base * minimum data value
            # (gives 1 full tick-label unit for the lowest filled bin)
            ndata = np.array(n)
            minimum = (np.min(ndata[ndata > 0])) / logbase
        else:
            # For non-normed data, set the min to log base,
            # again so that there is 1 full tick-label unit
            # for the lowest bin
            minimum = 1.0 / logbase

        y[0], y[-1] = minimum, minimum
    else:
        minimum = np.min(bins)

    if align == 'left' or align == 'center':
        x -= 0.5*(bins[1]-bins[0])
    elif align == 'right':
        x += 0.5*(bins[1]-bins[0])

    # If fill kwarg is set, it will be passed to the patch collection,
    # overriding this

    xvals, yvals = [], []

    if stacked:
        # starting point for drawing polygon
        y[0] = y[1]
        # top of the previous polygon becomes the bottom
        y[2*len(bins)-1:] = y[1:2*len(bins)-1][::-1]
    # set the top of this polygon
    y[1:2*len(bins)-1:2], y[2:2*len(bins):2] = (m + bottom,
                                                m + bottom)
    if log:
        y[y < minimum] = minimum

    plot.fill.update({di:x, dd:y})




@xyzplot.decorate()
def histogram2d(plot, *args, **kwargs):
    plot.update(kwargs.pop(KWS, {}), **kwargs)
    (x, y,
    bins, bin_range, normed, weights,
    cmin, cmax) = plot.parseargs(args, "x", "y",
                        "bins", "range", "normed", "weights",
                        "cmin", "cmax",
                        bins=10, range=None, normed=False, weights=None,
                        cmin=None, cmax=None)


    h, xedges, yedges = np.histogram2d(x, y, bins=bins, range=bin_range,
                                       normed=normed, weights=weights)

    if cmin is not None:
        h[h < cmin] = None
    if cmax is not None:
        h[h > cmax] = None

    X, Y = np.meshgrid(xedges, yedges)


    plot.update(xedges=xedges, yedges=yedges, hist=h,
                x=alias("xedges"), y=alias("yedges"),
                X=X[:-1,:-1], Y=Y[:-1,:-1],
                colors=h.T,
                Z = h.T
                )
    plot.contour.update(colors=None)
    plot.contourf.update(colors=None)
    plot.imshow.update(extent=(xedges.min(),xedges.max(),yedges.min(),yedges.max()))
    plot.goifgo()


histogram["_example_"] = ("histogram", None)

DataPlot.histogram = histogram
ImgPlot.histogram = histogram.derive(data=alias("img", lambda p,k: np.asarray(p[k]).flatten()))
XYZPlot.histogram = histogram.derive(data=alias("z", lambda p,k: np.asarray(p[k]).flatten()))


XYPlot.yhistogram2y = histogram.derive(data=alias("y"),
                                       direction="y"
                                       )
XYPlot.yhistogram2x = histogram.derive(data=alias("y"),
                                       direction="x"
                                       )
XYPlot.xhistogram2y = histogram.derive(data=alias("x"),
                                       direction="x"
                                       )
XYPlot.xhistogram2x = histogram.derive(data=alias("x"),
                                       direction="x"
                                       )

XYPlot.histogram2d = histogram2d











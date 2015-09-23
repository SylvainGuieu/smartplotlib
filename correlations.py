import matplotlib.mlab as mlab
import numpy as np
from .recursive import KWS, alias
from .plotclasses import (XYPlot, xyplot)


@xyplot.decorate()
def xcorr(plot, *args, **kwargs):
    """ Plot Wrapper of function xcorr

    contrarly to matplolib.xcorr, xcorr return a new xyplot-like instance
    ready to plot result of the correlation.

    Altered Parameters:
        lags, corr: corelation result
        xerr, yerr :  set to None
        data1, data2 : original data
        lines : alias(lags),
        min, max : 0 and alias("corr") for lines

      if direction == "y"
        x and y : alias of "lags" and "corr" for plot
        ymin : set to 0
        ymax : set y correlation result (to be used with vlines)
      if deirection == "x"
        y and x : alias of "lags" and "corr" for plot
        xmin : set to 0
        xmax : alias of "corr" (to be used with vlines/lines)

    the matplotlib doc is copied below

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    Plot the cross correlation between *data1* and *data2*.

    Parameters
    ----------

    data1 : sequence of scalars of length n (can be aliases to "x" for instance)

    data2 : sequence of scalars of length n (can be aliases to "y" for instance)

    hold : boolean, optional, default: True

    detrend : callable, optional, default: `mlab.detrend_none`
        x is detrended by the `detrend` callable. Default is no
        normalization.

    normed : boolean, optional, default: True
        if True, normalize the data by the autocorrelation at the 0-th
        lag.

    usevlines : boolean, optional, default: True
        if True, Axes.vlines is used to plot the vertical lines from the
        origin to the acorr. Otherwise, Axes.plot is used.

    maxlags : integer, optional, default: 10
        number of lags to show. If None, will return all 2 * len(x) - 1
        lags.

    Returns
    -------
    (lags, c, line, b) : where:

      - `lags` are a length 2`maxlags+1 lag vector.
      - `c` is the 2`maxlags+1 auto correlation vectorI
      - `line` is a `~matplotlib.lines.Line2D` instance returned by
        `plot`.
      - `b` is the x-axis (none, if plot is used).

    Other parameters
    -----------------
    linestyle : `~matplotlib.lines.Line2D` prop, optional, default: None
        Only used if usevlines is False.

    marker : string, optional, default: 'o'

    Notes
    -----
    The cross correlation is performed with :func:`numpy.correlate` with
    `mode` = 2.
    """
    plot.update(kwargs.pop(KWS, {}), **kwargs)

    (x, y, normed,
     detrend, maxlags) = plot.parseargs(args, "data1", "data2", "normed",
                                      "detrend", "maxlags",
                                      normed=True,
                                      detrend=mlab.detrend_none,
                                      maxlags=10)

    Nx = len(x)
    if Nx != len(y):
        raise ValueError('x and y must be equal length')

    x = detrend(np.asarray(x))
    y = detrend(np.asarray(y))

    c = np.correlate(x, y, mode=2)

    if normed:
        c /= np.sqrt(np.dot(x, x) * np.dot(y, y))

    if maxlags is None:
        maxlags = Nx - 1

    if maxlags >= Nx or maxlags < 1:
        raise ValueError('maglags must be None or strictly '
                         'positive < %d' % Nx)

    lags = np.arange(-maxlags, maxlags + 1)
    c = c[Nx - 1 - maxlags:Nx + maxlags]

    di, dd = plot._get_direction()

    plot.update(
                {di:alias("lags"), dd:alias("corr"),
                dd+"min":0, dd+"max":alias("corr")},
                min=0, max=alias("corr"),
                data=alias("corr"),
                xerr = None, yerr=None,
                lags=lags, corr=c,
                data1 =x, data2=y
                )

    plot.goifgo()


######
# add instances to XYPlot
XYPlot.xcorr = xcorr.derive(data1=alias("x"), data2=alias("y"))





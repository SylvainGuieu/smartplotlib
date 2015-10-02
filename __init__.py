"""  A Wrapper of the matplotlib library with advanced feature.




"""


from .recursive import *
from .plotfuncs import *
from .figaxes import SubPlot, subplot, Plots, plots

from .histogram import histogram
from .distribfit import distribfit

from .correlations import xcorr
from .polyfit import polyfit, linearfit
from .binedstatplot import binedstat, ybinedstat, xbinedstat
from .statplot import stat
from .img2data import img2data
from .specgram import (specgram, magnitude_spectrum, angle_spectrum,
                       phase_spectrum, cohere)

from plotclasses import (XYPlot, DataPlot, ImgPlot,
                         XYZPlot, ScalarPlot,
                         xyplot, dataplot, imgplot,
                         xyzplot, scalarplot
                        )

from .base import PlotFactory, PlotFunc
from .stack import stack, stackd

plot_axes_classes.extend([PlotFactory, PlotFunc])

debug = False
if debug:
    import matplotlib.pyplot as plt
    import recursive as rec
    import base as b
    import plotfuncs as pfs
    import figaxes as fa
    import polyfit as pft
    import histogram as _histo
    import distribfit as _distribfit

    import dataplot as _dataplot

    import xyplot as xyp
    import correlations as corr
    import examples
    reload(rec); reload(b);
    reload(pfs); reload(fa); reload(_histo); reload(_distribfit);
    reload(xyp);
    reload(pft);
    reload(corr);
    reload(examples);

    SubPlot, subplot, Plots, plots = fa.Subplot, fa.subplot, fa.Plots, fa.plots
    xcorr = corr.xcorr
    polyfit, linearfit = pft.polyfit, pft.linearfit

    (XYPlot, xyplot, ystat, xstat,
     ybinedstat) = (xyp.XYPlot, xyp.xyplot, xyp.ystat, xyp.xstat,
                    xyp.ybinedstat)


#####
## fill what cannot be done before because recursive imports
SubPlot.xyplot   = xyplot
Plots.xyplot = xyplot


# indexes are None by default
XYPlot.xdata = dataplot.derive(data=alias("x"), indexes=alias("y",lambda p,k:p.get(k,None)))
XYPlot.ydata = dataplot.derive(data=alias("y"), indexes=alias("x",lambda p,k:p.get(k,None)))









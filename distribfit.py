from __future__ import division, absolute_import, print_function
import numpy as np
from . import plotfuncs as pfs
from .plotclasses import (XYPlot, DataPlot,  xyplot, dataplot)

from .recursive import KWS, alias
from .base import PlotFactory

###
# TODO complete list of import and lookup
from scipy.stats import (norm,)
##
# will generate a xyplot

distrib_lookup = {
    "norm":norm
}


@xyplot.decorate()
def distribfit(plot, *args, **kwargs):
    plot.update(kwargs.get(KWS, {}), **kwargs)
    (data, distrib, npoints, _range,
     _min, _max, amplitude) = plot.parseargs(args, "data", "distrib",
                                         "npoints", "range",
                                         "min", "max", "amplitude",
                                         npoints = 100, min=None,
                                         max=None, amplitude=1.0,
                                         distrib="norm", range=(None, None)
                                        )



    if isinstance(distrib, basestring):
        try:
            distrib = distrib_lookup[distrib]
        except KeyError:
            raise ValueError("distrib must be one of %s got '%s"%(", ".join(distrib_lookup.keys()),
                                                                  distrib))


    elif (not hasattr(distrib,"pdf")) or (not hasattr(distrib,"fit")):
        raise ValueError("distrib function must have .pdf and .fit methods")

    fdata = data
    mini, maxi = _range
    if mini is not None:
        fdata = data[data>=mini]
    if maxi is not None:
        fdata = fdata[fdata<=maxi]

    loc, scale = distrib.fit(fdata, **plot.gets("loc","scale", "floc", "fscale",
                                              "optimizer"
                                            )
                           )

    di, dd = plot._get_direction()

    if _min is None:
        _min = -4*scale+loc
    if _max is None:
       _max =  4*scale+loc
    #x = np.linspace(_min, _max, npoints)
    #y = distrib.pdf(x, loc, scale)*amplitude

    x = alias(["min","max","npoints"],
                  lambda p,a: np.linspace(p[a[0]],p[a[1]],p[a[2]]),
                  "-> linspace(min, max, npoints)")
    y = alias("x",
              lambda p,x: distrib.pdf(p[x],loc, scale)*amplitude,
              "-> fit(x)"
              )
    #x = np.linspace(_min, _max, npoints)
    #y = distrib.pdf(x, loc, scale)*amplitude



    label = plot.get("label", None)
    if label is True:
        plot["label"] = "{name}.({loc:{label_fmt}}, {scale:{label_fmt}})*{amplitude}".format(
                            name = getattr(distrib,"name",""),
                            loc=loc,
                            scale=scale,
                            label_fmt = plot.get("label_fmt", ".3g"),
                            amplitude = amplitude

                           )

    plot.update({di:x, dd:y, dd+"min":0, dd+"max":alias(dd)},
                min=_min, max=_max, scale=scale, std=alias("scale"),
                loc=loc, xerr=None, yerr=None, data=data, npoints=npoints
               )

    plot.goifgo()

DataPlot.distribfit = distribfit

#XYPlot.distribfit = distribfit
#XYPlot.ydistribfit2y = distribfit.derive(data=alias("y"), direction="y")
#XYPlot.ydistribfit2x = distribfit.derive(data=alias("y"), direction="x")
#XYPlot.xdistribfit2y = distribfit.derive(data=alias("x"), direction="y")
#XYPlot.xdistribfit2x = distribfit.derive(data=alias("x"), direction="x")


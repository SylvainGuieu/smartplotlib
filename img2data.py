from .plotclasses import (ImgPlot, dataplot, xyplot)
from recursive import alias
import numpy as np
KWS = "params"

@dataplot.decorate(data=alias("img", lambda p,k: np.asarray(p[k]).flatten(), "-> img.flatten()"))
def img2data(plot, *args, **kwargs):
    plot.update(kwargs.pop(KWS, {}), **kwargs)
    (img, x_idx, y_idx,
     x_reduce, y_reduce) = plot.parseargs(args, "img", "x_idx", "y_idx",
                                      "x_reduce", "y_reduce",
                                      x_idx=slice(0,None),
                                      y_idx=slice(0,None),
                                      x_reduce=None,
                                      y_reduce=None
                                     )
    x_axis, y_axis = 1,0
    shape = img.shape

    section =  (y_idx if y_axis==0 else x_idx,
                x_idx if x_axis==1 else y_idx)

    # if the idx is a int switch of the reduce function
    if (not isinstance(x_idx, slice) and not hasattr(x_idx,"__iter__")):
        x_reduce = None
    if (not isinstance(y_idx, slice) and not hasattr(y_idx,"__iter__")):
        y_reduce = None

    data = img[section]
    shape = data.shape
    if x_reduce is not None:
        data = x_reduce(data, axis=x_axis)
    # an axis is lost, the y_reduce must be executed on axis=0 always
    if len(data.shape)<data.shape:
        y_axis = 0
    elif len(data.shape)>data.shape:
        raise ValueError("the reduce function cannot add axis")
    if y_reduce is not None:
        data = y_reduce(data, axis=y_axis)

    plot["data"] = np.asarray(data).flatten()


@xyplot.decorate()
def profile(plot, *args, **kwargs):
    """ xyplot factory, compute image profile from 2 points defining a line

    Args:
        img (2d array): the 2d image
        c0 (2 tuple) : coorinate of the first point in pixel coordinate.
        c1 (2 tuple) : coordinate of the second point in pixel coordinate.
        direction (string) : "y" (default) or "x" define the axis on wich the
            profile will be ploted
        **kwargs : all other parameters for plots

    Machined Parameter:
        x (array) : the pixel distance from c0
        y (array) : the intensity of each nearest neighbor pixel crossing the line.

    Return:
        xyplot

    See Also:
        img2data (or todata) : convert image or sub-image to flat data


    """
    plot.update(kwargs.pop(KWS, {}), **kwargs)
    img, c0, c1 = plot.parseargs(args, "img", "c0", "c1")
    x0, y0 = c0
    x1, y1 = c1

    length = int(np.hypot(x1-x0, y1-y0))
    x, y = np.linspace(x0, x1, length), np.linspace(y0, y1, length)

    # Extract the values along the line
    zi = img[x.astype(np.int), y.astype(np.int)]


    di, dd = plot._get_direction()
    plot.update( {di:np.arange(len(zi)), dd:zi} )





ImgPlot.todata = img2data
ImgPlot.profile = profile

# Smartplotlib

This python package is a wrapper around the famous matplotlib package.

**Note this is a early beta version (and a beta Readme). However the principle and skeleton will not change. If you find the package interesting, any contribution on anything is more than welcome.**


## Purpose
The matplotlib package is huge and complete but in some case I often been frustrated with it. I often end up to write the same line of codes to plot a graphic slightly different than the one before, with other data.

I used to build function to represent/plot my data with the matplotlib functions. Sufficient for what I wanted to do at that time. But after re-using it, I didn't want blue lines anymore but red cross, so I add the color=, marker= keywords. Then I realized that my function was setting the axes label or limits, I do not want that for an other case, I can add more and more keywords until I decide to add kw_axes=dict(), kw_errorbar=, kw_legend= etc ...
At the end the function end up to be a huge confusing machinery.

Also I often wanted to set plot parameters defaults for particular objects, not only for the full package as the matplolib.rcparams does. I often wanted to create an object to plot, for instance a model with its plot parameters, a data set with other parameters etc ... One can define dictionaries for each kind of data to plot and pass them to plots. But it is still confusing and not handy. One can create function for each data set , but it ends-up with the same problems and it is a lot of work to do.

Smartplotlib provides tools to make easy plot templates and plots maker with a hierarchical parameter assignment.

The benchmark for me is that the package has to be logic and intuitive. Easy to use and not far from matplolib function, so that we do not have do learn a lot of extra stuff. And easy to implement.

## Engine

smartplotlib provides to main kind of objects : plot factories (PlotFactory class) and plot function (PlotFunc class ). PlotCollection is a third one but is almost  the same thing than a PlotFactory let see that later.

- Plot factories contain plot functions and other plot factories object (or collection) and an engine to create themselves (like \_\_init\_\_ is for classes).
- Plot function are executing the plotting, they are functioning  exactly like their matplotlib counterparts (plot, bar, vlines, ...).

Both of these objects has item (=default parameters) setting like a dictionary does. These parameters are used differently:

#### PlotFunc

For plot function the parameters are used as function arguments substitution. Positional argument and keyword argument can be substituted. Let see with a dummy example:
```python
from smartplotlib import PlotFunc
# create a new independent PlotFunc object
# the first integer define the number of positional (=obligatory arguments)
myplot = PlotFunc(2,"x","y","color","marker")

# decorate the 'caller' function
@myplot.caller
def myplot(x,y,color="black", marker="+",  notsubstituedkwargs=None):
    # do some stuff
    return (x,y,color,marker)
```
Now one can use the myplot function like a normal function:

```python
>>> myplot( [1,2,3,4], [1,4,6,8], color="red")
([1,2,3], [1,2,3], "red", "+")
```
But also set the default :
```python
>>> myplot["color"] = "red"
# -or-
>>> myplot.update(x=[1,2,3], y=[1,2,3], color="red", marker="-")
>>> myplot()
([1,2,3], [1,2,3], "red", "-")
```

Or define 'derived' function :
```python
plotmodel = myplot.derive(color="red", marker="-")
plotmeasure = myplot.derive(color="blue", marker="+")
# -or- in one line
plotmodel, plotmeasure = myplot.iter(color=["red", "blue"], marker=list("-+"))
```
Then you can re-use plotmodel and plotmeasure without having to care about the color and marker because they have been defined before.

All or almost the plot functions of matplolib Axes has been rewritten in PlotFunc, so instead of the myplot example you can use the plot, vlines, hlines, bar, step, hist, ... etc ...
At the beginning of a project one can define all the different type of plots:
```python
from smartplotlib import plot
plot_stars = plot.derive( marker="+", linestyle="none", color="black")

plot_giant = plot_stars.derive(marker="*")
plot_dwarf = plot_stars.derive(marker=".")

```
The giant and dwarf are 'derived' from stars, the marker is redefine but the color is the default of stars e.i. "black" in this example.

```python
>>> plot_dwarf["color"]
"black"
>>> plot_stars["color"] = "blue"
>>> plot_dwarf["color"]
"blue"
```

The default parameters are hierarchic, if not defined locally they are taken from the parent from whom they have been derived. But their is more ! They can also be set in a parent PlotFactory or PlotCollection. Let us see that.

### PlotCollection / PlotFactory
There is no physical differences between PlotFactory and PlotCollection. They are the same object,  but serve a different purpose: a PlotCollection just set parameters and hold other child PlotFunc/PLotCollection/PlotFactory. PlotFactory is the same but compute more stuff and need to be called to work correctly. For instance, in smartplotlib,  'histogram' is a plot factory that create x, y, (.. and more) parameters for the child plot function to plot the computed histogram.


When called, a Plot CollectionFactory return always a new instance of itself.

Let see an example with the xyplot collection, it is a collection  to plot, and do more advanced stuff, on two data vectors x and y.

Following the example above for stars, you can use it as template:
```python
stars = xyplot.derive( marker="+", linestyle="none", color="black")
giant = stars.derive(marker="*")
dwarf  = stars.derive(marker=".")

>>> dwarf.plot(x,y) # -or- dwarf(x,y).plot()
```

One can also define the plot x,y data inside the template:
```python
from smartplotlib import xyplot
import numpy as np
x = np.arange(50)
parabola = xyplot(x, x*x, color="red", xlabel="x", ylabel="x^2")
```

We have defined parabola which is a new instance of a xyplot with some parameters defined : 'x', 'y' (the second parameter), 'color', 'xlabel', 'ylabel'. All the children of parabola will inherit these parameter but that does not mean they will care about all of them. For instance 'plot' (which plot the data) will used the inherited 'x', 'y' and 'color'. 'aset' which set the axes labels, title, scale, grid , .... etc will only use, in our case, the parameters 'xlabel' and 'ylabel'.

```python
>>> parabola.plot() # plot the data
>>> parabola.aset() # set the axes stuff
>>> parabola.show() # show the figure
# -or- in one line:
>>> parabola.go("plot", "aset", "show")
```

Let see an simple example on how to create a plotfactory easily. Imagine you have to plot often a sinus on your graphs, you can of course make a normal function and parse all the keywords to your function with all the different case of plotting, or, you can use a plot factory. As the sinus is a 2d data x/y kind of plot, one can start from the xyplot.
Each PlotFactory, PlotCollection, PlotFunc has a attribute 'derive' to create a derived instance or an attribute 'decorate' to decorate the engine function (the engine function is called finit in case of PlotFactory and fcall in case of PlotFunc).

A plot factory function maker receive always a fresh new plot
instance and must return None (as \_\_init\_\_ for classes)
below we decorate from xyplot and add a lienestyle default parameter on the fly:

```python
from smartplotlib import xyplot
import numpy as np

@xyplot.decorate(linestyle="--")
def psinus(plot, freq=1.0, phase=0.0, nperiod=1, npoints=50, **kwargs):
    """ Sinus plot factory """

    plot.update(**kwargs) # save all kwargs for future plot

    x = np.linspace(0, 2*np.pi*nperiod, int(npoints*nperiod))
    plot.update(x=x, y=np.sin(x*freq+phase), ylabel="sin(x)", xlabel="x")


# put some default, for instance,  here in the fill method
psinus.fill.update(linewidth=None, linestyle="solid")
```
Then you can use you psinus and plot what you need from it:
```python
>>> psinus(2.0, 0.0, 3).plot(color="red") # a line plot
# or
>>> psinus(2.0, 0.0, 3, color="red").plot() # samething
# or
>>> psinus(2.0, 0.0, 3, axes=(2,1,1)).go("fclear", "aset", "plot", "fill", "show", "draw")

```
The last form clear the figure, set the axes labels title, etc, plot the line, fill the plot, show the figure (figure.show) and redraw the graphic (figure.canvas.draw()). Everything is done on a (2,1,1) axes, meaning the first axes of a 2x1 grid.

A useful method is the '.info', it prints a state of the object with all the value set (inherited or set locally). Try it:
```python
>>> psinus.info
>>> psinus().info
```

The go method is just a short cut : psinus(4.0).go("aset", "plot") is equivalent to do : p = psinus(4.0); p.aset(); p.plot()
One can define a list of actions inside the object for the go method, the list of actions are parameters starting with '-':
```python
# "-" is the default action when go is called without argument
psinus["-"] = ["plot"]
psinus["-all"] = ["fclear", "aset", "plot", "show", "draw"]

psinus().go() #  is go("plot")
psinus().go("-all") # is go("fclear", "aset", "plot", "show", "draw")
```

Of course the psinus example above does not make any sense if you have to plot your sinus only ones, but it does when you plot it often and, you want the default render to be defined separatly. Moreover you can decide to do what ever you want with your psinus, plot, fill, set axes , etc.. without having to add extra keyword as you would have done with a normal function.

#### xyplot
As mentioned above xyplot serve to represent x/y data in a two dimensional plot.

The xyplot collection has built in factories (like other collection see below). One good example is the polyfit which fit a polynome to the data and machine an other plot ready xyplot to represent the fit results:
```python
from smartplotlib import xyplot
import numpy as np
# let us make some noisy data
x = np.arange(100);
yerr = np.random.rand(100)*2.0*x
y = x*x + yerr

# create our xyplot holding data and parameters
xy = xyplot(x,y, yerr=yerr, xlabel="t [s]")

# plot the data with errorbar
xy.errorbar(linestyle="None", label="data")
# fit a polynome and plot it (label=True -> replace label by fit result text)
xy.polyfit(dim=2, color="red", linestyle="--", label=True).plot()
xy.go("aset", "legend", "show", "draw")
```

See the doc of plotfunc for a full list of PlotFactory and PlotFunc methods.

#### dataplot

dataplot is a collection of PlotFunc and PlotFactory to represent one dimensional data (materialized by the parameter 'data'). For instance it has the hist PlotFunc wrapped around the hist matplotlib function  but also a PlotFactory histogram which serve the same purpose but is more handy to represent computed histogram as we want. histogram, return a xyplot collection.
```python
import numpy as np
from smartplotlib import dataplot

data = np.random.normal(size=(1000,))
dp = dataplot(data, figure="histograms")
h = dp.histogram(bins=20, rwidth=0.8)

h.bar()
h.errorbar(linestyle="none", color="k")
```

A dataplot can be extracted form a xyplot with the ydata, xdata attribute, for instance:
```python
xy = xyplot( np.random.normal(size=(1000,)), np.random.normal(size=(1000,)) )
xy.ydata.hist( bins=10,  orientation="horizontal")
```

the 'stat' is a PlotFactory to compute statistic of the data 'distribfit' is fitting a distribution on the data sample:
```python
data = np.random.normal(size=(1000,))
dp = dataplot(data, figure="histograms")
dp.hist(bins=30, normed=True)
dp.stat(fstat="median").axvline(color="red")
dp.distribfit(label=True).plot(color="k")
dp.legend()
```

See the doc of dataplot for a list of PlotFunc and Plot Factories

#### imgplot
Plot collection for image representation plus some capabilities taken from dataplot (histogram, stat, etc...).
```python
import numpy as np
from smartplotlib import imgplot

N = 100
x, y = np.mgrid[-5:5:0.1, -5:5:0.1]
z = np.sqrt(x**2 + y**2) + np.sin(x**2 + y**2)
imgp = imgplot(z, bins=np.linspace(0,7,20), vmin=0, vmax=7, figure="image example")
imgp.fclear() # clear the figure
imgp.fset(size_inches=(15,5))
ims = imgp.imshow(axes=131)
imgp.colorbar(ims, ax=[131,132], orientation="horizontal")
sub = imgp.sub[35:65,50:80] # this is a imgplot with a subimage
sub.imshow(axes=132) # plot a zoom
imgp.hist(axes=133)
sub.hist(axes=133, color="green")
imgp.go("show", "draw")
```
[!ScreenShot]{https://github.com/SylvainGuieu/smartplotlib/blob/master/screenshots/imgplot.png}


#### scalarplot
Use to represent a scalar single value, for instance with axvline. For instance the stat plot factory is a scalarplot collection:

```python
import numpy as np
from smartplotlib import xyplot
N=10000
x = np.linspace(0, 2, N)
yerr = np.random.rand(N)*np.exp(x)*np.sign(np.random.rand(N)-0.5)
y = 5+yerr
xy = xyplot(x, y, fmt="k+", axes=211, figure="stat example")
xy.go("fclear", "aset", "plot")

for stat in xy.ydata.stat.iter(fstat=["+std","mean","-std"], linestyle=list(":-:")):
    stat().axhline(color="red")

xy.go("show", "draw")
```

## Installation
TODO: Describe the installation process
## Usage
TODO: Write usage instructions
## Contributing
TODO: Write history
## Credits
TODO: Write credits
## License
TODO: Write license


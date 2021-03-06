# Smartplotlib

This python package is a convenient wrapper around the famous matplotlib package.

It allows to well separate the plotting and the data painlessly. 

**Note this is a early beta version (and a beta Readme). However the principle and skeleton will not change. If you find the package interesting, any contribution on anything is more than welcome.**

## How it works 

### PlotFunc
In smartplotlib all the plot function can have their default parameters.


     from smartplotlib import plot
     x = np.arange(100)
     y = x**2
     plot(x,y)


So far nothing fancy, it works like matplotlib, but the function can accept default parameters and can be 'derived':

     from smartplotlib import plot
     ## a plot_function object for stars and galaxies 
     plot_stars    = plot.derive( marker="+", linestyle="none", color="black") 
     plot_galaxies = plot.derive( marker="O", linestyle="none", color="red")
     
     ## rgb and brow dwarfs are stars so they are derived from plot_stars
     plot_rgbs = plot_stars.derive(marker="*") #same color them stars 
     plot_bds  = plot_stars.derive(marker=".")


One can then use the created `plot_*` later in the code without taking care of how symbols, markers, etc are for each objects. 

     plot_rgbs(ra, dec)
     plot_galaxies(ra, dec)


When a plotfunc is inherited the child got the default parameters of the parent.
And parameters can be accessed and set by item assignation :

    >>> plot_bds['color']
     'black'
    >>> plot_stars['color'] = "blue"
    >>> plot_bds['color']
     'blue'


Other example


     from smartplotlib import axvline, plot
     plot_valid_range = axvline.derive(x=[-10,100], color="red", linestyle="--")
     
     ##
     # and later on embeded in your code 
     plot( *something* )
     plot_valid_range()


creating a plofunc object is one line more difficult than creating a normal function. The object needs to know how many positional parameters and their names. The plotfunc object has a `.decorator` decorator method.
Let us create a dummy plotfunc to understand how it works


     from smartplotlib import plotfunc
     
     @plotfunc.decorate(2,"ra","dec", "marker", "color")
     def sky(ra, dec, **kwargs):
         ## do something with ra, dec
         return (ra, dec, kwargs)



    >>> sky( 4.545, 23.456)
    (4.545, 23.456, {})
    >>> sky['color'] = "red"
    >>> sky(4.545, 23.456)
    (4.545, 23.456, {'color': 'red'})


The `sky` object is a function where defaults can be set with parameter assignment. 
We can create the sky function from a plot plotfunc, it will get all the line2d parameters.


     from smartplotlib import plot
     
     @plot.decorate(2,"ra","dec")
     def sky(ra, dec, *args, **kwargs):    
         ## <--- CHECK ra and dec range raise errors ---> 
         return plot(ra, dec, *args, **kwargs)


### Aliases
Aliases are usefull to create parameter linked to other parameter.
In our example one can alias 'x' to 'ra' and 'y' to 'dec'.

    from smartplotlib import plot, alias
    
    sky = plot.derive(x=alias('ra'), y=alias('dec'))
    ####
    # later in your code 
    sky(ra=[4.5], dec=[24.5676])


Aliases can also be a function (second argument is a small description)

     parabola = plot.derive(x=np.linspace(-10,10,50), y=alias(lambda p:p["x"]**2), "y->x**2")

### Plot Factories


## Purpose
The matplotlib package is huge and complete but in some case I often left frustrated with it. I often end up to write the same line of codes to plot a graphic slightly different than the one before, but with other data, color, marker ...

I used to build function to plot my data with the matplotlib functions. Sufficient for what I wanted to do at that time. But after re-using it, I didn't want blue lines anymore but red cross, so I add the color=, marker= keywords. Then I realized that my function was setting the axes label or limits, I do not want that for an other case, I can add more and more keywords until I decide to add kw_axes=dict(), kw_errorbar=, kw_legend= etc ...
At the end the function end up to be a huge confusing machinery.

Also I often wanted to set plot parameters defaults for particular objects, not only for the full package as the `matplolib.rcparams` does. I often wanted to create an object to plot, for instance a model with its plot parameters, a data set with other parameters etc ... One can define dictionaries for each kind of data to plot and pass them to plots. But it is still confusing and not handy. One can create function for each data set , but it ends-up with the same problems and it is a lot of work to do.

Smartplotlib provides tools to make easy plot templates and plots maker with a hierarchical parameter assignment.

The benchmark for me is that the package has to be logic and intuitive. Easy to use and not far from matplolib function, so that we do not have do learn a lot of extra stuff. And easy to implement.

## Engine

smartplotlib provides two main kind of objects : plot factories (PlotFactory class) and plot function (PlotFunc class ). PlotCollection is a third one but is almost  the same thing than a PlotFactory let see that later.

- Plot factories contain plot functions and other plot factories object (or collection) and an engine to create themselves (like `__init__` is for classes).
- Plot function are executing the plotting, they are functioning  exactly like their matplotlib counterparts (plot, bar, vlines, ...).

Both of these objects has item (=default parameters) setting like a dictionary does. These parameters are used differently:

#### PlotFunc

For plot function the parameters are used as function arguments substitution. Positional argument and keyword argument can be substituted. Let see with a dummy example:

     from smartplotlib import PlotFunc
     # create a new independent PlotFunc object
     # the first integer define the number of positional (=obligatory arguments)
     myplot = PlotFunc(2,"x","y","color","marker")
     
     # decorate the 'caller' function
     @myplot.caller
     def myplot(x,y,color="black", marker="+",  notsubstituedkwargs=None):
         # do some stuff
         return (x,y,color,marker)

Now one can use the myplot function like a normal function:


    >>> myplot( [1,2,3,4], [1,4,6,8], color="red")
    ([1,2,3], [1,2,3], "red", "+")

But also set the default :

    >>> myplot["color"] = "red"
    # -or-
    >>> myplot.update(x=[1,2,3], y=[1,2,3], color="red", marker="-")
    >>> myplot()
    ([1,2,3], [1,2,3], "red", "-")


Or define 'derived' function :

    plotmodel = myplot.derive(color="red", marker="-")
    plotmeasure = myplot.derive(color="blue", marker="+")
    # -or- in one line
    plotmodel, plotmeasure = myplot.iter(color=["red", "blue"], marker=list("-+"))

Then you can re-use plotmodel and plotmeasure without having to care about the color and marker because they have been defined before.

All or almost the plot functions of matplolib Axes has been rewritten in PlotFunc, so instead of the myplot example you can use the plot, vlines, hlines, bar, step, hist, ... etc ...
At the beginning of a project one can define all the different type of plots:

    from smartplotlib import plot
    plot_stars = plot.derive( marker="+", linestyle="none", color="black")
    
    plot_giant = plot_stars.derive(marker="*")
    plot_dwarf = plot_stars.derive(marker=".")    

The giant and dwarf are 'derived' from stars, the marker is redefine but the color is the default of stars e.i. "black" in this example.


     >>> plot_dwarf["color"]
     "black"
     >>> plot_stars["color"] = "blue"
     >>> plot_dwarf["color"]
     "blue"


The default parameters are hierarchic, if not defined locally they are taken from the parent from whom they have been derived. But their is more ! They can also be set in a parent PlotFactory or PlotCollection. Let us see that.

### PlotCollection / PlotFactory
There is no physical differences between PlotFactory and PlotCollection. They are the same object,  but serve a different purpose: a PlotCollection just set parameters and hold other child PlotFunc/PLotCollection/PlotFactory. PlotFactory is the same but compute more stuff and need to be called to work correctly. For instance, in smartplotlib,  'histogram' is a plot factory that create x, y, (.. and more) parameters for the child plot function to plot the computed histogram.


When called, a Plot CollectionFactory return always a new instance of itself.

Let see an example with the xyplot collection, it is a collection  to plot, and do more advanced stuff, on two data vectors x and y.

Following the example above for stars, you can use it as template:

    stars = xyplot.derive( marker="+", linestyle="none", color="black")
    giant = stars.derive(marker="*")
    dwarf  = stars.derive(marker=".")
    
    >>> dwarf.plot(x,y) # -or- dwarf(x,y).plot()


One can also define the plot x,y data inside the template:

    from smartplotlib import xyplot
    import numpy as np
    x = np.arange(50)
    parabola = xyplot(x, x*x, color="red", xlabel="x", ylabel="x^2")


We have defined parabola which is a new instance of a xyplot with some parameters defined : 'x', 'y' (the second parameter), 'color', 'xlabel', 'ylabel'. All the children of parabola will inherit these parameter but that does not mean they will care about all of them. For instance 'plot' (which plot the data) will used the inherited 'x', 'y' and 'color'. 'axes' which set the axes labels, title, scale, grid , .... etc will only use, in our case, the parameters 'xlabel' and 'ylabel'.


     >>> parabola.plot() # plot the data
     >>> parabola.axes() # set the axes stuff
     >>> parabola.show() # show the figure
     # -or- in one line:
     >>> parabola.go("plot", "axes", "show")


Let see an simple example on how to create a plotfactory easily. Imagine you have to plot often a sinus on your graphs, you can of course make a normal function and parse all the keywords to your function with all the different case of plotting, or, you can use a plot factory. As the sinus is a 2d data x/y kind of plot, one can start from the xyplot.
Each PlotFactory, PlotCollection, PlotFunc has a attribute 'derive' to create a derived instance, and an attribute 'decorate' to decorate the engine function (the engine function is called finit in case of PlotFactory and fcall in case of PlotFunc).

A plot factory function maker receive always a fresh new plot
instance and must return None (as \_\_init\_\_ for classes)
below we decorate from xyplot and add a lienestyle default parameter on the fly:


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

Then you can use your psinus and plot what you need from it:
```python
>>> psinus(2.0, 0.0, 3).plot(color="red") # a line plot
# or
>>> psinus(2.0, 0.0, 3, color="red").plot() # samething
# or
>>> psinus(2.0, 0.0, 3, axes=(2,1,1)).go("fclear", "axes", "plot", "fill", "show", "draw")

```
The last form clear the figure, set the axes labels title, etc, plot the line, fill the plot, show the figure (figure.show) and redraw the graphic (figure.canvas.draw()). Everything is done on a (2,1,1) axes, meaning the first axes of a 2x1 grid.

A useful method is the '.info', it prints a state of the object with all the value set (inherited or set locally). Try it:
```python
>>> psinus.info
>>> psinus().info
>>> psinus().plot.info
```

The go method is just a short cut : psinus(4.0).go("axes", "plot") is equivalent to do : p = psinus(4.0); p.axes(); p.plot()
One can define a list of actions inside the object for the go method, the list of actions are parameters starting with '-':
```python
# "-" is the default action when go is called without argument
psinus["-"] = ["plot"]
psinus["-all"] = ["fclear", "axes", "plot", "show", "draw"]

psinus().go() #  is go("plot")
psinus().go("-all") # is go("fclear", "axes", "plot", "show", "draw")
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
xy.go("axes", "legend", "show", "draw")
```
![image](../screenshots/screenshots/fitpoly.png)

See the doc of plotfunc for a full list of PlotFactory and PlotFunc methods.

#### dataplot

dataplot is a collection of PlotFunc and PlotFactory to represent one dimensional data (materialized by the parameter 'data'). It has the 'hist' PlotFunc wrapped around the hist matplotlib function, but has also a PlotFactory histogram which serve the same purpose, but is more handy for advanced  representation of histograms with little extra line code. histogram, return a xyplot collection.
```python
import numpy as np
from smartplotlib import dataplot

data = np.random.normal(size=(1000,))
dp = dataplot(data, figure="histograms")
h = dp.histogram(bins=20, rwidth=0.8)

h.bar()
h.errorbar(linestyle="none", color="k")
```

![image](../screenshots/screenshots/histogram.png)

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
![image](../screenshots/screenshots/histogram_fit.png)

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
![image](../screenshots/screenshots/imgplot.png)

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
xy.go("fclear", "axes", "plot")

for stat in xy.ydata.stat.iter(fstat=["+std","mean","-std"], linestyle=list(":-:")):
    stat().axhline(color="red")

xy.go("show", "draw")
```
![image](../screenshots/screenshots/stat.png)

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


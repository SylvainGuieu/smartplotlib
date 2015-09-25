



def xcorr():
    from smartplotlib import xcorr
    import numpy as np

    x,y = np.random.randn(2,100)

    ##  build the correlation plot
    corr = xcorr(x, y, usevlines=True, maxlags=50, normed=True, lw=2)

    # for my correlation better add a black line at y=0
    corr.axes.axhline.update(y=0, xmin=0, xmax=1, color='black', lw=2)

    # clear the figure
    corr.fclear()
    # turn on grid
    corr.axes.grid(True)

    # set the axes plot the y=0 line, plot vlines of the corelation
    # plus scatter to make it nice, show and canvas.draw the figure
    corr.go("aset", "axes.axhline", "vlines", "scatter",
            "show", "draw")
    return corr


def xyplot():
    from smartplotlib import xyplot
    import numpy as np
    N = 100
    mx = np.linspace(0, 8*np.pi, N);
    my = np.sin(mx)
    yerr = np.random.rand(N)*0.1
    xerr = np.random.rand(N)*0.1
    x = mx + xerr
    y = my + yerr

    # itercall iter on iterables, makes a duplicate instances
    # and call the instance. iter should work as well because
    # xyplot(*args,**kwarg) does nothing else than storing x,y, kwargsetc..
    model, data = xyplot.itercall(x=[mx,x], y=[my,y],
                                  xerr=[None,xerr], yerr=[None,yerr],
                                  label=["model", "data"],
                                  color=["red", "black"],
                                  linestyle=["-","None"],
                                  xlabel="t [s]", #scalar always the same
                                  ylabel="Signal"
                                 )
    model.fclear() # fclear is the same can be called on who you want
    model.aset()

    model.plot() # plot the model
    data.errorbar() # plot data with errorbar

    ##
    # plot mean, max and  +/-std around the mean
    # contrary to itercall, iter does not call the new plot instance
    # one must call it to compute the statistic
    # need also to change linestyle  sinse it is inerited
    # from data it has linestyle = "None" by default
    data.ystat["linestyle"] = "--"
    [stat.axline() for stat in data.ystat.itercall(fstat=["mean","max", "std"],
                                           color=list("krg"),
                                           label=["mean", "max", "std"]
                                           )]

    model.go("legend", "show", "draw")

    return model


def polyfit():

    from smartplotlib import xyplot
    import numpy as np

    x = np.arange(100);
    yerr = np.random.rand(100)*2.0*x
    y = x*x + yerr

    xyplot.fclear()

    # make a new xyplot with my data
    xy = xyplot(x,y, yerr=yerr, xlabel="t [s]")

    # plot the data with errobar
    xy.errorbar(linestyle="None", label="data")

    # fit a polynome and plot it
    # note that color and linestyle can also be in .plot
    xy.polyfit(dim=2, color="red", linestyle="--", label=True).plot()

    # fit a tangent to a xrange
    # by default plot only for the given range
    # so we need to make it a bit longer with xmin and xmax
    # also xmin and xmax can be True, that mean, min and max of data
    # not range
    plf = xy.polyfit(dim=1, xrange=(55,65),  color="green",
                     xmin=35, xmax=90,
                     linestyle="--", label="tangent @ 55<x<65").plot()

    ##
    # other method can be done with the go method
    # here. aset plot, set the axes labels etc ..., legend plot
    # the legend,  than show and draw are figure.show() and figure.canvas.draw()
    xy.go("aset", "legend", "show", "draw")
    return plf


def specgram():
    """ smartplotlib example of specgram """
    from pylab import np, pi, sin, arange, logical_and, where, randn, cm
    from smartplotlib import xyplot, axes


    dt = 0.0005
    t = arange(0.0, 20.0, dt)
    s1 = sin(2*pi*100*t)
    s2 = 2*sin(2*pi*400*t)

    # create a transient "chirp"
    mask = where(logical_and(t>10, t<12), 1.0, 0.0)
    s2 = s2 * mask

    # add some noise into the mix
    nse = 0.01*randn(len(t))

    x = s1 + s2 + nse # the signal
    NFFT = 1024       # the length of the windowing segments
    Fs = int(1.0/dt)  # the sampling frequency

    # Pxx is the segments x freqs array of instantaneous power, freqs is
    # the frequency vector, bins are the centers of the time bins in which
    # the power is computed, and im is the matplotlib.image.AxesImage
    # instance

    xy = xyplot(t, x, axes=211, xlabel="t", ylabel="x")

    ###
    # xy.ydata is a dataplot from whish data is aliased to "y"
    # a dataplot contain a collection of plot that can be obtain
    # from a 1d data
    spec = xy.ydata.specgram(NFFT=NFFT, Fs=Fs, noverlap=900,
                             cmap=cm.gist_heat, axes=212)
    xy.fclear()
    xy.aset()
    xy.plot()
    # above is same as xy.go("fclear", "aset", "plot")
    spec.go("aset", "imshow", "show", "aset", "draw")
    return spec

def spectrum():
    """ example of magnitude_spectrum, angle_spectrum and phase_spectrum
    with smartplotlib
    """
    import numpy as np
    from smartplotlib import xyplot, axes

    ###
    # make some data
    Fs = 150.0;  # sampling rate
    Ts = 1.0/Fs; # sampling interval
    t = np.arange(0,1,Ts) # time vector

    ff = 5;   # frequency of the signal
    y = np.sin(2*np.pi*ff*t)

    ###
    # make an new instance of xyplot with the data
    xy = xyplot(t, y, xlabel="time", ylabel="Signal", axes=311)
    ###
    ###
    # plot the original data
    xy.go("fclear", "aset", "plot")

    ###
    # xy.ydata is a dataplot from whish data is aliased to "y"
    # a dataplot contain a collection of plot that can be obtain
    # from a 1d data
    m = xy.ydata.magnitude_spectrum(axes=312,
                                    #
                                    )
    a = xy.ydata.angle_spectrum(axes=313,
                                sharex=311 # note the sharex
                               )
    p = xy.ydata.phase_spectrum(axes=313, color="red")

    a.go("aset", "plot")
    p.plot() # p is on same axes than a no need to make aset
    m.go("aset", "plot", "draw", "show")

    return m

def psd():
    import numpy as np
    from smartplotlib import xyplot, alias
    Fs = 150.0;  # sampling rate
    Ts = 1.0/Fs; # sampling interval
    t = np.arange(0,1,Ts) # time vector

    noises = np.zeros( (len(t),), dtype=float )
    for a,f in zip([1e-2,2e-2,0.5e-2,1e-3],[20,40,60,80]):
        noises += np.sin(2*np.pi*f*t)*a
    ff = 5;   # frequency of the signal
    y = np.sin(2*np.pi*ff*t)+noises
    xy = xyplot(t, y, xlabel="time", ylabel="Signal",
                axes=211, hspace=0.4)


    xy.go("fclear", "fset", "aset", "plot")
    psd = xy.ydata.psd(axes=212, Fs=Fs)
    psd.axvline([5, 20,40,60,80], color="red", linestyle="--")
    ###
    # psd is plotted in 10*log10(psd) ('dB/Hz' or dB)
    # one may want to plot the linear scale
    # that easy :
    #    psd.plot(y=alias("psd"))

    psd.go("aset", "plot")

    xy.go("show", "draw")
    return psd

def csd():
    import numpy as np
    from smartplotlib import xyplot, alias
    # make some data
    dt = 0.01
    t = np.arange(0, 30, dt)
    nse1 = np.random.randn(len(t))                 # white noise 1
    nse2 = np.random.randn(len(t))                 # white noise 2
    r = np.exp(-t/0.05)

    cnse1 = np.convolve(nse1, r, mode='same')*dt   # colored noise 1
    cnse2 = np.convolve(nse2, r, mode='same')*dt   # colored noise 2

    # two signals with a coherent part and a random part
    s1 = 0.01*np.sin(2*np.pi*10*t) + cnse1
    s2 = 0.01*np.sin(2*np.pi*10*t) + cnse2

    xy = xyplot.derive(xlabel="time", ylabel="s1 & s2",
                       xlim=(0,5), axes=211)


    csd = xyplot.csd(s1, s2, 256, 1./dt, axes=212)

    xy.go("fclear", "aset")
    xy.plot(t, s1, 'b-', t, s2, 'g-')
    csd.go("plot", "aset", "show", "draw")




def binedstat():
    import numpy as np
    from smartplotlib import xyplot

    N=10000
    x = np.linspace(0, 2, N)
    yerr = np.random.rand(N)*np.exp(x)*np.sign(np.random.rand(N)-0.5)
    y = 5+yerr
    xy = xyplot(x, y, fmt="k+", axes=211)

    xy.go("fclear", "aset", "plot")

    stat = xy.ydata.binedstat.derive(linestyle="-")


    sp = stat(fstat="+std", color="red")
    sp.step()
    ## call sp.binedstat to enable the fill_between
    ## count = 0 is necessary here to have both lines sharing the same x
    ## otherwhis they will be shifted (for histogram purpose)
    sm = sp.binedstat(fstat="-std", color="red", count=0)
    sm.step()
    ## can fill between the last two calls
    sm.fill_between(alpha=0.3)

    m  = stat(fstat="mean", color="b")
    m.plot()

    m.errorbar(linestyle="-", marker="None")

    std = stat(axes=212, fstat="std", ylabel="Std",
               linestyle="solid", label="bined std")
    std.go("aset","fill")
    ##
    # fit a polynome on the newly created standar deviation
    # histogram. label=True mean that result of the fit is plotted
    # as label
    std.polyfit(dim=2, label=True).plot(fmt="r-")
    std.legend(loc="upper left")
    xy.go("show", "draw")
    return stat

def xbinedstat():
    import numpy as np
    from smartplotlib import xyplot

    N=10000
    x = np.linspace(0, 2, N)
    yerr = np.random.rand(N)*np.exp(x)*np.sign(np.random.rand(N)-0.5)
    y = 5+yerr
    xy = xyplot(y, x, fmt="k+")

    xy.go("fclear", "aset", "plot")


    stat = xy.xdata.binedstat.derive(linestyle="-", direction="x")
    ## itertcall iter on iterable and call the instances
    ps = [s.plot() for s in stat.itercall(fstat=["-std", "+std", "mean", "median"],
                                          color=list("rrgb"))]

    xy.go("show", "draw")
    return ps


    import numpy as np
    from smartplotlib import xyplot

    N=10000
    x = np.linspace(0, 2, N)
    yerr = np.random.rand(N)*np.exp(x)*np.sign(np.random.rand(N)-0.5)
    y = 5+yerr
    xy = xyplot(y, x, marker="+", color="k")

    xy.go("fclear", "aset", "plot")

    ## itertcall iter on iterable and call the instances
    s, m = xy.xbinedstat.itercall(fstat=["std","mean"],color=["red", "blue"])
    s.plot(linestyle="-")
    m.errorbar(linestyle="-", marker="None")

    xy.go("show", "draw")
    return xy


def histogram():
    import numpy as np
    from smartplotlib import dataplot, axes, alias


    data1 = np.random.normal(size=(1000,))
    data2 = np.random.normal(scale=0.8, size=(1000,))
    dp = dataplot(data1, figure="histograms")

    ## clear the figure
    dp.go("fclear")

    # make a copy of dp.histogram
    h = dp.histogram.derive(bins=20,
                            rwidth=0.8,
                            align="mid")

    # set default for errorbar and turn of label so it does not
    # a appear twice
    h.errorbar.update(color="k", linestyle="none", label=None)

    ###
    # histogram version does not accept several set of data
    # but one can still stack by calling back the histogram plot
    h1 = h(axes=221,
           density=False,
           ylabel="Stacked Histogram",
           label="some data"
          )

    h1.go("aset", "bar", "errorbar")

    ###
    # make a second histogram on the same figure
    # calling histogram again assure that the same bins are used for
    # both, because they are now set in h1 as an array
    h1.histogram(data2, stacked=True, color="green", label="more data").bar()
    h1.legend()





    h2 = h(density=True,
           ylabel="Fitted Density",
           axes=222
           )
    h2.go("aset", "bar", "errorbar")
    ##
    # fit the distribution an plot
    # label=True will generate a label with fit result
    h2.distribfit(label=True).plot()
    h2.legend() # should print fir result

    ####
    # make a second density histogram
    #h2.histogram(data2, stacked=True, color="green").bar()


    ####
    # Age pyramid like histogram
    h3 = h(
           ylabel="+- Histogram",
           axes=223
          )
    h3.go("aset", "bar", "errorbar")
    ####
    # make a opposite histogram, since stacked is false one must
    # put the counter to 0
    h3.histogram(data2, stacked=False, count=0, amplitude=-1, color="green").bar()



    ####
    # Side by side histogram
    # since we are going to make to histogram, put the rwidth to 0.4
    # and since align="mid" (="center") shift the histograms by -0.2
    h4 = h(
           ylabel="Side by Side Histogram",
           axes=224, rwidth=0.4, align="mid",
           roffset=-0.2
          )
    h4.go("aset", "bar", "errorbar")
    ####
    # make a opposite histogram, since stacked is false one must
    # put the counter to 0
    h4.histogram(data2, stacked=False, color="green").bar()

    h4.go("show", "draw")

    return h1, h2, h3, h4

    a = axes(figure="matplotlib.hist", go=["fclear","aset"],
             sharey=h, sharex=h, axes=211
             )
    a.hist([data1,data2], bins=bins, color=["blue", "green"],
           stacked=True, align=align)

    a2 = axes(figure="matplotlib.hist",
              sharey=h2, sharex=h2,
              axes=212)
    a2.hist([data1,data2], bins=bins, color=["blue", "green"],
            stacked=False, align=align)

    a.go("show", "draw")

    return h



def cohere():
    """
    Compute the coherence of two signals
    mpl_examples/pylab_examples/cohere_demo.py
    """
    import numpy as np
    from smartplotlib import xyplot, axes, alias


    # make a little extra space between the subplots

    dt = 0.01
    t = np.arange(0, 30, dt)
    nse1 = np.random.randn(len(t))                 # white noise 1
    nse2 = np.random.randn(len(t))                 # white noise 2
    r = np.exp(-t/0.05)

    cnse1 = np.convolve(nse1, r, mode='same')*dt   # colored noise 1
    cnse2 = np.convolve(nse2, r, mode='same')*dt   # colored noise 2

    # two signals with a coherent part and a random part
    s1 = 0.01*np.sin(2*np.pi*10*t) + cnse1
    s2 = 0.01*np.sin(2*np.pi*10*t) + cnse2

    ps1 = xyplot(t, s1, fmt='b-', y2= s2, fmt2="g-",
                 axes=211, xlabel="time", ylabel="s1 & s2")

    ps1.go("fclear", "aset", "plot")

    c = xyplot.cohere(s1, s2, 256, 1./dt,
                      ylabel="coherence", axes=212)

    c.go("aset", "plot", "draw", "show")
    return c


def annotates():
    import numpy as np
    from smartplotlib import xyplot, cycle
    n=10
    x = np.arange(n)
    y = x*x
    dy = ([10,-15]*(int(n/2)+1))[:n]
    print (dy)

    xy = xyplot(x, y, marker="*", dx=0.1, dy=dy,
                arrowprops=dict(width=2), axes=211,
                ylim=(-20,100), xlim=(-1,10)
                )
    xy.go("fclear", "aset", "plot", "annotates")

    # or an other fancy way to cycle is to use the iter method
    xy.plot(axes=212)
    xy.aset(axes=212)
    ans = [a() for a in  xyplot.annotates.iter(len(x), x=x, y=y,
                                              texts=list("abcdefghijklmnopqrstuvwxyz"),
                                              dx=0.0,
                                              dy=[10,-10], axes=212)
           ]
    xy.go("show", "draw")
    return xy


def eventplot():
    """ copied from http://matplotlib.org/xkcd/examples/pylab_examples/eventplot_demo.html"""
    import numpy as np
    from smartplotlib import axes
    np.random.seed(0)

    # create random data
    data1 = np.random.random([6, 50])

    # set different colors for each set of positions
    colors1 = np.array([[1, 0, 0],
                        [0, 1, 0],
                        [0, 0, 1],
                        [1, 1, 0],
                        [1, 0, 1],
                        [0, 1, 1]])

    # set different line properties for each set of positions
    # note that some overlap
    lineoffsets1 = np.array([-15, -3, 1, 1.5, 6, 10])
    linelengths1 = [5, 2, 1, 1, 3, 1.5]




    ax1, ax2 = axes.iteraxes(2,1, title=["horizontal eventplot", "vertical eventplot"],
                             orientation=["horizontal", "vertical"],
                             figure="way 1"
                            )
    # clear the figure
    ax1.fclear()
    ax1.eventplot(data1, colors=colors1, lineoffsets=lineoffsets1,
                  linelengths=linelengths1)
    ax1.aset()

    ax2.eventplot(data1, colors=colors1, lineoffsets=lineoffsets1,
                  linelengths=linelengths1)
    ax2.aset()

    ax1.go("show", "draw")

    ######
    # another way to do the same

    axs = axes(figure="way 2")
    ##
    # data are both the same, the only things that will change
    # is the orienatation and title
    axs.eventplot.update(positions=data1, colors=colors1, lineoffsets=lineoffsets1,
                         linelengths=linelengths1)

    for  a in axs.iteraxes(2,1,
                          title=["horizontal eventplot", "vertical eventplot"],
                          orientation=["horizontal", "vertical"]):
        a.go("aset","eventplot")

    axs.go("show", "draw")

    return axs


def histogram2d():
    from matplotlib.colors import LogNorm
    from smartplotlib import xyplot
    import numpy as np
    from pylab import randn

    #normal distribution center at x=0 and y=5
    x = randn(100000)
    y = randn(100000)+5
    xy = xyplot(x, y)
    xy.fclear()
    h = xy.histogram2d( bins=40, norm=LogNorm())

    pc = h.pcolorfast()
    h.colorbar(pc)
    h.contour(colors="k", contours=[10,300,700,900])
    h.go("show", "draw")
    return h





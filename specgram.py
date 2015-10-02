from __future__ import division, absolute_import, print_function
from .recursive import KWS, alias
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from .plotclasses import (imgplot, XYPlot, xyplot, DataPlot, dataplot)



import numpy as np


@imgplot.decorate(_example_=("specgram",None))
def specgram(plot, *args, **kwargs):
    """PlotFactory Wrapper of matplotlib.spectrogram: Compute and plot a spectrogram of data in *x*

    contrarly to matplolib.spectrogram, spectrogram return a new imgplot-like instance
    ready to plot result of the spectrogram.
    The parameter name from wich data is taken can be changed by data_key string parameter
    default is "x".

    Difrent parameters than matplotlib:
        data : the data used for the spectrogram. It can be aliased to 'x' or 'y'
            do specgram.info to see its state.
    Altered Parameters:
        img  : the img to plot from the spectrogram
        spec : the spectrogram
        extent : is None, set to 0, np.amax(t)

        freqs : frequences
        t :  time space
        axis : is set to "auto" (for imshow)
        scale : if None -> 'linear'

    the matplotlib doc is copied below
    Remember that this return a imgplot instance the output of spectrograph
    are in "spec", "freqs", "t" -> spec, freqs, t = obj.getargs("spec", "freqs", "t")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    """
    plot.update(kwargs.pop(KWS,{}), **kwargs)

    (data, NFFT, Fs, Fc, detrend,
     window, noverlap,
     xextent, pad_to, sides,
     scale_by_freq, mode, scale,
     )  = plot.parseargs(args, "data",
                    "NFFT", "Fs", "Fc", "detrend",
                    "window", "noverlap",
                     "xextent", "pad_to", "sides",
                    "scale_by_freq", "mode", "scale",

                    NFFT=None, Fs=None, Fc=None, detrend=None,
                    window=None, noverlap=None,
                    xextent=None, pad_to=None, sides=None,
                    scale_by_freq=None, mode=None, scale=None,
                    )


    if Fc is None:
        Fc = 0


    if mode == 'complex':
        raise ValueError('Cannot plot a complex specgram')

    if scale is None or scale == 'default':
        if mode in ['angle', 'phase']:
            scale = 'linear'
        else:
            scale = 'dB'
    elif mode in ['angle', 'phase'] and scale == 'dB':
        raise ValueError('Cannot use dB scale with angle or phase mode')

    spec, freqs, t = mlab.specgram(x=data, NFFT=NFFT, Fs=Fs,
                                   detrend=detrend, window=window,
                                   noverlap=noverlap, pad_to=pad_to,
                                   sides=sides,
                                   scale_by_freq=scale_by_freq,
                                   mode=mode)

    if scale == 'linear':
        Z = spec
    elif scale == 'dB':
        if mode is None or mode == 'default' or mode == 'psd':
            Z = 10. * np.log10(spec)
        else:
            Z = 20. * np.log10(spec)
    else:
        raise ValueError('Unknown scale %s', scale)

    Z = np.flipud(Z)

    if xextent is None:
        xextent = 0, np.amax(t)
    xmin, xmax = xextent
    freqs += Fc
    extent = xmin, xmax, freqs[0], freqs[-1]

    plot["img"] = Z

    plot.update(extent=extent, spec=spec, data=data,
                freqs=freqs, t=t, scale=scale, Fc=Fc)

    plot["axis"] = "auto"
    plot.goifgo()

specgram.finit.__doc__ = specgram.finit.__doc__ + plt.Axes.specgram.__doc__
specgram.__doc__ = specgram.finit.__doc__


_spectrum = dataplot.derive()

@_spectrum.decorate(_example_=("spectrum",None))
def magnitude_spectrum(plot,*args, **kwargs):
    """PlotFactory Wrapper of matplotlib.magniture_spectrum : Compute the magnitude spectrum of *x*.

    contrarly to matplolib.spectrogram, return a new xyplot instance
    ready to plot result of the spectrum.
    The parameter name from wich data is "data" but by default, data = alias("x")

    Parameters different than matplotlib:
        data : is the data to compute spectrum on. (can be aliases to 'x' or 'y')
        direction : the axis to plot the computed data, default is "y"

    Altered Parameters (if direction=="y"):
        x  : alias('freqs')
        y  : spectrum after scale
        freqs : frequences
        data : the input data

        spec : the spectrum before scale
        xlabel, ylabel :  are set if not already set
        ymin, ymax : set to 0, y  (for vlines plot)
        scale : if None -> 'linear'
        Fc : if None -> 0

      If direction == "x" swap  above x's and y's

    the matplotlib doc is copied below
    Remember that this return a xyplot instance the output of spectrograph
    are in "spec", "freqs"  ->  spec, freqs = getargs("spec", "freqs")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    plot.update(kwargs.pop(KWS,{}), **kwargs)
    (data, Fs, Fc, window,
     pad_to, sides, scale) = plot.parseargs(args,
                       "data", "Fs", "Fc", "window",
                       "pad_to", "sides", "scale",
                       Fs=None, Fc=None, window=None,
                       pad_to=None, sides=None, scale=None
                       )

    if Fc is None:
        Fc = 0

    if scale is None or scale == 'default':
        scale = 'linear'

    di, dd = plot._get_direction()

    spec, freqs = mlab.magnitude_spectrum(x=data, Fs=Fs, window=window,
                                          pad_to=pad_to, sides=sides)
    freqs += Fc

    if scale == 'linear':
        Z = spec
        yunits = 'energy'
    elif scale == 'dB':
        Z = 20. * np.log10(spec)
        yunits = 'dB'
    else:
        raise ValueError('Unknown scale %s', scale)


    plot.update( {di:alias("freqs"), dd:Z,
                  dd+"min":0, dd+"max":alias("y")},
                  min=0, max=alias("y"), lines=alias("freqs"),
                  spec=spec, Fc=Fc, scale=scale, data=data
                )

    plot.locals.setdefault(di+"label", 'Frequency')
    plot.locals.setdefault(dd+"label", 'Magnitude (%s)' % yunits)
    plot.goifgo()

magnitude_spectrum.finit.__doc__ = magnitude_spectrum.finit.__doc__ + plt.Axes.magnitude_spectrum.__doc__
magnitude_spectrum.__doc__ = magnitude_spectrum.finit.__doc__



@_spectrum.decorate(_example_=("spectrum",None))
def angle_spectrum(plot,*args, **kwargs):
    """PlotFactory Wrapper of matplotlib.angle_spectrum : Compute the angle spectrum (wrapped phase spectrum) of *x*

    contrarly to matplolib.phase_sectrum, return a new xyplot instance
    ready to plot result of the spectrum.


    Parameters different than matplotlib:
        data(str,alias) : is the data to compute the spectrum on. it can be aliased
            to 'x' or 'y' for instance. see obj.info

        direction("y"/"x") : the axis to plot the computed spectrum, default is "y"

    Altered Parameters (if direction=="y"):
        x  : alias('freqs')
        y  : alias('spec')
        freqs : frequences
        spec :  spectrum
        data :  the input data
        xlabel, ylabel :  are set if not already set
        ymin, ymax : set to 0, alias('spec')  (for vlines plot)

      if direction = "x" swap above x's and y's

    the matplotlib doc is copied below
    Remember that this return a xyplot instance the output of spectrograph
    are in "spec", "freqs"  ->  spec, freqs = getargs("spec", "freqs")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    plot.update(kwargs.pop(KWS,{}), **kwargs)
    (data, Fs, Fc, window,
     pad_to, sides) = plot.parseargs(args,
                       "data", "Fs", "Fc", "window",
                       "pad_to", "sides",
                       Fs=None, Fc=None, window=None,
                       pad_to=None, sides=None
                       )

    if Fc is None:
        Fc = 0

    di, dd = plot._get_direction()

    spec, freqs = mlab.angle_spectrum(x=data, Fs=Fs, window=window,
                                      pad_to=pad_to, sides=sides)
    freqs += Fc


    plot.update( {di:alias('freqs'), dd:alias('spec'),
                  dd+"min":0, dd+"max":alias('spec')},
                min=0, max=alias('spec'), lines=alias('freqs'),
                spec=spec, freqs=freqs, Fc=Fc , data=data)


    plot.locals.setdefault(di+"label", 'Frequency')
    plot.locals.setdefault(dd+"label", 'Angle (radians)')

    plot.goifgo()
angle_spectrum.finit.__doc__ = angle_spectrum.finit.__doc__ + plt.Axes.angle_spectrum.__doc__
angle_spectrum.__doc__ = angle_spectrum.finit.__doc__


@_spectrum.decorate(_example_=("spectrum",None))
def phase_spectrum(plot, *args,  **kwargs):
    """PlotFactory Wrapper of matplotlib.phase_spectrum : Compute the phase spectrum (unwrapped angle spectrum) of *data*

    contrarly to matplolib.phase_sectrum, return a new xyplot instance
    ready to plot result of the spectrum.


    Different Parameters than matplotlib:
        data : the data set to compute the spectrum on.it can be aliased
            to 'x' or 'y' for instance. see obj.info
        direction ("y"/"x") : in wich axis the spectrum is ploted, default is "y"

    Altered Parameters (if direction=="y"):
        x  : alias('freqs')
        y  : alias('spec')
        freqs : frequences
        spec : spectrum
        data : the input data
        xlabel, ylabel :  are set if not already set
        ymin, ymax : set to 0, alias('spec')  (for vlines plot)

      if direction == "x" swap above x's and y's

    the matplotlib doc is copied below
    Remember that this return a xyplot instance the output of spectrograph
    are in "spec", "freqs"  ->  getargs("spec", "freqs")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    plot.update(kwargs.pop(KWS,{}), **kwargs)
    (data, Fs, Fc, window,
     pad_to, sides) = plot.parseargs(args,
                       "data", "Fs", "Fc", "window",
                       "pad_to", "sides",
                       Fs=None, Fc=None, window=None,
                       pad_to=None, sides=None
                       )
    if Fc is None:
        Fc = 0

    di, dd = plot._get_direction()


    spec, freqs = mlab.phase_spectrum(x=data, Fs=Fs, window=window,
                                      pad_to=pad_to, sides=sides)
    freqs += Fc


    plot.update( {di:alias('freqs'), dd:alias('spec'),
                   dd+"min":0, dd+"max":alias('spec')},
                   min=0, max=alias('spec'), lines=alias('freqs'),
                   spec=spec, freqs=freqs, data=data,
                Fc=Fc)

    plot.locals.setdefault(di+"label", 'Frequency')
    plot.locals.setdefault(dd+"label", 'Phase (radians)')

    plot.goifgo()
phase_spectrum.finit.__doc__ = phase_spectrum.finit.__doc__ + plt.Axes.phase_spectrum.__doc__
phase_spectrum.__doc__ = phase_spectrum.finit.__doc__

@_spectrum.decorate(_example_=("psd", None))
def psd(plot, *args, **kwargs):
    """PlotFactory Wrapper of matplotlib.psd : Compute the psd(power spectral density) of *data*

    contrarly to matplolib.psd, return a new xyplot factory instance
    ready to plot result of the psd.


    Different Parameters than matplotlib:
        data : the data set to compute the psd on it can be aliased
            to 'x' or 'y' for instance. see obj.info
        direction ("y"/"x") : in wich axis the psd is ploted, default is "y"

    Altered Parameters (if direction=="y"):
        x  : alias('freqs')
        y  : 10*log10(psd)
        freqs : frequences
        psd  : psd result in linear space
        data : the input data
        xlabel, ylabel :  are set if not already set
        ymin, ymax : set to 0, alias('spec')  (for vlines plot)
        min, max, lines : set to 0, alias('spec'), alias('freq')

      if direction == "x" swap above x's and y's

    the matplotlib doc is copied below
    Remember that this return a xyplot instance the output of spectrograph
    are in "psd", "freqs"  ->  psd, freqs = getargs("psd", "freqs")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    plot.update(kwargs.pop(KWS,{}), **kwargs)

    (data,
     NFFT, Fs, Fc, detrend,
     window, noverlap, pad_to,
     sides, scale_by_freq) = plot.parseargs(args, "data",
                    "NFFT", "Fs", "Fc", "detrend",
                    "window", "noverlap", "pad_to",
                    "sides", "scale_by_freq",
                    NFFT=None, Fs=None, Fc=None, detrend=None,
                    window=None, noverlap=None, pad_to=None,
                    sides=None, scale_by_freq=None)

    if Fc is None:
        Fc = 0

    pxx, freqs = mlab.psd(x=data, NFFT=NFFT, Fs=Fs, detrend=detrend,
                          window=window, noverlap=noverlap, pad_to=pad_to,
                          sides=sides, scale_by_freq=scale_by_freq)
    pxx.shape = len(freqs),
    freqs += Fc

    if scale_by_freq in (None, True):
        psd_units = 'dB/Hz'
    else:
        psd_units = 'dB'
    di, dd = plot._get_direction()

    plot.update( {di:alias('freqs'), dd:10 * np.log10(pxx),
               dd+"min":0, dd+"max":alias(dd)},
               min=0, max=alias(dd), lines=alias('freqs'),
               psd=pxx, freqs=freqs, data=data,
               Fc=Fc)
    plot.locals.setdefault(di+"label", 'Frequency')
    plot.locals.setdefault(dd+"label", 'Power Spectral Density (%s)' % psd_units)


    plot.aset.update(grid=True)
    plot.goifgo()

psd.finit.__doc__ = psd.finit.__doc__ + plt.Axes.psd.__doc__
psd.__doc__ = psd.finit.__doc__


@_spectrum.decorate(_example_=("csd", None))
def csd(plot, *args, **kwargs):
    """PlotFactory Wrapper of matplotlib.csd : Compute the csd(cross-spectral) of *data1* vs *data2*

    contrarly to matplolib.psd, return a new xyplot factory instance
    ready to plot result of the csd.



    Different Parameters than matplotlib:
        data1 : fisrt data set
        data2 : second data set They can be liases to "x" and "y" for instance
        direction ("y"/"x") : in wich axis the spectrum is ploted, default is "y"

    Machined Parameters (if direction=="y"):
        x  : alias('freqs')
        y  : 10*log10(psd)
        freqs : frequences
        csd  : psd result in linear space
        data : the input data
        xlabel, ylabel :  are set if not already set
        ymin, ymax : set to 0, alias('spec') (for vlines plot)
        min, max, lines : set to 0, alias('spec'), alias('freq')

      if direction == "x" swap above x's and y's

    the matplotlib doc is copied below
    Remember that this return a xyplot instance the output of spectrograph
    are in "csd", "freqs"  ->  csd, freqs  =getargs("csd", "freqs")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    plot.update(kwargs.pop(KWS,{}), **kwargs)
    (data1, data2,
    NFFT, Fs, Fc, detrend,
    window, noverlap, pad_to,
    sides, scale_by_freq) = plot.parseargs(args,
          "data1", "data2",
          "NFFT", "Fs", "Fc", "detrend",
          "window", "noverlap", "pad_to",
          "sides", "scale_by_freq",
          NFFT=None, Fs=None, Fc=None, detrend=None,
          window=None, noverlap=None, pad_to=None,
          sides=None, scale_by_freq=None
         )
    if Fc is None:
        Fc = 0

    pxy, freqs = mlab.csd(x=data1, y=data2, NFFT=NFFT, Fs=Fs, detrend=detrend,
                          window=window, noverlap=noverlap, pad_to=pad_to,
                          sides=sides, scale_by_freq=scale_by_freq)
    pxy.shape = len(freqs),
    # pxy is complex
    freqs += Fc

    di, dd = plot._get_direction()

    plot.update( {di:alias('freqs'), dd:10 * np.log10(pxy),
               dd+"min":0, dd+"max":alias(dd)},
               min=0, max=alias(dd), lines=alias('freqs'),
               csd=pxy, freqs=freqs, data1=data1,data2=data2,
               Fc=Fc)
    plot.locals.setdefault(di+"label", 'Frequency')
    plot.locals.setdefault(dd+"label", 'Cross Spectrum Magnitude (dB)')

    plot.aset.update(grid=True)
    plot.goifgo()

csd.finit.__doc__ = csd.finit.__doc__ + plt.Axes.csd.__doc__
csd.__doc__ = csd.finit.__doc__

@_spectrum.decorate(_example_=("cohere", None))
def cohere(plot, *args, **kwargs):
    """PlotFactory Wrapper of function cohere : Plot the coherence between *x* and *y*.

    contrarly to matplolib.cohere, cohere return a new imgplot-like instance
    ready to plot result of the cohere.


    Different Parameters than matplotlib:
        data1 : first data set  (can be aliased to 'x' for instance)
        data2 : second data set (can be aliased to 'y' for instance)
            So by default compute corelation of x over y
        direction ("y"/"x") : in wich axis the coherence is ploted, default is "y"

    Altered Parameters (if direction=="y") :
        x  : alias('freqs')
        y  : alias('cohere')
        freqs : frequences
        cohere : computed coherence
        ymin, ymax : set to 0, alias('cohere') (for vlines plot)
        data1, data2 : copy of the inputs

      if direction == "x" swap x's and y's

    the matplotlib doc is copied below
    Remember that this return a  xyplot instance the output of spectrograph
    are in "cohere", "freqs" ->  cohere, freqs = obj.getargs("cohere", "freqs")

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    """
    plot.update(kwargs.pop(KWS,{}), **kwargs)
    (data1, data2, NFFT, Fs, Fc, detrend,
    window, noverlap, pad_to,
    sides, scale_by_freq)= plot.parseargs(args,
                "data1",
                "data2",
                "NFFT", "Fs", "Fc", "detrend",
                "window", "noverlap", "pad_to",
                "sides", "scale_by_freq",
                NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none,
                window=mlab.window_hanning, noverlap=0, pad_to=None,
                sides='default', scale_by_freq=None
                )

    # index_direction, data_direction
    di, dd = plot._get_direction()

    cxy, freqs = mlab.cohere(x=data1, y=data2, NFFT=NFFT, Fs=Fs, detrend=detrend,
                             window=window, noverlap=noverlap,
                             scale_by_freq=scale_by_freq)
    freqs += Fc

    plot.update({di:alias('freqs'), dd:alias('cohere'),
                 dd+"min":0, dd+"max":alias('cohere')},
                 min=0, max=0, lines=alias('freqs'),
                 cohere=cxy, freqs=freqs, data1=data1, data2=data2)


    plot.locals.setdefault(di+"label", 'Frequency')
    plot.locals.setdefault(dd+"label", 'Coherence')
    plot.goifgo()


######
# add them to the XPlot, YPlot, _XYPlot



DataPlot.specgram = specgram
XYPlot.xspecgram = specgram.derive(data=alias("x"))
XYPlot.yspecgram = specgram.derive(data=alias("y"))

DataPlot.magnitude_spectrum = magnitude_spectrum


XYPlot.xmagnitude_spectrum = magnitude_spectrum.derive(data=alias("x"))
XYPlot.ymagnitude_spectrum = magnitude_spectrum.derive(data=alias("y"))


DataPlot.angle_spectrum = angle_spectrum


XYPlot.xangle_spectrum = angle_spectrum.derive(data=alias("x"))
XYPlot.yangle_spectrum = angle_spectrum.derive(data=alias("y"))

DataPlot.phase_spectrum   = phase_spectrum
XYPlot.xphase_spectrum = phase_spectrum.derive(data=alias("x"))
XYPlot.yphase_spectrum = phase_spectrum.derive(data=alias("y"))


DataPlot.psd   = psd
XYPlot.xpsd = psd.derive(data=alias("x"))
XYPlot.ypsd = psd.derive(data=alias("y"))


# cohere only on _XYPlot
XYPlot.cohere = cohere.derive( data1=alias("x"), data2=alias("y"))
XYPlot.csd = csd.derive( data1=alias("x"), data2=alias("y"))




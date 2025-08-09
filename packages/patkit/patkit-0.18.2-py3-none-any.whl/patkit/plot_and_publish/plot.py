#
# Copyright (c) 2019-2025
# Pertti Palo, Scott Moisik, Matthew Faytak, and Motoki Saito.
#
# This file is part of the Phonetic Analysis ToolKIT
# (see https://github.com/giuthas/patkit/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# The example data packaged with this program is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License. You should have received a
# copy of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License along with the data. If not,
# see <https://creativecommons.org/licenses/by-nc-sa/4.0/> for details.
#
# When using the toolkit for scientific publications, please cite the
# articles listed in README.md. They can also be found in
# citations.bib in BibTeX format.
#
"""patkit plotting functions."""

import logging
from typing import Sequence

from matplotlib.collections import LineCollection
from matplotlib.image import AxesImage
from matplotlib.typing import ColorType
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

import numpy as np
from scipy import interpolate
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import kaiser

from patkit.computational import normalise_timeseries
from patkit.configuration import TimeseriesNormalisation
from patkit.constants import AnnotationType, GuiColorScheme
from patkit.data_structures import Modality
from patkit.gui.boundary_animation import AnimatableBoundary
from patkit.patgrid import PatTier

_logger = logging.getLogger('patkit.plot')


def plot_1d_modality(axes: Axes,
                     modality: Modality,
                     time_offset: float,
                     xlim: tuple[float, float],
                     **kwargs) -> Line2D:
    """
    Plot a modality assuming its data is one dimensional.

    Parameters
    ----------
    axes : Axes
        Axes to plot on.
    modality : Modality
        Modality to plot.
    time_offset : float
        time_offset to apply to the plot
    xlim : tuple[float, float]
        x-axis limits.
    Returns
    -------
    LegendItem
        _description_
    """
    data = modality.data
    time = modality.timevector - time_offset

    line = plot_timeseries(axes, data, time, xlim, **kwargs)
    return line


def plot_timeseries(axes: Axes,
                    data: np.ndarray,
                    time: np.ndarray,
                    xlim: tuple[float, float],
                    ylim: tuple[float, float] | None = None,
                    normalise: TimeseriesNormalisation | None = None,
                    y_offset: float = 0.0,
                    number_of_ignored_frames: int = 10,
                    ylabel: str | None = None,
                    picker=None,
                    color: str | None = "deepskyblue",
                    linestyle: tuple[int, tuple[int, int]] | str = "-",
                    label: str | None = None,
                    alpha: float = 1.0,
                    sampling_step: int = 1) -> Line2D:
    """
    Plot a timeseries.

    The timeseries most likely comes from a Modality, but that is left up to
    the caller. 

    Parameters
    ----------
    axes : Axes
        matplotlib axes to plot on.
    data : np.ndarray
        the timeseries.
    time : np.ndarray
        timestamps for the timeseries
    xlim : Tuple[float, float]
        limits for the x-axis in seconds.
    ylim : Optional[Tuple[float, float]], optional
        _description_, by default None
    normalise : Optional[TimeseriesNormalisation], optional
        Should minimum value be scaled to 0 ('bottom') and/or maximum to 1
        ('peak'), by default None
    y_offset : Optional[float], optional
        y-direction offset for to be applied to the whole timeseries, by
        default 0.0
    number_of_ignored_frames : int, optional
        how many values to ignore from the beginning of data when normalising,
        by default 10
    ylabel : Optional[str], optional
        label for this axes, by default None
    picker : _type_, optional
        a picker tied to the plotted PD curve to facilitate annotation, by
        default None
    color : str, optional
        matplotlib color for the line, by default "deepskyblue"
    linestyle : str, optional
        _description_, by default "-"
    label : Optional[str], optional
        label for the series, by default None
    alpha : float, optional
        alpha value for the line, by default 1.0
    sampling_step : int, optional
        Length of step to use in plotting, by default 1 This is used in e.g.
        plotting downsampled series.

    Returns
    -------
    Line2D
        Not the plotted line but one that can be used for adding a legend to
        the plot.
    """
    plot_data = data[number_of_ignored_frames:]
    plot_time = time[number_of_ignored_frames:]

    _logger.debug("Normalisation is %s.", normalise)
    plot_data = normalise_timeseries(plot_data, normalisation=normalise)
    plot_data = plot_data + y_offset

    if color == "rotation":
        color = None

    if picker:
        axes.plot(
            plot_time[:: sampling_step],
            plot_data[:: sampling_step],
            color=color, lw=1, linestyle=linestyle, picker=picker,
            alpha=alpha, label=label)
    else:
        axes.plot(plot_time[::sampling_step], plot_data[::sampling_step],
                  color=color, lw=1, linestyle=linestyle, alpha=alpha,
                  label=label)

    # The official fix for the above curve not showing up on the legend.
    timeseries = Line2D([], [], color=color, lw=1, linestyle=linestyle)

    axes.set_xlim(xlim)

    if ylim:
        axes.set_ylim(ylim)
    else:
        y_limits = list(axes.get_ylim())
        if normalise:
            if normalise.peak:
                y_limits[1] = 1.05
            elif normalise.bottom:
                y_limits[0] = -0.05
        axes.set_ylim(y_limits)

    if ylabel:
        axes.set_ylabel(ylabel)

    return timeseries


def mark_peaks(
        axes: Axes,
        modality: Modality,
        xlim: tuple[float, float] = None,
        display_prominence_values: bool = False,
        colors: ColorType | Sequence[ColorType] | None = 'sandybrown',
        time_offset: float = 0.0
) -> LineCollection | None:
    """
    Mark peak annotations from the modality on the axes.

    If valleys instead of peaks are wanted, just pass in -data.

    Parameters
    ----------
    axes : Axes
        Axes to draw on.
    modality : Modality
        A timeseries modality with peak annotations.
    xlim : Tuple[float, float], optional
        Limits of drawing, by default None. This is useful in avoiding GUI
        hiccups by not drawing outside of the current limits. 
    display_prominence_values : bool, optional
        If prominence values should be plotted next to the peaks, by default
        False
    colors : ColorType | Sequence[ColorType] | None, optional
        Color to use in plotting the peak marker lines, by default 'sandybrown'
    time_offset : float
        time_offset to apply to the peaks, by default 0.0.

    Returns
    -------
    LineCollection
        _description_
    """
    if AnnotationType.PEAKS not in modality.annotations:
        return None

    annotations = modality.annotations[AnnotationType.PEAKS]
    generating_parameters = annotations.generating_parameters
    number_of_ignored_frames = generating_parameters.number_of_ignored_frames

    data = modality.data[number_of_ignored_frames:]
    timevector = modality.timevector[number_of_ignored_frames:]
    timevector = timevector - time_offset

    peak_indeces = annotations.indeces - number_of_ignored_frames
    properties = annotations.properties
    normalise = annotations.generating_parameters.normalisation

    _logger.debug("Normalisation is %s.", normalise)
    data = normalise_timeseries(data, normalisation=normalise)

    prominences = properties['prominences']
    contour_heights = data[peak_indeces] - prominences
    line_collection = axes.vlines(
        x=timevector[peak_indeces],
        ymin=contour_heights,
        ymax=data[peak_indeces],
        colors=colors, linestyles=':')

    if display_prominence_values:
        for i, peak in enumerate(peak_indeces):
            x = timevector[peak]
            if not xlim or xlim[0] <= x <= xlim[1]:
                axes.text(
                    x=timevector[peak], y=data[peak],
                    s=f"{prominences[i]:,.3f}"
                )
    return line_collection


def plot_patgrid_tier(
    axes: Axes,
    tier: PatTier,
    time_offset: float = 0,
    draw_text: bool = True,
    text_y: float = 500,
    xlim: list[float, float] | None = None,
) -> tuple[list[AnimatableBoundary], Line2D | None]:
    """
    Plot a textgrid tier on the axis and return animator objects.

    This is used both for displaying tiers as part of the tier display 
    and for decorating other plots with either just the boundary lines 
    or both boundaries and the annotation text.

    Arguments:
    ax -- matplotlib axes to plot on.
    tier -- TextGrid Tier represented as a SatTier.

    Keyword arguments:
    stimulus_onset -- onset time of the stimulus in the recording in
        seconds. Default is 0s.
    draw_text -- boolean value indicating if each segment's text should
        be drawn on the plot. Default is True.
    draggable --
    text_y -- 

    Returns a line object for the segment line, so that it
    can be included in the legend.
    """
    text_settings = {
        'horizontalalignment': 'center',
        'verticalalignment': 'center',
    }

    line = None
    text = None
    boundaries = []
    for segment in tier:
        if xlim is not None:
            if segment.end is not None and xlim[0] > segment.end-time_offset:
                prev_text = text
                text = None
                continue
            if segment.begin-time_offset > xlim[1]:
                prev_text = text
                text = None
                continue

        time = segment.begin - time_offset
        line = axes.axvline(
            x=time,
            color="dimgrey",
            lw=1,
            linestyle='--')
        if draw_text and segment.label:
            prev_text = text
            if xlim is not None:
                visible_x_min = max(xlim[0], segment.begin - time_offset)
                visible_x_max = min(xlim[1], segment.end - time_offset)
                text_x = (visible_x_max + visible_x_min)/2
            else:
                text_x = segment.mid - time_offset
            text = axes.text(text_x,
                             text_y, segment.label,
                             text_settings, color="dimgrey")
            boundaries.append(
                AnimatableBoundary(axes, line, time, prev_text, text))
        else:
            prev_text = text
            text = None
            boundaries.append(
                AnimatableBoundary(axes, line, time, prev_text, text))
    return boundaries, line


def plot_wav(
        ax: Axes,
        waveform: np.ndarray,
        wav_time: np.ndarray,
        xlim: tuple[float, float],
        picker=None,
        mode: GuiColorScheme = GuiColorScheme.FOLLOW_SYSTEM,
) -> list[Line2D]:
    """
    Plot a waveform.

    Parameters
    ----------
    ax : Axes
        Axes to plot on.
    waveform : np.ndarray
        Waveform to plot
    wav_time : np.ndarray
        Timevector for the waveform. Must be of same shape and length as the
        waveform.
    xlim : Tuple[float, float]
        x-axis limits.
    picker : _type_, optional
        Picker for selecting points on the plotted line, by default None

    Returns
    -------
    Line2D
        The plotted line.
    """
    normalised_wav = waveform / np.amax(np.abs(waveform))

    match mode:
        case GuiColorScheme.DARK:
            color="lightgrey"
        case GuiColorScheme.LIGHT:
            color="k"
        case GuiColorScheme.FOLLOW_SYSTEM:
            _logger.warning(
                "GuiColorScheme FOLLOW_SYSTEM encountered in plot.")
            _logger.warning(
                "Can't actually deal with following the system in plot, "
                "so just going dark.")
    
    if picker:
        line = ax.plot(wav_time, normalised_wav,
                       color=color, lw=.25, picker=picker)
    else:
        line = ax.plot(wav_time, normalised_wav, color=color, lw=.25)

    ax.axvline(x=0, color="dimgrey", lw=1, linestyle=(0, (5, 10)))

    ax.set_xlim(xlim)
    ax.set_ylim((-1.1, 1.1))
    ax.set_ylabel("Wave")

    return line


def plot_spectrogram2(
        axes: Axes,
        waveform: np.ndarray,
        sampling_frequency: float,
        extent_on_x: tuple[float, float],
        window_length: int = 220,
        n_overlap: int = 215,
        cmap: str = 'Greys',
        ylim: tuple[float, float] = (0, 10000),
        ylabel: str = "Spectrogram",
        picker=None,
        mode: GuiColorScheme = GuiColorScheme.FOLLOW_SYSTEM,
) -> AxesImage:
    """
    Plot a spectrogram with background noise removal.

    The background noise is removed by setting the colormap's vmin (minimum
    value) to the median of the spectrogram values. This may not work for all
    samples especially if there is very little silence.

    Parameters
    ----------
    axes : Axes
        Axes to plot on.
    waveform : np.ndarray
        Waveform to calculate the spectrogram on.
    sampling_frequency : float
        Sampling frequency of the signal
    extent_on_x : Tuple[float, float]
        Time minimum and maximum values.
    window_length : int, optional
        Length of the fast fourier transform window, by default 220
    n_overlap : int, optional
        How many samples to overlap consecutive windows by, by default 215
    cmap : str, optional
        The colormap, by default 'Greys'
    ylim : Tuple[float, float], optional
        Y limits, by default (0, 10000)
    ylabel : str, optional
        Y label, by default "Spectrogram"
    picker : _type_, optional
        The picker for selecting points, by default None
    mode : GuiStyle, optional
        Dark or light mode plot, by default GuiStyle.FOLLOW_SYSTEM

    Returns
    -------
    np.ndarray
        The spectrogram as a 2d array.
    """

    normalised_wav = waveform / np.amax(np.abs(waveform))

    # g_std = 8  # standard deviation for Gaussian window in samples
    # w = gaussian(50, std=g_std, sym=True)  # symmetric Gaussian window
    intensity_window = kaiser(window_length, beta=20)  # copied from praat
    short_time_fft = ShortTimeFFT(
        intensity_window, hop=window_length-n_overlap, fs=sampling_frequency,
        mfft=window_length, scale_to='psd')
    spectrogram = short_time_fft.stft(normalised_wav)
    extent = list(short_time_fft.extent(len(normalised_wav)))
    extent[0:2] = extent_on_x

    spectrogram = 20*np.log(abs(spectrogram))
    # Make the median white/background colour.
    min_value = np.median(spectrogram)

    match mode:
        case GuiColorScheme.DARK:
            cmap = "Greys_r"
        case GuiColorScheme.LIGHT:
            cmap = "Greys"
        case GuiColorScheme.FOLLOW_SYSTEM:
            _logger.warning(
                "GuiColorScheme FOLLOW_SYSTEM encountered in plot.")
            _logger.warning(
                "Can't actually deal with following the system in plot, "
                "so just going dark.")

    image = axes.imshow(spectrogram, origin='lower', aspect='auto',
                        extent=extent, cmap=cmap, vmin=min_value,
                        picker=picker)

    axes.set_ylim(ylim)
    axes.set_ylabel(ylabel)

    return image


def plot_spectrogram(
        ax: Axes,
        waveform: np.ndarray,
        sampling_frequency: float,
        extent_on_x: tuple[float, float],
        window_length: int = 220,
        n_overlap: int = 215,
        cmap: str = 'Greys',
        ylim: tuple[float, float] = (0, 10000),
        ylabel: str = "Spectrogram",
        picker=None) -> tuple:
    """
    Plot a spectrogram.

    Background noise is not removed. If that is needed try spectrogram2.

    Parameters
    ----------
    ax : Axes
        Axes to plot on.
    waveform : np.ndarray
        Waveform to calculate the spectrogram on.
    sampling_frequency : float
        Sampling frequency of the signal
    extent_on_x : Tuple[float, float]
        Time minimum and maximum values.
    window_length : int, optional
        Length of the fast fourier transform window, by default 220
    n_overlap : int, optional
        How many samples to overlap consecutive windows by, by default 215
    cmap : str, optional
        The colormap, by default 'Greys'
    ylim : Tuple[float, float], optional
        Y limits, by default (0, 10000)
    ylabel : str, optional
        Y label, by default "Spectrogram"
    picker : _type_, optional
        The picker for selecting points, by default None

    Returns
    -------
    tuple
        Pxx, freqs, bins, im as returned by Axes.specgram.
    """

    normalised_wav = waveform / np.amax(np.abs(waveform))

    # xlim = [xlim[0]+time_offset, xlim[1]+time_offset]
    # the length of the windowing segments
    Pxx, freqs, bins, im = ax.specgram(
        normalised_wav, NFFT=window_length, Fs=sampling_frequency,
        noverlap=n_overlap, vcmap=cmap, xextent=extent_on_x, picker=picker)
    (bottom, top) = im.get_extent()[2:]
    im.set_extent(
        (extent_on_x[0]+bins[0], extent_on_x[0]+bins[-1], bottom, top))

    ax.set_ylim(ylim)
    ax.set_ylabel(ylabel)

    return Pxx, freqs, bins, im


def plot_density(
        ax: Axes,
        frequencies: np.ndarray,
        x_values: np.ndarray | None = None,
        ylim: tuple[float, float] | None = None,
        ylabel: str = "Densities)",
        picker=None):

    densities = frequencies/np.amax(frequencies)
    if not x_values:
        x_values = np.arange(len(densities))

    if picker:
        line = ax.plot(x_values, densities, color="k", lw=1, picker=picker)
    else:
        line = ax.plot(x_values, densities, color="k", lw=1)

    if ylim:
        ax.set_ylim(ylim)
    ax.set_ylabel(ylabel)

    return line


def plot_spline(
        ax: Axes,
        data: np.ndarray,
        limits: tuple[int, int] | None = None,
        display_line: bool = True,
        display_points: bool = False) -> None:
    """
    Plot a spline on the given axes.

    Parameters
    ----------
    ax : Axes
        matplotlib axes
    data : np.ndarray
        the spline Cartesian coordinates in axes order x-y, spline points.
    limits : Optional[tuple[int, int]], optional
        How many points to leave out from the (front, back) of the spline, by
        default None
    display_line : bool, optional
        should the interpolated spline line be drawn, by default True
    display_points : bool, optional
        should the spline control points be drawn, by default False
    """
    solid_data = data
    if limits:
        if limits[1] == 0:
            solid_data = data[:, limits[0]:]
        else:
            solid_data = data[:, limits[0]:-limits[1]]

    if display_line:
        if limits:
            interpolation_result = interpolate.splprep(data, s=0)
            tck = interpolation_result[0]
            interpolation_points = np.arange(0, 1.01, 0.01)
            interpolated_spline = interpolate.splev(interpolation_points, tck)
            ax.plot(interpolated_spline[0],
                    -interpolated_spline[1],
                    color='orange', linewidth=1, alpha=.5)

        interpolation_result = interpolate.splprep(solid_data, s=0)
        tck = interpolation_result[0]
        interpolation_points = np.arange(0, 1.01, 0.01)
        interpolated_spline = interpolate.splev(interpolation_points, tck)
        ax.plot(interpolated_spline[0],
                -interpolated_spline[1], color='red', linewidth=1)
    if display_points:
        ax.plot(data[0, :], -data[1, :], 'ob', markersize=2)

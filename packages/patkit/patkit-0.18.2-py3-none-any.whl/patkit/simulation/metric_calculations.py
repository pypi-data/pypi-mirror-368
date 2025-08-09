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
"""
This module contains functions used to apply metrics to simulated data.
"""

import numpy as np

from patkit.constants import ComparisonMember
from patkit.utility_functions import product_dict
from .simulation_datastructures import Comparison, MetricFunction

from .contour_tools import contour_point_perturbations


def get_distance_metric_baselines(
        metric: MetricFunction,
        contours: dict[str, np.ndarray]
) -> dict[Comparison, float]:
    """
    Get the metric evaluated between each pair of the contours.

    The pairs are formed as the Cartesian product of the keys in the contours
    dict.

    Note that this function is intended for pairwise comparisons. Timeseries
    comparisons should be/will be implemented as a separate function.

    Parameters
    ----------
    metric : MetricFunction
        Callable which will be called on each pair of contours.
    contours : dict[str, np.ndarray]
        Contours in a dict indexed by contour names.

    Returns
    -------
    dict[Comparison, float]
        Comparisons formed from the contour names and the metric value for
        performing the specified comparisons.
    """
    contour_names = list(contours.keys())
    combination_dict = {'first': contour_names,
                        'second': contour_names,
                        'perturbed': ComparisonMember.values()}
    name_combinations = product_dict(**combination_dict)
    comparisons = [
        Comparison(first=combination['first'],
                   second=combination['second'],
                   perturbed=combination['perturbed'])
        for combination in name_combinations
    ]

    raw_results = {
        comp: metric(
            np.stack([contours[comp.first], contours[comp.second]]))
        for comp in comparisons}

    results = {
        key: float(raw_results[key][0])
        for key in raw_results
    }

    return results


def get_shape_metric_baselines(
        metric: MetricFunction,
        contours: dict[str, np.ndarray]
) -> dict[str, float]:
    """
    Get the metric evaluated between each pair of the contours.

    The pairs are formed as the Cartesian product of the keys in the contours
    dict.

    Parameters
    ----------
    metric : MetricFunction
        Callable which will be called on each pair of contours.
    contours : dict[str, np.ndarray]
        Contours in a dict indexed by contour names.

    Returns
    -------
    dict[str, float]
        The unperturbed metric for each contour in a dict indexed by contour
        names.
    """
    contour_names = list(contours.keys())

    raw_results = {
        name: metric(np.expand_dims(contours[name], 0))
        for name in contour_names
    }

    results = {
        key: float(raw_results[key][0])
        for key in raw_results
    }

    return results


def calculate_perturbed_metric_series(
        metric: MetricFunction,
        contour_to_perturb: np.ndarray,
        reference_contour: np.ndarray | None = None,
        perturbations: list[float] | tuple[float] = (1.0,),
        interleave: bool = False,
        return_even: bool = True,
) -> dict[str, np.ndarray]:
    """
    Generate a series of perturbed contours and calculate the metric on them.

    This function is usually not called directly but only implicitly by
    calculate_metric_series_for_contours and
    calculate_metric_series_for_comparisons.

    Parameters
    ----------
    metric : MetricFunction
        The metric function. Should accept a 2D np.ndarray as its argument and
        return an `np.ndarray`. This can be generated with `functools.partial`
        from standard patkit metrics.
    contour_to_perturb : np.ndarray
        The contour the perturbations will be applied to.
    reference_contour : Optional[np.ndarray], optional
        A reference contour to compare the perturbed ones with. If None, the
        contour_to_perturb will be used instead. By default, None
    perturbations : Optional[tuple[float]], optional
        Tuple of perturbations to apply in absolute r values.
        By default, `(1.0,)`.
    interleave : Optional[bool], optional
        Should the reference contour be interleaved with the perturbed
        contours. Use this for pairwise metrics like ANND or MPBPD when
        comparisons with baseline are wanted. By default, False
    return_even: Optional[bool] optional,
        Whether the even or odd comparisons should be returned. True means
        comparing reference to perturbed, False means comparing perturbed to
        reference. By default, True, Ignored if `interleave` is False.

    Returns
    -------
    dict[str, np.ndarray]
        A dictionary of the results. Keys are the perturbation values and
        values are the series resulting from applying the metric with one value
        for each application.
    """
    results = {}
    for perturbation in perturbations:
        perturbed = contour_point_perturbations(
            contour_to_perturb.copy(),
            reference_contour,
            perturbation,
            interleave=interleave
        )
        if interleave:
            if return_even:
                results[perturbation] = metric(perturbed)[::2]
            else:
                results[perturbation] = metric(perturbed)[1::2]
        else:
            results[perturbation] = metric(perturbed)
    return results


def calculate_metric_series_for_contours(
        metric: MetricFunction,
        contours: dict[str, np.ndarray],
        perturbations: list[float] | tuple[float] = (1.0,)
) -> dict[str, dict[str, np.ndarray]]:
    """
    Calculate the metric for each contour while perturbing each point.

    Parameters
    ----------
    metric : MetricFunction
        The metric to calculate.
    contours : dict[str, np.ndarray]
        A dict of the contours.
    perturbations : Optional[tuple[float]], optional
        A tuple of perturbations to apply. By default, `(1.0,)`.

    Returns
    -------
    dict[str, dict[str, np.ndarray]]
        The outer dictionary's keys are same as those in contours, the inner
        dictionary's keys are perturbation values.
    """
    result_dicts = {}
    for contour_key in contours:
        result_dicts[contour_key] = calculate_perturbed_metric_series(
            metric=metric,
            contour_to_perturb=contours[contour_key],
            reference_contour=contours[contour_key],
            perturbations=perturbations,
            interleave=False
        )
    return result_dicts


def calculate_metric_series_for_comparisons(
        metric: MetricFunction,
        contours: dict[str, np.ndarray],
        comparisons: list[Comparison],
        perturbations: list[float] | tuple[float] = (1.0,),
        interleave: bool = True
) -> dict[Comparison, dict[str, np.ndarray]]:
    """
    Calculate the metric between the specified comparisons.

    The comparisons define a contour to use as is or as a baseline and a
    contour to run perturbations on. They may be the same contour, in which
    case the comparison is between the baseline and its perturbed versions.

    Parameters
    ----------
    metric : MetricFunction
        The metric function to apply.
    contours : dict[str, np.ndarray]
        The contours to run the metric on.
    comparisons : list[Comparison]
        List of which contours to compare with which.
    perturbations : Optional[list[float]], optional
        Tuple of perturbation sizes to apply, By default, (1.0,)
    interleave : bool
        Should the reference and result contours be interleaved.

    Returns
    -------
    dict[Comparison, dict[str, np.ndarray]]
        The outer dictionary is indexed with the Comparisons made and the inner
        one with the original keys of the contours dictionary.
    """
    result_dicts = {}
    for comparison in comparisons:
        if comparison.perturbed == ComparisonMember.FIRST:
            result_dicts[comparison] = calculate_perturbed_metric_series(
                metric=metric,
                contour_to_perturb=contours[comparison.first],
                reference_contour=contours[comparison.second],
                perturbations=perturbations,
                interleave=interleave,
                return_even=False,
            )
        else:
            result_dicts[comparison] = calculate_perturbed_metric_series(
                metric=metric,
                contour_to_perturb=contours[comparison.second],
                reference_contour=contours[comparison.first],
                perturbations=perturbations,
                interleave=interleave,
                return_even=True,
            )
    return result_dicts

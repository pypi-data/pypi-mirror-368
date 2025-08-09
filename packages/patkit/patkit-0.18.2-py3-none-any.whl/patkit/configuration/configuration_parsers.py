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
Configuration parsers import human written configuration files.

This module uses strictyaml to make the files safer and to provide
round tripping with mostly preserved comments.
"""

import logging
import sys
from contextlib import closing
from pathlib import Path

from strictyaml import (
    Bool, FixedSeq, Float, Int, Map,
    MapPattern, Optional, ScalarValidator, Seq, Str,
    UniqueSeq, YAML, YAMLError, load
)

from patkit.constants import (
    AxesType,
    DEFAULT_ENCODING,
    IntervalBoundary,
    IntervalCategory,
    PATKIT_CONFIG_DIR,
)

from .configuration_models import (
    TimeseriesNormalisation)

config_dict = {}
data_run_params = {}
gui_params = {}
plot_params = {}
publish_params = {}

# This is where we store the metadata needed to write out the configuration and
# possibly not mess up the comments in it.
_raw_config_dict = {}
_raw_data_run_params_dict = {}
_raw_gui_params_dict = {}
_raw_plot_params_dict = {}
_raw_publish_params_dict = {}

_logger = logging.getLogger('patkit.configuration_parsers')


class ConfigPathValidator(ScalarValidator):
    """
    Validate yaml representing a Path.

    Please note that empty fields are interpreted as not available and
    represented by None. If you want to specify current working directory, use
    '.'
    """
    def __init__(self, path: Path | None = None):
        self.path = path
        super().__init__()

    def validate_scalar(self, chunk):
        if chunk.contents:
            path = Path(chunk.contents).expanduser()
            if path.parent == Path('.'):
                if self.path is not None:
                    path = self.path/path
                else:
                    path = PATKIT_CONFIG_DIR/path
            return path.expanduser()
        return None


class PathValidator(ScalarValidator):
    """
    Validate yaml representing a Path.

    Please note that empty fields are interpreted as not available and
    represented by None. If you want to specify current working directory, use
    '.'
    """

    def validate_scalar(self, chunk):
        if chunk.contents:
            return Path(chunk.contents)
        return None


class NormalisationValidator(ScalarValidator):
    """
    Validate yaml representing a Path.

    Please note that empty fields are interpreted as not available and
    represented by None. If you want to specify current working directory, use
    '.'
    """

    def validate_scalar(self, chunk):
        if chunk.contents:
            return TimeseriesNormalisation.build(chunk.contents)
        return None


class IntervalCategoryValidator(ScalarValidator):
    """
    Validate yaml representing a Path.

    Please note that empty fields are interpreted as not available and
    represented by None. If you want to specify current working directory, use
    '.'
    """

    def validate_scalar(self, chunk):
        if chunk.contents:
            return IntervalCategory(chunk.contents)
        return None


class IntervalBoundaryValidator(ScalarValidator):
    """
    Validate yaml representing a Path.

    Please note that empty fields are interpreted as not available and
    represented by None. If you want to specify current working directory, use
    '.'
    """

    def validate_scalar(self, chunk):
        if chunk.contents:
            return IntervalBoundary(chunk.contents)
        return None


_search_pattern_schema = Map({
    "pattern": Str(),
    Optional("is_regexp", default=False): Bool()
})

_time_limit_schema = Map({
    "tier": Str(),
    "interval": IntervalCategoryValidator(),
    Optional("label"): Str(),
    "boundary": IntervalBoundaryValidator(),
    Optional("offset"): Float(),
})

# def load_main_config(filepath: Path | str | None = None) -> YAML:
#     """
#     Read the config file from filepath.
#
#     If filepath is None, read from the default file
#     'configuration/configuration.yaml'. In both cases if the file does not
#     exist, report this and exit.
#     """
#     print(filepath)
#     if isinstance(filepath, str):
#         filepath = Path(filepath)
#     elif not isinstance(filepath, Path):
#         filepath = Path('configuration/configuration.yaml')
#
#     _logger.info("Loading main configuration from %s", str(filepath))
#
#     config_path_validator = ConfigPathValidator(filepath.parent)
#     if filepath.is_file():
#         with closing(
#                 open(filepath, 'r', encoding=DEFAULT_ENCODING)) as yaml_file:
#             schema = Map({
#                 Optional("gui_config"): config_path_validator,
#                 Optional("data_config"): config_path_validator,
#                 Optional("simulation_config"): config_path_validator,
#                 Optional("publish_config"): config_path_validator,
#             })
#             try:
#                 _raw_config_dict = load(yaml_file.read(), schema)
#             except YAMLError as error:
#                 _logger.fatal("Fatal error in reading %s.",
#                               str(filepath))
#                 _logger.fatal(str(error))
#                 raise
#     else:
#         message = ("Didn't find main config file at %s.", str(filepath))
#         _logger.fatal(message)
#         print(message)
#         sys.exit()
#
#     config_dict.update(_raw_config_dict.data)
#     return _raw_config_dict


def load_data_params(filepath: Path | str | None = None) -> YAML:
    """
    Read the config file from filepath.

    If filepath is None, read from the default file
    'configuration/configuration.yaml'. In both cases if the file does not
    exist, report this and exit.
    """
    if filepath is None:
        print("Fatal error in loading data run parameters: filepath is None")
        sys.exit()
    elif isinstance(filepath, str):
        filepath = Path(filepath)

    _logger.info("Loading run configuration from %s", str(filepath))

    if filepath.is_file():
        with closing(
                open(filepath, 'r', encoding=DEFAULT_ENCODING)) as yaml_file:
            schema = Map({
                "epsilon": Float(),
                "mains_frequency": Float(),
                "recorded_data_path": PathValidator(),
                Optional("output_directory"): PathValidator(),
                "flags": Map({
                    "detect_beep": Bool(),
                    "test": Bool()
                }),
                Optional("aggregate_image_arguments"): Map({
                    "metrics": Seq(Str()),
                    Optional(
                        "run_on_interpolated_data", default=False): Bool(),
                    Optional("preload", default=True): Bool(),
                    Optional("release_data_memory", default=True): Bool(),
                }),
                Optional("distance_matrix_arguments"): Map({
                    "metrics": Seq(Str()),
                    Optional("exclusion_list"): PathValidator(),
                    Optional("preload", default=True): Bool(),
                    Optional("release_data_memory", default=False): Bool(),
                    Optional('slice_max_step'): Int(),
                    Optional('slice_step_to'): Int(),
                    Optional('sort'): Bool(),
                    Optional('sort_criteria'): UniqueSeq(Str()),
                }),
                Optional("pd_arguments"): Map({
                    "norms": Seq(Str()),
                    "timesteps": Seq(Int()),
                    Optional("mask_images", default=False): Bool(),
                    Optional("pd_on_interpolated_data", default=False): Bool(),
                    Optional("preload", default=True): Bool(),
                    Optional("release_data_memory", default=True): Bool(),
                }),
                Optional("spline_metric_arguments"): Map({
                    'metrics': Seq(Str()),
                    'timesteps': Seq(Int()),
                    Optional('exclude_points'): FixedSeq([Int(), Int()]),
                    Optional('preload', default=True): Bool(),
                    Optional('release_data_memory', default=False): Bool(),
                }),
                Optional("peaks"): Map({
                    "modality_pattern": _search_pattern_schema,
                    Optional("time_min"): _time_limit_schema,
                    Optional("time_max"): _time_limit_schema,
                    Optional("normalisation"): NormalisationValidator(),
                    Optional("number_of_ignored_frames"): Int(),
                    Optional("distance_in_seconds"): Float(),
                    Optional("find_peaks_args"): Map({
                        Optional('height'): Float(),
                        Optional('threshold'): Float(),
                        Optional("distance"): Int(),
                        Optional("prominence"): Float(),
                        Optional("width"): Int(),
                        Optional('wlen'): Int(),
                        Optional('rel_height'): Float(),
                        Optional('plateau_size'): Float(),
                    }),
                }),
                Optional("downsample"): Map({
                    "modality_pattern": _search_pattern_schema,
                    "match_timestep": Bool(),
                    "downsampling_ratios": Seq(Int()),
                }),
                Optional("cast"): Map({
                    "pronunciation_dictionary": PathValidator(),
                    "speaker_id": Str(),
                    "cast_flags": Map({
                        "only_words": Bool(),
                        "file": Bool(),
                        "utterance": Bool()
                    })
                })
            })
            try:
                _raw_data_run_params_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                _logger.fatal("Fatal error in reading %s.",
                              str(filepath))
                _logger.fatal(str(error))
                raise
    else:
        message = (
            "Didn't find run parameter file at %s.", str(filepath))
        _logger.fatal(message)
        print(message)
        sys.exit()

    data_run_params.update(_raw_data_run_params_dict.data)
    if 'peaks' in data_run_params:
        if 'normalisation' not in data_run_params['peaks']:
            data_run_params['peaks']['normalisation'] = (
                TimeseriesNormalisation.build('none'))
    return _raw_data_run_params_dict


def load_simulation_params(filepath: Path | str) -> YAML:
    """
    Load simulation parameters from a `yaml` file.

    Parameters
    ----------
    filepath : Path | str
        Path to the simulation parameters file or equivalent string.

    Returns
    -------
    YAML
        The parsed simulation parameters as a YAML object.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    _logger.info("Loading simulation configuration from %s.",
                 str(filepath))

    sound_pair_params = Map({
        "sounds": Seq(Str()),
        "combinations": Str(),
        Optional("perturbed"): Seq(Str()),
        Optional("sort"): Map({
            "matching_first": Bool(),
            "sort_by": Str(),
        })
    })

    ray_plot_params = Map(
        {
            Optional("figure_size"): FixedSeq([Float(), Float()]),
            "scale": Float(),
            "color_threshold": FixedSeq([Float(), Float()]),
        }
    )

    schema = Map(
        {
            "output_directory": PathValidator(),
            Optional("overwrite_plots"): Bool(),
            Optional("logging_notice_base"): Str(),
            Optional("make_demonstration_contour_plot"): Bool(),
            "sounds": Seq(Str()),
            "perturbations": Seq(Float()),
            "contour_distance": Map(
                {
                    "metrics": Seq(Str()),
                    "timestep": Int(),
                    "sound_pair_params": sound_pair_params,
                }
            ),
            "contour_shape": Map(
                {
                    "metrics": Seq(Str()),
                }
            ),
            Optional("demonstration_contour_plot"): Map(
                {
                    "filename": Str(),
                    "sounds": FixedSeq([Str(), Str()]),
                    Optional("figure_size"): FixedSeq([Float(), Float()]),
                }
            ),
            Optional("mci_perturbation_series_plot"): Map(
                {
                    Optional("filename"): Str(),
                    Optional("figure_size"): FixedSeq([Float(), Float()]),
                }
            ),
            Optional("distance_metric_ray_plot"): ray_plot_params,
            Optional("shape_metric_ray_plot"): ray_plot_params,
        }
    )

    if filepath.is_file():
        with closing(
                open(filepath, 'r', encoding=DEFAULT_ENCODING)) as yaml_file:
            try:
                simulation_params_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                _logger.fatal("Fatal error in reading %s.",
                              str(filepath))
                _logger.fatal(str(error))
                raise
    else:
        message = (
            "Didn't find simulation parameter file at %s.",
            str(filepath))
        _logger.fatal(message)
        print(message)
        sys.exit()

    return simulation_params_dict


def load_gui_params(filepath: Path | str | None = None) -> YAML:
    """
    Read the config file from filepath.

    If filepath is None, read from the default file
    'configuration/configuration.yaml'. In both cases if the file does not
    exist, report this and exit.
    """
    if filepath is None:
        print("Fatal error in loading GUI parameters: filepath is None")
        sys.exit()
    elif isinstance(filepath, str):
        filepath = Path(filepath)

    _logger.info("Loading GUI configuration from %s", str(filepath))

    axes_params_dict = {
        Optional(
            "colors_in_sequence", default=True): Bool(),
        Optional("legend"): Bool(),
        Optional("mark_peaks"): Bool(),
        Optional("sharex"): Bool(),
        Optional("ylim"): FixedSeq([Float(), Float()]),
        Optional("auto_ylim"): Bool(),
        Optional("y_offset"): Float(),
        Optional("normalisation"): NormalisationValidator(),
    }

    axes_definition_dict = axes_params_dict | {
        Optional("modalities"): Seq(Str()),
        Optional("modality_names"): Seq(Str()),
    }

    if filepath.is_file():
        with closing(
                open(filepath, 'r', encoding=DEFAULT_ENCODING)) as yaml_file:
            schema = Map({
                "data_and_tier_height_ratios": Map({
                    AxesType.DATA.value: Int(),
                    AxesType.TIER.value: Int()
                }),
                "general_axes_params": Map({
                    AxesType.DATA.value: Map(axes_params_dict),
                    AxesType.TIER.value: Map(axes_params_dict),
                }),
                "data_axes": MapPattern(
                    Str(), Map(axes_definition_dict)
                ),
                "pervasive_tiers": Seq(Str()),
                Optional("xlim"): FixedSeq([Float(), Float()]),
                Optional('auto_xlim', default=False): Bool(),
                "default_font_size": Int(),
                Optional("color_scheme", default="follow_system"): Str(),
            })
            try:
                _raw_gui_params_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                _logger.fatal("Fatal error in reading %s.",
                              str(filepath))
                _logger.fatal(str(error))
                raise
    else:
        message = (
            "Didn't find gui parameter file at %s.", str(filepath))
        _logger.fatal(message)
        print(message)
        sys.exit()

    gui_params.update(_raw_gui_params_dict.data)

    return _raw_gui_params_dict


def load_publish_params(filepath: Path | str | None = None) -> YAML:
    """
    Read the config file from filepath.

    If filepath is None, read from the default file
    'configuration/configuration.yaml'. In both cases if the file does not
    exist, report this and exit.
    """
    if filepath is None:
        print("Fatal error in loading publish parameters: filepath is None")
        sys.exit()
    elif isinstance(filepath, str):
        filepath = Path(filepath)

    _logger.info("Loading publish configuration from %s", str(filepath))

    if filepath.is_file():
        with closing(
                open(filepath, 'r', encoding=DEFAULT_ENCODING)) as yaml_file:
            schema = Map({
                "publish_directory": PathValidator(),
                Optional("timeseries_plot"): Map({
                    "output_file": Str(),
                    Optional("figure_size", default=[8.3, 11.7]): FixedSeq(
                        [Float(), Float()]),
                    Optional("legend"): Map({
                        Optional("handlelength"): Float(),
                        Optional("handletextpad"): Float(),
                    }),
                    "use_go_signal": Bool(),
                    "normalise": NormalisationValidator(),
                    "plotted_tier": Str(),
                    "subplot_grid": FixedSeq([Int(), Int()]),
                    "subplots": MapPattern(Str(), Str()),
                    "xlim": FixedSeq([Float(), Float()]),
                    Optional("xticks"): Seq(Str()),
                    Optional("yticks"): Seq(Str()),
                }),
                Optional("annotation_stats_plot"): Map({
                    "output_file": Str(),
                    Optional("figure_size", default=[8.3, 11.7]): FixedSeq(
                        [Float(), Float()]),
                    Optional("legend"): Map({
                        Optional("handlelength"): Float(),
                        Optional("handletextpad"): Float(),
                    }),
                    "modality_pattern": _search_pattern_schema,
                    "plotted_annotation": Str(),
                    "panel_by": Str(),
                    "aggregate": Bool(),
                    "aggregation_methods": Seq(Str()),
                }),
            })
            try:
                _raw_publish_params_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                _logger.fatal("Fatal error in reading %s.",
                              str(filepath))
                _logger.fatal(str(error))
                raise
    else:
        message = (
            "Didn't find the publish parameter file at %s.", str(filepath))
        _logger.fatal(message)
        print(message)
        sys.exit()

    publish_params.update(_raw_publish_params_dict.data)

    return _raw_publish_params_dict

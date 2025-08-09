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
"""PATKIT's main datastructures."""

from __future__ import annotations

import abc
import logging
from collections import OrderedDict, UserDict, UserList
from copy import deepcopy
from pathlib import Path
from textwrap import indent

import numpy as np
import textgrids

from patkit.configuration import SessionConfig
from patkit.constants import AnnotationType, SourceSuffix
from patkit.errors import (
    DimensionMismatchError, MissingDataError, OverwriteError
)
from patkit.utility_functions import stem_path
from patkit.patgrid import PatGrid
from .base_classes import AbstractDataContainer, AbstractData, Statistic
from .metadata_classes import (
    FileInformation, ModalityData, ModalityMetaData, PointAnnotations,
    RecordingMetaData
)

_logger = logging.getLogger('patkit.data_structures')



class Answer(UserList):
    """
    Answer is an answer to an Exercise and consists of PatGrids.

    The PatGrids correspond to the Recordings that the Exercise is based on.
    """
    def __init__(
        self,
        container: Exercise,
        scenario: Session,
        scramble: bool,
        cursor: int = 0,
    ):
        super().__init__()
        self.container = container
        self.scenario = scenario
        self.cursor = cursor

        for recording in self.scenario:
            patgrid = deepcopy(recording.patgrid)
            self.append(patgrid)

        if scramble:
            for patgrid in self:
                for tier in patgrid:
                    patgrid[tier].scramble()
            self.edited = [False for i in range(len(self))]
        else:
            self.edited = [True for i in range(len(self))]

    def __repr__(self) -> str:
        representation = ""
        for patgrid in self:
            patgrid_string = f"{patgrid}"
            representation += indent(text=patgrid_string,prefix="\t")
        return representation

    def current(self) -> PatGrid:
        """
        The PatGrid at the current index.

        Returns
        -------
        PatGrid
            The PatGrid.
        """
        return self[self.cursor]

    def go_to_recording(self, index: int) -> int:
        """
        Go to Recording at index.

        Returns
        -------
        int
            index of current recording
        """
        if len(self) > index and index >= 0:
            self.cursor = index
        return self.cursor

    def next(self) -> int:
        """
        Go to next Recording.

        Returns
        -------
        int
            index of next recording
        """
        if len(self) > self.cursor + 1:
            self.cursor += 1
        return self.cursor

    def previous(self) -> int:
        """
        Go to previous Recording.

        Returns
        -------
        int
            index of previous recording
        """
        if self.cursor > 0:
            self.cursor -= 1
        return self.cursor


class Exercise(UserDict):
    """
    Exercise is list of Answers relating to a Scenario (Session).

    If no example Answers are provided, the current PatGrids in the Session are
    copied and used as the example.
    """

    def __init__(
        self,
        scenario: Session,
        answers: list[Answer] | None = None,
        example: dict[str, Answer] | None = None,
        index: int = 0,
    ):
        super().__init__()
        if example is None:
            _logger.debug("Creating an example answer")
            self.example = Answer(
                container=self,
                scenario=scenario,
                scramble = False,
            )
        else:
            self.example = example
        self.scenario = scenario

        if answers is not None:
            self.update(answers)

        self.cursor = index

    def __repr__(self) -> str:
        representation = "Exercise:\n"
        scenario_repr = f"{self.scenario}"
        scenario_repr = indent(text=scenario_repr,prefix="\t\t")
        representation += f"\tScenario:\n{scenario_repr}\n"
        example_repr = f"{self.example}"
        example_repr = indent(text=example_repr,prefix="\t")
        representation += f"\tExample:\n{example_repr}\n"
        representation += "\tAnswers:\n"
        answers_string = ""
        for name in list(self.keys()):
            answers_string += f"{name}:\n{self[name]}"
        representation += indent(text=answers_string,prefix="\t\t")
        return representation

    @property
    def current_answer(self) -> Answer:
        return self[list(self.keys())[self.cursor]]

    def new_blank_answer(self, cursor: int = 0) -> None:
        """
        Create a new blank Answer and append it to this Exercise.

        Parameters
        ----------
        cursor : int
            Cursor position for the new Answer.
        """
        _logger.debug("Creating a blank answer.")
        blank = Answer(
                container=self,
                scenario=self.scenario,
                scramble = True,
                cursor=cursor,
            )
        name = f"Answer {len(self)+1}"
        self[name] = blank


class Manifest(UserList):
    """
    Manifest is a list of Scenario paths as strings.
    """
    @staticmethod
    def read_manifest(path: Path) -> list[str] | None:
        """
        Static method for reading a Manifest files contents.

        Parameters
        ----------
        path : Path
            Path of the file.

        Returns
        -------
        list[str] | None
            Either the contents of the file or None if the file was empty.
        """
        if not path.exists():
            return None
        with open(path, 'r', encoding='UTF-8') as file:
            lines = [line.rstrip() for line in file]
            return lines
        return None

    def __init__(self, path: Path | None = None):
        super().__init__()
        path = path.resolve()
        self.path = path
        if path is not None:
            scenario_paths = Manifest.read_manifest(path)
            if scenario_paths is not None:
                self.extend(scenario_paths)

    @property
    def scenarios(self) -> list[str]:
        """
        The contents of this Manifest as a list.

        Returns
        -------
        list[str]
            The contents.
        """
        return list(self)

    def save(self):
        """
        Write this manifest into its file. 
        """
        if self.path is not None:
            with open(self.path, 'w', encoding='UTF-8') as file:
                for scenario_path in self:
                    file.write(f"{scenario_path}\n")




class Session(AbstractDataContainer, UserList):
    """
    The metadata and Recordings of a recording session.

    This class behaves exactly like a list of Recordings with some extra
    fields. While some legacy code may be left behind, the preferred idiom for
    iterating over the recordings is `for recording in recording_session:`.

    Sessions can also hold aggregate data in the form of Statistics.
    """

    def __init__(
            self,
            name: str,
            config: SessionConfig,
            file_info: FileInformation,
            recordings: list[Recording] | None = None,
            statistics: dict[str, Statistic] | None = None
    ) -> None:
        super().__init__(
            container=None, name=name, metadata=config,
            file_info=file_info, statistics=statistics)

        if not recordings is None:
            for recording in recordings:
                if not recording.container:
                    recording.container = self
            self.extend(recordings)

        self.config = config

    def __repr__(self) -> str:
        representation = "Session:\n"
        for recording in self:
            representation += f"\tRecording: {recording.basename},\n"
        return representation

    @property
    def recordings(self) -> list[Recording]:
        """
        Property to access the list of Recordings directly.

        Returns
        -------
        list[Recording]
            The list of this Session's Recordings.
        """
        return self.data


class Recording(AbstractDataContainer, UserDict):
    """
    A Recording is a dictionary of 0-n synchronised Modalities.

    Adding modalities can be done by `recording[name] = modality`, but
    `recording.add_modality` is preferred as a safer way which checks for
    overwriting. The reason Recording is a dictionary is to make it possible to
    iterate with the idiom `for modality_name in recording`.

    The recording also contains the non-modality-specific metadata
    (participant, speech content, etc.) as a dictionary, as well as the
    textgrid for the whole recording.

    In general, inheriting should not be necessary, but if it is, inheriting
    classes should call `self._read_textgrid()` after calling
    `super.__init__()` (with correct arguments) and doing any updates to
    `self.meta['textgrid']` that are necessary.
    """
    container: Session

    def __init__(
            self,
            metadata: RecordingMetaData,
            file_info: FileInformation,
            container: Session | None = None,
            excluded: bool = False,
    ) -> None:
        """
        Construct a mainly empty recording without modalities.

        Modalities and annotations get added after constructions with their own
        add_[modality or annotation] functions.

        NOTE: `after_modalities_init` should be called on each new Recording
        after modalities have been loaded. It ensures that there is at least a
        minimal TextGrid in place to facilitate GUI functions.

        Parameters
        ----------
        metadata : RecordingMetaData
            Some of the contents of the meta data are available as properties.
        excluded : bool, optional
            _description_, by default False
        """
        if file_info.recorded_meta_file:
            name = file_info.recorded_meta_file
        else:
            name = file_info.patkit_meta_file
        super().__init__(
            container=container, name=name,
            metadata=metadata, file_info=file_info)

        self.excluded = excluded
        self.textgrid_path = None
        self.textgrid = None
        self.patgrid = None
        self.annotations = {}

    @property
    def modalities(self) -> dict[str, Modality]:
        """
        Dictionary of the modalities of this Recording.

        Returns
        -------
        dict[str, Modality]
            The dictionary of the Modalities.
        """
        return self.data

    @property
    def basename(self) -> str:
        """Filename of this Recording without extensions."""
        return self.file_info.basename

    def _read_textgrid(self) -> textgrids.TextGrid | None:
        """
        Read the textgrid specified in self.meta.

        If file does not exist or reading fails, recovery is attempted 
        by logging an error and creating an empty textgrid for this 
        recording.
        """
        textgrid = None
        if self.textgrid_path.is_file():
            try:
                textgrid = textgrids.TextGrid(self.textgrid_path)
                _logger.info("Read textgrid in %s.",
                             self.textgrid_path)
            except Exception as exception:
                _logger.critical(
                    "Could not read textgrid in %s.", self.textgrid_path)
                _logger.critical(
                    "Failed with: %s.", str(exception))
        else:
            notice = 'Note: ' + str(self.textgrid_path) + " did not exist."
            _logger.warning(notice)
        return textgrid

    def identifier(self) -> str:
        """
        Generate a unique identifier for this Recording from metadata.

        Returns
        -------
        str
            prompt followed by time of recording.
        """
        return (f"{self.metadata.prompt} "
                f"{str(self.metadata.time_of_recording)}")

    def exclude(self) -> None:
        """
        Set `self.excluded` to True with a method.

        This method exists to facilitate list comprehensions being used
        for excluding recordings e.g. 
        [recording.exclude() for recording in recordings if in some_list].
        """
        self.excluded = True

    def write_textgrid(self, filepath: Path = None) -> None:
        """
        Save this recording's textgrid to file.

        Keyword argument:
        filepath -- string specifying the path and name of the 
            file to be written. If filepath is not specified, this 
            method will try to overwrite the textgrid specified in 
            self.meta.

            If filepath is specified, subsequent calls to this 
            function will write into the new path rather than 
            the original one.
        """
        try:
            if filepath:
                self.textgrid_path = filepath
                self.textgrid.write(filepath)
            else:
                self.textgrid.write(self.textgrid_path)
        except Exception as exception:
            _logger.critical(
                "Could not write textgrid to %s.", str(self.textgrid_path))
            _logger.critical(
                "TextGrid save failed with error: %s", str(exception))

    def add_modality(
            self, modality: Modality, replace: bool = False
    ) -> None:
        """
        This method adds a new Modality object to the Recording.

        Replacing a modality has to be specified otherwise if a
        Modality with the same name already exists in this Recording
        and the `replace` argument is not True, an Error is raised.

        Arguments:
        modality -- object of type Modality to be added to 
            this Recording.

        Keyword arguments:
        replace -- a boolean indicating if an existing Modality should
            be replaced.
        """
        name = modality.name

        if name in self.modalities and not replace:
            raise OverwriteError(
                "A modality named " + name +
                " already exists and replace flag was False.")

        if replace:
            self.modalities[name] = modality
            _logger.debug("Replaced modality %s.", name)
        else:
            self.modalities[name] = modality
            _logger.debug("Added new modality %s.", name)

    def after_modalities_init(self) -> None:
        """
        Ensure everything is properly in place after loading modalities.

        Currently, this is only used to create placeholder TextGrids when
        needed.
        """
        textgrid_path  = None
        if self.recorded_meta_path:
            textgrid_path = self.recorded_meta_path.with_suffix(
                SourceSuffix.TEXTGRID
            )
        elif self.recorded_data_path:
            textgrid_path = self.recorded_data_path.with_suffix(
                SourceSuffix.TEXTGRID
            )

        if not textgrid_path or not textgrid_path.exists():
            if self.file_info.patkit_meta_file:
                textgrid_path = self.recorded_path
                name = Path(self.file_info.patkit_meta_file)
                textgrid_path = stem_path(textgrid_path/name)
                textgrid_path = textgrid_path.with_suffix(
                    SourceSuffix.TEXTGRID
                )

        if textgrid_path is not None and textgrid_path.exists():
            self.textgrid_path = textgrid_path
            self.textgrid = self._read_textgrid()

        if self.textgrid is None:
            if 'MonoAudio' in self.modalities:
                _logger.warning(
                    "%s: Creating a placeholder textgrid to make GUI function "
                    "correctly.", self.basename)
                textgrid = textgrids.TextGrid()
                interval = textgrids.Interval(
                    text=self.metadata.prompt,
                    xmin=self['MonoAudio'].min_time,
                    xmax=self['MonoAudio'].max_time,
                )
                tier = textgrids.Tier(
                    xmin=self['MonoAudio'].min_time,
                    xmax=self['MonoAudio'].max_time,
                )
                tier.append(interval)
                textgrid['Utterance'] = tier
                self.textgrid = textgrid
            else:
                _logger.warning("No audio found for %s.",
                                self.basename)
                _logger.warning("Can't create a textgrid so GUI may not "
                                "function correctly.")

        if self.textgrid:
            self.patgrid = PatGrid(self.textgrid)
        else:
            self.patgrid = None


    def __str__(self) -> str:
        """
        Bare minimum string representation of the Recording.

        Returns
        -------
        string
            'Recording [basename]'
        """
        return f"Recording {self.name}"

    def __repr__(self) -> str:
        """Overrides the default implementation"""
        modalities = "{\n"
        for modality in self.modalities:
            modalities += ("\t" + modality
                           + f": {self.modalities[modality].name},\n")
        modalities += "}"
        return (
            f"Recording {self.basename}\n"
            f"{modalities}")

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Recording):
            return self.name == other.name
        return NotImplemented


class Modality(AbstractData, OrderedDict):
    """
    Abstract superclass for all data Modality classes.

    Any annotations associated with a Modality instance are accessible directly
    by `modality[annotation_type]`, because a Modality is also a OrderedDict of
    its Annotations.
    """
    container: Recording

    @classmethod
    @abc.abstractmethod
    def generate_name(cls, params: ModalityMetaData) -> str:
        """Abstract version of generating a Modality name."""

    def __init__(
            self,
            container: Recording,
            file_info: FileInformation,
            parsed_data: ModalityData | None = None,
            metadata: ModalityMetaData | None = None,
            time_offset: float | None = None,
            point_annotations: dict[AnnotationType, PointAnnotations] | None =
            None
    ) -> None:
        """
        Modality constructor.

        Positional arguments:
        recording -- the containing Recording.

        Keyword arguments:
        data_path -- path of the data file
        load_path -- path of data when saved by patkit - both data and metadata
        parent -- the Modality this one was derived from. None means this 
            is a recorded data Modality.
        parsed_data -- ModalityData object containing waveform, sampling rate,
            and either timevector and/or time_offset. 
        parsed_data -- a ModalityData object containing parsed data 
            that's been either read from file, loaded from file 
            (previously saved by patkit), or calculated from another modality.
            Providing a timevector 
            overrides any time_offset value given, but in absence of a 
            timevector the time_offset will be applied on reading the data 
            from file. 
        time_offset -- offset of this modality in relation to the Recordings
            baseline - usually the audio track. This will be ignored if 
            parsed_data exists and effectively overridden by 
            parsed_data.timevector.
        """
        super().__init__(
            container=container,
            metadata=metadata,
            file_info=file_info)

        if point_annotations:
            self.update(point_annotations)

        if parsed_data:
            self._modality_data = parsed_data
        else:
            self._modality_data = None

        if (self._modality_data is None or
                self._modality_data.timevector is None):
            self._time_offset = time_offset
        else:
            self._time_offset = self._modality_data.timevector[0]

        # This is a property which when set to True will also set
        # parent.excluded to True.
        self.excluded = False
        self._time_precision = None

    @property
    def annotations(self) -> dict[AnnotationType, PointAnnotations]:
        """
        Property which is the annotations dictionary of this Modality.

        This is currently the Modality itself.

        Returns
        -------
        dict[AnnotationType, PointAnnotations]
            The dictionary.
        """
        return self

    @property
    def recording(self) -> Recording | None:
        """
        This modality's container available with this alias for ease of use.

        Returns
        -------
        Recording
            The Recording which contains this Modality.
        """
        return self.container

    def _get_data(self) -> ModalityData:
        # TODO: Provide a way to force the data to be derived or loaded. this
        # would be used when parent modality has updated in some way. If this
        # is actually necessary to implement, a call back would be probably the
        # way to go.
        if self._file_info.recorded_data_file:
            return self._read_data()

        if self._file_info.patkit_data_file:
            return self._load_data()

        if self._metadata.parent_name:
            return self._derive_data()

        raise MissingDataError(
            "Asked to get data but have no path and no parent Modality.\n"
            + "Don't know how to solve this.")

    def _derive_data(self) -> ModalityData:
        """
        Derive data from another modality -- overridden by inheriting classes.

        This method should be implemented by subclasses by calling 
        a suitable deriving function to provide on-the-fly loading of data.

        This method is intended to rely on `self.parent` to provide the data
        to be processed.
        """
        raise NotImplementedError(
            "This method should be overridden by inheriting classes.")

    def _load_data(self) -> ModalityData:
        """
        Load data from a saved file -- to be overridden by inheriting classes.

        This method should be implemented by subclasses by calling 
        a suitable loading function to provide on-the-fly loading of data.

        This method is intended to rely on self.load_path to know what to read.
        """
        raise NotImplementedError(
            "This method should be overridden by inheriting classes.")

    def _read_data(self) -> ModalityData:
        """
        Load data from file -- to be overridden by inheriting classes.

        This method should be implemented by subclasses by calling 
        a suitable reading function to provide on-the-fly loading of data.

        This method is intended to rely on self.data_path to know what to read.
        """
        raise NotImplementedError(
            "This method should be overridden by inheriting classes.")

    def _set_data(self, data: ModalityData):
        """Set data from _get_data, _load_data, and _derive_data."""
        self._modality_data = data

    def add_point_annotations(
            self, point_annotations: PointAnnotations
    ) -> None:
        """
        Add the PointAnnotations object to this Modality.

        If there were previous annotations in this Modality with the same
        AnnotationType, they will be overwritten.

        To add single annotation points, use the add_annotation method in
        PointAnnotations.

        Parameters
        ----------
        point_annotations : PointAnnotations
            The annotations to be added.
        """
        if point_annotations.annotation_type in self:
            _logger.debug(
                "In Modality add_annotations. "
                "Overwriting %s.", str(point_annotations.annotation_type))
        else:
            _logger.debug(
                "In Modality add_annotations. "
                "Adding %s.", str(point_annotations.annotation_type))

        self.annotations[point_annotations.annotation_type] = point_annotations

    @property
    def modality_data(self) -> ModalityData:
        """
        The data of this Modality as a NumPy array. 

        The data refers to the actual data this modality represents
        and for DerivedModality it is the result of running the 
        modality's algorithm on the original data.

        The dimensions of the array are in the 
        order of [time, others]

        If this modality is not preloaded, accessing this property will
        cause data to be loaded on the fly _and_ saved in memory. To 
        release the memory, assign None to this Modality's data.
        """
        if self._modality_data is None:
            _logger.debug(
                "In Modality modality_data getter. "
                "self._modality_data was None.")
            self._set_data(self._get_data())
        return self._modality_data

    @property
    def data(self) -> np.ndarray:
        """
        The data of this Modality as a NumPy array. 

        The data refers to the actual data this modality represents
        and for DerivedModality it is the result of running the 
        modality's algorithm on the original data.

        The dimensions of the array are in the 
        order of [time, others]

        If this modality is not preloaded, accessing this property will
        cause data to be loaded on the fly _and_ saved in memory. To 
        release the memory, assign None to this Modality's data.
        """
        if self._modality_data is None or self._modality_data.data is None:
            _logger.debug(
                "In Modality data getter. "
                "self._modality_data or self._modality_data.data was None.")
            self._set_data(self._get_data())
        return self._modality_data.data

    @data.setter
    def data(self, data: np.ndarray) -> None:
        """
        Data setter method.

        Arguments: 
        data -- either None or a numpy.ndarray with same dtype, size, 
            and shape as self.data.

        Assigning anything but None or a numpy ndarray with matching dtype,
        size, and shape will raise a OverWriteError.

        If shape of the data were to change then also shape of the timevector
        should potentially change. Unlikely that we'd try to deal that in any
        other way but to create a new Modality or even Recording.
        """
        self._data_setter(data)

    def _data_setter(self, data: np.ndarray) -> None:
        """Set the data property from this class and subclasses."""
        if self.data is not None and data is not None:
            if (data.dtype == self._modality_data.data.dtype and
                    data.size == self._modality_data.data.size and
                    data.shape == self._modality_data.data.shape):
                self._modality_data.data = data
            else:
                raise DimensionMismatchError(
                    "Trying to write over raw ultrasound data with a numpy " +
                    "array that has non-matching dtype, size, or shape.\n" +
                    " data.shape = " + str(data.shape) + "\n" +
                    " self.data.shape = " +
                    str(self._modality_data.data.shape) + ".")
        else:
            self._modality_data.data = data

    @property
    def sampling_rate(self) -> float:
        """Sampling rate of this Modality in Hz."""
        if not self._modality_data or not self._modality_data.sampling_rate:
            self._set_data(self._get_data())
        return self._modality_data.sampling_rate

    @property
    def parent_name(self) -> str:
        """Name of the Modality this Modality was derived from, if any."""
        return self._metadata.parent_name

    @property
    def time_offset(self):
        """
        The time offset of this modality.

        Assigning a value to this property is implemented so that
        `self.timevector[0]` stays equal to `self._time_offset`.

        If shape of the timevector were to change then also shape of the data
        should change. Unlikely that we'd try to deal that in any other way but
        to create a new Modality or even Recording.
        """
        if not self._time_offset:
            self._set_data(self._get_data())
        return self._time_offset

    @property
    def time_precision(self) -> float:
        """
        Timevector precision: the maximum of absolute deviations.

        Essentially this means that we are guesstimating the timevector to be
        no more precise than the largest deviation from the average timestep.
        """
        if not self._time_precision:
            differences = np.diff(self.timevector)
            average = np.average(differences)
            deviations = np.abs(differences - average)
            self._time_precision = np.max(deviations)
        return self._time_precision

    @time_offset.setter
    def time_offset(self, time_offset):
        self._time_offset = time_offset
        if self._modality_data.timevector:
            self._modality_data.timevector = (
                    self.timevector + (time_offset - self.timevector[0]))

    @property
    def timevector(self):
        """
        The timevector corresponding to `self.data` as a NumPy array.

        If the data has not been previously loaded, accessing this 
        property will cause data to be loaded on the fly _and_ saved 
        in memory. To release the memory, assign None to this 
        Modality's data. If the data has been previously 
        loaded and after that released, the timevector still persists and  
        accessing it does not trigger a new loading operation.

        Assigning a value to this property is implemented so 
        that `self.timevector[0]` stays equal to `self._timeOffset`.
        """
        if (self._modality_data is None or
                self._modality_data.timevector is None):
            self._set_data(self._get_data())
        return self._modality_data.timevector

    @timevector.setter
    def timevector(self, timevector):
        if (self._modality_data is None or
                self._modality_data.timevector is None):
            raise DimensionMismatchError(
                "Trying to overwrite the timevector when "
                "it has not yet been initialised."
            )
        elif timevector is None:
            raise NotImplementedError(
                "Trying to set timevector to None.\n" +
                "Freeing timevector memory is currently not implemented."
            )
        else:
            if (timevector.dtype == self._modality_data.timevector.dtype and
                    timevector.size == self._modality_data.timevector.size and
                    timevector.shape == self._modality_data.timevector.shape):
                self._modality_data.timevector = timevector
                self.time_offset = timevector[0]
            else:
                raise DimensionMismatchError(
                    "Trying to write over raw ultrasound data with a numpy " +
                    "array that has non-matching dtype, size, or shape.\n" +
                    " timevector.shape = " + str(timevector.shape) + "\n" +
                    " self.timevector.shape = "
                    + str(self._modality_data.timevector.shape) + ".")

    @property
    def min_time(self) -> float:
        """
        Minimum time stamp.

        Returns
        -------
        float
            The minimum time stamp in seconds.
        """
        return self.timevector[0]

    @property
    def max_time(self) -> float:
        """
        Maximum time stamp.

        Returns
        -------
        float
            The maximum time stamp in seconds.
        """
        return self.timevector[-1]

    @property
    def excluded(self) -> None:
        """
        Boolean property for excluding this Modality from processing.

        Setting this to `True` will result in the whole Recording being
        excluded by setting `self.parent.excluded = True`.
        """
        return self._excluded

    @excluded.setter
    def excluded(self, excluded):
        self._excluded = excluded

        if excluded:
            if self.recording:
                self.recording.excluded = True

    @property
    def is_derived(self) -> bool:
        """
        Is this Modality a result of processing another.

        This cannot be set from the outside.
        """
        if self._metadata and self._metadata.parent_name:
            return True
        return False

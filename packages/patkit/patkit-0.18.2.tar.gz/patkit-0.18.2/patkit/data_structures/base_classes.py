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
"""Base classes of the core datastructures."""

from __future__ import annotations

import abc
import logging
from pathlib import Path

import numpy as np

from patkit.errors import OverwriteError
from patkit.external_class_extensions import PatkitBaseModel

from .metadata_classes import FileInformation, StatisticMetaData

_datastructures_logger = logging.getLogger('patkit.data_structures')


class AbstractDataObject(abc.ABC):
    """
    Abstract base class for patkit data objects.

    Almost no class should directly inherit from this class. Exceptions are
    AbstractDataContainer and AbstractData. The latter is the abstract baseclass for
    Modality and Statistic and the former for all data base classes: Recording,
    Session, DataSet and any others that contain either DataContainers and/or
    AbstractDataContainers.
    """

    def __init__(self,
                 metadata: PatkitBaseModel,
                 container: AbstractDataContainer | None = None,
                 file_info: FileInformation | None = None,
                 ) -> None:
        # The super().__init__() call below is needed to make sure that
        # inheriting classes which also inherit from UserDict and UserList are
        # initialised properly.
        super().__init__()

        self._metadata = metadata
        self.container = container
        self._file_info = file_info

    def __getstate__(self) -> dict:
        """
        Return this AbstractData's pickle compatible state.

        To achieve pickle compatibility, subclasses should take care to delete
        any cyclical references, like is done with `self.container` here.

        NOTE! This also requires container to be reset after unpickling by the
        owners, because the unpickled class can not know who owns it.

        Returns
        -------
        dict
            The state without cyclical references.
        """
        state = self.__dict__.copy()
        del state['container']
        return state

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Name of this instance.

        In most cases name is supposed to be implemented with the following
        idiom:
        ```python
        return NAME_OF_THIS_CLASS.generate_name(self.metadata)
        ```
        For example, for PD:
        ```python
        return PD.generate_name(self.metadata)
        ```

        Returns
        -------
        str
            Name of this instance.
        """

    @property
    def file_info(self) -> FileInformation:
        """
        The paths and filenames of this AbstractDataObject as a FileInformation object.

        NOTE: Regularly you should not need to access this directly. Instead,
        use the `[recorded|patkit]_path`, `[recorded|patkit]_data_file`, and
        `[recorded|patkit]_meta_file` properties.

        Returns
        -------
        FileInformation
            The FileInformation.
        """
        return self._file_info

    @property
    def metadata(self) -> PatkitBaseModel:
        """
        Metadata of this AbstractDataObject.

        This will be of appropriate type for the subclasses and has been hidden
        behind a property to make it possible to change the internal
        representation without breaking the API.

        Returns
        -------
        PatkitBaseModel
            The meta data as a Pydantic model.
        """
        return self._metadata

    @property
    def recorded_data_path(self) -> Path | None:
        """
        Path of the recorded raw data file of this AbstractDataObject.

        May not be overwritten.

        Returns
        -------
        Path
            The path or None if no path was set.
        """
        if self._file_info.recorded_path:
            if self._file_info.recorded_data_file:
                return self.recorded_path / self._file_info.recorded_data_file
        return None

    @property
    def recorded_data_name(self) -> str | None:
        """
        Name the recorded raw data file of this AbstractDataObject.

        May not be overwritten.

        Returns
        -------
        str
            The name or None if no name was set.
        """
        return self._file_info.recorded_data_file

    @property
    def recorded_meta_path(self) -> Path | None:
        """
        Path to the recorded meta data file of this AbstractDataObject.

        This file will exist only for some recorded data. For example, wav
        files do not have a corresponding recorded meta data file. 

        This file may also cover more than one recorded data file - usually a
        whole Session if not just a single recorded data file.

        May not be overwritten.

        Returns
        -------
        Path
            The path or None if no path was set.
        """
        if not self._file_info.recorded_meta_file:
            return None
        if self._file_info.recorded_meta_file:
            return self.recorded_path / self._file_info.recorded_meta_file
        return None

    @property
    def recorded_meta_name(self) -> str | None:
        """
        Name the recorded meta data file of this AbstractDataObject.

        May not be overwritten.

        Returns
        -------
        str
            The name or None if no name was set.
        """
        return self._file_info.recorded_meta_file

    @property
    def recorded_path(self) -> Path | None:
        """
        Path to the recorded raw data files of this AbstractDataObject.

        This path will exist only for recorded data.

        May not be overwritten.

        Returns
        -------
        Path
            The path or None if no path was set.
        """
        if not self._file_info.recorded_path:
            return None
        if not self.container is None:
            return self.container.recorded_path / self._file_info.recorded_path
        return self._file_info.recorded_path

    @property
    def patkit_data_path(self) -> Path | None:
        """
        Path to the patkit (derived) data file of this AbstractDataObject.

        This file will exist only for saved derived data.

        May be overwritten.

        Returns
        -------
        Path
            The path or None if no path was set.
        """
        if not self._file_info.patkit_data_file:
            return None
        return self.patkit_path / self._file_info.patkit_data_file

    @patkit_data_path.setter
    def patkit_data_path(self, patkit_data_file: Path | None) -> None:
        if patkit_data_file is None:
            self._file_info.patkit_data_file = None
        else:
            self._file_info.patkit_data_file = patkit_data_file.name

    @property
    def patkit_data_name(self) -> str | None:
        """
        Name the patkit data file of this AbstractDataObject.

        May be overwritten.

        Returns
        -------
        str
            The name or None if no name was set.
        """
        return self._file_info.patkit_data_file

    @patkit_data_name.setter
    def patkit_data_name(self, patkit_data_file: str | None) -> None:
        self._file_info.patkit_data_file = patkit_data_file

    @property
    def patkit_meta_path(self) -> Path | None:
        """
        Path to the patkit meta data file of this AbstractDataObject.

        After saving this file will exist even for recorded data.

        May be overwritten.

        Returns
        -------
        Path
            The path or None if no path was set.
        """
        if not self._file_info.patkit_meta_file:
            return None
        return self.patkit_path / self._file_info.patkit_meta_file

    @patkit_meta_path.setter
    def patkit_meta_path(self, patkit_meta_file: Path | None) -> None:
        if patkit_meta_file is None:
            self._file_info.patkit_meta_file = None
        else:
            self._file_info.patkit_meta_file = patkit_meta_file.name

    @property
    def patkit_meta_name(self) -> str | None:
        """
        Name the patkit meta data file of this AbstractDataObject.

        May be overwritten.

        Returns
        -------
        str
            The name or None if no name was set.
        """
        return self._file_info.patkit_meta_file

    @patkit_meta_name.setter
    def patkit_meta_name(self, patkit_meta_file: str | None) -> None:
        self._file_info.patkit_meta_file = patkit_meta_file

    @property
    def patkit_path(self) -> Path | None:
        """
        Path to the patkit files of this AbstractDataObject.

        May be overwritten.

        Returns
        -------
        Path
            The path or None if no path was set.
        """
        if not self._file_info.patkit_path:
            return None
        if self.container:
            return self.container.patkit_path / self._file_info.patkit_path
        return self._file_info.patkit_path

    @patkit_path.setter
    def patkit_path(self, patkit_path: str | Path | None) -> None:
        if patkit_path is None or isinstance(patkit_path, Path):
            self._file_info.patkit_path = patkit_path
        else:
            self._file_info.patkit_path = Path(patkit_path)

    @property
    def is_fully_initialised(self) -> bool:
        """
        Check if this AbstractData has been fully initialised.

        This property will be false, if any required fields of the
        AbstractData are None.

        Returns
        -------
        bool
            True if this AbstractData is fully initialised.
        """
        if self.container:
            return True
        return False

    def get_meta(self) -> dict:
        """
        Get meta data as a dict.

        This is a helper method for saving as nested text. Allows for rewriting
        any fields that need a simpler representation. 

        Subclasses should override this method if any of their fields require
        special handling such as derived Enums needing to be converted to plain
        text etc. 

        Returns
        -------
        dict
            The meta data in a dict.
        """
        return self.metadata.model_dump()


class AbstractDataContainer(AbstractDataObject):
    """
    Abstract baseclass for Recording, Session, and DataSet. 

    This class collects behaviors that are shared by the data base classes i.e.
    classes which collect DataContainers and/or AbstractDataContainers.
    """

    def __init__(self,
                 name: str,
                 metadata: PatkitBaseModel,
                 container: AbstractDataContainer | None = None,
                 file_info: FileInformation | None = None,
                 statistics: dict[str, 'Statistic'] | None = None
                 ) -> None:
        super().__init__(
            container=container, metadata=metadata, file_info=file_info)

        self._name = name
        self.statistics = {}
        if statistics:
            self.statistics.update(statistics)

    @property
    def name(self) -> str:
        """
        Name of this instance.

        AbstractDataContainers get their names mainly from the file system. DataSets
        are named after the root directory name, Sessions for the session
        directories and Trials for the trial file names. 

        Returns
        -------
        str
            The name as string.
        """
        return self._name

    def add_statistic(
            self, statistic: 'Statistic', replace: bool = False) -> None:
        """
        Add a Statistic to this Session.

        Parameters
        ----------
        statistic : Statistic
            Statistic to be added.
        replace : bool, optional
            Should we replace any existing Statistic by the same name, by
            default False

        Raises
        ------
        OverwriteError
            In case replace was False and there exists already a Statistic with
            the same name in this Session.
        """
        name = statistic.name

        if name in self.statistics and not replace:
            raise OverwriteError(
                "A Statistic named '" + name +
                "' already exists and replace flag was False.")

        if replace:
            self.statistics[name] = statistic
            _datastructures_logger.debug("Replaced statistic %s.", name)
        else:
            self.statistics[name] = statistic
            _datastructures_logger.debug("Added new statistic %s.", name)


class AbstractData(AbstractDataObject):
    """
    Abstract baseclass for Modality and Statistic. 

    This class collects behaviors shared by the classes that contain data:
    Modalities contain time varying data and Statistics contain time
    independent data.
    """
    @classmethod
    @abc.abstractmethod
    def generate_name(cls, params: PatkitBaseModel) -> str:
        """Abstract version of generating a RecordingMetric name."""

    def __init__(self,
                 metadata: PatkitBaseModel,
                 container: AbstractDataContainer | None = None,
                 file_info: FileInformation | None = None,
                 ) -> None:
        super().__init__(
            container=container, metadata=metadata, file_info=file_info)

    @property
    def name(self) -> str:
        """
        Name of this instance.

        In most cases name is supposed to be overridden with the following
        idiom:
        ```python
        return NAME_OF_THIS_CLASS.generate_name(self.metadata)
        ```
        For example, for PD:
        ```python
        return PD.generate_name(self.metadata)
        ```

        Returns
        -------
        str
            Name of this instance.
        """
        return self.__class__.generate_name(self._metadata)

    @property
    def name_underscored(self) -> str:
        """
        Name of this instance with spaces replaced with underscores.

        Returns
        -------
        str
            Name of this instance with spaces replaced with underscores.
        """
        return self.name.replace(" ", "_")

    @property
    @abc.abstractmethod
    def data(self) -> np.ndarray:
        """
        The data contained in this AbstractData as a numpy ndarray.
        """


class Statistic(AbstractData):
    """
    Abstract baseclass for statistics generated from members of a container. 

    Specifically Statistics are time independent data while Modalities are
    time-dependent data.
    """
    _data: np.ndarray

    @classmethod
    @abc.abstractmethod
    def generate_name(cls, params: StatisticMetaData) -> str:
        """Abstract version of generating a Statistic name."""

    def __init__(
            self,
            metadata: PatkitBaseModel,
            container: AbstractDataContainer | None = None,
            file_info: FileInformation | None = None,
            parsed_data: np.ndarray | None = None,
    ) -> None:
        """
        Build a Statistic.       

        Parameters
        ----------
        metadata : PatkitBaseModel
            Parameters used in calculating this Statistic.
        container : AbstractDataContainer
            The container of this Statistic. Usually this will be the object whose
            contents this Statistic was calculated on. By default, None, to
            facilitate mass generation and setting the container after wards.
        file_info : FileInformation
            The patkit load path and names for this Statistic. Recorded path
            and names should usually be empty. Defaults to None, when the
            Statistic hasn't been saved yet.
        parsed_data : Optional[np.ndarray], optional
            the actual statistic, by default None
        """
        super().__init__(
            container=container, metadata=metadata, file_info=file_info)
        self._data = parsed_data

    @property
    def data(self) -> np.ndarray:
        return self._data

    @data.setter
    def data(self, data: np.ndarray) -> None:
        self._data = data

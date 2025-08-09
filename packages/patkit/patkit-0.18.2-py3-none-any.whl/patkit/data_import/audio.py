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
Adding MonoAudio to a Recording.
"""
import logging
from pathlib import Path
from typing import Optional

from patkit.constants import SourceSuffix
from patkit.data_structures import Recording, FileInformation
from patkit.import_formats import read_wav, read_wav_and_detect_beep
from patkit.modalities import MonoAudio

_generic_io_logger = logging.getLogger('patkit.data_structures')


def add_audio(
        recording: Recording,
        preload: bool = True,
        detect_beep: bool = False,
        path: Optional[Path] = None) -> None:
    """
    Create a MonoAudio Modality and add it to the Recording.

    Parameters
    ----------
    recording : Recording
        _description_
    preload : bool, optional
        _description_, by default True
    detect_beep : bool, optional
        Should (1kHz) beep be detected in the recording, by default False
    path : Optional[Path], optional
        _description_, by default None
    """
    if not path:
        if recording.recorded_meta_path is not None:
            wav_file = recording.recorded_meta_path.with_suffix(
                SourceSuffix.WAV)
        else:
            wav_file = recording.recorded_data_path.with_suffix(
                SourceSuffix.WAV)
    else:
        wav_file = path

    if wav_file.is_file():
        file_info = FileInformation(
            recorded_path=Path("."),
            recorded_data_file=wav_file.name
        )
        if preload and detect_beep:
            data, go_signal, has_speech = read_wav_and_detect_beep(
                wav_file)
            waveform = MonoAudio(
                container=recording,
                file_info=file_info,
                parsed_data=data,
                detect_beep=detect_beep,
                go_signal=go_signal,
                has_speech=has_speech
            )
            recording.add_modality(waveform)
        elif preload:
            data = read_wav(wav_file)
            waveform = MonoAudio(
                container=recording,
                file_info=file_info,
                parsed_data=data,
                detect_beep=detect_beep,
            )
            recording.add_modality(waveform)
        else:
            waveform = MonoAudio(
                container=recording,
                file_info=file_info,
                detect_beep=detect_beep,
            )
            recording.add_modality(waveform)
        _generic_io_logger.debug(
            "Added MonoAudio to Recording representing %s.",
            recording.recorded_data_name)
    else:
        notice = 'Note: ' + str(wav_file) + " does not exist. Excluding."
        _generic_io_logger.warning(notice)
        recording.exclude()

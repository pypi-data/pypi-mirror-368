# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from pydantic import PrivateAttr

from .common import Experiment, RangeIterable

DEFAULT_RECYCLE_DELAY_NS = 100_000
DEFAULT_SHOT_COUNT = 400


class T2(Experiment):
    """
    Parameters for running a Ramsey experiment.

    Parameters
    ----------
    transmon : str
        The reference for the transmon to target.
    delays_ns : list[int] or RangeIterable
        The delay times, in nanoseconds.
    virtual_detuning : float
        The virtual detuning added between SX pulses, in Hz.
    recycle_delay_ns : int, optional
        The delay between consecutive shots, in nanoseconds. Defaults to 100,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 400.
    run_mixer_calibration: bool
        Whether to run mixer calibrations before running a program. Defaults to False.
    """

    _experiment_name: str = PrivateAttr("t2")

    transmon: str
    delays_ns: list[int] | RangeIterable
    virtual_detuning: float
    recycle_delay_ns: int = DEFAULT_RECYCLE_DELAY_NS
    shot_count: int = DEFAULT_SHOT_COUNT
    run_mixer_calibration: bool = False

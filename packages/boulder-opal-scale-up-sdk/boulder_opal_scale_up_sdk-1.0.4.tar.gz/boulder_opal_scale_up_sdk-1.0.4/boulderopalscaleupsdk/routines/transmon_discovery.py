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

from boulderopalscaleupsdk.experiments import ConstantWaveform

from .common import Routine


class TransmonDiscovery(Routine):
    """
    Parameters for running a transmon discovery routine.

    Parameters
    ----------
    transmon : str
        The reference for the transmon to target.
    recycle_delay_ns : int, optional
        The delay between consecutive shots, in nanoseconds. Defaults to 100,000.
    readout_waveform : ConstantWaveform or None, optional
        The readout pulse used in transmon spectroscopy.
        Defaults to a constant waveform with a duration of 10,000 ns
        and an amplitude of 0.01.
    spectroscopy_waveform : ConstantWaveform or None, optional
        The drive pulse used during transmon spectroscopy and transmon anharmonicity.
        Defaults to a 10,000 ns pulse whose amplitude is defined by the logic of the experiment.
    """

    _routine_name: str = PrivateAttr("transmon_discovery")

    transmon: str
    recycle_delay_ns: int = 100_000
    readout_waveform: ConstantWaveform | None = None
    spectroscopy_waveform: ConstantWaveform | None = None

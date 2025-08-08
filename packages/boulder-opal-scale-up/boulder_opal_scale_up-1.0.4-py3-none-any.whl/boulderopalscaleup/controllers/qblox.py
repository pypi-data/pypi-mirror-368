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

import logging
from typing import TYPE_CHECKING, Self

import qblox_instruments as qbxi
from boulderopalscaleupsdk.device.controller import qblox as qbxs
from boulderopalscaleupsdk.protobuf.v1 import agent_pb2
from google.protobuf.struct_pb2 import Struct

from boulderopalscaleup import qblox as qbxc
from boulderopalscaleup.controllers import Controller

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from boulderopalscaleup.client import QctrlScaleUpClient


class QBLOXController(Controller):
    def __init__(self, stack: dict[str, qbxi.Cluster]):
        self._stack = stack

    @classmethod
    def new(cls, *cluster_hosts: tuple[str, str]) -> Self:
        stack = {name: qbxc.get_cluster(name, host) for name, host in cluster_hosts}
        return cls(stack)

    async def run_program(
        self,
        program_request: agent_pb2.RunProgramRequest,
        client: "QctrlScaleUpClient",  # noqa: ARG002
    ) -> agent_pb2.RunProgramResponse:
        program = qbxs.PreparedProgram.loads(program_request.program)
        if LOG.isEnabledFor(logging.DEBUG):
            for ch, psp in program.sequence_programs.items():
                LOG.info(
                    "Running program for '%s' on ch_out=%s\n %s",
                    psp.ch_out,
                    ch,
                    psp.sequence_program.program,
                )
        armed = qbxc.arm_sequencers(program, self._stack, reset=False)
        exec_results = qbxc.execute_armed_sequencers(armed)
        labelled = qbxc.expand_and_label_results(program, exec_results)
        post_processed = self._results_post_process(labelled)

        raw_data_struct = Struct()
        raw_data_struct.update(post_processed)
        return agent_pb2.RunProgramResponse(raw_data=raw_data_struct)

    @staticmethod
    def _results_post_process(results: dict[str, qbxs.OutputAcquisition]) -> dict[str, list[float]]:
        ret = {}
        for result_key, acquisition in results.items():
            LOG.info("Got results %s_i: %r", result_key, acquisition.bins.integration.path0)
            LOG.info("Got results %s_q: %r", result_key, acquisition.bins.integration.path1)

            ret[f"{result_key}_i"] = acquisition.bins.integration.path0
            ret[f"{result_key}_q"] = acquisition.bins.integration.path1
        return ret

    async def run_mixer_calibration(
        self,
        calibration_request: agent_pb2.RunQuantumMachinesMixerCalibrationRequest,  # noqa: ARG002
        client: "QctrlScaleUpClient",  # noqa: ARG002
    ) -> agent_pb2.RunQuantumMachinesMixerCalibrationResponse:
        LOG.warning(
            "Mixer calibration is not implemented for QBLOX controller. Skipping calibration.",
        )
        return agent_pb2.RunQuantumMachinesMixerCalibrationResponse(success=True)

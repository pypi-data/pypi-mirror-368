"""
Copyright (c) 2024 Massachusetts Institute of Technology 
SPDX-License-Identifier: BSD-2-Clause
"""


import cirq
import numpy as np
from typing import Tuple, Sequence
from functools import cached_property
from qualtran import Register, QAny, QBit, Signature, GateWithRegisters
from qualtran.bloqs.mcmt import And 
from qualtran.cirq_interop.t_complexity_protocol import TComplexity
from pyLIQTR.utils.global_ancilla_manager import GlobalQubitManager as manager
from qualtran.bloqs.mcmt import MultiControlPauli as mcmtp

class CyclicShiftPermutation(GateWithRegisters):
    """
    Implements
        A cyclic shift operator from figure 2 of https://arxiv.org/pdf/2203.10236.pdf which is of the form
    
    .. math::

        L_n=\\sum_{j=0}^{2^n-2}|1+j\\rangle\\langle j|+|0\\rangle\\langle2^n-1|

        R_n=\\sum_{j=0}^{2^n-2}|j\\rangle\\langle 1+j|+|2^n-1\\rangle\\langle 0|

    Parameters
        magnitude : int
            how many qubits to be targeted 
        direction : str
            either l(eft) or r(ight) for the two seperate cyclic shift matrices
        control : Tuple[bool, int]
            whether or not to control entire translation by some int number of registers
        optimize : bool
            less T gates when decomposed into component compute/uncompute Ands

    Raises
        valueError 
            If input direction not valid
            If magnitude < 1
    """

    def __init__(self, magnitude: int, direction: str, control: Tuple[bool, int], optimize: bool):

        if not ((direction == "left") or (direction == "right")):
            if not ((direction == "l") or (direction == "r")):
                raise ValueError("direction must be l(eft) or r(ight)")

        if magnitude < 1:
            raise ValueError("magnitude must be greater than or equal to one qubit")

        self.control = control
        self.optimize = optimize
        self.__dir = direction
        self.__mag = magnitude


    @cached_property
    def vector(self) -> Tuple[int, str]:
        return (self.__mag, self.__dir)
    

    @cached_property # don't forget to cache this
    def signature(self) -> Signature:
        data = Register('data', QAny(bitsize=self.vector[0]))
        if self.control[0]:
            if self.control[1] > 1:
                control = Register('control', QAny(bitsize=self.control[1]))
            elif self.control[1] == 1:
                control = Register('control', QBit())
            return Signature([data, control])
        else:
            return Signature([data])


    def _circuit_diagram_info_(self, _) -> cirq.CircuitDiagramInfo:
        wire_symbols = []
        for reg in self.signature:
            if reg.name == "control":
                wire_symbols += ["control"] * reg.total_bits()
            else:   
                wire_symbols += ["CyclicShift" + str(self.vector[1][0]).upper()] * reg.total_bits()
        return cirq.CircuitDiagramInfo(wire_symbols = wire_symbols)


    def __repr__(self) -> str:
        return f"Cyclic Shift"


    def decompose_from_registers(
        self, *, context: cirq.DecompositionContext, **quregs: Sequence[cirq.Qid]
    ) -> cirq.OP_TREE:

        data = quregs["data"]
        if self.control[0]:
            control = quregs["control"]
            all = list(data) + list(control)
        elif not self.control[0]:
            all = data

        data_dict = {}
        for idx, qbit in enumerate(data):
            data_dict[qbit] = "data" + str(idx)

        if not self.optimize or self.vector[0] <= 2:
            if self.vector[1][0] == "r":
                for reg in data[1:len(list(data))]:   
                    if self.control[0]:
                        register = [reg] + list(control)
                        yield mcmtp((1,) * self.control[1], target_gate=cirq.X).on(*register)
                    elif not self.control[0]:
                        yield cirq.X.on(reg)
            for jdx, qbit in enumerate(data[::-1][:-1]):
                cvs0 = tuple((1, ) * int(data_dict[qbit].split("data")[1]))
                cvs1 = tuple((1, ) * (int(data_dict[qbit].split("data")[1]) + self.control[1]))
                if len(cvs0) > 0:
                    if self.control[0]:
                        register = list(data[jdx:][::-1]) + list(control)
                        yield mcmtp(cvs1, target_gate=cirq.X).on(*register)
                    elif not self.control[0]:
                        yield mcmtp(cvs0, target_gate=cirq.X).on(*data[jdx:][::-1])
                elif len(cvs0) == 0:
                    yield cirq.X.on(data[jdx:][::-1]) 
            if self.vector[1][0] == "l" or self.vector[0] == 1:
                if self.control[0]:
                    register = [data[-1]] + list(control)
                    yield mcmtp((1,) * self.control[1], target_gate=cirq.X).on(*register)
                elif not self.control[0]:
                    yield cirq.X.on(data[-1])
            elif self.vector[1][0] == "r":
                for reg in data[1:len(list(data))-1]:   
                    if self.control[0]:
                        register = [reg] + list(control)
                        yield mcmtp((1,) * self.control[1], target_gate=cirq.X).on(*register)
                    elif not self.control[0]:
                        yield cirq.X.on(reg)
        elif self.optimize and self.vector[0] > 2:
            qm = manager()
            clean = np.array(qm.qalloc(n=(self.vector[0]+self.control[1]-2)))

            if self.vector[1][0] == "r":
                if self.control[1] <= 1:
                    yield cirq.CX.on(*all[-2:][::-1])
                if not self.control[0]:
                    yield cirq.X.on(all[-1])
            yield And().on(*all[-2:][::-1], clean[0])
            for idx in range(len(clean)-1):
                if self.vector[1][0] == "r" and (idx+self.vector[0]-2 > self.control[1]):
                    yield cirq.CX.on(clean[idx], all[-3-idx])
                yield And().on(clean[idx], all[-3-idx], clean[idx+1])
            yield cirq.CX.on(clean[-1], all[0])
            for jdx in range(len(clean)-1)[::-1]:
                yield And(uncompute=True).on(clean[jdx], all[-3-jdx], clean[jdx+1])
                if self.vector[1][0] == "l" and (jdx >= self.control[1]-2):
                    yield cirq.CX.on(clean[jdx], all[-3-jdx])
            yield And(uncompute=True).on(*all[-2:][::-1], clean[0])
            if self.vector[1][0] == "l":
                if self.control[1] <= 1:
                    yield cirq.CX.on(*all[-2:][::-1])
                if not self.control[0]:
                    yield cirq.X.on(all[-1])

            qm.qfree(qubits=[*clean])
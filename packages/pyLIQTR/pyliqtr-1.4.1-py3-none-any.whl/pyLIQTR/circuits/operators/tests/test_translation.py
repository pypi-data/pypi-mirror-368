"""
Copyright (c) 2024 Massachusetts Institute of Technology 
SPDX-License-Identifier: BSD-2-Clause
"""


import cirq
import pytest
import warnings
import numpy as np

from ..translation import Translation
from qualtran._infra.gate_with_registers import get_named_qubits

class TestTranslation:
    """
    Test functionality of Translation by comparing
    circuit generated to analytical unitaries

    TODO: more test coverage!!
    """

    @pytest.fixture(scope = "class")
    def getVector(self):
        return ((5, 7), (15, 31), ("left", "right"))


    @pytest.fixture(scope = "class")
    def getUnitary(self, getVector):

        translationL = Translation(getVector[0][0], (getVector[1][0], True), getVector[2][0], (False, 0), False)
        translationR = Translation(getVector[0][1], (getVector[1][1], True), getVector[2][1], (False, 0), False)

        registersL = get_named_qubits(translationL.signature)
        registersR = get_named_qubits(translationR.signature)

        return [cirq.Circuit(translationL.on_registers(**registersL)).unitary(),
                cirq.Circuit(translationR.on_registers(**registersR)).unitary()]

    def testUnitaryCS(self, getUnitary, getVector):
        
        warnings.warn("If there is an error related to decomposing MCX gates then it could be a bug that has been fixed in source but not released")

        basesL = 2**getVector[0][0]
        basesR = 2**getVector[0][1]

        left_test = []
        right_test = []
        for row in range(basesL):
            left_test.append([])
            for col in range(basesL):
                if col == basesL - getVector[1][0] + row:
                    left_test[row].append(1)
                elif col == row - getVector[1][0]:
                    left_test[row].append(1)
                else:
                    left_test[row].append(0)
        
        for row in range(basesR):
            right_test.append([])
            for col in range(basesR):
                if row == basesR - getVector[1][1] + col:
                    right_test[row].append(1)
                elif col == row + getVector[1][1]:
                    right_test[row].append(1)
                else:
                    right_test[row].append(0)

        np.testing.assert_allclose(left_test, getUnitary[0])
        np.testing.assert_allclose(right_test, getUnitary[1])
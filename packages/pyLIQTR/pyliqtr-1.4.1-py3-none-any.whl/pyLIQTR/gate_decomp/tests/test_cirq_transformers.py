"""
Copyright (c) 2024 Massachusetts Institute of Technology 
SPDX-License-Identifier: BSD-2-Clause
"""


import math
import unittest
import pytest
from random import random, seed
from time import perf_counter
from typing import Union

import cirq
import numpy as np
import pkg_resources

from pyLIQTR.gate_decomp.cirq_transforms import (
    clifford_plus_t_direct_transform,
    clifford_plus_T_ops,
    get_num_rotation_gates,
    get_approximate_t_depth,
    determine_gate_precision,
)
from pyLIQTR.gate_decomp.rotation_gates import rz_decomp

GSE_CIRCUIT_FILE = pkg_resources.resource_filename(
    "pyLIQTR", r"gate_decomp/tests/data/gse_h2_decomp_circuit_example.json"
)
CIRCUIT_FILE = pkg_resources.resource_filename(
    "pyLIQTR", r"gate_decomp/tests/data/test_circuit.json"
)


@pytest.mark.usefixtures("test_circuit_4_qubits")
@pytest.mark.usefixtures("test_circuit_no_rz")
class TestCirqTransforms(unittest.TestCase):
    def setUp(self):
        self.sim = cirq.Simulator(dtype=np.complex128)

    # Some timing tests - easy way to check that changes aren't dramatically increasing
    # the runtime
    def test_profile_prec10(self):
        q0 = cirq.NamedQubit("q0")
        original_circuit = cirq.Circuit()
        times = []
        for _ in range(50):
            original_circuit = cirq.Circuit()
            angle = random() * 2 * math.pi
            original_circuit.append(cirq.H(q0))
            original_circuit.append(cirq.rz(angle).on(q0))
            start = perf_counter()
            new_circuit = clifford_plus_t_direct_transform(original_circuit)
            end = perf_counter()
            times.append(end - start)
        avg_time = sum(times) / len(times)
        self.assertLessEqual(
            avg_time,
            0.1,
            "Avg time over 50 decomps was greater than 0.1s (prec=10)",
        )

    def test_profile_prec15(self):
        q0 = cirq.NamedQubit("q0")
        original_circuit = cirq.Circuit()
        times = []
        seed(1)
        for _ in range(50):
            original_circuit = cirq.Circuit()
            angle = random() * 2 * math.pi
            original_circuit.append(cirq.H(q0))
            original_circuit.append(cirq.rz(angle).on(q0))
            start = perf_counter()
            new_circuit = clifford_plus_t_direct_transform(
                original_circuit, circuit_precision=15
            )
            end = perf_counter()
            times.append(end - start)
        avg_time = sum(times) / len(times)
        self.assertLessEqual(
            avg_time,
            0.05,
            "Avg time over 50 decomps was greater than 0.05s (prec=15)",
        )

    def test_single_qubit_z_rotation(self):
        q0 = cirq.NamedQubit("q0")
        original_circuit = cirq.Circuit()
        original_circuit.append(cirq.H(q0))
        original_circuit.append(cirq.rz(0.43298).on(q0))
        new_circuit = clifford_plus_t_direct_transform(original_circuit)

        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

        original_circuit = cirq.Circuit()
        original_circuit.append(cirq.H(q0))
        original_circuit.append(cirq.rz(-1.87069546).on(q0))
        new_circuit = clifford_plus_t_direct_transform(original_circuit)

        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_single_qubit_x_rotation(self):
        q0 = cirq.NamedQubit("q0")
        original_circuit = cirq.Circuit()
        original_circuit.append(cirq.rx(0.1234).on(q0))
        new_circuit = clifford_plus_t_direct_transform(original_circuit)

        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

        original_circuit = cirq.Circuit()
        original_circuit.append(cirq.rx(-1.456897203).on(q0))
        new_circuit = clifford_plus_t_direct_transform(original_circuit)

        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_single_qubit_y_rotation(self):
        q0 = cirq.NamedQubit("q0")
        original_circuit = cirq.Circuit()
        original_circuit.append(cirq.ry(0.1234).on(q0))
        new_circuit = clifford_plus_t_direct_transform(original_circuit)

        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

        original_circuit = cirq.Circuit()
        original_circuit.append(cirq.ry(-1.456897203).on(q0))
        new_circuit = clifford_plus_t_direct_transform(original_circuit)

        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_multi_axis_rotation_prec10(self):
        q0 = cirq.NamedQubit("q0")
        precision = 10
        original_circuit = cirq.Circuit()
        original_circuit.append(cirq.ry(0.1234).on(q0))
        original_circuit.append(cirq.rx(-1.9687).on(q0))
        original_circuit.append(cirq.rz(0.834).on(q0))
        original_circuit.append(cirq.rx(-2.9687).on(q0))
        original_circuit.append(cirq.rz(1.7896).on(q0))
        original_circuit.append(cirq.ry(0.3421).on(q0))
        original_circuit.append(cirq.rx(-2.3241).on(q0))
        original_circuit.append(cirq.rz(-0.4312).on(q0))
        original_circuit.append(cirq.rx(1.3241).on(q0))
        original_circuit.append(cirq.rz(1.7896).on(q0))
        num_original_gates = 10
        new_circuit = clifford_plus_t_direct_transform(original_circuit, precision)
        max_error = num_original_gates * (2 * 10**-precision)

        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()

        self.assertLessEqual(abs((abs(vec1[0]) ** 2 - abs(vec2[0]) ** 2)), max_error)
        self.assertLessEqual(abs((abs(vec1[1]) ** 2 - abs(vec2[1]) ** 2)), max_error)

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_multi_axis_rotation_prec13(self):
        q0 = cirq.NamedQubit("q0")
        original_circuit = cirq.Circuit()
        precision = 13
        original_circuit.append(cirq.ry(0.1234).on(q0))
        original_circuit.append(cirq.rx(-1.9687).on(q0))
        original_circuit.append(cirq.rz(0.834).on(q0))
        original_circuit.append(cirq.rx(-2.9687).on(q0))
        original_circuit.append(cirq.rz(1.7896).on(q0))
        original_circuit.append(cirq.ry(0.3421).on(q0))
        original_circuit.append(cirq.rx(-2.3241).on(q0))
        original_circuit.append(cirq.rz(-0.4312).on(q0))
        original_circuit.append(cirq.rx(1.3241).on(q0))
        original_circuit.append(cirq.rz(1.7896).on(q0))
        new_circuit = clifford_plus_t_direct_transform(original_circuit, precision)
        num_original_gates = 10
        max_error = num_original_gates * (2 * 10**-precision)

        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()
        self.assertLessEqual(abs((abs(vec1[0]) ** 2 - abs(vec2[0]) ** 2)), max_error)
        self.assertLessEqual(abs((abs(vec1[1]) ** 2 - abs(vec2[1]) ** 2)), max_error)

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_qsp_circuit(self):
        original_circuit = cirq.read_json(CIRCUIT_FILE)
        num_original_rotations = 0
        precision = 10
        for moment in original_circuit:
            for op in moment:
                if "Rx" in str(op) or "Ry" in str(op) or "Rz" in str(op):
                    num_original_rotations += 1
        max_error = num_original_rotations * (2 * 10**-precision)
        new_circuit = clifford_plus_t_direct_transform(original_circuit)
        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()
        for i in range(len(vec1)):
            self.assertLessEqual(
                abs((abs(vec1[i]) ** 2 - abs(vec2[i]) ** 2)), max_error
            )

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_XPow_gates(self):
        q0, q1, q2 = cirq.LineQubit.range(3)
        original_circuit = cirq.Circuit()
        original_circuit.append(cirq.X.on(q0) ** 0.4254)
        original_circuit.append(cirq.X.on(q1) ** -1.7438)
        original_circuit.append(cirq.X.on(q2) ** 2.782)
        original_circuit.append(cirq.rz(0.437268).on(q1))
        original_circuit.append(cirq.Y.on(q1) ** 2.782)
        original_circuit.append(cirq.Z.on(q1) ** 0.782)
        transformed_circuit = clifford_plus_t_direct_transform(original_circuit)
        vec1 = self.sim.simulate(original_circuit).state_vector()
        vec2 = self.sim.simulate(transformed_circuit).state_vector()
        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_gse_circuit(self):
        original_circuit = cirq.read_json(GSE_CIRCUIT_FILE)
        new_circuit = clifford_plus_t_direct_transform(
            original_circuit, circuit_precision=1e-10
        )
        sim1 = cirq.Simulator(dtype=np.complex128, seed=1)
        sim2 = cirq.Simulator(dtype=np.complex128, seed=1)
        res1 = sim1.simulate(original_circuit)
        res2 = sim2.simulate(new_circuit)
        vec1 = res1.state_vector()
        vec2 = res2.state_vector()
        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_rz_decomp1(self):
        seed(0)
        q0 = cirq.NamedQubit("q0")
        circuit1 = cirq.Circuit()
        circuit1.append(cirq.rz(0.34).on(q0))
        circuit1 = clifford_plus_t_direct_transform(circuit1, circuit_precision=1e-10)

        seed(0)
        circuit2 = cirq.Circuit()
        circuit2.append(rz_decomp(rads=0.34).on(q0))
        circuit2 = cirq.expand_composite(
            circuit2, no_decomp=lambda g: g.gate in [cirq.H]
        )

        self.assertEqual(circuit1, circuit2)

    def test_rz_decomp2(self):
        seed(0)
        q0 = cirq.NamedQubit("q0")
        circuit = cirq.Circuit()
        circuit.append(cirq.rz(0.21 * np.pi).on(q0))
        circuit1 = clifford_plus_t_direct_transform(
            circuit, circuit_precision=1e-15, use_rotation_decomp_gates=True
        )
        circuit1 = cirq.expand_composite(
            circuit1, no_decomp=lambda g: g.gate in [cirq.H]
        )
        seed(0)
        circuit2 = clifford_plus_t_direct_transform(circuit, circuit_precision=1e-15)
        self.assertEqual(circuit1, circuit2)

    def test_rz_decomp_w_classical_controls(self):
        original_circuit = cirq.read_json(GSE_CIRCUIT_FILE)
        seed(0)
        new_circuit1 = clifford_plus_t_direct_transform(
            original_circuit, circuit_precision=1e-10, use_rotation_decomp_gates=True
        )
        new_circuit1 = cirq.expand_composite(
            new_circuit1, no_decomp=lambda g: g.gate in [cirq.H]
        )
        sim1 = cirq.Simulator(dtype=np.complex128, seed=1)
        sim2 = cirq.Simulator(dtype=np.complex128, seed=1)
        res1 = sim1.simulate(original_circuit)
        res2 = sim2.simulate(new_circuit1)
        vec1 = res1.state_vector()
        vec2 = res2.state_vector()

        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_rz_decomp_qsp_circuit(self):
        original_circuit = cirq.read_json(CIRCUIT_FILE)
        seed(0)
        new_circuit1 = clifford_plus_t_direct_transform(original_circuit)
        seed(0)
        new_circuit2 = clifford_plus_t_direct_transform(
            original_circuit, use_rotation_decomp_gates=True
        )
        new_circuit2 = cirq.expand_composite(
            new_circuit2, no_decomp=lambda g: g.gate in [cirq.H]
        )
        self.assertTrue(new_circuit1, new_circuit2)

    def test_rx_decomp_inverse_gate(self):
        q0 = cirq.NamedQubit("q0")
        circuit = cirq.Circuit()
        circuit.append(cirq.inverse(cirq.rx(0.947).on(q0)))
        new_circuit = clifford_plus_t_direct_transform(
            circuit, circuit_precision=1e-10, use_rotation_decomp_gates=True
        )
        new_circuit = cirq.expand_composite(
            new_circuit, no_decomp=lambda g: g.gate in [cirq.H]
        )
        vec1 = self.sim.simulate(circuit).state_vector()
        vec2 = self.sim.simulate(new_circuit).state_vector()
        self.assertTrue(cirq.allclose_up_to_global_phase(vec1, vec2))

    def test_rz_decomp_circuit2qasm(self):
        original_circuit = cirq.read_json(CIRCUIT_FILE)[0:2]
        seed(0)
        print("original")
        print(cirq.qasm(original_circuit))
        print()
        new_circuit2 = clifford_plus_t_direct_transform(
            original_circuit, use_rotation_decomp_gates=True
        )
        print("decomped")
        print(cirq.qasm(new_circuit2))
        print()
        print("expanded")
        new_circuit2 = cirq.expand_composite(
            new_circuit2, no_decomp=lambda g: g.gate in [cirq.H]
        )
        print(cirq.qasm(new_circuit2))

    def test_rz_decomp_to_qasm(self):
        seed(0)
        q0 = cirq.NamedQubit("q0")
        circuit = cirq.Circuit()
        circuit.append(cirq.rz(0.143).on(q0))
        new_circuit = clifford_plus_t_direct_transform(
            circuit, use_rotation_decomp_gates=True
        )
        qasm_string = cirq.qasm(new_circuit)
        # don't want the line in the header saying what version of cirq is used
        index = qasm_string.find("OPENQASM 2.0")
        qasm_string_no_version = qasm_string[index::]
        correct_string1 = (
            "OPENQASM 2.0;\ninclude"
            ' "qelib1.inc";\n\n\n// Qubits: [q0]\nqreg q[1];\n\n\nrz_d(pi*0.0455183137)'
            " q[0];\n// (False, 109050714056276670683333018392, 98, [S, H, (S**-1)])"
        )
        assert(qasm_string_no_version.endswith(correct_string1))

    def test_ry_decomp_to_qasm(self):
        seed(0)
        q0 = cirq.NamedQubit("q0")
        circuit = cirq.Circuit()
        circuit.append(cirq.ry(0.967).on(q0))
        new_circuit = clifford_plus_t_direct_transform(
            circuit, use_rotation_decomp_gates=True
        )
        qasm_string = cirq.qasm(new_circuit)
        index = qasm_string.find("OPENQASM 2.0")
        # whether you run this test individually or as part of the suite seems to affect
        # the random seeding for the decomposition - to deal with this just check if
        # the string is either of these.
        correct_string1 = (
            "OPENQASM 2.0;\ninclude"
            ' "qelib1.inc";\n\n\n// Qubits: [q0]\nqreg q[1];\n\n\n// Gate:'
            " Ry_d(0.3078056599397256π)\nsdg q[0];\nh q[0];\nrz_d(pi*0.3078056599)"
            " q[0];\n// (True, 648022807138153475916841871980, 101, [Z])\nh q[0];\ns"
            " q[0];"
        )
        correct_string2 = (
            "OPENQASM 2.0;\ninclude"
            ' "qelib1.inc";\n\n\n// Qubits: [q0]\nqreg q[1];\n\n\n// Gate:'
            " Ry_d(0.3078056599397256π)\nsdg q[0];\nh q[0];\nrz_d(pi*0.3078056599)"
            " q[0];\n// (True, 914503652851411841148494693424, 101, [Z])\nh q[0];\ns"
            " q[0];"
        )
        correct_string3 = (
            "OPENQASM 2.0;\ninclude"
            ' "qelib1.inc";\n\n\n// Qubits: [q0]\nqreg q[1];\n\n\n// Gate:'
            " Ry_d(0.3078056599397256π)\nsdg q[0];\nh q[0];\nrz_d(pi*0.3078056599)"
            " q[0];\n// (True, 444116479936266167563103318273, 101, [S, Y])\nh q[0];\ns"
            " q[0];"
        )
        # We removed the Cirq version from the test string to remove the version dependecy
        # so now we need to check both possible results.
        print(qasm_string)
        assert(any(x in qasm_string for x in [correct_string1, correct_string2, correct_string3]))

    def test_rx_decomp_to_qasm(self):
        q0 = cirq.NamedQubit("q0")
        circuit = cirq.Circuit()
        circuit.append(cirq.rx(0.246).on(q0))
        seed(0)
        new_circuit = clifford_plus_t_direct_transform(
            circuit, use_rotation_decomp_gates=True
        )
        qasm_string = cirq.qasm(new_circuit)
        index = qasm_string.find("OPENQASM 2.0")
        # whether you run this test individually or as part of the suite seems to affect
        # the random seeding for the decomposition - to deal with this just check if
        # the string is either of these.
        correct_string1 = (
            "OPENQASM 2.0;\ninclude"
            ' "qelib1.inc";\n\n\n// Qubits: [q0]\nqreg q[1];\n\n\n// Gate:'
            " Rx_d(0.0783042320012125π)\nh q[0];\nrz_d(pi*0.078304232) q[0];\n//"
            " (False, 156581822512854592575398412630, 98, [(S**-1), H, (S**-1)])\nh"
            " q[0];"
        )
        correct_string2 = (
            "OPENQASM 2.0;\ninclude"
            ' "qelib1.inc";\n\n\n// Qubits: [q0]\nqreg q[1];\n\n\n// Gate:'
            " Rx_d(0.0783042320012125π)\nh q[0];\nrz_d(pi*0.078304232) q[0];\n//"
            " (False, 244176282553465898102860881568, 98, [H, Z])\nh"
            " q[0];"
        )
        correct_string3 = (
            "OPENQASM 2.0;\ninclude"
            ' "qelib1.inc";\n\n\n// Qubits: [q0]\nqreg q[1];\n\n\n// Gate:'
            " Rx_d(0.0783042320012125π)\nh q[0];\nrz_d(pi*0.078304232) q[0];\n//"
            " (False, 208634673743336647316197590477, 98, [H, (S**-1)])\nh"
            " q[0];"
        )
        # We removed the Cirq version from the test string to remove the version dependecy
        # so now we need to check both possible results.
        print(qasm_string)
        assert(any(x in qasm_string for x in [correct_string1, correct_string2, correct_string3]))

    def test_multiple_decomp_rotations_to_qasm(self):
        seed(0)
        q0, q1, q2 = cirq.LineQubit.range(3)
        circuit = cirq.Circuit()
        circuit.append(cirq.rz(0.143).on(q0))
        circuit.append(cirq.ry(0.967).on(q1))
        circuit.append(cirq.rx(0.246).on(q2))
        correct_string1 = (
            "OPENQASM 2.0;\ninclude"
            ' "qelib1.inc";\n\n\n// Qubits: [q(0), q(1), q(2)]\nqreg'
            " q[3];\n\n\nrz_d(pi*0.0455183137) q[0];\n// (False,"
            " 66393976246411458480317831285, 98, [S, H, Z])\n// Gate:"
            " Ry_d(0.3078056599397256π)\nsdg q[1];\nh q[1];\nrz_d(pi*0.3078056599)"
            " q[1];\n// (True, 493997145995858371046147137373, 101, [S, Y])\nh q[1];\ns"
            " q[1];\n// Gate: Rx_d(0.0783042320012125π)\nh q[2];\nrz_d(pi*0.078304232)"
            " q[2];\n// (False, 244176282553465898102860881568, 98, [H, Z])\nh q[2];"
        )
        correct_string2 = (
            'OPENQASM 2.0;\ninclude "qelib1.inc";\n\n\n// Qubits: [q(0), q(1),'
            " q(2)]\nqreg q[3];\n\n\nrz_d(pi*0.0455183137) q[0];\n// (False,"
            " 109050714056276670683333018392, 98, [S, H, (S**-1)])\n// Gate:"
            " Ry_d(0.3078056599397256π)\nsdg q[1];\nh q[1];\nrz_d(pi*0.3078056599)"
            " q[1];\n// (True, 914503652851411841148494693424, 101, [Z])\nh q[1];\ns"
            " q[1];\n// Gate: Rx_d(0.0783042320012125π)\nh q[2];\nrz_d(pi*0.078304232)"
            " q[2];\n// (False, 208634673743336647316197590477, 98, [H, (S**-1)])\nh"
            " q[2];"
        )
        new_circuit = clifford_plus_t_direct_transform(
            circuit, use_rotation_decomp_gates=True
        )
        qasm_string = cirq.qasm(new_circuit)
        index = qasm_string.find("OPENQASM 2.0")
        self.assertIn(qasm_string[index:], [correct_string1, correct_string2])

    def test_random_decomp1(self):
        q0 = cirq.NamedQubit("q0")
        # mainly just want to check no errors get thrown here
        for _ in range(10):
            circuit = cirq.Circuit()
            circuit.append(
                rz_decomp(0.134, precision=1e-16, use_random_decomp=True).on(q0)
            )
            new_circuit = cirq.expand_composite(
                circuit, no_decomp=lambda g: g.gate in [cirq.H]
            )

    def test_random_decomp2(self):
        q0, q1 = cirq.LineQubit.range(2)
        for _ in range(10):
            circuit = cirq.Circuit()
            circuit.append(cirq.rz(0.312).on(q0))
            circuit.append(cirq.ry(0.123).on(q1))
            new_circuit = clifford_plus_t_direct_transform(
                circuit, use_random_decomp=True
            )

    def test_accuracy_issue(self):
        q0 = cirq.NamedQubit("q0")
        circuit = cirq.Circuit()
        circuit.append(cirq.ry(0.20483276469913342 * np.pi).on(q0))
        new_circuit = clifford_plus_t_direct_transform(circuit, circuit_precision=10)

    def test_pi_rots(self):
        q0 = cirq.NamedQubit("q0")
        for s in [-1, 1]:
            for p in [13, 14, 15, 16, 17, 18, 19]:
                for d in [1, 2, 4]:
                    circuit = cirq.Circuit()
                    circuit.append(cirq.rz(s * np.pi / d).on(q0))
                    new_circuit = clifford_plus_t_direct_transform(circuit, circuit_precision=p)

    def test_num_rotation_gates1(self):
        q0, q1 = cirq.LineQubit.range(2)
        circuit = cirq.Circuit()
        circuit.append(cirq.rz(0.312).on(q0))
        circuit.append(cirq.ry(0.123).on(q1))
        circuit.append(cirq.CX(q0, q1))
        circuit.append(cirq.X(q1))
        circuit.append(cirq.T(q0))
        circuit.append(cirq.ry(1.31).on(q0))
        self.assertEqual(get_num_rotation_gates(circuit), 3)

    def test_get_approx_t_depth(self):
        t_depth = get_approximate_t_depth(self.test_circuit_4_qubits)
        self.assertEqual(t_depth, 109)

    # The next set of tests should make sure the precision calculation stays in working order.
    # The default gate precision is 1e-10, which means the result should be within 1e-5 to 1e-50.
    def precision_is_valid(self, precision: Union[int, float] = None) -> bool:
        print("Precision = %f" % precision)
        if 1e-50 <= precision <= 1e-5:
            return True
        else:
            return False

    def test_determine_gate_precision_valid_params(self):
        precision = determine_gate_precision(circuit=self.test_circuit_4_qubits, 
                                                     gate_precision=1e-10,
                                                     circuit_precision=1e-10,
                                                     num_rotation_gates=1)
        assert self.precision_is_valid(precision)

    def test_determine_gate_precision_no_rotational_gates(self):
        precision = determine_gate_precision(circuit=self.test_circuit_no_rz, 
                                                     gate_precision=1e-20,
                                                     circuit_precision=1e-10,
                                                     num_rotation_gates=0)
        assert self.precision_is_valid(precision)

    def test_determine_gate_precision_circuit_precision_none(self):
        precision = determine_gate_precision(circuit=self.test_circuit_4_qubits, 
                                                     gate_precision=1e-15,
                                                     circuit_precision=None,
                                                     num_rotation_gates=1)
        assert self.precision_is_valid(precision)

    def test_determine_gate_precision_only_gate_precision(self):
        precision = determine_gate_precision(circuit=self.test_circuit_4_qubits, 
                                                     gate_precision=1e-10,
                                                     circuit_precision=None,
                                                     num_rotation_gates=1)
        assert self.precision_is_valid(precision)

    def test_determine_gate_precision_only_circuit_precision(self):
        precision = determine_gate_precision(circuit=self.test_circuit_4_qubits, 
                                                     gate_precision=None,
                                                     circuit_precision=1e-10,
                                                     num_rotation_gates=1)
        assert self.precision_is_valid(precision)

"""
Copyright (c) 2024 Massachusetts Institute of Technology 
SPDX-License-Identifier: BSD-2-Clause
"""


import unittest
from math import gcd
from random import randint
import random

import gmpy2
from gmpy2 import mpfr

from pyLIQTR.gate_decomp.exact_decomp import *
from pyLIQTR.gate_decomp.gate_approximation import (
    get_ring_elts_direct,
    get_ring_elts_fallback,
)
from pyLIQTR.gate_decomp.matrices import MAT_D_OMEGA


class TestExactDecomp(unittest.TestCase):
    # for angles from π/120 to 239π/120, (except for multiples of π/2, π/4, and π/8), make sure that
    # the gate decomposition is equal to the approximate unitary found
    def test_exact_decomp_prec10(self):
        prec = 10
        PI = gmpy2.const_pi()
        for i in range(239):
            i += 1
            if i % 15 != 0:
                u, t, k = get_ring_elts_direct(i * PI / 120, prec)
                circuit, _ = exact_decomp_to_matrix_string(u, t, k)
                mat = MAT_D_OMEGA(u, -t.conj(), t, u.conj(), k)
                self.assertTrue(
                    are_equivalent(circuit, mat, False), f"Failed for {i}π/120"
                )

    # for higher precisions just pick random gates instead of looping through everything
    def test_exact_decomp_prec20(self):
        prec = 20
        PI = gmpy2.const_pi()
        for _ in range(10):
            i = randint(1, 240)
            while i % 15 == 0:
                i = randint(1, 240)
            u, t, k = get_ring_elts_direct(i * PI / 120, prec)
            circuit, _ = exact_decomp_to_matrix_string(u, t, k)
            mat = MAT_D_OMEGA(u, -t.conj(), t, u.conj(), k)
            self.assertTrue(are_equivalent(circuit, mat, False), f"Failed for {i}π/120")

    def test_exact_decomp_prec30(self):
        prec = 30
        PI = gmpy2.const_pi()
        for _ in range(11):
            i = randint(1, 240)
            while i % 15 == 0:
                i = randint(1, 240)
            u, t, k = get_ring_elts_direct(i * PI / 120, prec)
            circuit, _ = exact_decomp_to_matrix_string(u, t, k)
            mat = MAT_D_OMEGA(u, -t.conj(), t, u.conj(), k)
            self.assertTrue(are_equivalent(circuit, mat, False), f"Failed for {i}π/120")

    def test_exact_decomp_prec40(self):
        prec = 40
        PI = gmpy2.const_pi()
        for _ in range(10):
            i = randint(1, 240)
            while i % 15 == 0:
                i = randint(1, 240)
            u, t, k = get_ring_elts_direct(i * PI / 120, prec)
            circuit, _ = exact_decomp_to_matrix_string(u, t, k)
            mat = MAT_D_OMEGA(u, -t.conj(), t, u.conj(), k)
            self.assertTrue(are_equivalent(circuit, mat, False), f"Failed for {i}π/120")

    def test_rand_angles_prec50(self):
        gmpy2.get_context().precision = 346
        for _ in range(5):
            denom = 10000
            num = randint(1, 20000)
            common_factor = gcd(num, denom)
            num //= common_factor
            denom //= common_factor
            while denom in [1, 2, 4, 8]:
                num = randint(1, 20000)
                denom = 10000
                common_factor = gcd(num, denom)
                num //= common_factor
                denom //= common_factor
            u, t, k = get_ring_elts_direct(num * gmpy2.const_pi() / denom, 50)
            circuit, _ = exact_decomp_to_matrix_string(u, t, k)
            mat = MAT_D_OMEGA(u, -t.conj(), t, u.conj(), k)
            self.assertTrue(
                are_equivalent(circuit, mat, False), f"Failed for {num}π/{denom}"
            )

    def test_exact_decomp_fallback_prec10(self):
        prec = 10
        PI = gmpy2.const_pi()
        r = mpfr("0.999")
        for i in range(10):
            i = randint(1, 240)
            while i % 15 == 0:
                i = randint(1, 240)
            angle = i * PI / 120
            u1, t1, k1, u2, t2, k2 = get_ring_elts_fallback(angle, prec, r)
            circuit1, _ = exact_decomp_to_matrix_string(u1, t1, k1)
            mat1 = MAT_D_OMEGA(u1, -t1.conj(), t1, u1.conj(), k1)
            self.assertTrue(
                are_equivalent(circuit1, mat1, False), f"Failed for {i}π/{120}"
            )
            circuit2, _ = exact_decomp_to_matrix_string(u2, t2, k2)
            mat2 = MAT_D_OMEGA(u2, -t2.conj(), t2, u2.conj(), k2)
            self.assertTrue(
                are_equivalent(circuit2, mat2, False), f"Failed for {i}π/{120}"
            )

    def test_exact_decomp_fallback_prec20(self):
        prec = 20
        PI = gmpy2.const_pi()
        r = mpfr("0.999")
        times = []
        for _ in range(10):
            i = randint(1, 240)
            while i % 15 == 0:
                i = randint(1, 240)
            angle = i * PI / 120
            u1, t1, k1, u2, t2, k2 = get_ring_elts_fallback(angle, prec, r)
            circuit1, _ = exact_decomp_to_matrix_string(u1, t1, k1)
            mat1 = MAT_D_OMEGA(u1, -t1.conj(), t1, u1.conj(), k1)
            self.assertTrue(
                are_equivalent(circuit1, mat1, False), f"Failed for {i}π/{120}"
            )
            circuit2, _ = exact_decomp_to_matrix_string(u2, t2, k2)
            mat2 = MAT_D_OMEGA(u2, -t2.conj(), t2, u2.conj(), k2)
            self.assertTrue(
                are_equivalent(circuit2, mat2, False), f"Failed for {i}π/{120}"
            )

    def test_exact_decomp_fallback_prec30(self):
        prec = 30
        PI = gmpy2.const_pi()
        r = mpfr("0.999")
        random.seed(1)
        for _ in range(10):
            i = randint(1, 240)
            while i % 15 == 0:
                i = randint(1, 240)
            angle = i * PI / 120
            u1, t1, k1, u2, t2, k2 = get_ring_elts_fallback(angle, prec, r)
            circuit1, _ = exact_decomp_to_matrix_string(u1, t1, k1)
            mat1 = MAT_D_OMEGA(u1, -t1.conj(), t1, u1.conj(), k1)
            self.assertTrue(
                are_equivalent(circuit1, mat1, False), f"Failed for {i}π/{120}"
            )
            circuit2, _ = exact_decomp_to_matrix_string(u2, t2, k2)
            mat2 = MAT_D_OMEGA(u2, -t2.conj(), t2, u2.conj(), k2)
            self.assertTrue(
                are_equivalent(circuit2, mat2, False), f"Failed for {i}π/{120}"
            )

    def test_exact_decomp_fallback_prec40(self):
        prec = 40
        PI = gmpy2.const_pi()
        r = mpfr("0.999")
        for _ in range(5):
            i = randint(1, 240)
            while i % 15 == 0:
                i = randint(1, 240)
            angle = i * PI / 120
            u1, t1, k1, u2, t2, k2 = get_ring_elts_fallback(angle, prec, r)
            circuit1, _ = exact_decomp_to_matrix_string(u1, t1, k1)
            mat1 = MAT_D_OMEGA(u1, -t1.conj(), t1, u1.conj(), k1)
            self.assertTrue(
                are_equivalent(circuit1, mat1, False), f"Failed for {i}π/{120}"
            )
            circuit2, _ = exact_decomp_to_matrix_string(u2, t2, k2)
            mat2 = MAT_D_OMEGA(u2, -t2.conj(), t2, u2.conj(), k2)
            self.assertTrue(
                are_equivalent(circuit2, mat2, False), f"Failed for {i}π/{120}"
            )

    def test_exact_decomp_fallback_prec50(self):
        prec = 50
        PI = gmpy2.const_pi()
        r = mpfr("0.999")
        for _ in range(5):
            i = randint(1, 240)
            while i % 15 == 0:
                i = randint(1, 240)
            angle = i * PI / 120
            u1, t1, k1, u2, t2, k2 = get_ring_elts_fallback(angle, prec, r)
            circuit1, _ = exact_decomp_to_matrix_string(u1, t1, k1)
            mat1 = MAT_D_OMEGA(u1, -t1.conj(), t1, u1.conj(), k1)
            self.assertTrue(
                are_equivalent(circuit1, mat1, False), f"Failed for {i}π/{120}"
            )
            circuit2, _ = exact_decomp_to_matrix_string(u2, t2, k2)
            mat2 = MAT_D_OMEGA(u2, -t2.conj(), t2, u2.conj(), k2)
            self.assertTrue(
                are_equivalent(circuit2, mat2, False), f"Failed for {i}π/{120}"
            )

    def test_compressed_rep1(self):
        gate_strs = ["S", "Sd", "H", "X", "Y", "Z", "T"]
        HT_ = H2 @ T2
        SHT_ = S2 @ H2 @ T2

        m = HT_ @ SHT_ @ SHT_ @ HT_ @ HT_

        (
            first_gate,
            gate_sequence,
            sequence_length,
            clifford_part,
        ) = exact_decomp_compressed_m(m, gate_strs)
        self.assertFalse(first_gate)
        self.assertEqual(clifford_part, [])
        self.assertEqual(gate_sequence, 12)
        self.assertEqual(sequence_length, 5)

    def test_compressed_rep2(self):
        gate_strs = ["S", "Sd", "H", "X", "Y", "Z", "T"]
        HT_ = H2 @ T2
        SHT_ = S2 @ H2 @ T2
        m = T2 @ HT_ @ SHT_ @ SHT_ @ HT_ @ SHT_ @ SHT_ @ Y2 @ S2
        (
            first_gate,
            gate_sequence,
            sequence_length,
            clifford_part,
        ) = exact_decomp_compressed_m(m, gate_strs)
        self.assertTrue(first_gate)
        self.assertEqual(gate_sequence, 27)
        self.assertEqual(sequence_length, 6)
        self.assertEqual(clifford_part, ["S", "Y"])


if __name__ == "__main__":
    unittest.main()

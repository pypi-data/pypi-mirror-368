"""
Copyright (c) 2024 Massachusetts Institute of Technology 
SPDX-License-Identifier: BSD-2-Clause
"""
import pytest
import cirq
import sys
from io import StringIO

from pyLIQTR.utils.Hamiltonian import Hamiltonian
from pyLIQTR.circuits.operators.selectV import ChildsSelectV,QROMSelectV
from pyLIQTR.utils.printing import _build_qasm_qubit_map

from pyLIQTR.utils.qsp_helpers import circuit_decompose_once

class TestSelectV:
    @pytest.fixture(scope="class")
    def getHamiltonianAndQubits(self):
        terms = [("XXXX",1),("YYYY",1),("ZZZZ",1),
                 ("XIIY",-1),("IXYI",-2),("IZIZ",-3)]
        ham = Hamiltonian(terms)
        allqubits = cirq.LineQubit.range(4+ham.loglen+1+3)
        trgt = allqubits[0:4]
        ctl = allqubits[4:7]
        phs = [allqubits[7]]
        anc = allqubits[8:]

        yield (ham,trgt,ctl,phs,anc)
        del (ham,trgt,ctl,phs,anc)
        
    @pytest.fixture(scope="class")
    def getHamiltonianAndQubits2(self):
        terms = [("XXXX",-1),("YYYY",-1),("ZZZZ",-1),
                 ("XIIY",+1),("IXYI",+2),("IZIZ",+3)]
        ham = Hamiltonian(terms)
        allqubits = cirq.LineQubit.range(4+ham.loglen+1+3)
        trgt = allqubits[0:4]
        ctl = allqubits[4:7]
        phs = [allqubits[7]]
        anc = allqubits[8:]

        yield (ham,trgt,ctl,phs,anc)
        del (ham,trgt,ctl,phs,anc)

    def test_childs_basic(self,getHamiltonianAndQubits):
        #just testing to make sure no error occurs during object creation
        #and "normal use"
        ham = getHamiltonianAndQubits[0]
        trgtQ = getHamiltonianAndQubits[1]
        ctlQ = getHamiltonianAndQubits[2]
        phsQ = getHamiltonianAndQubits[3]
        ancillaQ = getHamiltonianAndQubits[4]
        allQ = [*trgtQ,*ctlQ,*phsQ,*ancillaQ]
        
        #should be able to be created
        operator = ChildsSelectV(hamiltonian = ham,
                                 phase_qubit = phsQ,
                                 target_qubits = trgtQ,
                                 control_qubits = ctlQ,
                                 ancilla_qubits = ancillaQ)
        #should be able to be appended onto a circuit
        circuit = cirq.Circuit()
        circuit.append(operator.on(*allQ))

        #let's check the string version of this.
        opStr = str(operator)
        assert("ChildsSelectV q(7),q(8),q(9),q(10),q(4),q(5),q(6),q(0),q(1),q(2),q(3)")

        #check the openQASM decomposition
        qasm_args,__,__ = _build_qasm_qubit_map(circuit)
        trueQasmStr = "ChildsSelectV(q(7),q(8),q(9),q(10),q(4),q(5),q(6),q(0),q(1),q(2),q(3))\n"
        for op in circuit[0]:
            opQasmStr = cirq.qasm(op, args = qasm_args)
            assert(opQasmStr == trueQasmStr)
        
        #check the number of qubits.
        assert(operator.num_qubits() == 11)
    
    def test_childs_decomp(self, getHamiltonianAndQubits):
        ham = getHamiltonianAndQubits[0]
        trgtQ = getHamiltonianAndQubits[1]
        ctlQ = getHamiltonianAndQubits[2]
        phsQ = getHamiltonianAndQubits[3]
        ancillaQ = getHamiltonianAndQubits[4]
        allQ = [*trgtQ,*ctlQ,*phsQ,*ancillaQ]
        
        #should be able to be created
        operator = ChildsSelectV(hamiltonian = ham,
                                 phase_qubit = phsQ,
                                 target_qubits = trgtQ,
                                 control_qubits = ctlQ,
                                 ancilla_qubits = ancillaQ)
        circuit = cirq.Circuit()
        circuit.append(operator.on(*allQ))
        #lets 2qasm it
        #DO NOT ADJUST FORMATTING OF THIS STRING
        testStr = """
OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [q(0), q(1), q(2), q(3), q(4), q(5), q(6), q(7), q(8), q(9), q(10)]
qreg q[11];


ChildsSelectV(q(7),q(8),q(9),q(10),q(4),q(5),q(6),q(0),q(1),q(2),q(3))
"""
        assert(cirq.qasm(circuit).endswith(testStr))
        #decomp it
        decomposed_circuit = cirq.align_left(circuit_decompose_once(circuit))
        #difficult to actually test, since frozenset order is not fixed due to a security vulnerability
        #so all we will do is check to make sure this executes
    
    def test_equality(self, getHamiltonianAndQubits, getHamiltonianAndQubits2):
        ham = getHamiltonianAndQubits[0]
        trgtQ = getHamiltonianAndQubits[1]
        ctlQ = getHamiltonianAndQubits[2]
        phsQ = getHamiltonianAndQubits[3]
        ancillaQ = getHamiltonianAndQubits[4]
        allQ = [*trgtQ,*ctlQ,*phsQ,*ancillaQ]
        
        #should be able to be created
        operator1 = ChildsSelectV(hamiltonian = ham,
                                 phase_qubit = phsQ,
                                 target_qubits = trgtQ,
                                 control_qubits = ctlQ,
                                 ancilla_qubits = ancillaQ)
        operator1b = QROMSelectV(hamiltonian = ham,
                                 phase_qubit = phsQ,
                                 target_qubits = trgtQ,
                                 control_qubits = ctlQ,
                                 ancilla_qubits = ancillaQ)
        
        ham = getHamiltonianAndQubits2[0]
        trgtQ = getHamiltonianAndQubits2[1]
        ctlQ = getHamiltonianAndQubits2[2]
        phsQ = getHamiltonianAndQubits2[3]
        ancillaQ = getHamiltonianAndQubits2[4]
        allQ = [*trgtQ,*ctlQ,*phsQ,*ancillaQ]
        
        #should be able to be created
        operator2 = ChildsSelectV(hamiltonian = ham,
                                 phase_qubit = phsQ,
                                 target_qubits = trgtQ,
                                 control_qubits = ctlQ,
                                 ancilla_qubits = ancillaQ)
        
        assert((operator1!=operator2))
        assert(operator1==operator1)
        assert(operator2==operator2)
        assert(operator1!=operator1b)

    def test_childs_count(self, getHamiltonianAndQubits):
        ham = getHamiltonianAndQubits[0]
        trgtQ = getHamiltonianAndQubits[1]
        ctlQ = getHamiltonianAndQubits[2]
        phsQ = getHamiltonianAndQubits[3]
        ancillaQ = getHamiltonianAndQubits[4]
        allQ = [*trgtQ,*ctlQ,*phsQ,*ancillaQ]
        
        #should be able to be created
        operator = ChildsSelectV(hamiltonian = ham,
                                 phase_qubit = phsQ,
                                 target_qubits = trgtQ,
                                 control_qubits = ctlQ,
                                 ancilla_qubits = ancillaQ)
    

        count_exact_dict = {'X': 12,
                'H': 20,
                'CNOT': 79,
                'T**-1': 37,
                'T': 33,
                'S': 13,
                'S**-1': 9,
                'CZ': 6,
                'Z': 3,
                'X**-1': 2}
        
        auto_count = operator.count_exact()
        for key in count_exact_dict:
            assert(auto_count[key] == count_exact_dict[key])

    
    


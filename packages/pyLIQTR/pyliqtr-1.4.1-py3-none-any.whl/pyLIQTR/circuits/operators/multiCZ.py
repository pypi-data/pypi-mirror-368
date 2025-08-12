"""
Copyright (c) 2024 Massachusetts Institute of Technology 
SPDX-License-Identifier: BSD-2-Clause
"""
import pyLIQTR.circuits.pyLOperator as pyLOperator
from pyLIQTR.utils.utils import getLineQubitIndexMap, getQubitFromMap
from cirq   import LineQubit, CCZ, CCX
import cirq
from typing import Dict, List, Optional, Tuple
from pyLIQTR.utils.circuit_decomposition import decompose_once
from pyLIQTR.gate_decomp.cirq_transforms import clifford_plus_t_direct_transform, get_approximate_t_depth



class MultiCZ(pyLOperator.pyLOperator):
    """
    Implements the MultiCZ operator using technique from https://arxiv.org/abs/1508.03273.
    """
      
    def __init__(self, control_qubits:List[LineQubit], target_qubit:List[LineQubit], ancilla_qubits:List[LineQubit]):
        """Initializer. <add details here>

        Args:
            control_qubits (List[LineQubit]): A list of control qubits.
            target_qubit (List[LineQubit]): A list containing the target qubit. It is often the phase qubit.
            ancilla_qubits (List[LineQubit]): A list of the ancilla qubits.
        """
        super(MultiCZ, self).__init__()
        self.__ctl_q = control_qubits
        self.__tgt_q = target_qubit
        self.__anc_q = ancilla_qubits
        
        self.allQ = [*self.__anc_q, *self.__ctl_q, *self.__tgt_q]
        self.total_decomp = 2
    
    def __str__(self) -> str:
        qStr = ",".join([str(x) for x in self.allQ])
        return "MultiCZ ({})".format(qStr)
        
    def _qasm_(self, args: 'cirq.QasmArgs', qubits: Tuple['cirq.Qid', ...]) -> Optional[str]:
        args.validate_version('2.0')
        args.validate_version('2.0')
        allQStr = ",".join([args.format(str(x)) for x in self.allQ])
        return f"MultiCZ({allQStr})\n"
    
    def _num_qubits_(self,):
        return len(self.__ctl_q) + len(self.__tgt_q) + len(self.__anc_q)
    
    def _circuit_diagram_info_(self,args):
        return ["MultiCZ"] * self.num_qubits()
    
    def _decompose_(self, qubits):
        """
        A function inherited from cirq.Gate that tells how to decompose this operator

        Parameters:
            qubits: Not used, mandated by cirq.Gate

        Returns:
            _: Yields CCZ and CCX gates
        """
         # Lets start by getting these tuple-maps:
        ctl_list = getLineQubitIndexMap(self.__ctl_q, 'ctl')
        tgt_list = getLineQubitIndexMap(self.__tgt_q, 'tgt')
        anc_list = getLineQubitIndexMap(self.__anc_q, 'anc')
        
        if len(ctl_list) == 2:
            yield(CCZ(self.__ctl_q[0],self.__ctl_q[1],self.__tgt_q[0]))
        else:
            while len(ctl_list) > 2:
                # get two ctl qubits:
                ctl_1 = ctl_list[0]
                ctl_2 = ctl_list[1]
                ctl_list.remove(ctl_1)
                ctl_list.remove(ctl_2)

                # Get the target qubit:
                tgt_1 = anc_list[0]
                anc_list.remove(tgt_1)
                
                # add the most recent target to the end of the control list
                ctl_list.append(tgt_1)

                # Grab the appropriate qubits
                ctl_q_1 = getQubitFromMap(ctl_1, self.__ctl_q, self.__tgt_q, self.__anc_q)
                ctl_q_2 = getQubitFromMap(ctl_2, self.__ctl_q, self.__tgt_q, self.__anc_q)
                tgt_q_1 = getQubitFromMap(tgt_1, self.__ctl_q, self.__tgt_q, self.__anc_q)

                # Send back the ccx gate
                yield(CCX(ctl_q_1, ctl_q_2, tgt_q_1))
                
                if len(ctl_list) == 2 and not anc_list:
                    ctl_q_1 = getQubitFromMap(ctl_list[0], self.__ctl_q, self.__tgt_q, self.__anc_q)
                    ctl_q_2 = getQubitFromMap(ctl_list[1], self.__ctl_q, self.__tgt_q, self.__anc_q)
                    tgt_q_1 = getQubitFromMap(tgt_list[0], self.__ctl_q, self.__tgt_q, self.__anc_q)
                    yield(CCZ(ctl_q_1, ctl_q_2, tgt_q_1))

    def _get_as_circuit(self):
        #Get the operator as a circuit.
        return cirq.Circuit(self.on(*self.allQ))

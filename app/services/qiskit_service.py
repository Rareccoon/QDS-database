import hashlib

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def prepare_signature_metadata(message: str):
    message_digest = hashlib.sha256(
        message.encode("utf-8")
    ).hexdigest()

    binary_digest = bin(
        int(message_digest[:8], 16)
    )[2:].zfill(32)

    bits = binary_digest[:8]

    return {
        "message_digest": message_digest,
        "basis_schedule": bits,
        "expected_bits": bits
    }


def run_signature_protocol(message: str):
    metadata = prepare_signature_metadata(message)

    bits = metadata["expected_bits"]

    simulator = AerSimulator()

    correction_records = []
    receiver_measurements = []

    for trial_no, bit in enumerate(bits, start=1):

        # Three qubits:
        # q0 = input state
        # q1 = entanglement qubit
        # q2 = receiver qubit
        qc = QuantumCircuit(3, 3)

        # Prepare input state
        if bit == "1":
            qc.x(0)

        # Create entangled pair
        qc.h(1)
        qc.cx(1, 2)

        # Bell-state measurement operations
        qc.cx(0, 1)
        qc.h(0)

        # Measure the two classical correction bits
        qc.measure(0, 0)
        qc.measure(1, 1)

        # Apply X correction when m2 = 1
        with qc.if_test((qc.clbits[1], 1)):
            qc.x(2)

        # Apply Z correction when m1 = 1
        with qc.if_test((qc.clbits[0], 1)):
            qc.z(2)

        # Measure the corrected receiver qubit
        qc.measure(2, 2)

        # Execute the circuit
        result = simulator.run(
            qc,
            shots=1
        ).result()

        counts = result.get_counts()

        measured_bits = next(iter(counts))

        # Qiskit displays classical bits in reverse order
        measured_bits = measured_bits[::-1]

        m1 = int(measured_bits[0])
        m2 = int(measured_bits[1])
        receiver_bit = int(measured_bits[2])

        correction_records.append(
            {
                "trial_no": trial_no,
                "qubit_index": 0,
                "m1": m1,
                "m2": m2
            }
        )

        receiver_measurements.append(
            {
                "trial_no": trial_no,
                "expected_bit": int(bit),
                "receiver_bit": receiver_bit
            }
        )

    return {
        "message_digest": metadata["message_digest"],
        "basis_schedule": metadata["basis_schedule"],
        "expected_bits": metadata["expected_bits"],
        "correction_records": correction_records,
        "receiver_measurements": receiver_measurements
    }
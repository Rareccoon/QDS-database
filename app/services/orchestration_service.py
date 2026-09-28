from datetime import datetime, timezone

from app.database.database import SessionLocal
from app.database.models import (
    ProtocolJob,
    CorrectionBit,
    ReceiverMeasurement
)
from app.services.qiskit_service import run_signature_protocol


def run_signature_background(
    job_id: int,
    message: str
):
    db = SessionLocal()

    try:
        job = (
            db.query(ProtocolJob)
            .filter(ProtocolJob.id == job_id)
            .first()
        )

        if not job:
            return

        job.status = "RUNNING"
        db.commit()

        protocol_result = run_signature_protocol(message)

        for record in protocol_result["correction_records"]:
            correction_bit = CorrectionBit(
                signature_id=job.signature_id,
                trial_no=record["trial_no"],
                qubit_index=record["qubit_index"],
                m1=record["m1"],
                m2=record["m2"]
            )

            db.add(correction_bit)

        for measurement in protocol_result["receiver_measurements"]:
            receiver_measurement = ReceiverMeasurement(
                signature_id=job.signature_id,
                trial_no=measurement["trial_no"],
                expected_bit=measurement["expected_bit"],
                receiver_bit=measurement["receiver_bit"]
            )

            db.add(receiver_measurement)

        job.status = "COMPLETED"
        job.completed_at = datetime.now(timezone.utc)

        db.commit()

    except Exception as exc:
        db.rollback()

        job = (
            db.query(ProtocolJob)
            .filter(ProtocolJob.id == job_id)
            .first()
        )

        if job:
            job.status = "FAILED"
            job.error_message = str(exc)
            db.commit()

    finally:
        db.close()
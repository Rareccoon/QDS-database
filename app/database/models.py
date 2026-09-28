from datetime import datetime, timezone
import sqlalchemy

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)

    username = sqlalchemy.Column(
        sqlalchemy.String(50),
        unique=True,
        nullable=False
    )

    password_hash = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False
    )

    role = sqlalchemy.Column(
        sqlalchemy.String(20),
        nullable=False
    )

    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class Session(Base):
    __tablename__ = "sessions"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)

    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    token_id = sqlalchemy.Column(
        sqlalchemy.String(255),
        unique=True,
        nullable=False
    )

    issued_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    expires_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False
    )

    revoked_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True
    )
    
class Signature(Base):
    __tablename__ = "signatures"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)

    signer_user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    sequence_no = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    message_digest = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False
    )

    basis_schedule = sqlalchemy.Column(
        sqlalchemy.String(1000),
        nullable=False
    )

    expected_bits = sqlalchemy.Column(
        sqlalchemy.String(1000),
        nullable=False
    )

    correction_bits = sqlalchemy.Column(
        sqlalchemy.String(100),
        nullable=False
    )

    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
class Verification(Base):
    __tablename__ = "verifications"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)

    signature_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    verifier_user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    observed_qber = sqlalchemy.Column(
        sqlalchemy.String(50),
        nullable=False
    )

    m_trials = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    k_mismatches = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    hoeffding_bound = sqlalchemy.Column(
        sqlalchemy.String(50),
        nullable=False
    )

    threshold_used = sqlalchemy.Column(
        sqlalchemy.String(50),
        nullable=False
    )

    verdict = sqlalchemy.Column(
        sqlalchemy.String(20),
        nullable=False
    )

    verified_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

class CorrectionBit(Base):
    __tablename__ = "correction_bits"

    __table_args__ = (
        sqlalchemy.UniqueConstraint(
            "signature_id",
            "trial_no",
            "qubit_index",
            name="uq_correction_bit_trial"
        ),
    )

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        index=True
    )

    signature_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    trial_no = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    qubit_index = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    m1 = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    m2 = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    logged_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
class QKDSession(Base):
    __tablename__ = "qkd_sessions"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)

    initiator_user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    receiver_user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    basis_log = sqlalchemy.Column(
        sqlalchemy.String(5000),
        nullable=False
    )

    estimated_qber = sqlalchemy.Column(
        sqlalchemy.String(50),
        nullable=False
    )

    accepted = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable=False
    )

    timestamp = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
class ReceiverMeasurement(Base):
    __tablename__ = "receiver_measurements"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        index=True
    )

    signature_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    trial_no = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    expected_bit = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    receiver_bit = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )

    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
class AttackEvent(Base):
    __tablename__ = "attack_events"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        index=True
    )

    module2_scenario = sqlalchemy.Column(
        sqlalchemy.String(100),
        nullable=False
    )

    target_signature_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=True
    )

    injected_by = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=True
    )

    detected = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable=False,
        default=False
    )

    notes = sqlalchemy.Column(
        sqlalchemy.String(1000),
        nullable=True
    )

    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
class ProtocolJob(Base):
    __tablename__ = "protocol_jobs"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    signature_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String(20), nullable=False, default="PENDING")
    error_message = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    completed_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True)
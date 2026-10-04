from dotenv import load_dotenv
load_dotenv()

"""Sanad data layer — MySQL (Aiven) via SQLAlchemy. Tenant-scoped, hash-chained audit."""
import hashlib, json, os, uuid
from contextlib import contextmanager
from datetime import datetime
import structlog
from sqlalchemy import (create_engine, Column, String, Integer, BigInteger, Text, DateTime,
                        Numeric, JSON, ForeignKey, UniqueConstraint, Index, select, func)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

log = structlog.get_logger("sanad.db")
Base = declarative_base()

def _engine():
    from pathlib import Path
    url = os.environ["DATABASE_URL"]
    ca = os.environ.get("SANAD_SSL_CA", "C:/Users/DELL-PC/Downloads/ca.pem")
    if not Path(ca).exists():
        raise SystemExit(f"✖ CA certificate not found at: {ca}  (set SANAD_SSL_CA in .env)")
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
                connect_args={"ssl_ca": ca, "ssl_verify_cert": True},
    )

ENGINE = _engine()
Session = sessionmaker(bind=ENGINE, expire_on_commit=False)

def new_id(): return str(uuid.uuid4())

# ---------------- Models ----------------
class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String(36), primary_key=True); name = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True); tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    email = Column(String(190), nullable=False); password_hash = Column(String(255), nullable=False)
    role = Column(String(24), nullable=False); created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_email"),)

class Business(Base):
    __tablename__ = "businesses"
    id = Column(String(36), primary_key=True); tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(160), nullable=False); sector = Column(String(160)); cr_number = Column(String(60))
    status = Column(String(20), nullable=False, default="prospect"); data_quality = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow); created_by = Column(String(36))

class Session_(Base):
    __tablename__ = "sessions"
    id = Column(String(36), primary_key=True); business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    status = Column(String(16), default="open"); current_evaluation_id = Column(String(36))
    created_at = Column(DateTime, default=datetime.utcnow); updated_at = Column(DateTime, default=datetime.utcnow)

class Source(Base):
    __tablename__ = "sources"
    id = Column(String(36), primary_key=True); session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    filename = Column(String(255), nullable=False); kind = Column(String(32), nullable=False)
    storage_key = Column(String(500), nullable=False); sha256 = Column(String(64), nullable=False)
    size_bytes = Column(Integer, nullable=False); ocr_status = Column(String(16), default="none")
    ocr_confidence = Column(Numeric(5, 4)); table_count = Column(Integer, default=0)
    soft_deleted = Column(Integer, default=0); legal_hold = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow); uploaded_by = Column(String(36)); superseded_by = Column(String(36))

class SourceExtract(Base):
    __tablename__ = "source_extracts"
    id = Column(String(36), primary_key=True); source_id = Column(String(36), ForeignKey("sources.id"), nullable=False)
    page = Column(Integer); region = Column(String(120)); extract_type = Column(String(16), nullable=False)
    content_json = Column(JSON, nullable=False); confidence = Column(Numeric(5, 4))
    review_state = Column(String(16), default="auto"); reviewed_by = Column(String(36)); reviewed_at = Column(DateTime)

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(String(36), primary_key=True); session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    version = Column(Integer, nullable=False); score = Column(Integer)
    score_explain_json = Column(JSON); data_quality_json = Column(JSON); parent_evaluation_id = Column(String(36))
    soft_deleted = Column(Integer, default=0); legal_hold = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("session_id", "version", name="uq_eval_version"),)

class MemoSection(Base):
    __tablename__ = "memo_sections"
    id = Column(String(36), primary_key=True); evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False)
    ordinal = Column(Integer, nullable=False); title = Column(String(160), nullable=False)
    body_text = Column(Text); generated_mode = Column(String(16))

class Citation(Base):
    __tablename__ = "citations"
    id = Column(String(36), primary_key=True); memo_section_id = Column(String(36), ForeignKey("memo_sections.id"), nullable=False)
    source_extract_id = Column(String(36), ForeignKey("source_extracts.id"), nullable=False); anchor_text = Column(String(500))

class ComputedMetric(Base):
    __tablename__ = "computed_metrics"
    id = Column(String(36), primary_key=True); evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False)
    metric_key = Column(String(60), nullable=False); value = Column(Numeric(18, 4))
    formula_version = Column(String(20), nullable=False); input_extract_ids_json = Column(JSON)

class Flag(Base):
    __tablename__ = "flags"
    id = Column(String(36), primary_key=True); evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False)
    rule_id = Column(String(40), nullable=False); severity = Column(String(12), nullable=False)
    finding = Column(Text); evidence_extract_id = Column(String(36)); recommendation = Column(Text)

class ScuDecision(Base):
    __tablename__ = "scu_decisions"
    id = Column(String(36), primary_key=True); flag_id = Column(String(36), ForeignKey("flags.id"), nullable=False)
    decision = Column(String(16), nullable=False); note = Column(Text)
    decided_by = Column(String(36)); decided_at = Column(DateTime, default=datetime.utcnow)

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(String(36), primary_key=True); evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False)
    role = Column(String(24), nullable=False); user_id = Column(String(36)); approved_at = Column(DateTime, default=datetime.utcnow)

class Export(Base):
    __tablename__ = "exports"
    id = Column(String(36), primary_key=True); evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False)
    storage_key = Column(String(500), nullable=False); content_sha256 = Column(String(64), nullable=False)
    format = Column(String(12), nullable=False); exported_at = Column(DateTime, default=datetime.utcnow); exported_by = Column(String(36))

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(BigInteger, primary_key=True, autoincrement=True); tenant_id = Column(String(36), nullable=False)
    user_id = Column(String(36)); action = Column(String(40), nullable=False)
    target_type = Column(String(32)); target_id = Column(String(36)); detail_json = Column(JSON)
    prev_hash = Column(String(16), nullable=False); hash = Column(String(16), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow)

class LlmCall(Base):
    __tablename__ = "llm_calls"
    id = Column(String(36), primary_key=True); evaluation_id = Column(String(36))
    purpose = Column(String(40), nullable=False); model = Column(String(80)); prompt_sha256 = Column(String(64))
    output_text = Column(Text); citations_json = Column(JSON); guardrail_result = Column(String(24))
    latency_ms = Column(Integer); created_at = Column(DateTime, default=datetime.utcnow)

# ---------------- Helpers ----------------
@contextmanager
def tx():
    s = Session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback(); raise
    finally:
        s.close()

def _chain_hash(prev: str, payload: str) -> str:
    return hashlib.sha256((prev + payload).encode()).hexdigest()[:16]

def last_audit_hash(s, tenant_id: str) -> str:
    row = s.execute(select(AuditEvent.hash).where(AuditEvent.tenant_id == tenant_id)
                    .order_by(AuditEvent.id.desc()).limit(1)).scalar()
    return row or ("0" * 16)

def audit(s, tenant_id: str, user_id, action: str, target_type=None, target_id=None, detail=None):
    payload = json.dumps(dict(tenant_id=tenant_id, user_id=user_id, action=action,
                              target_type=target_type, target_id=target_id, detail=detail,
                              ts=datetime.utcnow().isoformat()), sort_keys=True)
    prev = last_audit_hash(s, tenant_id)
    h = _chain_hash(prev, payload)
    s.add(AuditEvent(tenant_id=tenant_id, user_id=user_id, action=action,
                     target_type=target_type, target_id=target_id, detail_json=detail,
                     prev_hash=prev, hash=h))
    log.info("audit", action=action, target_type=target_type, target_id=target_id)
    return h

def init_schema():
    Base.metadata.create_all(ENGINE)   # creates any missing tables (idempotent)

if __name__ == "__main__":
    init_schema()
    print("✔ schema ensured on", os.environ.get("DATABASE_URL", "?").split("@")[-1])
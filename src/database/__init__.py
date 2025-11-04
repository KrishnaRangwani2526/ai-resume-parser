# app/db.py
import os
import json
from datetime import datetime, date
from typing import Optional, Dict, Any, List

import sqlalchemy as sa
from sqlalchemy import Column, String, Integer, Boolean, Date, Text, DateTime, DECIMAL, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/resume_db")

Base = declarative_base()

def _server_gen_uuid():
    # server_default expecting gen_random_uuid() in Postgres (pgcrypto) or uuid_generate_v4()
    return sa.text("gen_random_uuid()")

# ---------------------------
# ORM models (matches your schema)
# ---------------------------

class Resume(Base):
    _tablename_ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=_server_gen_uuid())
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    file_hash = Column(String(128), unique=True, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_status = Column(String(50), default="pending")
    raw_text = Column(Text)
    structured_data = Column(JSONB)
    ai_enhancements = Column(JSONB)
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    person_info = relationship("PersonInfo", back_populates="resume", cascade="all, delete-orphan")
    work_experiences = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    education_items = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    ai_analysis = relationship("AIAnalysis", back_populates="resume", cascade="all, delete-orphan")
    job_matches = relationship("ResumeJobMatch", back_populates="resume", cascade="all, delete-orphan")


class PersonInfo(Base):
    _tablename_ = "person_info"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=_server_gen_uuid())
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(JSONB)
    social_links = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="person_info")


class WorkExperience(Base):
    _tablename_ = "work_experience"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=_server_gen_uuid())
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    location = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    achievements = Column(ARRAY(Text))
    technologies = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="work_experiences")


class Education(Base):
    _tablename_ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=_server_gen_uuid())
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(255))
    field_of_study = Column(String(255))
    institution = Column(String(255))
    location = Column(String(255))
    graduation_date = Column(Date)
    gpa = Column(DECIMAL(3, 2))
    honors = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="education_items")


class Skill(Base):
    _tablename_ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=_server_gen_uuid())
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(255), nullable=False)
    skill_category = Column(String(100))
    proficiency_level = Column(String(50))
    years_of_experience = Column(Integer)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="skills")


class AIAnalysis(Base):
    _tablename_ = "ai_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=_server_gen_uuid())
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    quality_score = Column(Integer)
    completeness_score = Column(Integer)
    industry_classifications = Column(JSONB)
    career_level = Column(String(50))
    salary_estimate = Column(JSONB)
    suggestions = Column(ARRAY(Text))
    confidence_scores = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="ai_analysis")


class ResumeJobMatch(Base):
    _tablename_ = "resume_job_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=_server_gen_uuid())
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255))
    job_description = Column(Text, nullable=False)
    job_requirements = Column(JSONB)
    overall_score = Column(Integer)
    confidence_score = Column(DECIMAL(3, 2))
    recommendation = Column(String(50))
    category_scores = Column(JSONB)
    strength_areas = Column(ARRAY(Text))
    gap_analysis = Column(JSONB)
    salary_alignment = Column(JSONB)
    competitive_advantages = Column(ARRAY(Text))
    explanation = Column(JSONB)
    processing_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="job_matches")

# ---------------------------
# Engine & Session
# ---------------------------

def get_engine() -> Engine:
    # For local dev with sqlite fallback you could change this, but schema uses PG types
    engine = sa.create_engine(DATABASE_URL, future=True)
    return engine

engine = get_engine()
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


def init_db():
    """
    Create all tables. Ensure pgcrypto (or uuid-ossp) installed for gen_random_uuid().
    For production migrations use Alembic instead.
    """
    Base.metadata.create_all(bind=engine)


# ---------------------------
# Helper CRUD / convenience functions
# ---------------------------

def create_resume_record(file_name: str, file_size: int, file_type: str, file_hash: str,
                         raw_text: Optional[str] = None,
                         structured_data: Optional[Dict[str, Any]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
    session = SessionLocal()
    try:
        r = Resume(
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            file_hash=file_hash,
            raw_text=raw_text,
            structured_data=structured_data or {},
            metadata=metadata or {},
            processing_status="processed" if structured_data else "pending",
            processed_at=datetime.utcnow() if structured_data else None
        )
        session.add(r)
        session.commit()
        session.refresh(r)
        return str(r.id)
    except IntegrityError as e:
        session.rollback()
        raise
    finally:
        session.close()


def attach_person_info(resume_id: str, person: Dict[str, Any]):
    session = SessionLocal()
    try:
        pi = PersonInfo(
            resume_id=resume_id,
            full_name=person.get("full_name"),
            first_name=person.get("first_name"),
            last_name=person.get("last_name"),
            email=person.get("email"),
            phone=person.get("phone"),
            address=person.get("address"),
            social_links=person.get("social_links")
        )
        session.add(pi)
        session.commit()
        session.refresh(pi)
        return str(pi.id)
    finally:
        session.close()


def attach_work_experiences(resume_id: str, experiences: List[Dict[str, Any]]):
    session = SessionLocal()
    created_ids = []
    try:
        for ex in experiences:
            start_date = ex.get("start_date")
            end_date = ex.get("end_date")
            # accept strings for dates, convert if necessary
            if isinstance(start_date, str):
                try:
                    start_date = date.fromisoformat(start_date)
                except Exception:
                    start_date = None
            if isinstance(end_date, str):
                try:
                    end_date = date.fromisoformat(end_date)
                except Exception:
                    end_date = None

            we = WorkExperience(
                resume_id=resume_id,
                job_title=ex.get("job_title") or ex.get("title") or "Unknown",
                company_name=ex.get("company_name") or ex.get("company") or "Unknown",
                location=ex.get("location"),
                start_date=start_date,
                end_date=end_date,
                is_current=ex.get("is_current", False),
                description=ex.get("description"),
                achievements=ex.get("achievements"),
                technologies=ex.get("technologies")
            )
            session.add(we)
            session.flush()
            created_ids.append(str(we.id))
        session.commit()
        return created_ids
    finally:
        session.close()


def attach_education(resume_id: str, education_list: List[Dict[str, Any]]):
    session = SessionLocal()
    created_ids = []
    try:
        for ed in education_list:
            gd = ed.get("graduation_date")
            if isinstance(gd, str):
                try:
                    gd = date.fromisoformat(gd)
                except Exception:
                    gd = None
            e = Education(
                resume_id=resume_id,
                degree=ed.get("degree"),
                field_of_study=ed.get("field_of_study"),
                institution=ed.get("institution"),
                location=ed.get("location"),
                graduation_date=gd,
                gpa=ed.get("gpa"),
                honors=ed.get("honors")
            )
            session.add(e)
            session.flush()
            created_ids.append(str(e.id))
        session.commit()
        return created_ids
    finally:
        session.close()


def attach_skills(resume_id: str, skills: List[Dict[str, Any]]):
    session = SessionLocal()
    created_ids = []
    try:
        for sk in skills:
            s = Skill(
                resume_id=resume_id,
                skill_name=sk.get("skill_name"),
                skill_category=sk.get("skill_category"),
                proficiency_level=sk.get("proficiency_level"),
                years_of_experience=sk.get("years_of_experience"),
                is_primary=sk.get("is_primary", False)
            )
            session.add(s)
            session.flush()
            created_ids.append(str(s.id))
        session.commit()
        return created_ids
    finally:
        session.close()


def add_ai_analysis(resume_id: str, analysis: Dict[str, Any]):
    session = SessionLocal()
    try:
        a = AIAnalysis(
            resume_id=resume_id,
            quality_score=analysis.get("quality_score"),
            completeness_score=analysis.get("completeness_score"),
            industry_classifications=analysis.get("industry_classifications"),
            career_level=analysis.get("career_level"),
            salary_estimate=analysis.get("salary_estimate"),
            suggestions=analysis.get("suggestions"),
            confidence_scores=analysis.get("confidence_scores")
        )
        session.add(a)
        session.commit()
        session.refresh(a)
        return str(a.id)
    finally:
        session.close()


def add_resume_job_match(resume_id: str, match: Dict[str, Any]):
    session = SessionLocal()
    try:
        m = ResumeJobMatch(
            resume_id=resume_id,
            job_title=match["job_title"],
            company_name=match.get("company_name"),
            job_description=match["job_description"],
            job_requirements=match.get("job_requirements"),
            overall_score=match.get("overall_score"),
            confidence_score=match.get("confidence_score"),
            recommendation=match.get("recommendation"),
            category_scores=match.get("category_scores"),
            strength_areas=match.get("strength_areas"),
            gap_analysis=match.get("gap_analysis"),
            salary_alignment=match.get("salary_alignment"),
            competitive_advantages=match.get("competitive_advantages"),
            explanation=match.get("explanation"),
            processing_metadata=match.get("processing_metadata")
        )
        session.add(m)
        session.commit()
        session.refresh(m)
        return str(m.id)
    finally:
        session.close()


def get_resume_by_id(resume_id: str) -> Optional[Dict[str, Any]]:
    session = SessionLocal()
    try:
        r = session.query(Resume).filter(Resume.id == resume_id).first()
        if not r:
            return None
        return {
            "id": str(r.id),
            "file_name": r.file_name,
            "file_size": r.file_size,
            "file_type": r.file_type,
            "file_hash": r.file_hash,
            "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
            "processed_at": r.processed_at.isoformat() if r.processed_at else None,
            "processing_status": r.processing_status,
            "raw_text": r.raw_text,
            "structured_data": r.structured_data,
            "ai_enhancements": r.ai_enhancements,
            "metadata": r.metadata
        }
    finally:
        session.close()


def search_resumes_by_keyword(keyword: str, limit: int = 25) -> List[Dict[str, Any]]:
    session = SessionLocal()
    try:
        q = session.query(Resume).filter(Resume.raw_text.ilike(f"%{keyword}%")).limit(limit).all()
        return [{"id": str(r.id), "file_name": r.file_name} for r in q]
    finally:
        session.close()
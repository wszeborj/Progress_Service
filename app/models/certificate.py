"""Model for course certificates earned by users."""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, func, Float, Text, Index

from ..db.base import Base


class CourseCertificate(Base):
    __tablename__ = "course_certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    certificate_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    final_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


    grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    completion_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    digital_signature: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index('idx_user_course_cert', 'user_id', 'course_id', unique=True),
    )


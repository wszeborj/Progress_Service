import strawberry
from datetime import datetime
from typing import Optional

from ...models.certificate import CourseCertificate as CourseCertificateModel


@strawberry.type
class CourseCertificate:
    id: int
    certificate_id: str
    user_id: int
    course_id: int
    earned_at: datetime
    expires_at: Optional[datetime]
    final_score: Optional[float]
    grade: Optional[str]
    completion_time: float
    digital_signature: str
    pdf_url: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model: CourseCertificateModel) -> "CourseCertificate":
        return cls(
            id=model.id,
            certificate_id=model.certificate_id,
            user_id=model.user_id,
            course_id=model.course_id,
            earned_at=model.earned_at,
            expires_at=model.expires_at,
            final_score=model.final_score,
            grade=model.grade,
            completion_time=model.completion_time,
            digital_signature=model.digital_signature,
            pdf_url=model.pdf_url,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


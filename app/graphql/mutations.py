import strawberry
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import select, func, and_

from ..models.progress import Progress as ProgressModel
from ..models.progress import ProgressStatus as ProgressStatusEnum
from ..models.achievement import Achievement as AchievementModel
from ..models.certificate import CourseCertificate as CertificateModel
from ..graphql.types.progress import Progress, ProgressStatus
from ..graphql.types.achievement import Achievement
from ..graphql.types.certificate import CourseCertificate


@strawberry.input
class UpdateProgressInput:
    course_id: int
    status: Optional[ProgressStatus] = None
    completion_percentage: Optional[float] = None
    time_spent_seconds: Optional[int] = None
    notes: Optional[str] = None


@strawberry.input
class CreateAchievementInput:
    achievement_type: str
    achievement_name: str
    description: Optional[str] = None


@strawberry.input
class CreateCertificateInput:
    course_id: int
    final_score: Optional[float] = None
    grade: Optional[str] = None
    completion_time: Optional[float] = None
    expires_at: Optional[datetime] = None
    pdf_url: Optional[str] = None
    notes: Optional[str] = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def update_user_progress(
            self,
            user_id: int,
            input: UpdateProgressInput,
            info: strawberry.Info
    ) -> Progress:
        db_session: AsyncSession = info.context["db_session"]

        # Check if progress exists
        stmt = select(ProgressModel).where(
            and_(
                ProgressModel.user_id == user_id,
                ProgressModel.course_id == input.course_id
            )
        )
        result = await db_session.execute(stmt)
        existing_progress = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if existing_progress:
            # Update existing progress
            if input.status:
                existing_progress.status = ProgressStatusEnum(input.status.value)
                if input.status == ProgressStatus.COMPLETED:
                    existing_progress.completed_at = now
                    existing_progress.completion_percentage = 100.0
                elif existing_progress.status == ProgressStatusEnum.NOT_STARTED and input.status != ProgressStatus.NOT_STARTED:
                    existing_progress.started_at = existing_progress.started_at or now

            if input.completion_percentage is not None:
                existing_progress.completion_percentage = input.completion_percentage

            if input.time_spent_seconds is not None:
                existing_progress.total_time_spent += input.time_spent_seconds

            if input.notes is not None:
                existing_progress.notes = input.notes

            existing_progress.last_accessed_at = now
            await db_session.commit()
            await db_session.refresh(existing_progress)
            return Progress.from_model(existing_progress)
        else:
            # Create new progress
            status = ProgressStatusEnum.NOT_STARTED
            if input.status:
                status = ProgressStatusEnum(input.status.value)

            started_at = None
            if status != ProgressStatusEnum.NOT_STARTED:
                started_at = now

            completed_at = None
            completion_percentage = input.completion_percentage or 0.0
            if status == ProgressStatusEnum.COMPLETED:
                completed_at = now
                completion_percentage = 100.0

            new_progress = ProgressModel(
                user_id=user_id,
                course_id=input.course_id,
                status=status,
                started_at=started_at,
                completed_at=completed_at,
                last_accessed_at=now,
                completion_percentage=completion_percentage,
                total_time_spent=input.time_spent_seconds or 0,
                notes=input.notes,
            )
            db_session.add(new_progress)
            await db_session.commit()
            await db_session.refresh(new_progress)
            return Progress.from_model(new_progress)

    @strawberry.mutation
    async def create_achievement(
            self,
            user_id: int,
            input: CreateAchievementInput,
            info: strawberry.Info
    ) -> Achievement:
        db_session: AsyncSession = info.context["db_session"]

        achievement = AchievementModel(
            user_id=user_id,
            achievement_type=input.achievement_type,
            achievement_name=input.achievement_name,
            description=input.description,
        )
        db_session.add(achievement)
        await db_session.commit()
        await db_session.refresh(achievement)
        return Achievement.from_model(achievement)

    @strawberry.mutation
    async def create_certificate(
            self,
            user_id: int,
            input: CreateCertificateInput,
            info: strawberry.Info
    ) -> CourseCertificate:
        db_session: AsyncSession = info.context["db_session"]

        # Check if certificate already exists
        stmt = select(CertificateModel).where(
            and_(
                CertificateModel.user_id == user_id,
                CertificateModel.course_id == input.course_id
            )
        )
        result = await db_session.execute(stmt)
        existing_cert = result.scalar_one_or_none()

        if existing_cert:
            return CourseCertificate.from_model(existing_cert)

        # Get progress to calculate completion time
        progress_stmt = select(ProgressModel).where(
            and_(
                ProgressModel.user_id == user_id,
                ProgressModel.course_id == input.course_id
            )
        )
        progress_result = await db_session.execute(progress_stmt)
        progress = progress_result.scalar_one_or_none()

        completion_time = input.completion_time
        if completion_time is None and progress:
            # Convert seconds to hours
            completion_time = progress.total_time_spent / 3600.0

        certificate = CertificateModel(
            user_id=user_id,
            course_id=input.course_id,
            final_score=input.final_score,
            grade=input.grade,
            completion_time=completion_time or 0.0,
            expires_at=input.expires_at,
            pdf_url=input.pdf_url,
            notes=input.notes,
        )
        db_session.add(certificate)
        await db_session.commit()
        await db_session.refresh(certificate)
        return CourseCertificate.from_model(certificate)

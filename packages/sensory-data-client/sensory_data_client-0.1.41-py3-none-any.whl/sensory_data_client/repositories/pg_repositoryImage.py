# src/sensory_data_client/repositories/pg_repositoryImage.py

import logging
from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlalchemy import update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from sensory_data_client.db.documentImage_orm import DocumentImageORM
from sensory_data_client.db.base import get_session
from sensory_data_client.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class ImageRepository:
    """
    Репозиторий для управления жизненным циклом записей об изображениях (DocumentImageORM).
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def claim_task(self, image_id: UUID) -> Optional[DocumentImageORM]:
        """
        Атомарно "захватывает" задачу на обработку.
        
        Находит задачу в статусе 'pending' или 'enqueued', переводит ее в 'processing'
        и возвращает ORM-объект. Если задача уже захвачена или обработана,
        возвращает None. Это предотвращает гонку состояний между воркерами.
        """
        async for session in get_session(self._session_factory):
            try:
                stmt = (
                    update(DocumentImageORM)
                    .where(
                        DocumentImageORM.id == image_id,
                        DocumentImageORM.status.in_(('pending', 'enqueued'))
                    )
                    .values(
                        status='processing',
                        attempts=DocumentImageORM.attempts + 1,
                        updated_at=datetime.utcnow()
                    )
                    .returning(DocumentImageORM)
                )
                result = await session.execute(stmt)
                await session.commit()
                # .scalar_one_or_none() важен для получения одного объекта или None
                return result.scalar_one_or_none()
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Failed to claim image task {image_id}: {e}")
                raise DatabaseError(f"Failed to claim image task {image_id}: {e}") from e

    async def update_task_status(
        self,
        image_id: UUID,
        status: str,
        result_text: Optional[str] = None,
        last_error: Optional[str] = None,
        llm_model: Optional[str] = None,
    ):
        """
        Универсальный метод для обновления статуса и связанных полей задачи.
        """
        values_to_update = {"status": status, "updated_at": datetime.utcnow()}
        if result_text is not None:
            values_to_update["result_text"] = result_text
        if last_error is not None:
            values_to_update["last_error"] = last_error
        if llm_model is not None:
            values_to_update["llm_model"] = llm_model
        if status == 'done':
            values_to_update["processed_at"] = datetime.utcnow()

        async for session in get_session(self._session_factory):
            try:
                stmt = update(DocumentImageORM).where(DocumentImageORM.id == image_id).values(**values_to_update)
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Failed to update status for image task {image_id}: {e}")
                raise DatabaseError(f"Failed to update status for image task {image_id}: {e}") from e
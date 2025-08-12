from fastapi import Request
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import text
from typing import AsyncGenerator
from typing import Generator
from typing import Callable
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


def get_bd_session_factory(SessionLocal) -> Callable[..., Generator[Session, None, None]]:
    """
    Factoría de alto nivel. Recibe un SessionLocal síncrono y retorna
    una única dependencia 'get_db' configurable.
    """

    def get_db(request: Request, public_access: bool = False) -> Generator[Session, None, None]:
        tenant_id = getattr(request.state, "tenant_id", None)

        if not tenant_id:
            if not public_access:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Header de tenant requerido.")
            else:
                search_path = "public"
        else:
            search_path = f'"{tenant_id}", public'

        db = SessionLocal()
        try:
            db.execute(text(f'SET search_path TO {search_path}'))
            yield db
        finally:
            db.close()

    return get_db


def get_bd_async_session_factory(db_manager) -> Callable[..., AsyncGenerator[AsyncSession, None]]:
    """
    Factoría de alto nivel. Recibe un db_manager asíncrono y retorna
    una única dependencia 'get_db' configurable.
    """

    async def get_db(request: Request, public_access: bool = False) -> AsyncGenerator[AsyncSession, None]:
        tenant_id = getattr(request.state, "tenant_id", None)

        if not tenant_id:
            if not public_access:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Header de tenant requerido.")
            else:
                search_path = "public"
        else:
            search_path = f'"{tenant_id}", public'

        async for session in db_manager.get_session():
            try:
                await session.execute(text(f'SET search_path TO {search_path}'))
                yield session
            except Exception:
                raise

    return get_db

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


def create_tenant_middleware(header_name: str = "X-Tenant"):
    """
    Factoría que crea y retorna una clase de Middleware configurada.

    Args:
        header_name (str): Nombre de la cabecera HTTP para el tenant.

    Returns:
        Una clase de Middleware lista para ser usada por FastAPI.
    """

    class TenantMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
            tenant_id = request.headers.get(header_name.lower())
            request.state.tenant_id = tenant_id if tenant_id else None
            response = await call_next(request)
            return response

    return TenantMiddleware

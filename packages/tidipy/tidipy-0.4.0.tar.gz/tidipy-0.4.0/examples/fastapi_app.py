from uuid import uuid4

from fastapi import FastAPI, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from tidipy import get_resolver, ensure_scope, clear_scope, auto_compose


def di(dependency_type):
    def dependency(request: Request):
        return request.state.resolve(dependency_type)
    return Depends(dependency)


class RequestScopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        ensure_scope(request_id, scope_type='request')
        request.state.resolve = get_resolver(request_id)
        try:
            return await call_next(request)
        finally:
            clear_scope(request_id)


class NameSayer:
    def my_name(self) -> str:
        return 'TiDIpy'


auto_compose(NameSayer, scope_type='request')


app = FastAPI()
app.add_middleware(RequestScopeMiddleware)


@app.get('/say-my-name')
def add_to_basket(name_sayer: NameSayer = di(NameSayer)):
    return name_sayer.my_name()

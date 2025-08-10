from abc import ABC, abstractmethod
from typing import Type
from uuid import uuid4

from fastapi import FastAPI
from starlette.requests import Request

from tidipy import get_resolver, ensure_scope, clear_scope, auto_compose


class NameSayer:
    def my_name(self) -> str:
        return 'TiDIpy'


class Controller(ABC):
    @abstractmethod
    def handle(self):
        ...


class MyController(Controller):
    def __init__(self, name_sayer: NameSayer):
        self._name_sayer = name_sayer

    def handle(self):
        return self._name_sayer.my_name()


auto_compose(NameSayer, scope_type='request')
auto_compose(MyController, scope_type='request')


class FastApiAdapter:
    def __init__(self, controller_type: Type[Controller]):
        self._controller_type = controller_type

    def handle(self, request: Request):
        return request.state.resolve(self._controller_type).handle()


app = FastAPI()


@app.middleware("http")
async def add_request_scope(request: Request, call_next):
    request_id = str(uuid4())
    ensure_scope(request_id, scope_type='request')
    request.state.resolve = get_resolver(request_id)
    try:
        return await call_next(request)
    finally:
        clear_scope(request_id)

app.add_api_route(
    path='/say-my-name',
    methods=['GET'],
    endpoint=FastApiAdapter(MyController).handle
)

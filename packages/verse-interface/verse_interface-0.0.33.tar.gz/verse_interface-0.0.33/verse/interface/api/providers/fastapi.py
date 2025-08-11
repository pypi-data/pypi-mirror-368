from __future__ import annotations

__all__ = ["FastAPI"]

import asyncio
import inspect
from typing import Any, Callable

import uvicorn
from fastapi import APIRouter, Body, Depends
from fastapi import FastAPI as BaseFastAPI
from fastapi import Header, HTTPException, Path, Query, Security
from fastapi.security import HTTPBasic, HTTPBearer
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from pydantic import BaseModel, create_model
from starlette.middleware.cors import CORSMiddleware

from verse.core import (
    Context,
    DataAccessor,
    DataModel,
    Operation,
    OperationParser,
    Provider,
    Response,
    TypeConverter,
)
from verse.core.exceptions import BaseError
from verse.core.spec import ComponentSpec, SpecBuilder

from .._helper import OperationInfo, get_operations
from .._models import (
    APIAuth,
    APIAuthType,
    APIInfo,
    ArgSourceType,
    ComponentMapping,
    OperationMapping,
)
from .._operation import APIOperation

app = None


class FastAPI(Provider):
    host: str | None
    port: int | None
    reload: bool
    workers: int
    root_path: str | None
    openapi_url: str | None
    cors_origins: str | list[str] | None
    cors_methods: str | list[str] | None
    cors_headers: str | list[str] | None
    cors_credentials: bool | None
    nparams: dict[str, Any]

    _app: BaseFastAPI

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        reload: bool = False,
        workers: int = 1,
        root_path: str | None = None,
        openapi_url: str | None = "/openapi.json",
        cors_origins: str | list[str] | None = None,
        cors_methods: str | list[str] | None = "*",
        cors_headers: str | list[str] | None = "*",
        cors_credentials: bool | None = True,
        nparams: dict[str, Any] = dict(),
        **kwargs,
    ):
        """Initialize.

        Args:
            host:
                Host IP address.
            port:
                HTTP port.
            reload:
                A value indicating whether the app should be reloaded
                when any files are modified.
            workers:
                Number of uvicorn worker processes.
            root_path:
                Root path for the app.
            openapi_url:
                OpenAPI URL for the app.
            cors_origins:
                Allowed origins for CORS.
                If None, CORS middleware is not enabled.
            cors_methods:
                Allowed methods for CORS.
                Defaults to *.
            cors_headers:
                Allowed headers for CORS.
                Defaults to *.
            cors_credentials:
                A value indicating whether credentials
                are allowed for CORS. Defaults to true.
            nparams:
                Native parameters to FastAPI and uvicorn client.
        """
        self.host = host
        self.port = port
        self.reload = reload
        self.workers = workers
        self.root_path = root_path
        self.openapi_url = openapi_url
        self.cors_origins = cors_origins
        self.cors_methods = cors_methods
        self.cors_headers = cors_headers
        self.cors_credentials = cors_credentials
        self.nparams = nparams
        self._app = BaseFastAPI(
            root_path=self.root_path or "",
            openapi_url=self.openapi_url,
            **self.nparams,
        )

    def __run__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        return self._run_internal(
            generic_api_type=GenericAPI,
            operation=operation,
            context=context,
        )

    async def __arun__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        return self._run_internal(
            generic_api_type=GenericAsyncAPI,
            operation=operation,
            context=context,
        )

    def _run_internal(
        self,
        generic_api_type: Any,
        operation: Operation | None = None,
        context: Context | None = None,
    ) -> Any:
        result = None
        op_parser = OperationParser(operation)
        if op_parser.op_equals(APIOperation.GET_INFO):
            result = self._get_info()
            return Response(result=result)
        else:
            component_mappings: list[ComponentMapping] = (
                self.__component__.components
            )
            api_router = APIRouter()
            for component_mapping in component_mappings:
                api = generic_api_type(
                    component_mapping, self.__component__.auth
                )
                tags: Any = component_mapping.tags or []
                if isinstance(tags, str):
                    tags = [tags]
                api_router.include_router(
                    api.router,
                    prefix=component_mapping.prefix or "",
                    tags=tags,
                )
            self._app.include_router(
                api_router, prefix=self.__component__.prefix or ""
            )
            server = self._get_server()
            try:
                asyncio.run(server.serve())
            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:
                pass
        return Response(result=result)

    def _get_server(self) -> uvicorn.Server:
        if self.cors_origins:
            allow_origins = (
                [self.cors_origins]
                if isinstance(self.cors_origins, str)
                else self.cors_origins
            )
            allow_methods = (
                [self.cors_methods]
                if isinstance(self.cors_methods, str)
                else self.cors_methods
            )
            allow_headers = (
                [self.cors_headers]
                if isinstance(self.cors_headers, str)
                else self.cors_headers
            )
            allow_credentials = self.cors_credentials
            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=allow_origins,
                allow_credentials=allow_credentials,
                allow_methods=allow_methods,
                allow_headers=allow_headers,
            )
        if self.reload is False and self.workers == 1:
            config = uvicorn.Config(
                self._app,
                host=self.host or self.__component__.host,
                port=self.port or self.__component__.port,
                reload=self.reload,
                workers=self.workers,
            )
            server = uvicorn.Server(config)
            return server
        else:
            global app
            app = self._app
            config = uvicorn.Config(
                self._get_app_string(),
                host=self.host or self.__component__.host,
                port=self.port or self.__component__.port,
                reload=self.reload,
                workers=self.workers,
            )
            server = uvicorn.Server(config)
            return server

    def _get_app_string(self) -> str:
        module = inspect.getmodule(self)
        if module is not None:
            return f"{module.__name__}:app"
        raise ModuleNotFoundError("Module not found")

    def _get_info(self) -> APIInfo:
        return APIInfo(
            host=self.host or self.__component__.host,
            port=self.port or self.__component__.port,
        )


class BaseAPI:
    component_mapping: ComponentMapping
    auth: APIAuth | None
    router: APIRouter

    def _get_security_scheme(self, auth: APIAuth | None) -> Any:
        if auth and auth.type == APIAuthType.API_KEY:
            if auth.config and auth.config.header:
                security_scheme: Any = APIKeyHeader(
                    name=auth.config.header, auto_error=True
                )
            elif auth.config and auth.config.query:
                security_scheme = APIKeyQuery(
                    name=auth.config.query, auto_error=True
                )
            else:
                security_scheme = APIKeyHeader(
                    name="Authorization", auto_error=True
                )
        elif auth and auth.type == APIAuthType.BEARER_TOKEN:
            security_scheme = HTTPBearer(auto_error=True)
        elif auth and auth.type == APIAuthType.BASIC:
            security_scheme = HTTPBasic(auto_error=True)
        else:
            security_scheme = None
        return security_scheme

    def _create_auth_validate_method(
        self,
        auth: APIAuth | None,
    ) -> Callable | None:
        security_scheme = self._get_security_scheme(auth)
        if not security_scheme:
            return None

        def auth_validate(credentials=Security(security_scheme)):
            from verse.identity.authentication import (
                Authentication,
                UserCredential,
            )

            if isinstance(auth.component, Authentication):
                if isinstance(security_scheme, APIKeyHeader):
                    if security_scheme.model.name == "Authorization":
                        start = len("Bearer ")
                        return auth.component.validate(
                            credentials.credentials[start:]
                        )
                    return auth.component.validate(credentials)
                elif isinstance(security_scheme, APIKeyQuery):
                    return auth.component.validate(credentials)
                elif isinstance(security_scheme, HTTPBearer):
                    return auth.component.validate(credentials.credentials)
                elif isinstance(security_scheme, HTTPBasic):
                    return auth.component.validate(
                        UserCredential(
                            username=credentials.username,
                            password=credentials.password,
                        )
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Auth component is not an instance of "
                        "Authentication"
                    ),
                )

        return auth_validate

    def _create_auth_get_user_info_method(
        self,
        auth: APIAuth | None,
    ) -> Callable | None:
        security_scheme = self._get_security_scheme(auth)
        if not security_scheme:
            return None

        def auth_get_user_info(credentials=Security(security_scheme)):
            from verse.identity.authentication import (
                Authentication,
                UserCredential,
            )

            if isinstance(auth.component, Authentication):
                if isinstance(security_scheme, APIKeyHeader):
                    if security_scheme.model.name == "Authorization":
                        start = len("Bearer ")
                        return auth.component.get_user_info(
                            credentials.credentials[start:]
                        )
                    return auth.component.get_user_info(credentials)
                elif isinstance(security_scheme, APIKeyQuery):
                    return auth.component.get_user_info(credentials)
                elif isinstance(security_scheme, HTTPBearer):
                    return auth.component.get_user_info(
                        credentials.credentials
                    )
                elif isinstance(security_scheme, HTTPBasic):
                    return auth.component.get_user_info(
                        UserCredential(
                            username=credentials.username,
                            password=credentials.password,
                        )
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Auth component is not an instance of "
                        "Authentication"
                    ),
                )

        return auth_get_user_info

    def _create_wrapped_operation_method(
        self,
        op_info: OperationInfo,
    ) -> Callable:
        new_params: list[inspect.Parameter] = []
        use_generated_body_model = False
        body_primitive_field_count = 0
        for arg in op_info.args:
            if arg.source.type == ArgSourceType.BODY and not issubclass(
                arg.type, (BaseModel, DataModel)
            ):
                body_primitive_field_count += 1
        if body_primitive_field_count == 1:
            use_generated_body_model = True

        require_auth_user = False
        for arg in op_info.args:
            if arg.source.type == ArgSourceType.BODY:
                if use_generated_body_model:
                    model_name = f"Body_{op_info.name}"
                    model_name += f"{op_info.path.lower()}"
                    model_name += f"_{op_info.http_method.lower()}"
                    model_name = (
                        model_name.replace("/", "_")
                        .replace("{", "_")
                        .replace("}", "_")
                        .replace("-", "_")
                    )
                    model = create_model(
                        model_name,
                        **{
                            arg.name: (
                                arg.type,
                                ... if arg.required else arg.default,
                            )
                        },
                    )  # type: ignore
                    new_params = [
                        inspect.Parameter(
                            "__body__",
                            kind=inspect.Parameter.KEYWORD_ONLY,
                            default=Body(...),
                            annotation=model,
                        )
                    ]
                else:
                    new_params.append(
                        inspect.Parameter(
                            arg.name,
                            kind=inspect.Parameter.KEYWORD_ONLY,
                            default=Body(
                                ... if arg.required else arg.default,
                                alias=arg.source.field,
                            ),
                            annotation=arg.type,
                        )
                    )
            elif arg.source.type == ArgSourceType.QUERY:
                new_params.append(
                    inspect.Parameter(
                        arg.name,
                        kind=inspect.Parameter.KEYWORD_ONLY,
                        default=Query(
                            ... if arg.required else arg.default,
                            alias=arg.source.field,
                        ),
                        annotation=arg.type,
                    )
                )
            elif arg.source.type == ArgSourceType.HEADER:
                new_params.append(
                    inspect.Parameter(
                        arg.name,
                        kind=inspect.Parameter.KEYWORD_ONLY,
                        default=Header(
                            ... if arg.required else arg.default,
                            alias=arg.source.field,
                        ),
                        annotation=arg.type,
                    )
                )
            elif arg.source.type == ArgSourceType.PATH:
                new_params.append(
                    inspect.Parameter(
                        arg.name,
                        kind=inspect.Parameter.KEYWORD_ONLY,
                        default=Path(
                            ... if arg.required else arg.default,
                            alias=arg.source.field,
                        ),
                        annotation=arg.type,
                    )
                )
            elif arg.source.type == ArgSourceType.AUTH:
                pass
            elif arg.source.type == ArgSourceType.AUTH_USER:
                require_auth_user = True

        auth_validate_method = self._create_auth_validate_method(op_info.auth)
        if auth_validate_method:
            new_params.append(
                inspect.Parameter(
                    "__auth__",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(auth_validate_method),
                )
            )

        if require_auth_user:
            if op_info.auth:
                auth_get_user_info_method = (
                    self._create_auth_get_user_info_method(op_info.auth)
                )
                if auth_get_user_info_method:
                    new_params.append(
                        inspect.Parameter(
                            "__auth_user__",
                            kind=inspect.Parameter.KEYWORD_ONLY,
                            default=Depends(auth_get_user_info_method),
                        )
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Operation requires authentication, but no auth "
                        "component is provided."
                    ),
                )

        new_sig = inspect.Signature(
            parameters=new_params,
            return_annotation=op_info.return_type,
        )

        async def wrapped_operation_method(*args: Any, **kwargs: Any):
            bound = new_sig.bind(*args, **kwargs)
            bound.apply_defaults()
            auth = bound.arguments.pop("__auth__", None)
            auth_user = bound.arguments.pop("__auth_user__", None)
            body = bound.arguments.pop("__body__", None)
            mapped_args = {}
            for arg in op_info.args:
                if arg.source.type == ArgSourceType.AUTH:
                    if arg.source.field:
                        if auth:
                            mapped_args[arg.name] = DataAccessor.get_field(
                                auth, arg.source.field
                            )
                        else:
                            mapped_args[arg.name] = None
                    else:
                        mapped_args[arg.name] = auth
                elif arg.source.type == ArgSourceType.AUTH_USER:
                    if arg.source.field:
                        if auth_user:
                            mapped_args[arg.name] = DataAccessor.get_field(
                                auth_user, arg.source.field
                            )
                        else:
                            mapped_args[arg.name] = None
                    else:
                        mapped_args[arg.name] = auth_user
            bound.arguments.update(mapped_args)
            if body:
                bound.arguments.update(body.model_dump())
            converted_args = TypeConverter.convert_args(
                op_info.method, bound.arguments
            )
            try:
                result = op_info.method(**converted_args)
                return await result if asyncio.iscoroutine(result) else result
            except BaseError as e:
                raise HTTPException(status_code=e.status_code, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail={str(e)})

        wrapped_operation_method.__name__ = op_info.name
        wrapped_operation_method.__doc__ = op_info.__doc__
        setattr(wrapped_operation_method, "__signature__", new_sig)
        return wrapped_operation_method

    def _init_operation_routes(self) -> None:
        operations = get_operations(self.component_mapping, self.auth)
        for _, op_info in operations.items():
            wrapped_operation_method = self._create_wrapped_operation_method(
                op_info,
            )
            self.router.add_api_route(
                path=op_info.path,
                endpoint=wrapped_operation_method,
                methods=[op_info.http_method],
                response_model=op_info.return_type,
                status_code=op_info.status_code,
            )

    def _get_operation_mapping(
        self, operation_name: str
    ) -> OperationMapping | None:
        for operation in self.component_mapping.operations:
            if operation.name == operation_name:
                return operation
        return None


class RunRequest(DataModel):
    operation: Operation | None = None
    context: Context | None = None


class GenericAPI(BaseAPI):
    def __init__(
        self,
        component_mapping: ComponentMapping,
        auth: APIAuth | None = None,
    ):
        self.component_mapping = component_mapping
        self.auth = auth
        self.router = APIRouter()
        auth_validate_method = self._create_auth_validate_method(self.auth)
        dependencies = []
        if auth_validate_method:
            dependencies.append(Depends(auth_validate_method))
        self.router.add_api_route(
            "/__run__", self.run, methods=["POST"], dependencies=dependencies
        )
        self.router.add_api_route(
            "/__spec__", self.spec, methods=["GET"], dependencies=dependencies
        )
        self._init_operation_routes()

    def run(self, request: RunRequest) -> Any:
        """Run operation."""
        try:
            return self.component_mapping.component.__run__(
                operation=request.operation, context=request.context
            )
        except BaseError as e:
            raise HTTPException(status_code=e.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail={str(e)})

    def spec(self) -> ComponentSpec:
        """Get component spec."""
        component_type = self.component_mapping.component.__type__
        spec_builder = SpecBuilder()
        spec = spec_builder.build_component_spec(component_type=component_type)
        return spec


class GenericAsyncAPI(BaseAPI):
    def __init__(
        self,
        component_mapping: ComponentMapping,
        auth: APIAuth | None = None,
    ):
        self.component_mapping = component_mapping
        self.auth = auth
        self.router = APIRouter()
        auth_validate_method = self._create_auth_validate_method(self.auth)
        dependencies = []
        if auth_validate_method:
            dependencies.append(Depends(auth_validate_method))
        self.router.add_api_route(
            "/__run__", self.run, methods=["POST"], dependencies=dependencies
        )
        self.router.add_api_route(
            "/__spec__", self.spec, methods=["GET"], dependencies=dependencies
        )
        self._init_operation_routes()

    async def run(self, request: RunRequest) -> Any:
        """Run operation."""
        try:
            return await self.component_mapping.component.__arun__(
                operation=request.operation,
                context=request.context,
            )
        except BaseError as e:
            raise HTTPException(status_code=e.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail={str(e)})

    async def spec(self) -> ComponentSpec:
        """Get component spec."""
        component_type = self.component_mapping.component.__type__
        spec_builder = SpecBuilder()
        spec = spec_builder.build_component_spec(component_type=component_type)
        return spec

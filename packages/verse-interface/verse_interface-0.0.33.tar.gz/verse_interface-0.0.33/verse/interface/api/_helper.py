import inspect
import re
from typing import Any, Callable, get_type_hints

from ._models import (
    APIAuth,
    ArgMapping,
    ArgSource,
    ArgSourceType,
    ComponentMapping,
    OperationMapping,
)


class ArgInfo:
    name: str
    type: Any
    default: Any | None
    required: bool
    source: ArgSource

    def __init__(
        self,
        name: str,
        type: Any,
        default: Any | None,
        required: bool,
        source: ArgSource,
    ):
        self.name = name
        self.type = type
        self.default = default
        self.required = required
        self.source = source


class OperationInfo:
    name: str
    path: str
    method: Callable[..., Any]
    http_method: str
    status_code: int
    return_type: Any | None
    path_params: list[str]
    auth: APIAuth | None
    args: list[ArgInfo]
    operation_mapping: OperationMapping | None

    def __init__(self, name: str, method: Callable[..., Any]):
        self.name = name
        self.path = f"/{self.name}"
        self.method = method
        self.http_method = "POST"
        self.status_code = 200
        self.path_params = []
        self.auth = None
        self.operation_mapping = None


def get_operations(
    component_mapping: ComponentMapping,
    auth: APIAuth | None = None,
) -> dict[str, OperationInfo]:
    """
    Get operations from component
    """
    operations: dict[str, OperationInfo] = {}
    # Get all the sync methods first.
    for method_name, method in inspect.getmembers(
        component_mapping.component, predicate=inspect.ismethod
    ):
        if (
            callable(method)
            and not inspect.iscoroutinefunction(method)
            and hasattr(method, "operation")
        ):
            operations[method_name] = OperationInfo(method_name, method)

    # Next, iterate over async methods.
    # If there is an async equivalent of a sync method,
    # then resolve based on the resolution policy.
    for method_name, method in inspect.getmembers(
        component_mapping.component, predicate=inspect.iscoroutinefunction
    ):
        if callable(method) and hasattr(method, "operation"):
            if method_name.startswith("a") and method_name[1:] in operations:
                if component_mapping.sync_async_resolution == "async":
                    operations[method_name[1:]] = OperationInfo(
                        method_name[1:], method
                    )
                elif component_mapping.sync_async_resolution == "both":
                    operations[method_name] = OperationInfo(
                        method_name, method
                    )
            else:
                if (
                    method_name.startswith("a")
                    and component_mapping.remove_async_prefix
                ):
                    operations[method_name[1:]] = OperationInfo(
                        method_name[1:], method
                    )
                else:
                    operations[method_name] = OperationInfo(
                        method_name, method
                    )
    # Remove operations that are suppressed.
    for operation in component_mapping.operations:
        if operation.supress:
            operations.pop(operation.name, None)

    # Update operation info with mappings.
    for op_name, op_info in operations.items():
        op_info.auth = component_mapping.auth or auth
        op_info.return_type = get_return_type(op_info.method)
        if component_mapping.predict_http_method:
            op_info.http_method = predict_http_method(op_name)
        else:
            op_info.http_method = "POST"
        op_mapping = get_operation_mapping(component_mapping, op_name)
        arg_mappings = []
        if op_mapping:
            op_info.path = (
                op_mapping.path
                if op_mapping.path is not None
                else op_info.path
            )
            op_info.http_method = op_mapping.method or op_info.http_method
            op_info.status_code = op_mapping.status_code or op_info.status_code
            op_info.path_params = re.findall(r"\{(.*?)\}", op_info.path)
            op_info.path_params.extend(
                re.findall(r"\{(.*?)\}", component_mapping.prefix or "")
            )
            op_info.auth = op_mapping.auth or op_info.auth
            op_info.operation_mapping = op_mapping
            arg_mappings = op_mapping.args

        op_info.http_method = op_info.http_method.upper()
        for arg_mapping in component_mapping.args:
            if arg_mapping.name not in [a.name for a in arg_mappings]:
                arg_mappings.append(arg_mapping)
        op_info.args = get_args(
            op_info,
            arg_mappings,
        )
    return operations


def get_operation_mapping(
    component_mapping: ComponentMapping,
    operation_name: str,
) -> OperationMapping | None:
    for operation in component_mapping.operations:
        if operation.name == operation_name:
            return operation
    return None


def get_arg_mapping(
    arg_mappings: list[ArgMapping],
    arg_name: str,
) -> ArgMapping | None:
    for arg_mapping in arg_mappings:
        if arg_mapping.name == arg_name:
            return arg_mapping
    return None


def get_return_type(method: Any) -> Any:
    sig = inspect.signature(method)
    return (
        sig.return_annotation
        if sig.return_annotation != inspect.Signature.empty
        else None
    )


def predict_http_method(operation_name: str) -> str:
    mapping = {
        "GET": (
            "get",
            "aget",
            "list",
            "alist",
            "query",
            "aquery",
            "fetch",
            "afetch",
            "retrieve",
            "aretrieve",
            "find",
            "afind",
            "search",
            "asearch",
            "read",
            "aread",
        ),
        "PUT": (
            "put",
            "aput",
            "update",
            "aupdate",
            "replace",
            "areplace",
            "modify",
            "amodify",
            "save",
            "asave",
        ),
        "DELETE": (
            "delete",
            "adelete",
            "remove",
            "aremove",
            "destroy",
            "adestroy",
            "purge",
            "apurge",
            "clear",
            "aclear",
        ),
        "PATCH": (
            "patch",
            "apatch",
        ),
    }
    for method, prefixes in mapping.items():
        if operation_name.startswith(prefixes):
            return method
    return "POST"


def get_args(
    op_info: OperationInfo,
    arg_mappings: list[ArgMapping],
) -> list[ArgInfo]:
    sig = inspect.signature(op_info.method)
    type_hints = get_type_hints(op_info.method)
    args: list[ArgInfo] = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if name == "kwargs" and param.kind == inspect.Parameter.VAR_KEYWORD:
            continue
        arg_mapping = get_arg_mapping(arg_mappings, name)
        if arg_mapping and arg_mapping.source:
            source = arg_mapping.source
        else:
            if name in op_info.path_params:
                source = ArgSource(type=ArgSourceType.PATH, field=name)
            elif op_info.http_method in ["POST", "PUT", "PATCH"]:
                source = ArgSource(type=ArgSourceType.BODY, field=name)
            else:
                source = ArgSource(type=ArgSourceType.QUERY, field=name)
        type = type_hints.get(name, Any)
        arg_info = ArgInfo(
            name=name,
            type=type,
            default=(
                param.default
                if param.default != inspect.Parameter.empty
                else None
            ),
            required=param.default == inspect.Parameter.empty,
            source=source,
        )
        args.append(arg_info)
    return args

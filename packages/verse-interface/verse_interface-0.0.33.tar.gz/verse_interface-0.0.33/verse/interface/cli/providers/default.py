import sys
from typing import Any

from verse.core import ArgParser, Component, Context, Operation, Provider
from verse.core.exceptions import BadRequestError
from verse.core.spec import SpecBuilder


class Default(Provider):
    component: Component | None = None

    def __init__(self, component: Component | None = None, **kwargs):
        self.component = component

    def __run__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        component = self.component or self.__component__.component
        if not component:
            raise BadRequestError("No component provided")
        self._print_welcome()
        while True:
            try:
                statement = input("> ")
                if statement.strip():
                    try:
                        if statement == "?":
                            component_type = component.__type__
                            spec_builder = SpecBuilder()
                            component_spec = spec_builder.build_component_spec(
                                component_type=component_type
                            )
                            spec_builder.print(component_spec)
                        else:
                            operation = ArgParser.convert_execute_operation(
                                statement, None
                            )
                            output = component.__run__(operation=operation)
                            print(output)
                    except Exception as e:
                        import traceback

                        print(traceback.format_exc())
                        print(f"{type(e).__name__}: {e}")
            except KeyboardInterrupt:
                sys.exit(0)
            except EOFError:
                sys.exit(0)

    async def __arun__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        component = self.component or self.__component__.component
        if not component:
            raise BadRequestError("No component provided")
        self._print_welcome()
        while True:
            try:
                statement = input("> ")
                if statement.strip():
                    try:
                        if statement == "?":
                            component_type = component.__type__
                            spec_builder = SpecBuilder()
                            component_spec = spec_builder.build_component_spec(
                                component_type=component_type
                            )
                            spec_builder.print(component_spec)
                        else:
                            operation = ArgParser.convert_execute_operation(
                                statement, None
                            )
                            output = await component.__arun__(
                                operation=operation
                            )
                            print(output)
                    except Exception as e:
                        import traceback

                        print(traceback.format_exc())
                        print(f"{type(e).__name__}: {e}")
            except KeyboardInterrupt:
                sys.exit(0)
            except EOFError:
                sys.exit(0)

    def _print_welcome(self):
        print("Welcome to Verse CLI. Use Verse QL to run operations.")

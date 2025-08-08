from importlib import import_module
from typing import Any, Callable, Annotated

from pydantic import GetCoreSchemaHandler, BeforeValidator
from pydantic_core import CoreSchema, core_schema
from .web import URL


type StringDict = dict[str, str]


class Identifier(URL):
    def __new__(cls, url: URL | str, strict: bool = False):
        if isinstance(url, URL):
            _url = url
        else:
            _url = URL(url)

        return super().__new__(
            cls,
            URL.build(
                scheme="id",
                username=_url.username,
                password=_url.password,
                host=_url.host_root.lower(),
                path=_url.path.rstrip("/"),
                query=_url.query_params("flat"),
            ),
        )

    @property
    def root(self) -> URL:
        """
        Return ID without zz_* parameters
        """

        return URL(self).update(
            query={
                k: v
                for k, v in self.query_params("flat").items()
                if not k.startswith("zz_")
            }
        )

    @property
    def domain(self) -> str:
        return self.host


class PythonImportableObjectType(str):
    """
    function or class
    """

    def __new__(cls, obj: Any):
        # if
        if not isinstance(obj, str):
            if hasattr(obj, "__module__") and hasattr(obj, "__name__"):
                obj = f"{obj.__module__}:{obj.__name__}"
            else:
                raise ValueError(f"Cannot convert {obj} to PythonImportableObject")
        instance = super().__new__(cls, obj)
        if ":" in obj:
            instance._path, instance._func = obj.rsplit(":", 1)
        else:
            instance._path, instance._func = obj.rsplit(".", 1)
        return instance

    def resolve(self) -> Callable:
        module = import_module(self._path)
        return getattr(module, self._func)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


PythonImportableObject = Annotated[
    PythonImportableObjectType,
    BeforeValidator(
        lambda x: PythonImportableObjectType(x), json_schema_input_type=str
    ),
]

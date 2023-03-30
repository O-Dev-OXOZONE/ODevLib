from .utils import deprecate as deprecate
from _typeshed import Incomplete

DEFAULTS: Incomplete
DEPRECATED_SETTINGS: Incomplete

def is_callable(value): ...

class Settings:
    def __getattr__(self, name): ...
    def get_setting(self, setting): ...
    def change_setting(self, setting, value, enter, **kwargs) -> None: ...

settings: Incomplete

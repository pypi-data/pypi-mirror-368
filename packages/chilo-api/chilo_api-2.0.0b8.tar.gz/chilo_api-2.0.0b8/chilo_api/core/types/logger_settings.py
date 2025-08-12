from typing_extensions import TypedDict, Any, NotRequired, Callable


class LoggerSettings(TypedDict, total=False):
    condition: NotRequired[Callable[[Any], bool]]
    level: NotRequired[str]

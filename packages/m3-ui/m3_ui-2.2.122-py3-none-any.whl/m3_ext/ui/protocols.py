from typing import (
    Protocol,
    Union,
)


class HasTemplateGlobals(Protocol):
    """
    Протокол, определяющий компоненты с атрибутом template_globals,
    в котором хранятся js-шаблоны экземпляра компонента.
    """

    template_globals: Union[str, list[str], tuple[str, ...]]

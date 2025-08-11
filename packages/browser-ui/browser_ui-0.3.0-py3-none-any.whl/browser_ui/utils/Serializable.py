from typing import Callable, Union, TypeAlias, Generator

Serializable: TypeAlias = Union[
    bool, str, int, float, None,
    list["Serializable"], tuple["Serializable", ...], dict["Serializable", "Serializable"]]
SerializableCallable: TypeAlias = Callable[..., Serializable]
GeneratorCallable: TypeAlias = Callable[..., Generator[Serializable, None, None]]

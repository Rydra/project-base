from typing import T, Type  # type: ignore

import pinject
from singleton import Singleton

from contexts.auth.binding_specs import AuthBindingSpec
from contexts.sample.binding_specs import SampleBindingSpec


class Container(metaclass=Singleton):
    def __init__(self) -> None:
        self.obj_graph = pinject.new_object_graph(
            modules=None,
            binding_specs=[SampleBindingSpec(), AuthBindingSpec()],
        )

    def provide(self, klass: Type[T]) -> T:
        return self.obj_graph.provide(klass)


def provide(klass: Type[T]) -> T:
    return Container().provide(klass)

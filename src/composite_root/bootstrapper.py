from contexts.shared.cache import init_cache
from contexts.shared.command_bus import CommandBus
from contexts.sample.core.commands.sample import CreateSampleHandler
from composite_root.container import provide


def bootstrap() -> None:
    init_cache()

    for handler in [CreateSampleHandler]:
        CommandBus().register_handler(provide(handler))

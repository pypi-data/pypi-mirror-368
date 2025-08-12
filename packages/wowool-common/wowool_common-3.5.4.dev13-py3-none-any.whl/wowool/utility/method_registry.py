import types
from typing import Callable, Dict


jump_table: Dict[str, Callable] = {}


def register(command: str | None = None) -> Callable:
    """Register a function in the jump table.

    Args:
        command: Command name to register. If None, uses function name.

    Returns:
        Decorator function.
    """

    def decorator(func: Callable) -> Callable:
        if command:
            jump_table[command] = func
        else:
            jump_table[func.__name__] = func
        return func

    return decorator


def get_bound_jump_table(self) -> Dict[str, Callable]:
    """Get bound methods for all registered functions.

    Args:
        self: Instance to bind methods to.

    Returns:
        Dictionary mapping command names to bound methods.
    """
    return {command: types.MethodType(func, self) for command, func in jump_table.items()}

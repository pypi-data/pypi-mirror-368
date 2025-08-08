"""Decorators for SDK functions."""

from typing import Any, Callable, Optional


def prompt_confirmation(prompt_text: str) -> Callable:
    """Show prompt asking user whether they want to continue. Exits on anything but y(es)."""

    def outer_wrapper(func: Callable) -> Callable:
        def wrapper(self: Any, force: Optional[bool] = False) -> Optional[Callable]:
            if not force:
                if input(prompt_text).lower() not in ["y", "yes"]:
                    print("Delete cancelled.")
                    return None
                return func(self, force)
            return func(self, force)

        return wrapper

    return outer_wrapper

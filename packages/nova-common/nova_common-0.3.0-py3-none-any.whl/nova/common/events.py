"""Events."""

import asyncio
from typing import Any, Dict, List

import blinker
from typing_extensions import Callable

from nova.common.signals import get_signal_id


class Event:
    """Wrapper around a Blinker signal that supports both synchronous and asynchronous event sending."""

    def __init__(self, name: str) -> None:
        """
        Initialize the Event with a given signal name.

        Args:
            name (str): The name of the signal.
        """
        self.signal = blinker.signal(name)

    def connect(self, receiver: Callable[..., Any]) -> None:
        """
        Connect a receiver function to this event's signal.

        Args:
            receiver (Callable[..., Any]): The callback function to be connected to the signal.
        """
        self.signal.connect(receiver, weak=False)

    async def send_async(self, sender: Any = None, **kwargs: Any) -> List[Any]:
        """
        Send the event asynchronously, awaiting all connected receivers.

        Args:
            sender (Any, optional): The sender of the signal. Defaults to None.
            **kwargs: Additional keyword arguments passed to receivers.

        Returns
        -------
            List[Any]: A list of results returned by the connected receivers.
        """

        def sync_wrapper(func: Any) -> Any:
            async def inner(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

            return inner

        results = await self.signal.send_async(sender, _sync_wrapper=sync_wrapper, **kwargs)
        return [res[1] for res in results]

    def send_sync(self, sender: Any = None, **kwargs: Any) -> List[Any]:
        """
        Send the event synchronously, wrapping asynchronous receivers as futures which require a running event loop.

        Args:
            sender (Any, optional): The sender of the signal. Defaults to None.
            **kwargs: Additional keyword arguments passed to receivers.

        Raises
        ------
            RuntimeError: If called outside a running async event loop.

        Returns
        -------
            List[Any]: A list of results returned by the connected receivers.
        """

        def async_wrapper(func: Any) -> Any:
            def inner(*args: Any, **kwargs: Any) -> Any:
                try:
                    asyncio.get_running_loop()
                except RuntimeError as err:
                    raise RuntimeError("Cannot send outside a running async loop.") from err
                # theoretically we can, but we don't want to - async function is supposed
                # to run in an original loop, not in a new one
                # return asyncio.run(func(*args, **kwargs))
                else:
                    coro = func(*args, **kwargs)
                    return asyncio.ensure_future(coro)

            return inner

        results = self.signal.send(sender, _async_wrapper=async_wrapper, **kwargs)
        return [res[1] for res in results if res[1] is not None]


_events_map: Dict[str, Event] = {}


def get_event(signal_id: str, unique_id: str = "") -> Event:
    """
    Get or create an Event instance based on the given id and signal_id.

    Args:
        id (str): The identifier string that can be appended to the signal name.
        signal_id (str): The signal name.

    Returns
    -------
        Event: The Event instance corresponding to the combined signal name.
    """
    name = get_signal_id(unique_id, signal_id)
    if name not in _events_map:
        _events_map[name] = Event(name)

    return _events_map[name]

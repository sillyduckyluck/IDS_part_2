import asyncio
from datetime import datetime, timedelta
from typing import TypedDict, List

Main = TypedDict("Main", {"rev_slot_content_model": str, "rev_slot_origin_rev_id": int, "rev_slot_sha1": str,
                          "rev_slot_size": int})

RevSlots = TypedDict("RevSlots", {"main": Main})

Performer = TypedDict("Performer",
                      {"user_edit_count": int, "user_groups": List[str], "user_id": int, "user_is_bot": bool,
                       "user_registration_dt": datetime, "user_text": str})

Meta = TypedDict("Meta", {"domain": str, "dt": datetime, "stream": str, "uri": str})

PageCreate = TypedDict("PageCreate", {"$schema": str, "database": str, "dt": datetime, "meta": Meta, "page_id": int,
                                      "page_is_redirect": bool, "page_namespace": int, "page_title": str,
                                      "performer": Performer, "rev_content_changed": bool, "rev_content_format": str,
                                      "rev_content_model": str, "rev_id": int, "rev_is_revert": bool, "rev_len": int,
                                      "rev_minor_edit": bool, "rev_parent_id": int, "rev_sha1": str,
                                      "rev_slots": RevSlots, "rev_timestamp": datetime})

RevisionCreate = TypedDict("RevisionCreate",
                           {"$schema": str, "database": str, "dt": datetime, "meta": Meta, "page_id": int,
                            "page_is_redirect": bool, "page_namespace": int, "page_title": str, "performer": Performer,
                            "rev_content_changed": bool, "rev_content_format": str, "rev_content_model": str,
                            "rev_id": int, "rev_is_revert": bool, "rev_len": int, "rev_minor_edit": bool,
                            "rev_parent_id": int, "rev_sha1": str, "rev_slots": RevSlots, "rev_timestamp": datetime})

CreationEvent = PageCreate

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from pywikibot.comms.eventstreams import EventStreams


class Switch:

    def __init__(self, initial_state=True):
        self.on = initial_state

    @property
    def off(self) -> bool:
        return not self.on

    @off.setter
    def off(self, value: bool) -> None:
        self.on = not value

    def toggle(self):
        self.on = not self.on

    def turn_off(self):
        self.off = True

    def turn_on(self):
        self.on = True


@contextmanager
def wiki_stream(**kwargs) -> Generator[EventStreams, Any, None]:
    stream = EventStreams(**kwargs)
    # stream.register_filter(server_name='en.wikipedia.org', type='edit')
    try:
        yield stream
    finally:
        if stream is not None:
            stream.close()

async def auto_off(time: timedelta, switch: Switch):
    print(f'Switching off in {time}')
    await asyncio.sleep(time.total_seconds())
    print(f'Switching off now')
    switch.turn_off()


def run_loop(loop_func, timeout: timedelta, **kwargs) -> tuple[asyncio.Task, asyncio.Task, Switch]:
    loop = asyncio.get_event_loop()
    sw = Switch(True)
    t_stop = loop.create_task(auto_off(timeout, sw))
    t = loop.create_task(loop_func(sw, **kwargs))
    return t, t_stop, sw
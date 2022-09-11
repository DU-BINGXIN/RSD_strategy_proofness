import itertools
from typing import Dict, List

from vaccine_booking.elements.message import Message
from vaccine_booking.elements.slot import Slot


class SiteBasedMessage(Message):
    def __init__(
        self,
        message_name: str,
        message_structure: Dict[str, str],
        slot_list: List[Slot],
    ):
        self.name = message_name
        self.message_structure = message_structure
        self.element_slots: List[Slot] = []

        # self.slots に入る Slot をチェック＆セット
        message_site = self.message_structure["site"]
        days_times_combinations = list(
            itertools.product(
                self.message_structure["day"],
                self.message_structure["time"],
            )
        )
        for slot in slot_list:
            slot_attributes = slot.get_attributes()
            if (
                message_site == slot_attributes["site"]
                and (slot_attributes["day"], slot_attributes["time"])
                in days_times_combinations
            ):
                self.element_slots.append(slot)

    def get_elements(self):
        return self.element_slots

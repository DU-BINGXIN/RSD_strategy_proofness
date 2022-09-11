from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, List

from vaccine_booking.elements.message import Message
from vaccine_booking.elements.preference import Preference
from vaccine_booking.elements.slot import Slot, outside

# Refs https://zenn.dev/ganariya/articles/python-lazy-annotation
if TYPE_CHECKING:
    from vaccine_booking.elements.applicant import Applicant


class Strategy(metaclass=ABCMeta):
    """
    抽象クラス。
    各戦略はこれを継承してクラスを作る。
    """

    @abstractmethod
    def make_decision(
        self,
        applicant: Applicant,  # 自分自身
        slots: List[Slot],
        messages: List[Message],
    ) -> List[Message]:
        pass

    def get_sorted_acceptable_slots(
        self,
        pref: Preference,
        slot_list: List[Slot],
    ) -> List[Slot]:


        acceptable_slots = []
        for slot in pref.sorted_list(slot_list):
            if pref.get_utility_value(slot) > pref.get_utility_value(outside):
                acceptable_slots.append(slot)
            else:
                break

        return acceptable_slots

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Union

import numpy as np
from typing_extensions import Final

from vaccine_booking.elements.slot import Slot

if TYPE_CHECKING:
    from vaccine_booking.elements.applicant import Applicant


class Message:
    """
    ワクチン接種の予約時間帯（スロット）を表すクラス。
    """

    def __init__(
        self,
        name: str,
        capacity: Union[int, float],
        slot_list: List[Slot]
    ) -> None:
        self.name = name
        self.capacity = capacity
        self.allocation = []
        self.cancel_nums = 0  # このSlotに割り当てられたApplicantのうちキャンセルした数
        self.slot_list=slot_list

    def __str__(self):
        return self.name

    def available(self) -> bool:
        if len(self.allocation) < self.capacity:
            return True
        else:
            return False

    def add(self, applicant: Applicant) -> None:
        self.allocation.append(applicant)

    def get_allocation(self):
        return self.allocation

    def get_cancel_nums(self):
        return self.cancel_nums

    def get_capacity(self):
        return self.capacity

    def get_name(self):
        return self.name
    
    # def get_slot_name_list(self):
    #     return self.slot_name_list

    def get_slot_list(self):
        return self.slot_list    

    def initialize(self):
        self.allocation = []
        self.cancel_nums = 0

    def remove(self, applicant: Applicant):
        self.allocation.remove(applicant)
        self.cancel_nums += 1


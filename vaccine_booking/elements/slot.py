from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Union

import numpy as np
from typing_extensions import Final

if TYPE_CHECKING:
    from vaccine_booking.elements.applicant import Applicant


class Slot:
    """
    ワクチン接種の予約時間帯（スロット）を表すクラス。
    """

    def __init__(
        self,
        name: str,
        capacity: Union[int, float],
    ) -> None:
        self.name = name
        self.capacity = capacity
        self.allocation = []
        self.cancel_nums = 0  # このSlotに割り当てられたApplicantのうちキャンセルした数

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

    def initialize(self):
        self.allocation = []
        self.cancel_nums = 0

    def remove(self, applicant: Applicant):
        self.allocation.remove(applicant)
        self.cancel_nums += 1


# Outside は特別なのでここに定義する
# [Usage]
# from vaccine_booking.elements.slot import outside
# のようにインポートすれば、outside としてどこでも使える
outside: Final = Slot(
    "Outside",
    np.inf,  # キャパシティは無限大
)

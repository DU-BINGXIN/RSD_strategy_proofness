from abc import ABCMeta, abstractmethod
from typing import Dict, List

from vaccine_booking.elements.allocation import Allocation
from vaccine_booking.elements.applicant import Applicant
from vaccine_booking.elements.slot import Slot


class Algorithm(metaclass=ABCMeta):
    """
    マッチングアルゴリズムの規定クラス
    このクラスを継承して、具体的なアルゴリズムを作る
    """

    def __init__(self) -> None:
        self.applicant_list: List[Applicant] = []
        self.slot_list: List[Slot] = []

    @abstractmethod
    def execute(
        self,
        applicant_list: List[Applicant],
        slot_list: List[Slot],
    ) -> Allocation:
        """
        具体的なマッチングのアルゴリズムの内容を書く。
        結果をreturnで返す。

        交換のマッチングのような場合には、player_list2 はなくても可。
        """
        pass

    def set(self, applicant_list: List[Applicant], slot_list: List[Slot]):
        self.applicant_list = applicant_list
        self.slot_list = slot_list

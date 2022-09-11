import logging
from typing import List, Tuple

from vaccine_booking.elements.message import Message
from vaccine_booking.elements.organisation import Organisation
from vaccine_booking.elements.preference import Preference
from vaccine_booking.elements.slot import Slot, outside
from vaccine_booking.strategies.strategy import Strategy


class Applicant:
    """
    ワクチン希望者を表すプレイヤクラス。
    """

    def __init__(
        self,
        name: str,
        all_slots: List[Slot],
        all_messages: List[Message],
        strategy: Strategy,
    ):
        self.name = name
        self.random_value = -100  # まずはマイナス値で初期化しておく
        self.all_slots = all_slots
        self.all_messages = all_messages
        self.allocations: List[Slot] = []  # 複数予約可 → リストに追加
        self.message_allocation: List[Message] = []
        self.strategy = strategy
        self.vaccination_nums = 0  # ワクチン接種回数
        self.vaccination_nums_random = 0  # ワクチン接種回数 for random_game
        self.cancel = False
        self.decisions = []
        self.priority = 1
        self.outside_value = 0

    def __str__(self):
        return self.name

    def compare(self, slot1: Slot, slot2: Slot) -> int:
        """
        このメソッドは選好順序の観点で比較する。
        slot1、slot2が無差別ならば0 を返す。
        （Java の Comparator と同様の発想で定義）
        """
        u1 = self.preference.get_utility_value(slot1)
        u2 = self.preference.get_utility_value(slot2)
        if u1 > u2:
            return 1
        elif u2 < u1:
            return -1
        else:
            return 0

    def get_name(self) -> str:
        return self.name

    def get_priority(self) -> int:
        return self.priority

    def get_preference(self) -> Preference:
        """
        選好を返すメソッド。
        """
        return self.preference

    def get_random_preference(self) -> Preference:
        """
        選好を返すメソッド。
        """
        return self.random_preference

    def get_random_value(self) -> int:
        return self.random_value

    def get_decision(self):
        return self.decisions

    def get_vaccination_nums(self) -> int:
        return self.vaccination_nums

    def get_vaccination_nums_random(self) -> int:
        return self.vaccination_nums_random

    def initialize(self) -> None:
        self.random_value = -100
        self.allocations = []
        self.message_allocation = []
        self.cancel = False
        self.decisions = []

    def is_cancelled(self) -> bool:
        return self.cancel

    def make_decision(
        self, message_list: List[Message], slot_list: List[Slot]
    ) -> List[Message]:
        current_decision = self.strategy.make_decision(
            self,
            message_list,
            slot_list,
        )
        self.decisions.append(current_decision)
        return current_decision

    def make_random_decision(
        self, message_list: List[Message], slot_list: List[Slot]
    ) -> List[Message]:
        current_decision = self.strategy.make_random_decision(
            self,
            message_list,
            slot_list,
        )
        self.decisions.append(current_decision)
        return current_decision

    def prefer(self, player1, player2) -> bool:
        """
        このメソッドはどちらのプレイヤを選好するかどうかで true or false を返す。
        ただし、無差別でも false を返すことに注意。

        Player#prefer(A,B) で prefer A to B を意味する。
        """

        u1 = self.preference.get_utility_value(player1)
        u2 = self.preference.get_utility_value(player2)
        if u1 >= u2:
            return True
        else:
            return False

    def set_preference(self, preference: Preference) -> None:
        """
        選好をセットするメソッド。
        引数は Preference クラスのインスタンス。
        """
        self.preference = preference

    def set_random_preference(self, preference: Preference) -> None:
        self.random_preference = preference

    def set_random_value(self, random_value: int) -> None:
        self.random_value = random_value

    def reserve_slot(self, slot: Slot) -> None:
        self.allocations.append(slot)

    def reserve_message(self, message: Message) -> None:
        self.message_allocation.append(message)

    def vaccinate(self) -> None:
        """
        予約できた人は、self.vacctination_num を1増やす。
        複数予約できた場合は、最も好ましいもの以外はキャンセル。
        配分されたものが、Outside slot よりも好ましくない場合、キャンセル処理を行う。
        キャンセルする場合、self.cancel = True に変更。
        """
        sorted_list = self.preference.sorted_list(
            self.allocations + [outside]  # Outside も入れてソート
        )
        # print(sorted_list)
        # print(sorted_list[0].get_allocation())
        # for applicant in sorted_list[1].get_allocation():
        #     print(applicant.name)
        # print(self)
        if self.prefer(sorted_list[0], outside):
            self.vaccination_nums += 1
        else:
            for slot in sorted_list:
                if slot is not outside:
                    slot.remove(self)
                    self.cancel = True

        # # 1つ以上予約できた場合
        # if len(self.allocations) > 0:
        #     sorted_list = self.preference.sorted_list(
        #         self.allocations + [outside] # Outside も入れてソート
        #     )
        #     # 最も選好するものがOutsideより好ましければ
        #     if self.prefer(sorted_list[0], outside):
        #         sorted_list.pop(0)
        #         self.vaccination_nums += 1

        #     for slot in sorted_list:
        #         if slot is not outside:
        #             slot.remove(self)
        #             self.cancel = True

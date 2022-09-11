from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from util.logger import logger
from vaccine_booking.elements.slot import Slot

if TYPE_CHECKING:
    from vaccine_booking.elements.applicant import Applicant


class Preference:
    """
    選好を表現するクラス。

    選好はハッシュ (utility_dict) で表現。 key=Slotクラスのインスタンス, value=数値。

    数値で選好の度合いを表す。大きいほど選好する。数字は効用値と思えば良い。
    """

    def __init__(self):
        self.utility_dict = {}
        self.utility_slotname_dict={}

    def set(self, slot, utility_value):
        self.utility_dict[slot] = utility_value
    
    def set_slotname_and_utility(self, slot_name:str, utility_value:int):
        self.utility_slotname_dict[slot_name] = utility_value

    def set_owner(self, applicant: Applicant):
        self.owner = applicant

    def sorted_list(self, slot_list: List[Slot] = None) -> List[Slot]:
        """
        引数のslot_list に対して、効用値順にソートして並べ直したものを返す。

        引数を指定しない場合、全てのSlotをソートしたものを返す。
        """
        if slot_list is not None:  # プレイヤのリストの指定がある場合
            temp_list = []  # 初期化
            sorted_tuple_list = self.sorted_tuple_list()
            for k, v in sorted_tuple_list:
                if k in slot_list:
                    temp_list.append(k)
            return temp_list
        elif slot_list is None:  # 指定がなければ
            return [i[0] for i in self.sorted_tuple_list()]
        else:
            logger.error(f"Player_list is wrong!: player_list={slot_list}")
            raise BaseException

    def sorted_tuple_list(self):
        """
        全てのslotに対して、効用値順にソートして並べ直したものを返す。
        ただし、返るものは、(player, 効用値) のタプルのリスト
        """
        return sorted(
            self.utility_dict.items(),
            key=lambda x: x[1],
            reverse=True,
        )

    def get_utility_value(self, slot: Slot) -> int:
        return self.utility_dict[slot]  # 効用値を返す

    def print_preference(self):
        """
        選好順序の中身をソートしてprintする。
        name1(utility_value1) > name2(utility_value2) > ...
        という形式で表示。
        """
        preference_sorted = sorted(
            self.utility_slotname_dict.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        print(preference_sorted)

        result = f"[{self.owner}]: "
        for i, j in zip(preference_sorted[:-1], preference_sorted[1:]):
            if i[1] > j[1]:
                temp = f"{str(i[0])}({str(i[1])})"
                result = result + f"{temp:14s}" + " > "
            else:
                temp = f"{str(i[0])}({str(i[1])})"
                result = result + f"{temp:14s}" + " = "
        result = result + f"{preference_sorted[-1][0]}({preference_sorted[-1][1]})"
        logger.debug(result)
        logger.info(result)
    def return_preference_not_kimita(self):
        output=[]
        for slot, utility in self.utility_dict.items():
            # print(f"slot{slot.get_name()}")
            # output.append(slot.get_name())
            # print(f"utility{utility}")
            output.append(utility)
        return(output)
    
    def get_slot_and_utility(self,slot_names: List[str]) -> Dict[str,int]:
        slot_and_utility_dict : Dict[str,int] = {}
        for slot_name in slot_names:
            utility=self.utility_slotname_dict[slot_name]
            slot_and_utility_dict[slot_name]=utility
        return slot_and_utility_dict

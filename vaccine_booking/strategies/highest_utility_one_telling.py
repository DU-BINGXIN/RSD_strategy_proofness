import random
from typing import List

from vaccine_booking.elements.applicant import Applicant
from vaccine_booking.elements.message import Message
from vaccine_booking.elements.slot import Slot
from vaccine_booking.strategies.strategy import Strategy


class HighestUtilityOneTelling(Strategy):
    """
    全てのメッセージの中で最も選好順序の高いものを1つ申告する。
    """

    def __init__(self):
        pass

    def make_decision(
        self,
        applicant: Applicant,
        possible_candidates: List[Slot],
        message_list: List[Message],
    ) -> List[Message]:

        pref = applicant.get_preference()

        # Outsideよりも好むSlotをソートして取り出す
        sorted_slots = self.get_sorted_acceptable_slots(
            pref,
            possible_candidates,
        )

        temp_list = []  # 初期化
        for i in sorted_slots:
            # ソート後のトップのプレイヤの効用値と同じ値の時、temp_listに追加する
            if pref.get_utility_value(sorted_slots[0]) == pref.get_utility_value(i):
                temp_list.append(i)
            else:
                break

        # 選択したメッセージを入れるリスト
        message_candidates = []
        for message in message_list:
            # メッセージを構成するslotを取得
            slots_in_message = set(message.get_elements())
            # メッセージを構成するslotが全て受け入れ可能か判定
            if slots_in_message.issubset(set(temp_list)):
                message_candidates.append(message)

        best_message = []
        # message_candidatesが空の場合の対応
        if len(message_candidates) != 0:
            # ランダムに1つ選んで返す
            best_message.append(random.choice(message_candidates))

        return best_message

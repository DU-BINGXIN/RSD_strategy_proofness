import random
from typing import List

from vaccine_booking.elements.applicant import Applicant
from vaccine_booking.elements.message import Message
from vaccine_booking.elements.slot import Slot
from vaccine_booking.strategies.strategy import Strategy


class RandomOneTelling(Strategy):
    """
    全てのメッセージの中からランダムに一つ選んで申告する
    """

    def __init__(self, seed=None) -> None:
        if seed is not None:
            random.seed(seed)

    def make_decision(
        self,
        applicant: Applicant,
        possible_candidates: List[Slot],
        message_list: List[Message],
    ) -> List[Message]:

        # Outsideよりも好むSlotをソートして取り出す
        sorted_slots = self.get_sorted_acceptable_slots(
            applicant.get_preference(),
            possible_candidates,
        )

        # 選択したメッセージを入れるリスト
        message_candidates = []
        for message in message_list:
            # メッセージを構成するslotを取得
            slots_in_message = set(message.get_elements())
            # メッセージを構成するslotが全て受け入れ可能か判定
            if slots_in_message.issubset(set(sorted_slots)):
                message_candidates.append(message)

        random_one_message = []
        # ランダムに1つ選んで返す
        if len(message_candidates) > 0:
            random_one_message.append(random.choice(message_candidates))
        return random_one_message

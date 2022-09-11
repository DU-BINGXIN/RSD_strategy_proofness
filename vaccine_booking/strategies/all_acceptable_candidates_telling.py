import random
from typing import List

from vaccine_booking.elements.applicant import Applicant
from vaccine_booking.elements.message import Message
from vaccine_booking.elements.slot import Slot
from vaccine_booking.strategies.strategy import Strategy


class AllAcceptableCandidatesTelling(Strategy):
    """
    全ての受け入れ可能（Outsideより上位）なメッセージを申告する
    """

    def __init__(self):
        pass

    def make_decision(
        self,
        applicant: Applicant,
        possible_candidates: List[Slot],
        message_list: List[Message],
    ) -> List[Slot]:

        # Outsideよりも好むSlotをソートして取り出す
        sorted_slots = self.get_sorted_acceptable_slots(
            applicant.get_preference(),
            possible_candidates,
        )

        """
        今回の加古川のメッセージは、会場、曜日、時間の組み合わせ、すなわち、複数のslotの組み合わせにより表現される
        あるメッセージを構成するslotが全て受け入れ可能（Outsideより上位）な場合、そのメッセージは選択可能である。
        """
        # 選択したメッセージを入れるリスト
        message_candidates = []
        for message in message_list:
            # メッセージを構成するslotを取得
            slots_in_message = set(message.get_elements())
            # メッセージを構成するslotが全て受け入れ可能か判定
            if slots_in_message.issubset(set(sorted_slots)):
                message_candidates.append(message)

        # シャッフル
        random.shuffle(message_candidates)

        return message_candidates

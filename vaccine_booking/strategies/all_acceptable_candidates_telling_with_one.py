import random
from typing import List

from vaccine_booking.elements.applicant import Applicant
from vaccine_booking.elements.message import Message
from vaccine_booking.elements.slot import Slot
from vaccine_booking.strategies.strategy import Strategy


class AllAcceptableCandidatesTellingWithOne(Strategy):
    """
    全ての受け入れ可能（Outsideより上位）なメッセージに受け入れ不可のメッセージを一つ加えて申告する
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
        """
        TruthTellingWithOneFalseでは、TruthTellingでは選択できないメッセージを追加
        今回、TruthTellingWithOneFalseで選択するメッセージは、4つのslotを保持し（ある会場の「全ての曜日」&「ampm（終日）」）
        かつ、受け入れ可能な（Outsideより上位の）slotが3つ
        """

        MAX_NUM_OF_SLOTS_IN_MESSAGE = 4  # メッセージを構成するSlotの最大値
        NUM_OF_ACCEPTABLE_SLOTS_IN_MESSAGE = 3  # メッセージを構成するSlotのうち受け入れ可能なSlotの数

        for message in message_list:
            # TruthTellingでは選択できないメッセージか判定
            if message not in message_candidates:
                # メッセージを構成するslot数と、その中で受け入れ可能なslot数を判定
                if (
                    len(message.get_elements()) == MAX_NUM_OF_SLOTS_IN_MESSAGE
                    and len(set(sorted_slots) & set(message.get_elements()))
                    == NUM_OF_ACCEPTABLE_SLOTS_IN_MESSAGE
                ):
                    message_candidates.append(message)

        # シャッフル
        random.shuffle(message_candidates)

        return message_candidates

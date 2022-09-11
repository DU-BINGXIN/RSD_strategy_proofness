import random
from typing import List

from vaccine_booking.elements.applicant import Applicant
from vaccine_booking.elements.message import Message
from vaccine_booking.elements.slot import Slot
from vaccine_booking.strategies.strategy import Strategy


class Mean(Strategy):
    """
    一番効用の高い値を参照してメッセージを送る。
    """

    def __init__(self):
        pass

    def make_decision(
        self,
        applicant: Applicant,
        message_list: List[Message],
        slot_list: List[Slot],
    ) -> List[Message]:

        #preference をもとにmaximaxでmessageの選好順位表を作る
        message_candidates_list = []
        message_candidates_dict = {}
        for message in message_list:
            slot_utility_list=[]
            for slot in message.get_slot_list():
                slot_utility_list.append(applicant.get_preference().utility_dict[slot])
            mean_slot_utility = sum(slot_utility_list)/len(slot_utility_list)
            if mean_slot_utility >= 0:
                message_candidates_dict[message]=mean_slot_utility
        message_candidates_sorted_list=sorted(message_candidates_dict.items(), key=lambda x: -x[1])    
        for candidates in message_candidates_sorted_list:
            message_candidates_list.append(candidates[0])
        return message_candidates_list

    def make_random_decision(
        self,
        applicant: Applicant,
        message_list: List[Message],
        slot_list: List[Slot],
    ) -> List[Message]:

        #preference をもとにmaximaxでmessageの選好順位表を作る
        message_candidates_list = []
        message_candidates_dict = {}
        for message in message_list:
            slot_utility_list=[]
            for slot in message.get_slot_list():
                slot_utility_list.append(applicant.get_random_preference().utility_dict[slot])
            mean_slot_utility = sum(slot_utility_list)/len(slot_utility_list)
            if mean_slot_utility >= 0:
                message_candidates_dict[message]=mean_slot_utility
        message_candidates_sorted_list=sorted(message_candidates_dict.items(), key=lambda x: -x[1])    
        for candidates in message_candidates_sorted_list:
            message_candidates_list.append(candidates[0])
        return message_candidates_list
            

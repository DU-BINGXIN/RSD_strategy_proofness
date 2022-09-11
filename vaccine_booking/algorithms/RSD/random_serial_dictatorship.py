import random
import copy
from typing import List

from numpy import rint

from util.logger import logger
from vaccine_booking.algorithms.algorithm import Algorithm
from vaccine_booking.algorithms.RSD.site_based_message import SiteBasedMessage
from vaccine_booking.elements.allocation import Allocation
from vaccine_booking.elements.applicant import Applicant
from vaccine_booking.elements.message import Message
from vaccine_booking.elements.organisation import Organisation
from vaccine_booking.elements.slot import Slot


class RandomSerialDictatorship(Algorithm):
    """
    Random Serial Dictatorshipアルゴリズム。
    """

    def __init__(
        self,
        organisation: Organisation,
    ):
        from vaccine_booking.game import configs

        super().__init__()
        self.organisation = organisation
        self.round: int
        self.organisation_name = organisation.get_name()  # このアルゴリズムを使っている組織名
        # self.message_list: List[Message] = []

        # Messageの初期化
        # for name, structure in configs[self.organisation_name].messages.items():
        #     self.message_list.append(
        #         SiteBasedMessage(
        #             name,
        #             structure,
        #             organisation.get_slot_list(),
        #         )
        #     )

    def execute(
        self,
        applicant_list: List[Applicant],
        slot_list: List[Slot],
        message_list: List[Message],
    ) -> Allocation:
        # from vaccine_booking.game import preference_csv
        # from vaccine_booking.game import message_csv
        # from vaccine_booking.game import allocation_csv

        # 各Priority (優先度名称, 優先度intのTuple) 別にプレイヤをリストとして辞書で保存
        # key=(str, int) value=List[Player]
        priority_player_dict = {}
        for player in applicant_list:
            if player.get_priority() in priority_player_dict.keys():
                priority_player_dict[player.get_priority()].append(player)
            else:
                priority_player_dict[player.get_priority()] = [player]
        # Priorityが高いグループは、数字が下位グループよりも小さくなるようにランダム値を設定
        # 乱数値は小さい方が優先度が高いものとする
        cnt = 0
        for tuple in sorted(priority_player_dict.items(), key=lambda x: x[1]):
            # print(tuple)
            # FIXME ここの tuple は (priority, List[Player])。ただし、priority=(str,int)
            temp_rand_values = [i for i in range(cnt, cnt + len(tuple[1]))]
            cnt = cnt + len(tuple[1])
            # random.seed(1)
            random.shuffle(temp_rand_values)
            for value, player in zip(temp_rand_values, tuple[1]):
                player.set_random_value(value)
                # if player.name == "applicant_1":
                #     print(player.get_random_value())
                # csv
                # row_csv=[]
                # row_csv.append(self.organisation.round)
                # row_csv.append(player.get_name())
                # row_csv.extend(player.get_preference().return_preference_not_kimita())
                # row_csv.append(player.random_value)
                # preference_csv.append(row_csv)

        # print(preference_csv)

        # 乱数値に基づきソート
        sorted_players = sorted(applicant_list, key=lambda x: x.get_random_value())
        logger.debug("今回の割当順")
        logger.debug(f"プレイヤー名: {[v.name for v in sorted_players]}")
        logger.debug(f"プレイヤーの優先順: {[v.priority for v in sorted_players]}")
        # logger.info(f"プレイヤー名: {[v.name for v in sorted_players]}")
        # logger.info(f"プレイヤーの優先順: {[v.priority for v in sorted_players]}")

        # 希望順に割り当て
        allocation = Allocation(slot_list)
        for applicant in sorted_players:
            decision_list = applicant.make_decision(message_list, slot_list)
            # if len(decision_list) > 0:
            # 1つ以上希望を出したので、その組織に予約希望を出した応募者として登録
            # self.organisation.register_requested_applicant(applicant)
            # logger.debug(f"{applicant.name}のメッセージ")
            # logger.debug([v.name for v in decision_list])
            # csv
            # row_csv=[]
            # row_csv.append(self.organisation.round)
            # row_csv.append(applicant.name)
            # for v in decision_list:
            #     row_csv.append(v.name)
            # message_csv.append(row_csv)

            for message in decision_list:
                agent_added_in_messaged = []
                slot_in_message = message.get_slot_list()
                random.shuffle(slot_in_message)
                for slot in slot_in_message:
                    if slot.available():
                        slot.add(applicant)
                        applicant.reserve_slot(slot)
                        allocation.add(slot, applicant)
                        agent_added_in_messaged.append(applicant)
                        break
                if len(agent_added_in_messaged) != 0:
                    break
        # csv
        # row_csv=[]
        # row_csv.append(self.organisation.round)
        # for key,value in allocation.allocation.items():
        #     applicant_list=[]
        #     for applicant in value:
        #         applicant_list.append(applicant.name)
        #     row_csv.append(applicant_list)
        # allocation_csv.append(row_csv)

        return allocation

    def execute_random(
        self,
        applicant_list: List[Applicant],
        slot_list: List[Slot],
        message_list: List[Message],
    ) -> Allocation:
        # from vaccine_booking.game import preference_csv
        # from vaccine_booking.game import message_csv
        # from vaccine_booking.game import allocation_csv

        # 各Priority (優先度名称, 優先度intのTuple) 別にプレイヤをリストとして辞書で保存
        # key=(str, int) value=List[Player]
        priority_player_dict = {}
        for player in applicant_list:
            if player.get_priority() in priority_player_dict.keys():
                priority_player_dict[player.get_priority()].append(player)
            else:
                priority_player_dict[player.get_priority()] = [player]
        # # Priorityが高いグループは、数字が下位グループよりも小さくなるようにランダム値を設定
        # # 乱数値は小さい方が優先度が高いものとする
        cnt = 0
        for tuple in sorted(priority_player_dict.items(), key=lambda x: x[1]):
            # FIXME ここの tuple は (priority, List[Player])。ただし、priority=(str,int)
            temp_rand_values = [i for i in range(cnt, cnt + len(tuple[1]))]
            cnt = cnt + len(tuple[1])
            # random.seed(1)
            random.shuffle(temp_rand_values)
            for value, player in zip(temp_rand_values, tuple[1]):
                player.set_random_value(value)
                # if player.name == "applicant_1":
                #     print(player.get_random_value())
        # csv
        # row_csv=[]
        # row_csv.append(self.organisation.round)
        # row_csv.append(player.get_name())
        # row_csv.extend(player.get_preference().return_preference_not_kimita())
        # row_csv.append(player.random_value)
        # preference_csv.append(row_csv)

        # print(preference_csv)

        # 乱数値に基づきソート
        sorted_players = sorted(applicant_list, key=lambda x: x.get_random_value())
        logger.debug("今回の割当順")
        logger.debug(f"プレイヤー名: {[v.name for v in sorted_players]}")
        logger.debug(f"プレイヤーの優先順: {[v.priority for v in sorted_players]}")
        # logger.info(f"プレイヤー名: {[v.name for v in sorted_players]}")
        # logger.info(f"プレイヤーの優先順: {[v.priority for v in sorted_players]}")

        # 希望順に割り当て
        allocation = Allocation(slot_list)
        for applicant in sorted_players:
            if applicant.name == "applicant_1":
                decision_list = applicant.make_random_decision(message_list, slot_list)
            else:
                decision_list = applicant.make_decision(message_list, slot_list)
            # if len(decision_list) > 0:
            #     # 1つ以上希望を出したので、その組織に予約希望を出した応募者として登録
            #     self.organisation.register_requested_applicant(applicant)
            # logger.debug(f"{applicant.name}のメッセージ")
            # logger.debug([v.name for v in decision_list])
            # csv
            # row_csv=[]
            # row_csv.append(self.organisation.round)
            # row_csv.append(applicant.name)
            # for v in decision_list:
            #     row_csv.append(v.name)
            # message_csv.append(row_csv)

            for message in decision_list:
                agent_added_in_messaged = []
                slot_in_message = message.get_slot_list()
                random.shuffle(slot_in_message)
                for slot in slot_in_message:
                    if slot.available():
                        slot.add(applicant)
                        applicant.reserve_slot(slot)
                        allocation.add(slot, applicant)
                        agent_added_in_messaged.append(applicant)
                        break
                if len(agent_added_in_messaged) != 0:
                    break
        # csv
        # row_csv=[]
        # row_csv.append(self.organisation.round)
        # for key,value in allocation.allocation.items():
        #     applicant_list=[]
        #     for applicant in value:
        #         applicant_list.append(applicant.name)
        #     row_csv.append(applicant_list)
        # allocation_csv.append(row_csv)

        return allocation
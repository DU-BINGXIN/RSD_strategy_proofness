from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

import pandas as pd
import random
import copy
from util.logger import logger
from vaccine_booking.elements.allocation import Allocation
from vaccine_booking.elements.basics.result_writer import Result, Writable
from vaccine_booking.elements.message import Message
from vaccine_booking.elements.slot import Slot, outside

if TYPE_CHECKING:
    from vaccine_booking.algorithms.algorithm import Algorithm
    from vaccine_booking.elements.applicant import Applicant

# kakogawa city/hospital
class Organisation(Writable):
    def __init__(self, name: str) -> None:
        from vaccine_booking.game import config_manager

        super().__init__(name)
        self.name = name
        self.round: int
        self.slot_list: List[Slot] = []  # この組織が持ってるスロットのリスト(outside含まず)
        self.message_list: List[Message] = []  # この組織が採用しているMessageのList
        self.applicant_list: List[Applicant] = []
        self.object_allocation: Dict[str, list] = {}
        # ↓ちゃんと希望を出したApplicantのリスト (make_decisionが[]では無かったApplicant)
        self.requesting_applicant_list: List[Applicant] = []
        self.result = Result(
            [
                "applicant_nums",
                "cancel_nums",
                "vaccination_nums",
                "capacity",
            ]
        )

        logger.info(f"set up slots in {self.name}")
        for slot_name, capacity in config_manager.get_level1_slot_data(
            organisation_name=self.name
        ):
            self.slot_list.append(
                Slot(
                    name=slot_name,
                    capacity=capacity,
                )
            )
        logger.info(f"set up messages in {self.name}")
        for (
            message_name,
            capacity,
            message_slot_name_list,
        ) in config_manager.get_level1_message_data(organisation_name=self.name):
            slot_list_temp = []
            for slot_name in message_slot_name_list:
                for slot in self.slot_list:
                    if slot_name == slot.get_name():
                        slot_list_temp.append(slot)
            self.message_list.append(
                Message(name=message_name, capacity=capacity, slot_list=slot_list_temp)
            )

    def initialize(self) -> None:
        self.applicant_list = []
        self.requesting_applicant_list = []

    def get_allocation(self) -> Allocation:
        return self.allocation

    def get_object_allocation(self) -> Allocation:
        return self.object_allocation

    def get_applicant_list(self) -> List[Applicant]:
        return self.applicant_list

    def get_requesting_applicant_list(self) -> List[Applicant]:
        return self.requesting_applicant_list

    def get_name(self) -> str:
        return self.name

    def get_slot_list(self) -> List[Slot]:
        return self.slot_list

    def get_message_list(self) -> List[Message]:
        return self.message_list

    def set_algorithm(self, algorithm: Algorithm) -> None:
        self.algorithm = algorithm

    def set_applicant_list(self, applicant_list: List[Applicant]) -> None:
        self.applicant_list = applicant_list

    def register_requested_applicant(self, applicant: Applicant) -> None:
        self.requesting_applicant_list.append(applicant)

    def execute(self) -> Allocation:
        """
        申込者（applicant_list）に対して、予約割り当てのアルゴリズムを実行する。
        """
        self.allocation = self.algorithm.execute(
            applicant_list=self.applicant_list,
            slot_list=self.slot_list,
            message_list=self.message_list,
        )
        return self.allocation

    def execute_random(self) -> Allocation:
        """
        申込者（applicant_list）に対して、予約割り当てのアルゴリズムを実行する。
        """
        self.random_allocation = self.algorithm.execute_random(
            applicant_list=self.applicant_list,
            slot_list=self.slot_list,
            message_list=self.message_list,
        )
        return self.random_allocation

    def current_print(self):
        from vaccine_booking.game import config_manager

        logger.info(f"[{self.name}]")
        cancel_nums = 0
        for slot in self.slot_list:
            cancel_nums += slot.get_cancel_nums()
        vaccination_nums = 0
        for slot in self.slot_list:
            vaccination_nums += len(slot.get_allocation())
        capacity = sum(config_manager.set_capacity(organisation_name=self.name))
        applicant_nums = len(self.requesting_applicant_list)
        logger.info(f"# of Applicants: {applicant_nums}")
        logger.info(f"# of Cancels: {cancel_nums}")
        logger.info(f"Vaccination rate: {vaccination_nums}/{capacity}")

        # Result にこのRoundのデータを追加
        self.result.add_row(
            column_names=[
                "applicant_nums",
                "cancel_nums",
                "vaccination_nums",
                "capacity",
            ],
            row_data=[
                applicant_nums,
                cancel_nums,
                vaccination_nums,
                capacity,
            ],
        )

    def current_print_random(self):
        from vaccine_booking.game import config_manager

        logger.info(f"[{self.name}]")
        cancel_nums = 0
        for slot in self.slot_list:
            cancel_nums += slot.get_cancel_nums()
        vaccination_nums = 0
        for slot in self.slot_list:
            vaccination_nums += len(slot.get_allocation())
        capacity = sum(config_manager.set_capacity(organisation_name=self.name))
        applicant_nums = len(self.requesting_applicant_list)
        logger.info(f"# of Applicants: {applicant_nums}")
        logger.info(f"# of Cancels: {cancel_nums}")
        logger.info(f"Vaccination rate: {vaccination_nums}/{capacity}")

        # Result にこのRoundのデータを追加
        self.result.add_row(
            column_names=[
                "applicant_nums",
                "cancel_nums",
                "vaccination_nums",
                "capacity",
            ],
            row_data=[
                applicant_nums,
                cancel_nums,
                vaccination_nums,
                capacity,
            ],
        )

    def get_result(self) -> Dict[str, List[float]]:
        return self.result.get_data_dict()

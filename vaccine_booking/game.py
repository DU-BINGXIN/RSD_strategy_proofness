from __future__ import annotations

import os
import random
from typing import TYPE_CHECKING, Dict, List

import pandas as pd
from util.logger import logger

from vaccine_booking.algorithms.RSD.random_serial_dictatorship import (
    RandomSerialDictatorship,
)
from vaccine_booking.elements.applicant import Applicant
from vaccine_booking.elements.basics.result_writer import Result, ResultWriter, Writable
from vaccine_booking.elements.message import Message
from vaccine_booking.elements.organisation import Organisation
from vaccine_booking.elements.preference import Preference
from vaccine_booking.elements.slot import Slot, outside
from vaccine_booking.settings.config import ConfigManager
from vaccine_booking.strategies.maximax import Maximax
from vaccine_booking.strategies.minimax import Minimax
from vaccine_booking.strategies.mean import Mean
from vaccine_booking.strategies.strategy import Strategy
import ray
import wandb


logger.info("(reading json file ...)")
# Json から読み込んだデータを DataClass として config に保存
config_manager = ConfigManager(os.environ["SETTING_NAME"])
global_config = config_manager.get_global_config()
configs = config_manager.get_configs()
## csv関連
# preference_csv=[]
# preference_csv.append(["round","applicant_id","市民会館_weekday_Mon_am_9-10","市民会館_weekday_Mon_am_10-11","市民会館_weekday_Mon_pm_13-14","市民会館_weekday_Mon_pm_14-15","市民会館_weekend_Sat_am_9-10","市民会館_weekend_Sat_am_10-11","市民会館_weekend_Sat_pm_13-14","市民会館_weekend_Sat_pm_14-15","outside","RSDの順番"])
# message_csv=[]
# message_csv.append(["round","applicant_id","メッセージ1","メッセージ2","メッセージ3","メッセージ4"])
# allocation_csv=[]
# allocation_csv.append(["round","市民会館_weekday_Mon_am_9-10","市民会館_weekday_Mon_am_10-11","市民会館_weekday_Mon_pm_13-14","市民会館_weekday_Mon_pm_14-15","市民会館_weekend_Sat_am_9-10","市民会館_weekend_Sat_am_10-11","市民会館_weekend_Sat_pm_13-14","市民会館_weekend_Sat_pm_14-15"])
# cancel_csv=[]
# cancel_csv.append(["round","applicant_0","applicant_1","applicant_2","applicant_3","applicant_4","applicant_5","applicant_6","applicant_7","applicant_8","applicant_9"])


class Game(Writable):
    def __init__(self, name: str, strategy: Strategy, seed: int, iter: int):
        # super().__init__(name)  # Wrirable親クラスの init を呼び出す
        self.seed = seed
        self.iter = iter
        self.name = name
        self.strategy = strategy
        self.false_utility = 0
        self.truth_utility = 0
        self.all_applicant_list: List[Applicant] = []
        self.organisation_list: List[Organisation] = []
        self.all_slot_list: List[Slot] = []
        self.all_message_list: List[Message] = []
        self.result = Result(
            [
                "truth_telling_utility",
            ]
        )
        self.result_random = Result(
            [
                "false_telling_utility",
            ]
        )
        self._setup()

    def _setup(self):
        logger.info("set up organisations")
        for organisation_name, config in configs.items():
            organisation = Organisation(organisation_name)
            cls = globals()[config.algorithm]  # jsonで書かれたクラス名をインスタンス化
            algorithm = cls(organisation)
            organisation.set_algorithm(algorithm)
            self.organisation_list.append(organisation)
            logger.info(
                f"   -> {organisation_name} uses **{algorithm.__class__.__name__}**"
            )

        logger.info("set up all slots")
        slot_list_temp = []
        for organisation in self.organisation_list:
            slot_list_temp.append(organisation.get_slot_list())
        self.all_slot_list = sum(slot_list_temp, [])  # Listの入れ子を解除
        # Outside として特別なスロットを追加
        self.all_slot_list.append(outside)

        logger.info("set up all messages")
        message_list_temp = []
        for organisation in self.organisation_list:
            message_list_temp.append(organisation.get_message_list())
        self.all_message_list = sum(message_list_temp, [])  # Listの入れ子を解除
        # # Outside として特別なスロットを追加
        # self.all_message_list.append(outside) # messageの平均値はoutsideより低くなると、outsideを報告する

        logger.info("set up applicants")
        # for applicant_name, priority in config_manager.get_applicant_data():
        for applicant_name in config_manager.get_applicant_data():
            self.all_applicant_list.append(
                Applicant(
                    applicant_name,
                    self.all_slot_list,  # 組織を超えた全Slot
                    self.all_message_list,
                    self.strategy,
                )
            )

        logger.info("set up preference for slot")
        # 選好の設定 (ランダム、無差別含む)
        # random.seed(self.iter)
        for applicant in self.all_applicant_list:
            slot_pref = Preference()
            outside_value = random.gauss(5, 2)
            applicant.outside_value = outside_value
            for slot in self.all_slot_list:
                if slot != outside:
                    slot_pref.set(slot, random.gauss(10, 3) - applicant.outside_value)
                else:
                    slot_pref.set(slot, 0)
            applicant.set_preference(slot_pref)
            slot_pref.set_owner(applicant)
        random.seed(self.seed + 100 * self.iter)
        for applicant in self.all_applicant_list:
            if applicant.name == "applicant_1":
                slot_pref_random = Preference()
                outside_value = random.gauss(5, 2)
                applicant.outside_value = outside_value
                for slot in self.all_slot_list:
                    if slot != outside:
                        slot_pref_random.set(
                            slot, random.gauss(10, 3) - applicant.outside_value
                        )
                    else:
                        slot_pref_random.set(slot, 0)
                applicant.set_random_preference(slot_pref_random)
                slot_pref_random.set_owner(applicant)
        # 確認のためのprint
        # for applicant in self.all_applicant_list:
        #     applicant.get_preference().print_preference()

    def current_print(self) -> None:
        wandb.init(
            entity="pj_vb",
            project="RSD_strategy_proofness",
            group="level1_ALLbids",
            name=f"run{self.iter}",
        )
        logger.info("[Summary]")
        logger.info(f"# of Unvaccinated People：{self.unvaccination_nums}")
        logger.info(f"# of People who canceled more than one: {self.cancel_nums}")

        resident_j_utility = 0
        vaccination_nums = 0
        residents_utility = 0
        total_capacity = 0
        for organisation in self.organisation_list:
            total_capacity = sum(
                config_manager.set_capacity(organisation_name=organisation.name)
            )
        for i in self.all_slot_list:
            # print(i.get_allocation())
            vaccination_nums += len(i.get_allocation())
            for app in i.get_allocation():
                residents_utility += (
                    app.get_preference().get_utility_value(i) + app.outside_value
                )
                if app.name == "applicant_1":
                    resident_j_utility = (
                        app.get_preference().get_utility_value(i) + app.outside_value
                    )
                    self.truth_utility = resident_j_utility
        # logger.info(f"Vaccination Rate: {vaccination_nums}/{total_capacity}")
        logger.info(f"resident j's truth-telling value: {resident_j_utility}")
        # Resultクラスにデータを保存
        self.result.add_row(
            column_names=[
                "truth_telling_utility",
            ],
            row_data=[
                resident_j_utility,
            ],
        )
        wandb.log(
            {
                "true_resident_utility": residents_utility,
                "truth_telling_utility": resident_j_utility,
            }
        )

        # ****** 以下、Debug時の出力 *****
        logger.debug("結果を出力します")
        for organisation, allocation in self.allocation_dict.items():
            logger.debug(f"{organisation.get_name()}:")
            # allocation.print_allocation()
        logger.debug("接種状況の詳細を出力します(キャンセル処理後)")
        for slot in self.all_slot_list:
            logger.debug(
                f"{slot.get_name()}: {[str(v) for v in slot.get_allocation()]}"
            )

    def current_print_random(self) -> None:
        logger.info("[Summary]")
        logger.info(f"# of Unvaccinated People：{self.unvaccination_nums}")
        logger.info(f"# of People who canceled more than one: {self.cancel_nums}")
        resident_j_utility = 0
        vaccination_nums = 0
        residents_utility = 0
        total_capacity = 0
        for organisation in self.organisation_list:
            total_capacity = sum(
                config_manager.set_capacity(organisation_name=organisation.name)
            )
        for i in self.all_slot_list:
            # print(i.get_allocation())
            vaccination_nums += len(i.get_allocation())
            for app in i.get_allocation():
                residents_utility += (
                    app.get_preference().get_utility_value(i) + app.outside_value
                )
                if app.name == "applicant_1":
                    resident_j_utility = (
                        app.get_preference().get_utility_value(i) + app.outside_value
                    )
                    self.false_utility = resident_j_utility
        # logger.info(f"Vaccination Rate: {vaccination_nums}/{total_capacity}")
        logger.info(f"resident j's false-telling value: {resident_j_utility}")
        # Resultクラスにデータを保存
        self.result_random.add_row(
            column_names=[
                "false_telling_utility",
            ],
            row_data=[
                resident_j_utility,
            ],
        )

        wandb.log(
            {
                "false_resident_utility": residents_utility,
                "false_telling_utility": resident_j_utility,
            }
        )
        # ****** 以下、Debug時の出力 *****
        logger.debug("結果を出力します")
        for organisation, allocation in self.allocation_dict.items():
            logger.debug(f"{organisation.get_name()}:")
            # allocation.print_allocation()
        logger.debug("接種状況の詳細を出力します(キャンセル処理後)")
        for slot in self.all_slot_list:
            logger.debug(
                f"{slot.get_name()}: {[str(v) for v in slot.get_allocation()]}"
            )

    def get_all_applicant_list(self) -> List[Applicant]:
        return self.all_applicant_list

    def get_all_slot_list(self) -> List[Slot]:
        return self.all_slot_list

    def get_result(self) -> Dict[str, List[float]]:
        return self.result.get_data_dict()

    def start(self):
        round_nums = global_config.round_nums  # 繰り返しゲームのラウンド数

        logger.info("run algorithm")
        for round in range(1, round_nums + 1):
            logger.info(f"########## True Round {round} ############")
            # random.seed()
            # 初期化
            self.current_applicant_list = []
            for applicant in self.all_applicant_list:
                applicant.initialize()
                if applicant.get_vaccination_nums() == 0:
                    self.current_applicant_list.append(applicant)
            for slot in self.all_slot_list:
                slot.initialize()
            for organisation in self.organisation_list:
                organisation.initialize()
                organisation.set_applicant_list(self.current_applicant_list)

            # 各組織でアルゴリズム実行
            self.allocation_dict = {}
            for organisation in self.organisation_list:
                # key=Organisationクラス、value=Allocationクラス として設定
                organisation.round = round
                self.allocation_dict[organisation] = organisation.execute()

            # ワクチン接種とキャンセルカウント
            logger.debug("キャンセル確認：")
            self.unvaccination_nums = 0
            self.cancel_nums = 0
            row_csv = []
            row_csv.append(round)
            for i in self.current_applicant_list:
                if len(i.get_decision()) > 0:
                    self.unvaccination_nums += 1
                    i.vaccinate()  # ワクチン接種（キャンセルしたらcancel=Trueに）
                    if i.is_cancelled():
                        self.cancel_nums += 1
                        logger.debug(f"cancel:{i.get_name()}")

            # for player in self.all_applicant_list:
            #     row_csv.append(player.cancel)
            # cancel_csv.append(row_csv)

            # 結果の出力
            if round == 1:
                self.result_writer = ResultWriter(*self.organisation_list)
                self.result_writer.add(self)  # このゲーム自身も Writableの子クラスのため追加可
            self.result_writer.current_print()

    def start_random(self):
        round_nums = global_config.round_nums  # 繰り返しゲームのラウンド数
        logger.info("run algorithm")
        for round in range(1, round_nums + 1):
            logger.info(f"########## False Round {round} ############")
            # random.seed()
            # 初期化
            self.current_applicant_list = []
            for applicant in self.all_applicant_list:
                applicant.initialize()
                if applicant.get_vaccination_nums_random() == 0:
                    self.current_applicant_list.append(applicant)
            for slot in self.all_slot_list:
                slot.initialize()
            for organisation in self.organisation_list:
                organisation.initialize()
                organisation.set_applicant_list(self.current_applicant_list)

            # 各組織でアルゴリズム実行
            self.allocation_dict = {}
            for organisation in self.organisation_list:
                # key=Organisationクラス、value=Allocationクラス として設定
                organisation.round = round
                self.allocation_dict[organisation] = organisation.execute_random()

            # ワクチン接種とキャンセルカウント
            logger.debug("キャンセル確認：")
            self.unvaccination_nums = 0
            self.cancel_nums = 0
            row_csv = []
            row_csv.append(round)
            for i in self.current_applicant_list:
                if len(i.get_decision()) > 0:
                    self.unvaccination_nums += 1
                    i.vaccinate()  # ワクチン接種（キャンセルしたらcancel=Trueに）
                    if i.is_cancelled():
                        self.cancel_nums += 1
                        logger.debug(f"cancel:{i.get_name()}")

            # for player in self.all_applicant_list:
            #     row_csv.append(player.cancel)
            # cancel_csv.append(row_csv)

            # 結果の出力
            if round == 1:
                self.result_writer = ResultWriter(*self.organisation_list)
                self.result_writer.add(self)  # このゲーム自身も Writableの子クラスのため追加可
            self.result_writer.current_print_random()

        logger.info("########## End of Simulation ############")
        logger.info("save summary output as csv")

        # import csv
        # f = open('./output/preference.csv', 'w')
        # writer = csv.writer(f)
        # writer.writerows(preference_csv)
        # f.close()
        # f = open('./output/message.csv', 'w')
        # writer = csv.writer(f)
        # writer.writerows(message_csv)
        # f.close()
        # f = open('./output/allocation.csv', 'w')
        # writer = csv.writer(f)
        # writer.writerows(allocation_csv)
        # f.close()
        # f = open('./output/cancel_csv.csv', 'w')
        # writer = csv.writer(f)
        # writer.writerows(cancel_csv)
        # f.close()

        # self.result_writer.write_to_csv("./output")

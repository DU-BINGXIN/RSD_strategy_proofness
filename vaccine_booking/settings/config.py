import json
import logging
import random
from dataclasses import dataclass
from typing import Dict, List, Optional

# from pydantic import BaseModel

from util.logger import logger
from vaccine_booking.elements.slot import Slot


@dataclass
class Config:
    """
    jsonの設定ファイルから読み込みこんだデータの Dataclass。
    本クラスで定義する変数名と、json の key の名称を揃えること。
    """

    algorithm: str
    hierarchy_structure: Dict[str, list]
    venues: Dict[str, list]
    days: Dict[str, list]
    dates: Dict[str, list]
    times: Dict[str, list]

    def __post_init__(self):

        self.venue_list = []
        for venue_name in self.venues.keys():
            self.venue_list.append(venue_name)

        self.days_list = []
        for day_name in self.days.keys():
            self.days_list.append(day_name)

        self.dates_list = []
        for date_name in self.dates.keys():
            self.dates_list.append(date_name)

        self.times_list = []
        for time_name in self.times.keys():
            self.times_list.append(time_name)

        logger.debug(f"venue_list={self.venue_list}")
        logger.debug(f"days_list={self.days_list}")
        logger.debug(f"dates_list={self.dates_list}")
        logger.debug(f"times_list={self.times_list}")


@dataclass
class GlobalConfig:
    """
    jsonの設定ファイルから読み込みこんだデータの Dataclass。
    Config クラスは各組織（Organisationクラス）に関わるデータを保持
    するのに対して、GlobalConfig はシミュレーション全般に関わる変数を格納している。
    """

    #    # ゲームのトータルの繰り返し回数
    round_nums: int
    # # 応募者の人数
    # applicants: int
    # message level
    message_level: int
    # 応募者の人数
    applicant_nums: int


class ConfigManager:

    # Dataclass を管理するクラス。

    # #使い方サンプル
    # import configs #(game.py で configs を定義するのが吉)

    # x = configs['organisation_name'].sites

    def __init__(self, setting_name: str) -> None:
        self.name = setting_name
        self.global_config: Optional[GlobalConfig] = None
        self.config_dict: Dict[str, Config] = {}

        with open(f"settings/{setting_name}.json", encoding="utf-8") as f:
            self.config_json = json.load(f)

        for key, value in self.config_json.items():
            if key == "global_settings":
                self.global_config = GlobalConfig(**value)
            else:  # key=kakogawa city
                logging.debug(f"Organisation={key}")
                # keyは組織名で value は json ファイルの organisation 毎のデータセット一式が入る
                self.config_dict[key] = Config(**value)

    def get_applicant_data(self) -> zip:
        name_list = []
        for i in range(self.global_config.applicant_nums):
            name_list.append(f"applicant_{i}")
        return list(name_list)

    def get_configs(self) -> Dict[str, Config]:
        return self.config_dict

    def get_global_config(self) -> Optional[GlobalConfig]:
        return self.global_config

    def set_capacity(self, organisation_name: str) -> List[int]:
        capacity_list = []
        for venue, days in self.config_dict[organisation_name].venues.items():
            for day in days:
                for date in self.config_dict[organisation_name].days[day]:
                    for time in self.config_dict[organisation_name].dates[date]:
                        for hour in self.config_dict[organisation_name].times[time]:
                            # capacity_list.append(random.randint(1,2))
                            capacity_list.append(1)  # test用
        return capacity_list

    def get_level1_slot_data(self, organisation_name: str) -> zip:
        slot_list = []
        capacity_list = self.set_capacity(organisation_name)
        for venue, days in self.config_dict[organisation_name].venues.items():
            for day in days:
                for date in self.config_dict[organisation_name].days[day]:
                    for time in self.config_dict[organisation_name].dates[date]:
                        for hour in self.config_dict[organisation_name].times[time]:
                            slot_list.append(f"{venue}_{day}_{date}_{time}_{hour}")
        return zip(slot_list, capacity_list)

    def get_level1_message_data(self, organisation_name: str) -> zip:
        a = 0  # record the iteriation rounds
        message_name_list = []
        capacity_list = []
        slot_list_list: List(List(str)) = []
        for venue, days in self.config_dict[organisation_name].venues.items():
            for day in days:
                for date in self.config_dict[organisation_name].days[day]:
                    for time in self.config_dict[organisation_name].dates[date]:
                        for hour in self.config_dict[organisation_name].times[time]:
                            message_name_list.append(
                                f"{venue}_{day}_{date}_{time}_{hour}"
                            )
                            temp_cap = 0
                            slotlist = []
                            temp_cap = self.set_capacity(organisation_name)[a]
                            a += 1
                            slotlist.append(f"{venue}_{day}_{date}_{time}_{hour}")
                            slot_list_list.append(slotlist)
                            capacity_list.append(temp_cap)
        return zip(message_name_list, capacity_list, slot_list_list)

    def get_level2_message_data(self, organisation_name: str) -> zip:
        a = 0  # record the iteriation rounds
        message_name_list = []
        capacity_list = []
        slot_list_list: List(List(str)) = []
        for venue, days in self.config_dict[organisation_name].venues.items():
            for day in days:
                for date in self.config_dict[organisation_name].days[day]:
                    for time in self.config_dict[organisation_name].dates[date]:
                        message_name_list.append(f"{venue}_{day}_{date}_{time}")
                        temp_cap = 0
                        slotlist = []
                        for hour in self.config_dict[organisation_name].times[time]:
                            temp_cap = (
                                temp_cap + self.set_capacity(organisation_name)[a]
                            )
                            a += 1
                            slotlist.append(f"{venue}_{day}_{date}_{time}_{hour}")
                        slot_list_list.append(slotlist)
                        capacity_list.append(temp_cap)
        return zip(message_name_list, capacity_list, slot_list_list)

    def get_level3_message_data(self, organisation_name: str) -> zip:
        a = 0  # record the iteriation rounds
        message_name_list = []
        capacity_list = []
        slot_list_list: List(List(str)) = []
        for venue, days in self.config_dict[organisation_name].venues.items():
            for day in days:
                for date in self.config_dict[organisation_name].days[day]:
                    message_name_list.append(f"{venue}_{day}_{date}")
                    temp_cap = 0
                    slotlist = []
                    for time in self.config_dict[organisation_name].dates[date]:
                        for hour in self.config_dict[organisation_name].times[time]:
                            temp_cap = (
                                temp_cap + self.set_capacity(organisation_name)[a]
                            )
                            a += 1
                            slotlist.append(f"{venue}_{day}_{date}_{time}_{hour}")
                    slot_list_list.append(slotlist)
                    capacity_list.append(temp_cap)
        return zip(message_name_list, capacity_list, slot_list_list)

    def get_level4_message_data(self, organisation_name: str) -> zip:
        a = 0  # record the iteriation rounds
        message_name_list = []
        capacity_list = []
        slot_list_list: List(List(str)) = []
        for venue, days in self.config_dict[organisation_name].venues.items():
            for day in days:
                message_name_list.append(f"{venue}_{day}")
                temp_cap = 0
                slotlist = []
                for date in self.config_dict[organisation_name].days[day]:
                    for time in self.config_dict[organisation_name].dates[date]:
                        for hour in self.config_dict[organisation_name].times[time]:
                            temp_cap = (
                                temp_cap + self.set_capacity(organisation_name)[a]
                            )
                            a += 1
                            slotlist.append(f"{venue}_{day}_{date}_{time}_{hour}")
                slot_list_list.append(slotlist)
                capacity_list.append(temp_cap)
        return zip(message_name_list, capacity_list, slot_list_list)

    def get_level5_message_data(self, organisation_name: str) -> zip:
        a = 0  # record the iteriation rounds
        message_name_list = []
        capacity_list = []
        slot_list_list: List(List(str)) = []
        for venue, days in self.config_dict[organisation_name].venues.items():
            message_name_list.append(f"{venue}")
            temp_cap = 0
            slotlist = []
            for day in days:
                for date in self.config_dict[organisation_name].days[day]:
                    for time in self.config_dict[organisation_name].dates[date]:
                        for hour in self.config_dict[organisation_name].times[time]:
                            temp_cap = (
                                temp_cap + self.set_capacity(organisation_name)[a]
                            )
                            a += 1
                            slotlist.append(f"{venue}_{day}_{date}_{time}_{hour}")
            slot_list_list.append(slotlist)
            capacity_list.append(temp_cap)
        return zip(message_name_list, capacity_list, slot_list_list)
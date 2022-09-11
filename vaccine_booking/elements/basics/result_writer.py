import sys
from abc import ABCMeta, abstractmethod
from typing import Dict, List

import pandas as pd
from util.logger import logger


class Result:
    """
    結果のデータを格納するクラス。Dict[str, List[float]] としてメンバ変数を持つ。
    Dictのkeyにcolumn_nameを、valueにRound順のデータをリストとして保持する。

    Writableクラスを継承したクラスで利用すると良い。
    """

    def __init__(self, column_names: List[str] = []) -> None:
        self.data_dict: Dict[str, List[float]] = {}
        self.index_list: List[int] = []  # DataFrameのindexの指定のために使う
        for column_name in column_names:
            self.data_dict[column_name] = []  # 空で初期化

    def set_column_names(self, column_names: List[str] = []) -> None:
        self.column_names = column_names

    def add_row(self, column_names: List[str], row_data: List[float]) -> None:
        """
        1行分のデータを追加する。データサイズの異なる値が引数に入れられるとエラーで強制終了する。
        """
        if (len(self.data_dict.keys()) == len(row_data)) and (
            len(self.data_dict.keys()) == len(column_names)
        ):
            for column_name, value in zip(column_names, row_data):
                self.data_dict[column_name].append(value)
        else:
            logger.error("Data size is different!")
            sys.exit()  # 強制終了させる

    def get_data_dict(self):
        return self.data_dict


class Writable(metaclass=ABCMeta):
    """
    抽象クラス。このクラスを継承し、current_print(), csv_write() メソッドを実装する。
    ResultWriterクラスに、このクラスを継承したクラスのインスタンスを追加し、
    そこから呼び出される。

    JavaのInterfaceとしての使い方と同様。
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def current_print(self) -> None:
        pass 

    @abstractmethod
    def current_print_random(self) -> None:
        pass 

    def get_name(self) -> str:
        return self.name

    @abstractmethod
    def get_result(self) -> Dict[str, List[float]]:
        pass


class ResultWriter:
    def __init__(self, *writables: Writable) -> None:
        self.writable_list: List[Writable] = list(writables)

    def add(self, writable: Writable) -> None:
        self.writable_list.append(writable)

    def current_print(self) -> None:
        for writable in self.writable_list:
            writable.current_print()   

    def current_print_random(self) -> None:
        for writable in self.writable_list:
            writable.current_print_random()   

    def write_to_csv(self, file_path: str):
        for writable in self.writable_list:
            filename = writable.get_name()
            df = pd.DataFrame(writable.get_result())
            df.to_csv(f"{file_path}/{filename}.csv")

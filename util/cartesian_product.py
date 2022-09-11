from typing import Any, Generator, Iterator, List, Optional, Tuple

import numpy as np


class CartesianProduct:
    def __init__(self) -> None:
        pass

    def product(self, *args: Any) -> Generator[Tuple[Any, ...], None, None]:  # 可変長引数
        """
        引数から直積を生成するGenerator。引数には文字列や数値のリストを2つ以上設定する。

        戻り値でgeneratorを返すので、next() で1つずつ取り出せる。
        for i in Cartesian#product() で利用するのが一般的な使い方。
        """

        # 引数で与えられた全てのリストをここにlist of lists で保存
        self.__full_list = []
        for i in args:
            self.__full_list.append(i)

        # イテレータのリストを作成
        it_list = []
        for i in self.__full_list:
            it_list.append(iter(i))

        # 初期状態をセット
        output = []
        for i in it_list:
            output.append(next(i))
        yield tuple(output)  # 1回目の yield はここで

        while True:
            try:
                update_list = self.__get_target_element(0, it_list)
                for index, target in update_list:
                    output[index] = target  # outputを更新
                yield tuple(output)  # 2回目以降はここ
            except StopIteration:
                break  # 返すものが無くなればループを出て generator は終了

    def __get_target_element(
        self,
        index: int,
        it_list: List[Iterator],
    ) -> List[Tuple[int, Any]]:
        """
        再帰関数で定義。戻り値は outputの変更すべき index値と、そこに代入する
        値 (String or float) のタプル (index, target) のリストが返る。
        リストになっている理由は、桁が上がる（outputのindex値が上がる）場合に
        複数の箇所を更新する場合があるからである。もしも次がなければ StopIteration を投げる。
        """

        if index < len(it_list):
            try:
                # ↓もし次がなければここで StopIteration が投げられる
                target = next(it_list[index])
                return [(index, target)]
            except StopIteration:
                new_it = iter(self.__full_list[index])  # イテレータを新規作成
                it_list[index] = new_it  # 古いのと入れ替え
                return [(index, next(new_it))] + self.__get_target_element(
                    index + 1,
                    it_list,
                )
        else:
            raise StopIteration

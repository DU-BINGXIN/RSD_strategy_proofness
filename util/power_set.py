from typing import Any, Generator, List


class PowerSet:
    """
    冪集合を作るクラス。
    """

    def generator(self, args: List) -> Generator[List[Any], None, None]:
        """
        引数で与えられた要素から冪集合を生成する。なお、可変長引数に
        しているので、必要な集合の要素を全て引数にセットすればOK。
        Generator として定義。CartesianProduct#product()
        と同じように使う。
        """
        if len(args) > 0:
            for i in self.generator(args[1:]):
                yield [args[0]] + i
                yield i
        else:
            yield []

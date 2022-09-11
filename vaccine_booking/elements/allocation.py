from util.logger import logger


class Allocation:
    """
    全てのSlotの割り当て格納するクラス。扱いやすようにするため。
    スロットは (Slot, List[player]) のDictionary型で定義。その全組み合わせのリストを内部で保持する。
    """

    def __init__(self, slot_list) -> None:
        # 辞書形式で持つ key=Slot, value=List[Player]
        self.allocation = {}
        for key in slot_list:
            self.allocation[key] = []  # まずは空で初期化

    def items(self):
        return self.allocation.items()
        
    def add(self, slot, player):
        self.allocation[slot].append(player)

    def print_allocation(self):
        for k, v in self.allocation.items():
            temp = [str(player) for player in v]
            logger.debug(f"{str(k)}: {temp}")

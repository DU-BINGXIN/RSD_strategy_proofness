import random
import click
import wandb
from util.logger import logger
from vaccine_booking.algorithms.RSD.random_serial_dictatorship import (
    RandomSerialDictatorship,
)
from vaccine_booking.game import Game
from vaccine_booking.strategies.all_acceptable_candidates_telling_with_one import (
    AllAcceptableCandidatesTellingWithOne,
)
from vaccine_booking.strategies.all_acceptable_candidates_telling import (
    AllAcceptableCandidatesTelling,
)
from vaccine_booking.strategies.all_highest_utility_candidates_telling import (
    AllHighestUtilityCandidatesTelling,
)
from vaccine_booking.strategies.highest_utility_one_telling import (
    HighestUtilityOneTelling,
)
from vaccine_booking.strategies.random_one_telling import (
    RandomOneTelling,
)
from vaccine_booking.strategies.maximax import (
    Maximax
)
from vaccine_booking.strategies.minimax import (
    Minimax
)
from vaccine_booking.strategies.mean import (
    Mean
)
from vaccine_booking.strategies.strategy import Strategy
import wandb

@click.command()
@click.option("-s", "--setting_name", required=True, type=str)
@click.option("--applicant_strategy", required=True, type=str)
@click.option("--iter", required=True, type=int)
def main(setting_name, applicant_strategy, iter):
    for x in range(100):
    ##################
    #random.seed(1)
    ##################

        logger.info("run simulation: Vaccine booking mechanisms")
        logger.info(f"setting: {setting_name}")
        logger.info(f"strategy: {applicant_strategy}")
            
        # 引数で指定したクラス名の Strategy をインスタンス化する
        cls = globals()[applicant_strategy]
        strategy = cls()

        # Game, Algorithmのインスタンス化
        g = Game(name="VBG", strategy=strategy, seed=x, iter=iter)

        # Game 開始
        false_utility=0
        for i in range(10):
            g.start_random()
            false_utility += g.false_utility
        mean_false_utility = false_utility/10

        wandb.log({"Mean utility of false-telling": mean_false_utility})


if __name__ == "__main__":
    main()

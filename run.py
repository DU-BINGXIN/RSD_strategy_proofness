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
from vaccine_booking.strategies.maximax import Maximax
from vaccine_booking.strategies.minimax import Minimax
from vaccine_booking.strategies.mean import Mean
from vaccine_booking.strategies.strategy import Strategy
import wandb

# import ray
# ray.init()
@click.command()
@click.option("-s", "--setting_name", required=True, type=str)
@click.option("--applicant_strategy", required=True, type=str)
@click.option("--iter", required=True, type=int)
def main(setting_name, applicant_strategy, iter):

    ##################
    # random.seed(1)
    ##################

    logger.info("run simulation: Truth-telling")
    logger.info(f"setting: {setting_name}")
    logger.info(f"strategy: {applicant_strategy}")

    # 引数で指定したクラス名の Strategy をインスタンス化する
    cls = globals()[applicant_strategy]
    strategy = cls()

    # Game, Algorithmのインスタンス化
    g = Game(name="VBG", strategy=strategy, seed=1, iter=iter)
    random.seed(g.iter)
    # Game 開始
    g.start()
    true_utility = g.truth_utility
    false_utility = 0

    for x in range(100):

        logger.info("run simulation: False-telling")
        logger.info(f"setting: {setting_name}")
        logger.info(f"strategy: {applicant_strategy}")

        # 引数で指定したクラス名の Strategy をインスタンス化する
        cls = globals()[applicant_strategy]
        strategy = cls()

        # Game, Algorithmのインスタンス化
        g_random = Game(name="VBG", strategy=strategy, seed=x, iter=iter)
        random.seed(g_random.iter)
        # Game 開始
        g_random.start_random()
        false_utility += g_random.false_utility
    mean_false_utility = false_utility / 100
    # false_utility_list.append(mean_false_utility)
    wandb.log({"Mean utility of false-telling": mean_false_utility})
    # list_temp = [mean for mean in false_utility_list if mean < true_utility]
    # if len(list_temp) >= 90:
    if true_utility >= mean_false_utility:
        wandb.log({"Probablity of Strategy-proofness": 1})


if __name__ == "__main__":
    main()

from os import PathLike

import gevent
from locust.stats import (
    stats_printer,
    stats_history
)

from core.Exceptions.SwarmExceptions import SwarmExceptions
from core.Locust import (
    Locust
)
from core.Strategies import Context


class Swarm:
    """
    ❝ I am the Swarm. Armies will be defeated. Planets will be consumed by fire.
    And eventually, on this planet, I will exact my revenge. I am the Queen of Blades. ❞

    StarCraft 2
    """

    def __init__(self, page_to_destroy: str | PathLike, env, strat_context: Context, logger):
        """
        Wrapper class for locust swarm to check web performance
        """
        self.__strategy_context = strat_context
        self.locusts: list[Locust] = list()  # Users list
        self.page = page_to_destroy
        self.env = env
        self.logger = logger

    def get_locusts(self):
        """
        Null safety Get method for locusts list
        Returns locusts list;
        :return: list with Locust entity
        """
        if self.locusts is not None and len(self.locusts) != 0:
            return self.locusts
        else:
            self.logger.log('Trying to get locusts, but locusts are None or len is 0')
            raise SwarmExceptions('Trying to get locusts, but locusts are None or len is 0')

    def get_locust_count(self) -> int:
        """
        Null safety method for locusts count.
        Return locusts count.
        :return: int value or exception
        """
        if self.locusts is not None:
            return len(self.locusts)
        else:
            self.logger.log('Trying to get locusts count, but locusts are None or len is 0')
            raise SwarmExceptions('Trying to get locusts, but locusts are None or len is 0')

    def proceed_locusts(self, app_runner, locust_spawn_rate: int):
        """
        Main function for load testing of the web page.
        :param app_runner: app runner to proceed attack on web page
        :param locust_spawn_rate: spawn rate of the locusts
        :return: None
        """
        try:
            self.logger.log(f'Using "{self.__strategy_context.strategy.get_strat_name()}" strategy from swarm')
            self.logger.log("App started work")

            start_locust_count = self.__strategy_context.strategy.get_user_count_start()
            user = Locust(self.page, env=self.env)
            self.locusts.append(user)
            self.logger.log('Locust added')
            gevent.spawn(stats_printer(self.env.stats))
            gevent.spawn(stats_history, app_runner)
            app_runner.start(start_locust_count, spawn_rate=locust_spawn_rate)
            gevent.spawn_later(self.__strategy_context.strategy.get_time_max(), app_runner.quit)
            app_runner.greenlet.join()

            self.logger.log("App finished work")

        except Exception as e:
            self.logger.log(f'Error occurred in proceed_locusts - {e}')
            raise SwarmExceptions(f'Exception in proceed_locusts - {e}.')

    def get_page(self):
        """
        Null safety Get method for page in swarm
        :return: page for destroy
        """
        if self.page is not None:
            return self.page
        else:
            self.logger.log('Page should not be None to get from swarm')
            raise SwarmExceptions('Page should not be None to get from swarm')

    def get_env(self):
        """
        Null safety Get method for env in swarm
        :return: env
        """
        if self.env is not None:
            return self.env
        else:
            self.logger.log('Env should not be None to get from swarm')
            raise SwarmExceptions('Env should not be None to get from swarm')

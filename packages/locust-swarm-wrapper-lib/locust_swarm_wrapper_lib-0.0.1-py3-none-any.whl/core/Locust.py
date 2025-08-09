from locust import (
    HttpUser,
    between
)

from core.BotLogger import BotLogger as LocustLogger
from core.Exceptions.LocustExceptions import LocustExceptions
from core.LocustSettings import TIME_TOO_LONG

global_logger = LocustLogger('LocustLogger')  # global instance of logger in Locust swarm


class Locust(HttpUser):

    def __init__(self, page_to_destroy: str, env, time_at_least: int = 1, time_at_max: int = 15, *args, **kwargs):
        """
        Class representing one web user (Locust) that perform action and load performance
        :param page_to_destroy: page that will be destroying
        :param args: some args that will be given to inner library
        :param kwargs: some kwargs that will be given to inner library
        """
        self.page_to_destroy = page_to_destroy
        self.time_at_least = time_at_least
        self.time_at_max = time_at_max
        super().__init__(*args, **kwargs, environment=env)

    def on_start(self):
        """
        Inner locust function, executes during locust entity start
        :return: None
        """
        wait_time = between(self.time_at_least, self.time_at_max)
        global_logger.log('Locust born')
        with self.client.get(self.page_to_destroy, catch_response=True) as response:
            if response.text != "Success":
                response.failure("Got wrong response")
                global_logger.log('Got wrong response')
            elif response.elapsed.total_seconds() > TIME_TOO_LONG:
                response.failure("Request took too long")
                global_logger.log('Response took too long time')
            else:
                raise LocustExceptions('Unknown error in start locust method')

    def on_stop(self):
        """
        Inner locust function, executes during locust entity stop
        :return: None
        """
        global_logger.log('Locust die')

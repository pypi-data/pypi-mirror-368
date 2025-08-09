"""
Wrapper app class for Locust library.
Apply different strategies to Swarm execution
"""

import sys
from os import PathLike

from locust import Events
from locust.env import Environment
from locust.runners import Runner

from core import LocustSettings
from core.BotLogger import BotLogger
from core.Exceptions.AppExceptions import AppExceptions
from core.Locust import Locust
from core.Strategies.Context import (
    StrategyEnum,
    Context
)
from core.Strategies.PeakLoad import PeakLoad
from core.Strategies.RampUp import RampUp
from core.Strategies.SpikeTest import SpikeTest
from core.Strategies.SustainLoad import SustainLoad
from core.Swarm import Swarm

localhost = '127.0.0.1:1234'


class App:

    def __init__(self, strategy, is_need_for_log: bool = False, is_file_write: bool = False):
        """
        App object that encapsulated some app logic
        :param strategy: Strategy that will be applied to execution
        :param is_need_for_log: bool value if you need logs in console
        :param is_file_write: if you need to write logs to file
        """
        sys.argv.append('--host=' + localhost)  # append argument to the console interface
        self.__logger = BotLogger('LocustLogger', is_file_write=is_file_write, is_on=is_need_for_log)
        params = self.resolve_cli_args()
        if params is not None:
            LocustSettings.WEB_UI_ADDRESS = params.setdefault('web_ui_address', None)  # get or default
            LocustSettings.WEB_UI_PORT = params.setdefault('web_ui_port', None)  # get or default
            LocustSettings.LOCUSTS_START_COUNT = params.setdefault('locust_start_count', 10)
        else:
            self.__logger.log('No command line arguments found')
        try:
            self.__swarm: Swarm | None = None
            self.__strategy = self.get_strategy_by_enum(strategy)
            self.__env = Environment(user_classes=[Locust], events=Events(), host=localhost)
            self.__runner = self.__env.create_local_runner()
            self.__web_ui = self.__env.create_web_ui(LocustSettings.WEB_UI_ADDRESS, LocustSettings.WEB_UI_PORT)
            self.__env.events.init.fire(environment=self.__env, runner=self.__runner, web_ui=self.__web_ui)
        except Exception as e:
            self.__logger.log(f'Error in app entity initialization - {e}')
            raise AppExceptions(f'Error in app entity initialization - {e}.')

    def open_web_ui(self):
        """
        Function for opening Locust web ui
        :return: Web Locust ui or error message if error
        """
        try:
            self.__logger.log('Open web ui')
            self.__web_ui.start()
        except Exception as e:
            self.__logger.log(f'Error occurred while opening Locust web ui - {e}')
            raise AppExceptions(f'Error occurred while opening Locust web ui - {e}')

    ## Runner methods

    def get_runner(self):
        """
        Null safety get swarm runner method
        :return: runner
        """
        if self.__runner is not None:
            return self.__runner
        else:
            self.__logger.log('Runner class is None')

    def set_runner(self, runner: Runner):
        """
        Null safety Set runner method
        :return: None
        """
        if type(runner) is Runner:
            self.__runner = runner
            self.__logger.log(f'Runner changed to - {runner}')
        else:
            self.__logger.log('Wrong runner type')

    ##Logger actions

    def get_logger(self):
        """
        Null safety get logger instance
        :return: logger instance
        """
        if self.__logger is not None:
            return self.__logger
        else:
            print('Logger is None!')
            print('Create it first')

    def set_logger(self, logger: BotLogger):
        """
        Null safety set logger
        :param logger: another logger to set
        :return: None
        """
        if logger is not None:
            self.__logger = logger
        else:
            self.__logger.log('Error in logger set')

    ## Swarm methods

    def get_swarm(self):
        """
        Null safety Get method for swarm;
        :return: Swarm object if it not None
        """
        if self.__swarm is not None:
            return self.__swarm
        else:
            self.__logger.log('Attempt to get swarm while swarm is None')
            self.__logger.log('Create swarm first')

    def set_swarm_attack_to_page(self, page_to_destroy: str | PathLike, logger):
        """
        Null safety Set swarm off to some given page.
        :param logger: swarm logger
        :param page_to_destroy: page that will be destroyed by swarm
        :return: None
        """
        try:
            if page_to_destroy is not None:
                self.__swarm = Swarm(
                    page_to_destroy=page_to_destroy,
                    env=self.__env,
                    strat_context=self.__strategy,
                    logger=logger
                )
                self.__logger.log('Swarm created')
            else:
                self.__logger.log('Page is None!')
                raise AppExceptions('Page cannot be None')
        except Exception as e:
            self.__logger.log(f'Error occurred in Setting swarm instance - {e}')
            raise AppExceptions(f'Error occurred in Setting swarm instance - {e}.')

    @staticmethod
    def resolve_cli_args() -> dict[str, str | int] | None:
        """
        Function for accessing CLI arguments
        :return: dict with arguments or None if no command line interface arg given
        """
        sys_args = sys.argv
        lenght = len(sys_args)
        if lenght >= 1:
            sys_args = sys_args[1:]  # remove first path name argument
            resolved_args: dict[str, str | int] = dict()  # dict with split arguments
            for param in sys_args:
                if '--' in param and '=' in param:
                    arg_pair = param.split('=')
                    arg_name = arg_pair[0]  # name of the argument, ex. web_ui_port
                    arg_value = arg_pair[1]  # value of the argument, ex. 127.0.0.1
                    resolved_args[arg_name] = arg_value
                else:
                    raise AppExceptions('Wrong argument received, expect arg with "--" and "="')
            return resolved_args
        elif lenght == 2 and sys_args[1] == 'help':
            get_help()
        else:
            return None

    def get_strategy_by_enum(self, strat: StrategyEnum) -> Context:
        """
        Null safety function for getting app strategy from enum string to Context with Strategy;
        :param strat: strategy to apply
        :return: created Context
        """
        if strat is not None:
            match strat:
                case StrategyEnum.PEAK:
                    strategy = PeakLoad()
                case StrategyEnum.RAMP_UP:
                    strategy = RampUp()
                case StrategyEnum.SUSTAIN_LOAD:
                    strategy = SustainLoad()
                case StrategyEnum.SPIKE_TEST:
                    strategy = SpikeTest()
                case _:
                    raise AppExceptions('Not implemented strategy yet')
            context = Context(strategy)
            return context
        else:
            self.__logger.log('Given strategy is None')
            raise AppExceptions('None value strategy is given')


def get_help():
    """
    Function for given help to user.
    Prints all information about app.
    Also prints allowed command line interface flags, which you can use
    :return: None
    """
    print(f'Locust swarm with version {LocustSettings.APP_VERSION}.')
    print('''
    App need to get load test of web sites
    
    '''
          )
    print(
        f"""
        App params as follows:
        locust_count=<number, ex. 10>
        web_ui_port=<numbers, ex. 8089>
        web_ui_address='127.0.0.1' for localhost or your ip address
        strategy=<one of {(StrategyEnum.PEAK, StrategyEnum.SPIKE_TEST, StrategyEnum.SUSTAIN_LOAD, StrategyEnum.RAMP_UP)}>
        """
    )

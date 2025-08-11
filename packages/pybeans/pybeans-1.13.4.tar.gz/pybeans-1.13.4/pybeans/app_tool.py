import os, sys, logging
from logging import handlers
from os import path
from email.utils import formataddr
from collections.abc import Iterable
import functools
import time
import re, json
import traceback
import requests
from munch import Munch

from pprint import pformat
from colorama import Fore, Back, init, Style
init()

from .utils import now, create_sign_for_dingtalk
from .utils import deep_merge, send_email, get, cast, deprecated
from .exception import AppToolError
from .ColorfulFormatter import ColorfulFormatter


class MySMTPHandler(handlers.SMTPHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials=None, secure=None, timeout=5.0, use_ssl=True, time_interval=0):
        super().__init__(mailhost, fromaddr, toaddrs, subject,
                         credentials, secure, timeout)
        self._use_ssl = use_ssl
        self._time_interval = time_interval
        self._msg_map = dict()  # 是一个内容为键时间为值的映射
        
    def getSubject(self, record):
        #all_formatter = logging.Formatter(fmt='%(name)s - %(levelno)s - %(levelname)s - %(pathname)s - %(filename)s - %(module)s - %(lineno)d - %(funcName)s - %(created)f - %(asctime)s - %(msecs)d  %(relativeCreated)d - %(thread)d -  %(threadName)s -  %(process)d - %(message)s ')        
        #print('Ex. >>> ',all_formatter.formatMessage(record))

        #help(record)
        #help(formatter)
        
        formatter = logging.Formatter(fmt=self.subject)
        record.message = record.msg # To be compatible with Python 3.10 to avoid KeyError in formatMessage
        return formatter.formatMessage(record)

    def emit(self, record: logging.LogRecord):
        """
        支持多线程
        """
        from threading import Thread
        if sys.getsizeof(self._msg_map) > 10 * 1000 * 1000:
            self._msg_map.clear()
        Thread(target=self.__emit, args=(record,)).start()
        
    def __emit(self, record):
        '''
        支持ssl
        避免频繁发送相同内容的邮件
        '''
        if record.msg not in self._msg_map or time.time() - self._msg_map[record.msg] > self._time_interval:
            try:
                smtp = {
                    'host': self.mailhost,
                    'port': self.mailport,
                    'user': self.username,
                    'pwd': self.password,
                    'type': 'ssl' if self._use_ssl else 'plain'
                }
                send_email(from_addr=self.fromaddr
                    , to_addrs=','.join(self.toaddrs)
                    , subject=self.getSubject(record)
                    , text_body=self.format(record)
                    , smtp_config=smtp
                )
                self._msg_map[record.msg] = time.time()
            except Exception:
                self.handleError(record)
        else:
            pass

class AppTool(object):
    def __init__(self, app_name: str, app_path: str='', local_config_dir: str='', config_name: str='config', ignore_env:bool=False):
        self._app_name = app_name
        self._app_path = app_path if app_path else os.getcwd()
        self._config = {}
        self._config_obj = None
        self._logger = None

        self.load_config(local_config_dir, config_name)
        self.init_logger()


    @property
    def name(self):
        return self._app_name


    @property
    def config(self):
        return self._config_obj


    @property
    def logger(self):
        return self._logger


    @deprecated
    def _use_env_var(self, config: dict, parent_key: str) -> dict:
        """Replace config variable with env

        Args:
            config (dict): config dict
            parent_key (str, optional): parent key (connected by dot). Defaults to ''.

        Returns:
            dict: result
        """
        if type(config) is tuple:
            config = list(config)

        if type(config) is dict:
            for key in config.keys():
                full_key = (parent_key + '_' + re.sub(r'\W+', '_', key)).upper()
                #print(full_key)
                if full_key in os.environ.keys():
                    try:
                        config[key] = cast(config[key], os.environ.get(full_key))
                    except ValueError as ex:
                        print('[pybeans]: parent-key:', parent_key, 'key:', key, 'fullkey:', full_key)
                        raise ex
                elif type(config[key]) in (list, dict, tuple):
                    config[key] = self._use_env_var(config[key], full_key)
        elif type(config) is list:
            for index, _ in enumerate(config):
                full_key = f'{parent_key}_{index}'.upper()
                #print(full_key)
                if full_key in os.environ.keys():
                    try:
                        config[index] = cast(config[index], os.environ.get(full_key))
                    except ValueError as ex:
                        print('[pybeans]: parent-key:',parent_key, 'index:', index, 'fullkey:', full_key)
                        raise ex
                elif type(config[index]) in (list, dict, tuple):
                    config[index] = self._use_env_var(config[index], full_key)
        return config


    def help(self):
        desc = '''
Config priority: config_dev var > config_local > config.
Env var: Ex. a.b             -> APP_A
             a.b[0][1].e'    -> APP_A_B_0_1_E
'''
        print(desc)
        

    def load_config(self, local_config_dir: str = '', config_name: str='config', read_env:bool=True) -> dict:
        """Load config locally then replace some with env value if NOT ignore_env
        NOTE! 
            - If exists APP_ENV_TEST=dev environment var, will load config_dev.py and cover default.
            - env key of config key will be UPPER of APP_NAME and KEY_NAMEs (connected by '_')
            - ANY char which is NOT A-Za-z0-9_ , that's say \\w in re, will be replaced by '_'
            Ex. a.b             -> APP_A
                a.b[0][1].e'    -> APP_A_B_0_1_E

        Keyword Arguments:
            local_config_dir {str} -- Dir name of local config files. (default: {''})
        
        Returns:
            [dict] -- Merged config dictionary.
        """
        assert(type(local_config_dir) == str)

        sys.path.append(self._app_path)
        config = {}
        try:
            config = __import__(config_name).CONFIG
        except ModuleNotFoundError:
            config = {}
        except Exception as ex:
            raise ex
        
        config_local_path = path.join(self._app_path, local_config_dir)
        sys.path.append(config_local_path)
        try:
            config_local = __import__(config_name + '_local').CONFIG
            config = deep_merge(config, config_local)
        except ModuleNotFoundError:
            pass
        except Exception as ex:
            raise ex
        
        regular_app_name = re.sub(r'\W+', '_', self._app_name.upper())
        env_key = regular_app_name + '_ENV'        
        env = os.environ.get(env_key)
        
        if env:
            try:
                config_test = __import__(config_name + f'_{env}').CONFIG
                config = deep_merge(config, config_test)
            except ModuleNotFoundError:
                pass
            except Exception as ex:
                raise ex
        
        self._config = config
        self._config_obj = Munch.fromDict(config)
        return self._config


    def init_logger(self) -> logging.Logger:
        """Initialize logger
        
        Returns:
            [logger] -- Initialized logger.
        """
        
        smtp = self._config.get('smtp')
        mail = self._config.get('mail')
        logConfig = self._config.get('log', {})

        logger = logging.getLogger(self._app_name)
        logLevel = logConfig.get('level', logging.DEBUG)
        logger.setLevel(logLevel)

        logDst = logConfig.get('dest', {})

        fileDest = logDst.get('file')
        if fileDest is not None:
            if not fileDest: # Empty
                logs_path = path.join(self._app_path, '.logs')
                if not os.path.exists(logs_path):
                    os.mkdir(logs_path)
                regular_log_name = re.sub(r'\W+', '_', self._app_name.lower())
                fileDest = path.join(logs_path, f'{regular_log_name}.log')
            regular_log_name = re.sub(r'\W+', '_', self._app_name.lower())
            rf_handler = handlers.TimedRotatingFileHandler(fileDest, when='D', interval=1, backupCount=7, encoding='utf-8')
            rf_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
            rf_handler.level = logging.INFO
            rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            logger.addHandler(rf_handler)

        mailDest = logDst.get('mail')
        if smtp and mailDest is not None:
            #TODO: Use schema to validate smtp
            if not mailDest:    # Empty
                to_addrs = mail.get('to')
            else:   # Ex. 'Henry TIAN <chariothy@gmail.com>'
                to_addrs = mailDest

            mail_handler = MySMTPHandler(
                    mailhost = (smtp['host'], smtp['port']),
                    fromaddr = mail.get('from'),
                    toaddrs = to_addrs,
                    subject = '%(name)s - %(levelname)s - %(message)s',
                    credentials = (smtp['user'], smtp['pwd']),
                )
            mail_handler.setLevel(logging.ERROR)
            logger.addHandler(mail_handler)

        stdoutDest = logDst.get('stdout', True)
        if stdoutDest is not None:
            st_handler = logging.StreamHandler()
            st_handler.level = logging.DEBUG
            st_handler.setFormatter(ColorfulFormatter())
            logger.addHandler(st_handler)
            
        syslogDest = logDst.get('syslog')
        if syslogDest is not None:
            sl_handler = logging.handlers.SysLogHandler(address=tuple(syslogDest))
            sl_handler.level = logging.DEBUG
            formatterDict = logConfig.get('formatter', {})
            syslogFormatter = formatterDict.get('syslog', None)
            if not syslogFormatter:
                syslogFormatter = f'{self._app_name}[%(process)d]: %(message)s'
            sl_handler.setFormatter(logging.Formatter(syslogFormatter))
            logger.addHandler(sl_handler)

        self._logger = logger
        return logger


    def send_email(self, subject: str, text_body: str='', from_addr: str=None, to_addrs:str=None, html_body: str=None, 
        image_paths: tuple=None, file_paths: tuple=None, 
        debug: bool=False, send_to_file: bool=False, email_file_dir=None) -> dict:
        """A shortcut of global send_email
        """
        smtp = self._config.get('smtp')
        #TODO: Use schema to validate smtp_config
        assert smtp
        assert text_body or html_body
        
        mail = self._config.get('mail')
        mail_from = from_addr if from_addr else mail['from']
        mail_to = to_addrs if to_addrs else mail['to']
        return send_email(mail_from, mail_to, subject, 
            text_body=text_body, 
            smtp_config=smtp, 
            html_body=html_body,
            image_paths=image_paths,
            file_paths=file_paths,
            debug=debug,
            send_to_file=send_to_file,
            email_file_dir=email_file_dir
        )


    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)


    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)


    def warn(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)


    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)


    def err(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)


    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)


    def ex(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)


    def fatal(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)


    def print(self, level, *args, exc_info=False):
        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        if level == 'DEBUG':
            header_style = Fore.BLUE + Back.WHITE
            fg = Fore.CYAN
        elif level == 'INFO':
            header_style = Fore.YELLOW + Back.BLUE + Style.BRIGHT
            fg = Fore.GREEN
        elif level == 'WARN':
            header_style = Fore.BLUE + Back.YELLOW
            fg = Fore.YELLOW
        elif level == 'ERROR':
            header_style = Fore.WHITE + Back.RED + Style.BRIGHT
            fg = Fore.RED + Style.BRIGHT
        else:
            header_style = Fore.RED
            fg = Fore.RED
        
        print(Style.DIM + local_time + Style.RESET_ALL + ' '\
            + header_style + f' {level} ' + Style.RESET_ALL + ' ' + fg, end='')
        for obj in args:
            if isinstance(obj, str):
              print(obj, end=' ')
            else:
              print(pformat(obj), end=' ')
        if exc_info:
            print()
            traceback.print_exc()
        print(Style.RESET_ALL, flush=True)


    def ding(self, title, text):
        token = self['dingtalk.token']
        secret = self['dingtalk.secret']    
        assert token and secret
        dt_msg = {
            "msgtype": 'markdown',
            "markdown": {
                'title': title,
                'text': f'''**<font color=#6A65FF>{title}</font>**\n
{now()}\n
---\n
{text}'''
            }
        }
        self.debug(dt_msg)
        timestamp, sign = create_sign_for_dingtalk(secret)
        url = f"https://oapi.dingtalk.com/robot/send?access_token={token}&timestamp={timestamp}&sign={sign}"
        
        @self.retry(n=3)
        def req():
            return requests.post(url=url, \
                headers = {'Content-Type': 'application/json'}, \
                data=json.dumps(dt_msg) \
            ).json()
        return req()
    

    def log(self, throw=False, message=''):
        """Decorator
        !!! Should be decorated first to avoid being shielded by other decorators, such as @click.
        
        Keyword Arguments:
            throw {bool} -- Re-raise exception (default: {False})
            message {str} -- Specify message
        
        Raises:
            ex: Original exception
        
        Example:
            @log()
            def func():
                pass

            @log(True)
            def func():
                pass

            @log(message='foo')
            def func():
                pass
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kw):
                try:
                    return func(*args, **kw)
                except Exception as ex:
                    self._logger.exception(message if message else str(ex))
                    if throw:
                        raise ex
            return wrapper
        return decorator


    def retry(self, n=3, delay=1, error=Exception):
        """
        A decorator to retry a function n times with a delay between attempts.

        :param n: Number of retries (default is 3)
        :param delay: Delay in seconds between retries (default is 1)
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(n):
                    try:
                        return func(*args, **kwargs)
                    except error as e:
                        if attempt < n - 1:  # Only log if not the last attempt
                            self.debug(f"Attempt {attempt + 1} failed due to {type(e).__name__}: {e}. Retrying...")
                            time.sleep(delay)
                        else:
                            self.debug(f"Attempt {attempt + 1} failed due to {type(e).__name__}: {e}. No more retries.")
                            raise  # Re-raise the exception after the last attempt
            return wrapper
        return decorator



    def get(self, key:str, default=None, check:bool=False, replacement_for_dot_in_key:str='#'):
        return get(self._config, key, default, check, replacement_for_dot_in_key)

    def __getitem__(self, key):
        return self.get(key, replacement_for_dot_in_key='#', check=True)
    
    
    def print_sample_config(self):
        from .config_sample import CONFIG
        from pprint import pprint
        pprint(CONFIG)
        
        
    def create_sample_config(self):
        config = ''
        with open(os.path.join(os.path.dirname(__file__), 'config_sample.py'), encoding='utf-8') as fp:
            config = fp.read()
        config_path = os.path.join(os.getcwd(), 'config.py')
        if os.path.exists(config_path):
            self.debug(f'"{config_path}" exists, please rename it first.')
        else:
            with open(config_path, mode='w') as fp:
                fp.write(config)
            self.debug(f'Please find sample config at "{config_path}"')
        config_local_path = os.path.join(os.getcwd(), 'config_local.py')
        if not os.path.exists(config_local_path):
            with open(config_local_path, mode='w') as fp:
                fp.write('CONFIG = {}')
                
                
    def demo_logging(self):
        '''Show color demo logging for multi-platform.
        '''
        lst = ['• New information revealed about how parents of suspect were arrested',
            '• Students and teachers face pyschological toll after Oxford High School shooting',
            '• A timeline of a school shooting tragedy',
            '• Exclusive video shows arrest of parents']
        dct = {
            'Prince reveals moment': [1,2,3],
            'Deeply concerned by': 'Russia putting up to 175,000 troops near Ukraine, US says',
            'China at twice the rate of US': lst
        }

        print('\n'+'#'*40+' Colorful Logger '+'#'*40+'\n')
        self.debug('this is demo output for AppTool.debug')
        self.info('this is demo output for AppTool.info')
        self.warn('this is demo output for AppTool.warning')
        self.error('this is demo output for AppTool.error')
        self.fatal('this is demo output for AppTool.fatal')
        try:
            do_nothing()
        except Exception:
            self.ex('this is demo output for AppTool.ex')
        self.debug(lst)
        self.debug(dct)
import unittest, os, logging

from pybeans import deep_merge, deep_merge_in, benchmark, is_win, is_linux, is_macos, is_darwin
from pybeans import random_sleep, dump_json, load_json, send_email, get
from pybeans import AppTool, AppToolError

from os import environ as env
#del env['DEMO_HOST']
from tests import CONFIG, CONFIG_DEV

class CoreTestCase(unittest.TestCase):
    def setUp(self):
        self.demo_value = 'DEMO_VALUE'
        env['TEST_ING_ENV'] = 'dev' # The first TESTING is app_name
        
        self.APP_NAME = 'test-ing'
        self.APP = AppTool(self.APP_NAME, os.getcwd())
        #print(self.APP.config)
        #print(env)

    def tearDown(self):
        del env['TEST_ING_ENV']
    
    def test_get_config(self):
        """
        docstring
        """
        self.assertEqual(CONFIG_DEV['mail']['from'][0], self.APP.get('mail.from[0]'))
        self.assertEqual(CONFIG_DEV['mail']['from'][-1], self.APP['mail.from[-1]'])

        self.assertEqual(CONFIG_DEV['mail']['to'][0][0], self.APP.get('mail.to[0][0]'))

        self.assertEqual(CONFIG_DEV['log']['level'], self.APP['log.level'])
        self.assertEqual(CONFIG_DEV['log']['dest']['file'], self.APP['log.dest.file'])
        

class CoreEnvTestCase(unittest.TestCase):
    def setUp(self):
        self.demo_value = 'DEMO_VALUE'        
        env['DEMO_HOST'] = self.demo_value
        self.APP_NAME = 'test-ing'
        self.APP = AppTool(self.APP_NAME, os.getcwd())
        #print(self.APP.config)
        #print(env)

    def tearDown(self):
        del env['DEMO_HOST']

    def test_get_env_config(self):
        """
        docstring
        """        
        self.assertEqual(self.APP['demo.host'], self.demo_value)

if __name__ == '__main__':
    unittest.main()
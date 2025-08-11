import unittest, os, logging

from pybeans import deep_merge, deep_merge_in, benchmark, is_win, is_linux, is_macos, is_darwin, utils
from pybeans import random_sleep, dump_json, load_json, send_email, get
from pybeans import AppTool, AppToolError

from tests import CONFIG, CONFIG_LOCAL


dict1 = {
    'a1': 1, 
    'a2': {
        'b1': 2,
        'b2': 3
    }
}
dict_ori = {
    'a1': 1, 
    'a2': {
        'b1': 2,
        'b2': 3
    }
}
dict2 = {
    'a2': {
        'b2': 4,
        'b3': 5
    }
}
dict3 = {
    'a1': 1, 
    'a2': {
        'b1': 2,
        'b2': 4,
        'b3': 5
    }
}


class CoreTestCase(unittest.TestCase):
    def setUp(self):
        from os import environ as env
        env['TEST_ING_ENV'] = '' # The first TESTING is app_name
        self.demo_value = 'DEMO_VALUE'
        self.demo_int = '4'
        
        self._write_email_to_file = env.get('MAIL_DEST') != 'mail'

        self.APP_NAME = 'test-ing'
        self.APP = AppTool(self.APP_NAME, os.getcwd())
        
        self.n = 0
        #print(self.APP.config)
        #print(env)

    def test_app_tool(self):
        logger = self.APP.init_logger()
        self.assertLogs(logger, logging.INFO)
        self.assertLogs(logger, logging.DEBUG)
        self.assertLogs(logger, logging.ERROR)

    def test_deep_merge_in(self):
        self.assertDictEqual(deep_merge_in(dict1, dict2), dict3)
        self.assertDictEqual(dict1, dict3)

    def test_deep_merge(self):
        self.assertDictEqual(deep_merge(dict1, dict2), dict3)
        self.assertDictEqual(dict1, dict_ori)

    def test_is_win(self):
        self.assertTrue(is_win())

    def test_is_linux(self):
        self.assertFalse(is_linux())
    
    def test_is_macos(self):
        self.assertFalse(is_macos())

    def test_is_darwin(self):
        self.assertFalse(is_darwin())

    @benchmark
    def test_benchmark(self):
        import time
        time.sleep(1)

    def test_random_sleep(self):
        random_sleep()

    def test_load_json(self):
        self.assertIsNone(load_json('/not-exist-file-path'))

    def test_dump_json(self):
        file_path = './data/dump.json'
        data = {'test': 'OK'}
        dump_json(file_path, data)
        self.assertTrue(os.path.exists(file_path))
        
        load_data = load_json(file_path)
        self.assertDictEqual(data, load_data)

        os.remove(file_path)
    
    def test_get_config(self):
        """
        docstring
        """
        self.assertEqual(CONFIG['mail']['from'], self.APP.get('mail.from'))
        self.assertEqual(CONFIG['mail']['from'], self.APP['mail.from'])

        self.assertRaises(AppToolError, lambda k: self.APP[k], 'mail.from.test')
        self.assertIsNone(self.APP.get('mail.from.test'))
        self.assertEqual(1, self.APP.get('mail.from.test', 1))

        self.assertRaises(AppToolError, lambda k: self.APP[k], 'mail.[0]')
        self.assertRaises(AppToolError, lambda k: self.APP.get(k), 'mail.[0]')

        self.assertRaises(AppToolError, lambda k: self.APP[k], 'mail.from[0]x')
        self.assertRaises(AppToolError, lambda k: self.APP.get(k), 'mail.from[0]x')

        self.assertRaises(AppToolError, lambda k: self.APP[k], 'mail.fromx[0]')
        self.assertRaises(AppToolError, lambda k: self.APP.get(k), 'mail.fromx[0]')

        self.assertRaises(AppToolError, lambda k: self.APP[k], 'mail.smtp[0]')
        self.assertRaises(AppToolError, lambda k: self.APP.get(k), 'mail.smtp[0]')

        self.assertRaises(AppToolError, lambda k: self.APP[k], 'mail.smtp.port.test')
        self.assertIsNone(self.APP.get('mail.smtp.port.test'))
        self.assertEqual(1, self.APP.get('mail.smtp.port.test', 1))
        
        self.assertEqual(CONFIG['demo.key2']['from'][0], self.APP['demo#key2.from[0]'])
        self.assertRaises(AppToolError, lambda k: self.APP[k], 'demo#key.from2[0]') # Because now demo.key is replaced by env
        
        self.assertEqual(CONFIG_LOCAL['log']['level'], self.APP['log.level'])

    def test_dot_config(self):
        """
        docstring
        """
        self.assertEqual(CONFIG['mail']['from'], self.APP.config.mail['from'])
        self.assertEqual(CONFIG['demo.key2']['from'][0], self.APP.config.key2['from'][0])
        self.assertEqual(CONFIG['demo']['host'], self.APP.config.demo.host)
        self.assertEqual(CONFIG_LOCAL['log']['level'], self.APP.config.log.level)

    def test_send_text_email(self):
        """
        docstring
        """
        result = send_email(
            self.APP['mail.from'], 
            self.APP['mail.to'], 
            'Send text mail for chariothy_common',
            'Send text mail for chariothy_common',
            self.APP['smtp'],
            send_to_file=self._write_email_to_file
        )
        self.assertDictEqual(result, {})

    def test_send_html_email(self):
        """
        docstring
        """
        body = """
<h3>Hi，all</h3>
<p>附件为本次自动化测试报告。</p>
"""
        result = send_email(
            self.APP['mail.from'], 
            self.APP['mail.to'], 
            'Send html mail for chariothy_common',
            smtp_config=self.APP['smtp'],
            html_body=body,
            send_to_file=self._write_email_to_file
        )
        self.assertDictEqual(result, {})


    def test_send_html_email_with_img(self):
        """
        docstring
        """
        body = """
<h3>Hi，all</h3>
<p>附件为本次自动化测试报告。</p>
<p><img src="cid:{}"></p>
<p><img src="cid:{}"></p>
"""
        pwd = os.path.dirname(__file__)
        images = (
            os.path.join(pwd, 'train.png'),
            os.path.join(pwd, 'boat.png'),
        )
        result = send_email(
            self.APP['mail.from'], 
            self.APP['mail.to'], 
            'Send html mail with image for chariothy_common',
            smtp_config=self.APP['smtp'],
            html_body=body,
            image_paths=images,
            send_to_file=self._write_email_to_file
        )
        self.assertDictEqual(result, {})


    def test_send_html_email_with_file(self):
        """
        docstring
        """
        body = """
<h3>Hi，all</h3>
<p>附件为本次自动化测试报告。</p>
"""
        pwd = os.path.dirname(__file__)
        files = (
            os.path.join(pwd, 'train.png'),
            os.path.join(pwd, 'boat.png'),
        )
        result = send_email(
            self.APP['mail.from'], 
            self.APP['mail.to'], 
            'Send html mail with file for chariothy_common',
            smtp_config=self.APP['smtp'],
            html_body=body,
            file_paths=files,
            send_to_file=self._write_email_to_file
        )
        self.assertDictEqual(result, {})
        
            
    def test_pad_filename(self):
        self.assertEqual(
            utils.pad_filename(r'D:\test\test.py', 'xoxo', '{FILENAME}_{PAD}.{FILEEXT}'), 
            r'D:\test\test_xoxo.py'
        )
        self.assertEqual(
            utils.pad_filename(r'D:\test\test.py', 'xoxo', '{PAD}_{FILENAME}.{FILEEXT}'), 
            r'D:\test\xoxo_test.py'
        )
        self.assertEqual(
            utils.pad_filename(r'D:\test\test.py', 'xoxo', '{FILENAME}.{PAD}_{FILEEXT}'), 
            r'D:\test\test.xoxo_py'
        )
        self.assertEqual(
            utils.pad_filename(r'D:\test\test', 'xoxo', '{FILENAME}_{PAD}'), 
            r'D:\test\test_xoxo'
        )
        print('\n### Empty template:', utils.pad_filename(r'D:\test\test.py'))
    
    def test_retry(self):
        self.n = 0
        @self.APP.retry(n=3, delay=1)
        def test_func():
            print('test_func')
            self.n += 1
            raise ValueError('test error')
        self.assertRaises(ValueError, test_func)
        self.assertEqual(self.n, 3)

        self.n = 0
        @self.APP.retry(n=3, delay=1, error=NameError)
        def test_func():
            print('test_func')
            self.n += 1
            raise ValueError('test error')
        self.assertRaises(ValueError, test_func)
        self.assertEqual(self.n, 1)

if __name__ == '__main__':
    unittest.main()
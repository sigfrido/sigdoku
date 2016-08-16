# -*- coding: utf-8 -*-

import console
import unittest


class TestConsole(unittest.TestCase):
    
    
    def setUp(self):
        self.console = console.Console(3)
    
        
    def test_console_parse_cmd_quit(self):
        self.assertTrue(self.console.do_play)
        self.console.execute_command_line('   q ')
        self.assertFalse(self.console.do_play)
        
        
    def test_console_parse_move(self):
        self.console.execute_command_line(' 2  5  8 ')
        self.assertEqual(8, self.console.board.row(2).cell(5).value)

        self.console.execute_command_line('8 9 1 ')
        self.assertEqual(1, self.console.board.row(8).cell(9).value)
        
        self.console.clear_error()
        self.console.execute_command_line('8 a 19')
        self.assertNotEqual('', self.console.error_message)

    
if __name__ == '__main__':
    unittest.main()



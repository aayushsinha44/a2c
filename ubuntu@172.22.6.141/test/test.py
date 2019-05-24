import unittest

class TestSSH(unittest.TestCase):

    def setup(self):
        from api.ssh import SSH
        print('loaded')

    def test_upper(self):         
        self.assertEqual('foo'.upper(), 'FOO') 


if __name__ == '__main__':
    unittest.main()
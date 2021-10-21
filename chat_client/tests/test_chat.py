import unittest
from files import server


class ChatTests(unittest.TestCase):
    def test_appending_usernames(self):
        server.appending("test username", "test client")
        self.assertEqual(server.usernames[0], "test username")

    def test_appending_clients(self):
        server.appending("test username", "test client")
        self.assertEqual(server.clients[0], "test client")

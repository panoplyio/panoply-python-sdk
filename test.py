from unittest import TestCase
from unittest.mock import patch, MagicMock
import panoply
import base64

TEST_KEY = "test/key"
TEST_SECRET = b"rand2/uuid/awsaccount/region"


class TestPanoplyPythonSDK(TestCase):
    def test_init(self):
        sdk = panoply.SDK(TEST_KEY, base64.b64encode(TEST_SECRET))
        expected_url = "https://sqs.region.amazonaws.com/awsaccount/sdk-test-rand2"  # noqa

        self.assertEqual(sdk.qurl, expected_url)

    def test_write(self):
        sdk = panoply.SDK(TEST_KEY, base64.b64encode(TEST_SECRET))
        sdk.write('table', {'data': 1})
        sdk.write('table', {'data': 2})

        self.assertEqual(sdk._buffer.qsize(), 2)


class TestSSHTunnel(TestCase):

    MOCKED_TUNNEL_OBJECT = {
        "active": True,
        "username": "panoply-user",
        "host": "233.23.11.223",
        "port": 22,
        "privateKey": "dasd2dsd"
    }

    class MockedSSHTunnel:
        def __init__(self, kwargs):
            self.server = kwargs

        @staticmethod
        def start():
            print("server started")

        @staticmethod
        def stop():
            print("server stopped")

    def test_tunnel_with_incorrect_port(self):
        mocked_message = "Port should be in range [0: 65535]"
        try:
            tunnel = panoply.SSHTunnel('127.0.0.1', -5, {}, False)
            print(tunnel)
        except panoply.errors.IncorrectParamError as err:
            self.assertEqual(str(err), mocked_message)

    def test_tunnel_with_incorrect_tunnel_object(self):
        mocked_message = "SSH tunnel object should contain `active` property"
        try:
            tunnel = panoply.SSHTunnel('127.0.0.1', 27017, {"key": "v"}, False)
            print(tunnel)
        except panoply.errors.IncorrectParamError as err:
            self.assertEqual(str(err), mocked_message)

    def test_tunnel_with_incorrect_platform_flag(self):
        tunnel = panoply.SSHTunnel(
            '127.0.0.1', 27017, self.MOCKED_TUNNEL_OBJECT, True
        )
        self.assertIsNone(tunnel.server)

    @patch("paramiko.RSAKey.from_private_key")
    @patch("panoply.ssh.SSHTunnelForwarder")
    def test_tunnel_ctxt_manager(self, SSHTunnelForwarder, from_private_key):
        SSHTunnelForwarder.return_value = self.MockedSSHTunnel(
            self.MOCKED_TUNNEL_OBJECT
        )
        SSHTunnelForwarder.start.return_value = self.MockedSSHTunnel.start
        SSHTunnelForwarder.stop.return_value = self.MockedSSHTunnel.stop
        from_private_key.return_value = self.MOCKED_TUNNEL_OBJECT["privateKey"]

        with panoply.SSHTunnel("127.0.0.1", 22, self.MOCKED_TUNNEL_OBJECT, False) as tunnel:  # noqa
            self.assertEqual(tunnel.server, self.MOCKED_TUNNEL_OBJECT)

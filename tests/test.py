from unittest import TestCase
import panoply

TEST_KEY = "key"
TEST_SECRET = "MmM0NWNvc2wwYmJ4ZDJ0OS84MmY3MzQ4NC02MDIzLTQyN2QtODdkMS0yY2I0NTAzNDk0NDQvMDM3MzM1OTk5NTYyL3VzLWVhc3QtMQ=="  # noqa


class TestPanoplyPythonSDK(TestCase):

    def test_init(self):
        sdk = panoply.SDK(TEST_KEY, TEST_SECRET)
        expected_url = "https://sqs.us-east-1.amazonaws.com/037335999562/sdk-key-2c45cosl0bbxd2t9"  # noqa

        self.assertEqual(sdk.qurl, expected_url)

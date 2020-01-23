from unittest import TestCase
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

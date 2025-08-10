import base64
import json
import unittest
from unittest.mock import patch

from maildeck.deck import NextcloudDeck


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    # Support context manager protocol used by urllib opener
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class RecordingOpener:
    def __init__(self):
        self.requests = []
        self.routes = {}

    def route(self, url, method, payload):
        self.routes[(url, method)] = payload

    def open(self, request):
        # record request for assertions
        self.requests.append(request)
        url = request.full_url
        method = request.get_method()
        payload = self.routes.get((url, method))
        if payload is None:
            raise AssertionError(f"No fake route for {method} {url}")
        return FakeResponse(payload)


class TestDeck(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://nc.example.com"
        self.api_base = self.base_url + "/index.php/apps/deck/api/v1.1"
        self.username = "user"
        self.password = "pass"
        self.expected_auth = (
            "Basic "
            + base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        )

    def test_get_stacks_and_headers(self):
        opener = RecordingOpener()
        opener.route(
            self.api_base + "/boards/1/stacks", "GET", payload=[{"id": 2, "order": 10}]
        )

        with patch("urllib.request.build_opener", return_value=opener):
            client = NextcloudDeck(self.base_url, self.username, self.password)
            stacks = client.get_stacks(1)

        self.assertEqual(stacks, [{"id": 2, "order": 10}])
        # Assert headers present on the recorded request
        req = opener.requests[0]
        self.assertEqual(req.get_method(), "GET")
        headers = {k.lower(): v for k, v in req.headers.items()}
        self.assertEqual(headers.get("ocs-apirequest"), "true")
        self.assertEqual(headers.get("authorization"), self.expected_auth)

    def test_get_first_stack_sorts_by_order_then_id(self):
        opener = RecordingOpener()
        unsorted = [
            {"id": 5, "order": 10},
            {"id": 3, "order": 10},
            {"id": 2, "order": 9},
        ]
        opener.route(self.api_base + "/boards/7/stacks", "GET", payload=unsorted)
        with patch("urllib.request.build_opener", return_value=opener):
            client = NextcloudDeck(self.base_url, self.username, self.password)
            first = client.get_first_stack(7)
        self.assertEqual(first, {"id": 2, "order": 9})

    def test_create_card_posts_json(self):
        opener = RecordingOpener()
        opener.route(
            self.api_base + "/boards/1/stacks/2/cards", "POST", payload={"id": 99}
        )
        with patch("urllib.request.build_opener", return_value=opener):
            client = NextcloudDeck(self.base_url, self.username, self.password)
            card = client.create_card(1, 2, title="T", description="D")

        self.assertEqual(card, {"id": 99})
        req = opener.requests[0]
        self.assertEqual(req.get_method(), "POST")
        headers = {k.lower(): v for k, v in req.headers.items()}
        self.assertEqual(headers.get("content-type"), "application/json")
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["title"], "T")
        self.assertEqual(body["description"], "D")
        self.assertEqual(body["type"], "plain")
        self.assertIn("order", body)

    def test_create_attachment_multipart(self):
        opener = RecordingOpener()
        opener.route(
            self.api_base + "/boards/1/stacks/2/cards/99/attachments",
            "POST",
            payload={"ok": True},
        )
        with patch("urllib.request.build_opener", return_value=opener):
            client = NextcloudDeck(self.base_url, self.username, self.password)
            resp = client.create_attachment(
                board_id=1,
                stack_id=2,
                card_id=99,
                filename="file.txt",
                mimetype="text/plain",
                content=b"HELLO",
            )

        self.assertEqual(resp, {"ok": True})
        req = opener.requests[0]
        headers = {k.lower(): v for k, v in req.headers.items()}
        self.assertIn("multipart/form-data", headers.get("content-type", ""))
        self.assertIn("boundary=", headers.get("content-type", ""))
        # Body checks
        body = req.data
        self.assertIsInstance(body, (bytes, bytearray))
        self.assertIn(
            b'Content-Disposition: form-data; name="file"; filename="file.txt"', body
        )
        self.assertIn(b"Content-Type: text/plain", body)
        self.assertIn(b"HELLO", body)
        # Content-Length should be correctly set
        self.assertEqual(int(headers.get("content-length")), len(body))


if __name__ == "__main__":
    unittest.main()

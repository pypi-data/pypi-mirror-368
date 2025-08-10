import json
import urllib.request
import base64
import uuid


class NextcloudDeck:
    API_BASE_PATH = "/index.php/apps/deck/api/v1.1"

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url

        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.default_headers = {
            "OCS-APIRequest": "true",
            "Authorization": f"Basic {encoded_credentials}",
        }

        self.opener = urllib.request.build_opener()

    def _get(self, path: str) -> dict | list[dict]:
        request = urllib.request.Request(
            self.base_url + self.API_BASE_PATH + path,
            method="GET",
            headers=self.default_headers,
        )

        with self.opener.open(request) as response:
            return json.loads(response.read().decode())

    def _post(self, path: str, data: dict) -> dict:
        headers = self.default_headers.copy()
        headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            self.base_url + self.API_BASE_PATH + path,
            method="POST",
            headers=headers,
            data=json.dumps(data).encode(),
        )

        with self.opener.open(request) as response:
            return json.loads(response.read().decode())

    def _post_multipart(
        self,
        path: str,
        *,
        data: dict,
        file_field: str,
        file_content: bytes,
        file_filename: str,
        file_mimetype: str,
    ):
        boundary = uuid.uuid4().hex
        headers = self.default_headers.copy()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        body = []
        for name, value in data.items():
            body.append(f"--{boundary}".encode("utf-8"))
            body.append(
                f'Content-Disposition: form-data; name="{name}"'.encode("utf-8")
            )
            body.append("".encode("utf-8"))
            body.append(str(value).encode("utf-8"))

        body.append(f"--{boundary}".encode("utf-8"))
        body.append(
            f'Content-Disposition: form-data; name="{file_field}"; filename="{file_filename}"'.encode(
                "utf-8"
            )
        )
        body.append(f"Content-Type: {file_mimetype}".encode("utf-8"))
        body.append("".encode("utf-8"))
        body.append(file_content)

        body.append(f"--{boundary}--".encode("utf-8"))
        body_data = b"\r\n".join(body)

        headers["Content-Length"] = str(len(body_data))

        request = urllib.request.Request(
            self.base_url + self.API_BASE_PATH + path,
            method="POST",
            headers=headers,
            data=body_data,
        )

        with self.opener.open(request) as response:
            return json.loads(response.read().decode())

    def get_stacks(self, board_id: int) -> list[dict]:
        stacks = self._get(f"/boards/{board_id}/stacks")
        if not isinstance(stacks, list):
            raise Exception("Unexpected response")

        return stacks

    def get_first_stack(self, board_id: int) -> dict | None:
        stacks = self.get_stacks(board_id)
        stacks.sort(key=lambda stack: (stack["order"], stack["id"]))

        return stacks[0] if stacks else None

    def create_card(
        self, board_id: int, stack_id: int, title: str, description: str
    ) -> dict:
        data = {
            "title": title,
            "description": description,
            "order": 999,
            "type": "plain",
        }

        return self._post(f"/boards/{board_id}/stacks/{stack_id}/cards", data)

    def create_attachment(
        self,
        *,
        board_id: int,
        stack_id: int,
        card_id: int,
        filename: str,
        mimetype: str,
        content: bytes,
    ) -> dict:
        data = {
            "type": "file",
        }

        return self._post_multipart(
            f"/boards/{board_id}/stacks/{stack_id}/cards/{card_id}/attachments",
            data=data,
            file_field="file",
            file_filename=filename,
            file_mimetype=mimetype,
            file_content=content,
        )

from dataclasses import dataclass
import imaplib
import email
from email.header import decode_header
import logging
from typing import Iterator
import uuid

logger = logging.getLogger(__name__)


@dataclass
class EmailAttachment:
    filename: str
    mimetype: str
    content: bytes


class Email:
    def __init__(self, id: str, mailbox: str, data: bytes):
        self.id = id
        self.mailbox = mailbox
        self.message = email.message_from_bytes(data)

    @property
    def subject(self) -> str:
        decoded_header = decode_header(self.message["Subject"])[0]
        header_content, encoding = decoded_header[0], decoded_header[1]
        if isinstance(header_content, bytes):
            return header_content.decode(encoding if encoding else "utf-8")
        else:
            return header_content

    @property
    def body(self) -> str:
        if self.message.is_multipart():
            for part in self.message.walk():
                content_type = part.get_content_type()
                if content_type != "text/plain":
                    continue

                content_disposition = part.get("Content-Disposition")
                if (
                    content_disposition
                    and "attachment" in str(content_disposition).lower()
                ):
                    continue

                charset = part.get_content_charset()
                body_bytes = bytes(part.get_payload(decode=True))
                return body_bytes.decode(charset or "utf-8")

            return ""
        else:
            content_type = self.message.get_content_type()
            if content_type != "text/plain":
                return ""

            body_bytes = bytes(self.message.get_payload(decode=True))
            return body_bytes.decode()

    @property
    def attachments(self) -> Iterator[EmailAttachment]:
        if not self.message.is_multipart():
            return

        for part in self.message.walk():
            content_disposition = part.get("Content-Disposition")
            if (
                not content_disposition
                or "attachment" not in str(content_disposition).lower()
            ):
                continue

            yield EmailAttachment(
                filename=part.get_filename() or uuid.uuid4().hex,
                mimetype=part.get_content_type(),
                content=bytes(part.get_payload(decode=True)),
            )


class ImapClient:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def __enter__(self):
        self.conn = imaplib.IMAP4_SSL(self.host, self.port)
        self.conn.login(self.username, self.password)
        return self

    def __exit__(self, *args):
        self.conn.close()
        self.conn.logout()

    def get_inbox_mails(self) -> Iterator[Email]:
        MAILBOX = "INBOX"

        self.conn.select(MAILBOX)

        status, data = self.conn.search(None, "ALL")
        if status != "OK":
            raise Exception("Error fetching emails")

        for message_id in data[0].split():
            status, data = self.conn.fetch(message_id, "(RFC822)")
            if status != "OK":
                logger.error(f"Error fetching message {message_id}")
                continue

            if data[0] is None:
                logger.error(f"Message {message_id} is empty")
                continue

            yield Email(
                id=message_id.decode(),
                mailbox=MAILBOX,
                data=bytes(data[0][1]),
            )

    def mark_mail_as_deleted(self, mailbox: str, message_id: str):
        """
        Mark a mail as deleted. The mail will not be deleted until the mailbox
        is expunged.
        """

        self.conn.select(mailbox)
        self.conn.store(message_id, "+FLAGS", "\\Deleted")

    def move_mail(
        self, *, message_id: str, source_mailbox: str, destination_mailbox: str
    ):
        """
        Move a mail from one mailbox to another. The mail will be marked as
        deleted in the source mailbox. Note that the mail will not be deleted
        until the mailbox is expunged.
        """

        self.conn.select(source_mailbox)
        self.conn.copy(message_id, destination_mailbox)
        self.conn.store(message_id, "+FLAGS", "\\Deleted")

    def expunge(self):
        self.conn.expunge()

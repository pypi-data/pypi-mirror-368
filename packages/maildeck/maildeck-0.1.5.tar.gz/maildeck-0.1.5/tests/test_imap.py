import unittest
from unittest.mock import patch, Mock
from email.message import EmailMessage

from maildeck.imap import ImapClient, Email


def build_email_bytes(
    subject="Subject",
    body_text="Body",
    attachments=None,
    include_plain_attachment=False,
):
    msg = EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "rcpt@example.com"
    msg["Subject"] = subject

    if attachments or include_plain_attachment:
        # multipart
        msg.set_content(body_text)
        # Add non-plain attachments by default
        for fname, mimetype, content in attachments or []:
            maintype, subtype = mimetype.split("/", 1)
            msg.add_attachment(
                content, maintype=maintype, subtype=subtype, filename=fname
            )
        if include_plain_attachment:
            msg.add_attachment(
                b"ATTACHMENT TEXT",
                maintype="text",
                subtype="plain",
                filename="note.txt",
            )
    else:
        # simple text/plain
        msg.set_content(body_text)

    return msg.as_bytes()


class TestImap(unittest.TestCase):
    def test_email_subject_and_body_plain(self):
        raw = build_email_bytes(subject="Hello", body_text="Hi there")
        email_obj = Email(id="1", mailbox="INBOX", data=raw)
        self.assertEqual(email_obj.subject, "Hello")
        self.assertEqual(email_obj.body.strip(), "Hi there")

    def test_email_body_multipart_picks_text_plain(self):
        raw = build_email_bytes(
            subject="Multipart",
            body_text="This is the body",
            attachments=[("file.pdf", "application/pdf", b"PDFDATA")],
        )
        email_obj = Email(id="2", mailbox="INBOX", data=raw)
        self.assertEqual(email_obj.body.strip(), "This is the body")

    def test_email_attachments_iterator(self):
        raw = build_email_bytes(
            subject="With attachment",
            body_text="Body",
            attachments=[("file.bin", "application/octet-stream", b"BIN")],
        )
        email_obj = Email(id="3", mailbox="INBOX", data=raw)
        atts = list(email_obj.attachments)
        self.assertEqual(len(atts), 1)
        self.assertEqual(atts[0].filename, "file.bin")
        self.assertEqual(atts[0].mimetype, "application/octet-stream")
        self.assertEqual(atts[0].content, b"BIN")

    def test_plain_text_attachment_not_treated_as_body(self):
        # Include a text/plain attachment and ensure body remains original text content
        raw = build_email_bytes(
            subject="S",
            body_text="Original body",
            attachments=[("doc.txt", "text/plain", b"ATTACHMENT TEXT")],
        )
        email_obj = Email(id="4", mailbox="INBOX", data=raw)
        self.assertEqual(email_obj.body.strip(), "Original body")

    def test_html_only_body_with_text_plain_attachment_not_treated_as_body(self):
        msg = EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "rcpt@example.com"
        msg["Subject"] = "S"
        # Only HTML body (no text/plain body part)
        msg.set_content("<p>HTML only</p>", subtype="html")
        # Add a text/plain attachment
        msg.add_attachment(
            b"ATTACHMENT TEXT",
            maintype="text",
            subtype="plain",
            filename="a.txt",
        )

        raw = msg.as_bytes()
        email_obj = Email(id="html-1", mailbox="INBOX", data=raw)
        # Expect empty body because there is no text/plain body part
        self.assertEqual(email_obj.body, "")

    def test_get_inbox_mails_yields_email_objects(self):
        # Prepare a simple message
        raw = build_email_bytes(subject="X", body_text="Y")

        conn = Mock()
        conn.login.return_value = ("OK", [])
        conn.select.return_value = ("OK", [])
        conn.search.return_value = ("OK", [b"1"])
        conn.fetch.return_value = ("OK", [(b"1", raw)])
        conn.close.return_value = ("OK", [])
        conn.logout.return_value = ("OK", [])

        with patch("imaplib.IMAP4_SSL", return_value=conn):
            with ImapClient("imap.example.com", 993, "u", "p") as client:
                mails = list(client.get_inbox_mails())

        self.assertEqual(len(mails), 1)
        self.assertEqual(mails[0].subject, "X")
        self.assertEqual(mails[0].mailbox, "INBOX")

    def test_mark_deleted_and_expunge(self):
        conn = Mock()
        with patch("imaplib.IMAP4_SSL", return_value=conn):
            with ImapClient("imap.example.com", 993, "u", "p") as client:
                client.mark_mail_as_deleted("INBOX", "5")
                client.expunge()

        conn.select.assert_called_with("INBOX")
        conn.store.assert_called_with("5", "+FLAGS", "\\Deleted")
        conn.expunge.assert_called_once()


if __name__ == "__main__":
    unittest.main()

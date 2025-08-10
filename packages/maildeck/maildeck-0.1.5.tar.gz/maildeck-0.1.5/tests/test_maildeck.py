import unittest

from maildeck.maildeck import Maildeck
from maildeck.imap import EmailAttachment


class FakeEmail:
    def __init__(self, subject, body, attachments=None, id_="1", mailbox="INBOX"):
        self.subject = subject
        self.body = body
        self.attachments = attachments or []
        self.id = id_
        self.mailbox = mailbox


class FakeImapClient:
    def __init__(self, emails):
        self._emails = emails
        self.deleted = []
        self.expunge_called = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get_inbox_mails(self):
        for e in self._emails:
            yield e

    def mark_mail_as_deleted(self, mailbox, message_id):
        self.deleted.append((mailbox, message_id))

    def expunge(self):
        self.expunge_called = True


class FakeDeckClient:
    def __init__(self, stacks=None):
        self._stacks = stacks if stacks is not None else [{"id": 7, "order": 0}]
        self.cards = []
        self.attach_calls = []

    def get_first_stack(self, board_id):
        return self._stacks[0] if self._stacks else None

    def create_card(self, *, board_id, stack_id, title, description):
        # simulate server returning a card id
        card = {"id": 101, "title": title, "description": description}
        self.cards.append((board_id, stack_id, title, description))
        return card

    def create_attachment(
        self,
        *,
        board_id,
        stack_id,
        card_id,
        filename,
        mimetype,
        content,
    ):
        self.attach_calls.append(
            (board_id, stack_id, card_id, filename, mimetype, content)
        )
        return {"ok": True}


class TestMaildeckOrchestration(unittest.TestCase):
    def test_import_with_explicit_stack(self):
        emails = [
            FakeEmail(
                subject="S1",
                body="B1",
                attachments=[EmailAttachment("a.txt", "text/plain", b"A")],
                id_="11",
            )
        ]
        deck_client = FakeDeckClient(stacks=[{"id": 5, "order": 0}])
        imap_client = FakeImapClient(emails)

        service = Maildeck(deck_client=deck_client, imap_client=imap_client)
        service.import_emails(board_id=1, stack_id=5)

        self.assertEqual(len(deck_client.cards), 1)
        self.assertEqual(deck_client.cards[0][1], 5)  # stack_id used
        self.assertEqual(len(deck_client.attach_calls), 1)
        self.assertEqual(imap_client.deleted, [("INBOX", "11")])
        self.assertTrue(imap_client.expunge_called)

    def test_import_uses_first_stack_when_none(self):
        emails = [FakeEmail("S", "B")]
        deck_client = FakeDeckClient(stacks=[{"id": 9, "order": 0}])
        imap_client = FakeImapClient(emails)

        service = Maildeck(deck_client=deck_client, imap_client=imap_client)
        service.import_emails(board_id=2, stack_id=None)

        self.assertEqual(deck_client.cards[0][1], 9)  # used first stack id

    def test_import_raises_when_no_stack(self):
        emails = [FakeEmail("S", "B")]
        deck_client = FakeDeckClient(stacks=[])  # no stacks available
        imap_client = FakeImapClient(emails)

        service = Maildeck(deck_client=deck_client, imap_client=imap_client)
        with self.assertRaises(Exception):
            service.import_emails(board_id=3, stack_id=None)


if __name__ == "__main__":
    unittest.main()

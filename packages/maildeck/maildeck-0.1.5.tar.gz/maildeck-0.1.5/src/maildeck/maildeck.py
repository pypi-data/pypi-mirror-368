from maildeck.imap import ImapClient
from maildeck.deck import NextcloudDeck


class Maildeck:
    def __init__(self, deck_client: NextcloudDeck, imap_client: ImapClient):
        self.deck_client = deck_client
        self.imap_client = imap_client

    def import_emails(self, board_id: int, stack_id: int | None = None):
        if stack_id is None:
            first_stack = self.deck_client.get_first_stack(board_id)
            stack_id = first_stack["id"] if first_stack else None

        if stack_id is None:
            raise Exception("No stack found")

        with self.imap_client:
            for mail in self.imap_client.get_inbox_mails():
                card = self.deck_client.create_card(
                    board_id=board_id,
                    stack_id=stack_id,
                    title=mail.subject,
                    description=mail.body,
                )

                for attachment in mail.attachments:
                    self.deck_client.create_attachment(
                        board_id=board_id,
                        stack_id=stack_id,
                        card_id=card["id"],
                        filename=attachment.filename,
                        mimetype=attachment.mimetype,
                        content=attachment.content,
                    )

                self.imap_client.mark_mail_as_deleted(mail.mailbox, mail.id)

            self.imap_client.expunge()

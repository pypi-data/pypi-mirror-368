import logging
import sys
import maildeck.config as config
import maildeck.deck as deck
import maildeck.imap as imap
import maildeck.maildeck as maildeck

logger = logging.getLogger(__name__)


class Command:
    def __init__(self, config: config.Config):
        imap_client = imap.ImapClient(
            host=config.imap_host,
            port=config.imap_port,
            username=config.imap_user,
            password=config.imap_password,
        )

        deck_client = deck.NextcloudDeck(
            base_url=config.nextcloud_base_url,
            username=config.nextcloud_user,
            password=config.nextcloud_password,
        )

        self.maildeck = maildeck.Maildeck(deck_client, imap_client)

        self.nextcloud_board_id = config.nextcloud_board_id
        self.nextcloud_stack_id = config.nextcloud_stack_id

    def run(self):
        self.maildeck.import_emails(
            board_id=self.nextcloud_board_id,
            stack_id=self.nextcloud_stack_id,
        )


def main() -> int:
    try:
        Command(config=config.Config.from_args(sys.argv[1:])).run()
    except Exception as e:
        logger.error(e)
        return 1
    return 0

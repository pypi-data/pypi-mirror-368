# maildeck

`maildeck` is a Python command-line tool designed to import emails into Nextcloud Deck. It fetches emails from an IMAP server and creates corresponding cards within a Nextcloud Deck board.

The idea is that you would run this script in a cron job or a systemd-timer.

## Features

- **IMAP:** No need to run a postfix server specifically for this use case, an IMAP mailbox is enough.
- **Attachments:** Any mail attachments will be attached to the ticket.
- **Automatic deletion of emails:** Emails are automatically deleted after they are converted to a ticket.

## Requirements

- Python 3.11 or higher
- A dedicated IMAP mailbox
- A Nextcloud instance with Deck 1.3.0 or higher installed

## Installation

```bash
pip install maildeck
```

## Usage

To use Maildeck, you need to provide your IMAP and Nextcloud credentials, either as environment variables or as command-line arguments. Here's how you can run it:

```bash
maildeck [ARGS]
```

### Required Arguments

- **`--imap-user`** IMAP_USER: Your IMAP account username.
- **`--imap-password`** IMAP_PASSWORD: Your IMAP account password.
- **`--imap-host`** IMAP_HOST: Your IMAP server host address.
- **`--nextcloud-base-url`** NEXTCLOUD_BASE_URL: The base URL for your Nextcloud instance.
- **`--nextcloud-user`** NEXTCLOUD_USER: Your Nextcloud account username.
- **`--nextcloud-password`** NEXTCLOUD_PASSWORD: Your Nextcloud account password.
- **`--nextcloud-board-id`** NEXTCLOUD_BOARD_ID: The Nextcloud Deck board ID.

### Optional Arguments

- **`--imap-port`** IMAP_PORT: The IMAP server port. Default is 993.
- **`--nextcloud-stack-id`** NEXTCLOUD_STACK_ID: The Nextcloud Deck stack ID. Default is the first stack in the board.

### Help

- **`-h, --help`**: Show the help message and exit.

**All arguments can also be set as environment variables** with the same name as the placeholder in this help message.

## Alternatives

- You might also want to have a look at [newroco/mail2deck](https://github.com/newroco/mail2deck), which works a bit
  differently.

## License

Maildeck is licensed under the EUPL-1.2 license. For more information, please refer to the LICENSE file in the repository.

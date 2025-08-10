import os
import unittest
from unittest.mock import patch

from maildeck.config import Config


class TestConfig(unittest.TestCase):
    def test_from_args_parses_and_coerces_types(self):
        argv = [
            "--imap-user",
            "user@example.com",
            "--imap-password",
            "secret",
            "--imap-host",
            "imap.example.com",
            "--nextcloud-base-url",
            "https://nc.example.com",
            "--nextcloud-user",
            "ncuser",
            "--nextcloud-password",
            "ncpass",
            "--nextcloud-board-id",
            "42",
            "--imap-port",
            "993",
        ]

        cfg = Config.from_args(argv)

        self.assertEqual(cfg.imap_user, "user@example.com")
        self.assertEqual(cfg.imap_password, "secret")
        self.assertEqual(cfg.imap_host, "imap.example.com")
        self.assertEqual(cfg.nextcloud_base_url, "https://nc.example.com")
        self.assertEqual(cfg.nextcloud_user, "ncuser")
        self.assertEqual(cfg.nextcloud_password, "ncpass")
        self.assertEqual(cfg.nextcloud_board_id, 42)
        self.assertEqual(cfg.imap_port, 993)
        self.assertIsNone(cfg.nextcloud_stack_id)

    def test_env_vars_make_args_optional(self):
        env = {
            "IMAP_USER": "user@example.com",
            "IMAP_PASSWORD": "secret",
            "IMAP_HOST": "imap.example.com",
            "NEXTCLOUD_BASE_URL": "https://nc.example.com",
            "NEXTCLOUD_USER": "ncuser",
            "NEXTCLOUD_PASSWORD": "ncpass",
        }
        # Provide the integer-only args via argv to ensure proper coercion
        argv = [
            "--nextcloud-board-id",
            "7",
        ]
        with patch.dict(os.environ, env, clear=True):
            cfg = Config.from_args(argv)

        self.assertEqual(cfg.imap_user, env["IMAP_USER"])
        self.assertEqual(cfg.imap_password, env["IMAP_PASSWORD"])
        self.assertEqual(cfg.imap_host, env["IMAP_HOST"])
        self.assertEqual(cfg.nextcloud_base_url, env["NEXTCLOUD_BASE_URL"])
        self.assertEqual(cfg.nextcloud_user, env["NEXTCLOUD_USER"])
        self.assertEqual(cfg.nextcloud_password, env["NEXTCLOUD_PASSWORD"])
        self.assertEqual(cfg.nextcloud_board_id, 7)
        # Default IMAP port should be used if not provided
        self.assertEqual(cfg.imap_port, 993)
        self.assertIsNone(cfg.nextcloud_stack_id)

    def test_missing_required_args_raises_system_exit(self):
        with self.assertRaises(SystemExit):
            Config.from_args([])


if __name__ == "__main__":
    unittest.main()

import argparse
import os
from dataclasses import dataclass, field, fields
from typing import Optional, List, Union, get_args, get_origin


@dataclass
class Config:
    imap_user: str = field(metadata={"help": "IMAP account username."})
    imap_password: str = field(metadata={"help": "IMAP account password."})
    imap_host: str = field(metadata={"help": "IMAP server host address."})

    nextcloud_base_url: str = field(
        metadata={"help": "Base URL for Nextcloud instance."}
    )
    nextcloud_user: str = field(metadata={"help": "Nextcloud account username."})
    nextcloud_password: str = field(metadata={"help": "Nextcloud account password."})
    nextcloud_board_id: int = field(metadata={"help": "Nextcloud board ID."})
    nextcloud_stack_id: Optional[int] = field(
        default=None, metadata={"help": "Nextcloud stack ID. Optional."}
    )

    imap_port: int = field(
        default=993, metadata={"help": "IMAP server port number. Default is 993."}
    )

    @classmethod
    def from_args(cls, argv: List[str]):
        parser = argparse.ArgumentParser(
            description="maildeck - Import emails into Nextcloud Deck.",
            epilog="""
                All arguments can be set as environment variables with the same
                name as the placeholder in this help message.
            """,
        )

        for field_info in fields(cls):
            arg_name = f"--{field_info.name.replace('_', '-')}"
            env_var_name = field_info.name.upper()

            type_origin = get_origin(field_info.type)
            type_args = get_args(field_info.type)
            is_optional = type_origin is Union and type(None) in type_args

            base_type = type_args[0] if is_optional else field_info.type

            default_value = os.getenv(
                env_var_name,
                field_info.default
                if field_info.default != field_info.default_factory
                else None,
            )
            is_required = False if default_value is not None or is_optional else True

            help_message = field_info.metadata.get("help", "")

            parser.add_argument(
                arg_name,
                type=base_type,
                help=help_message,
                default=default_value,
                required=is_required,
            )

        args = parser.parse_args(argv)
        args_dict = {k: v for k, v in vars(args).items() if v is not None}

        return cls(**args_dict)

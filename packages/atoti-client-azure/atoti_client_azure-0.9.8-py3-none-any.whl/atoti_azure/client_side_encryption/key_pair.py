from typing import final

import atoti as tt
from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from pydantic.dataclasses import dataclass


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class KeyPair(tt.KeyPair, tt.ClientSideEncryptionConfig):
    """Key pair to use for client side encryption.

    Warning:
        Each encrypted blob must have the metadata attribute ``unencrypted_content_length`` with the unencrypted file size.
        If this is not set, an :guilabel:`Issue while downloading` error will occur.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("session_with_azure_plugin")

        >>> from atoti_azure import KeyPair
        >>> client_side_encryption = KeyPair(
        ...     "public_key", "private_key", key_id="key_id"
        ... )
    """

    key_id: str
    """The ID of the key used to encrypt the blob."""

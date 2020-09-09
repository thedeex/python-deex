# -*- coding: utf-8 -*-
from graphenecommon.aio.message import (
    Message as GrapheneMessage,
    InvalidMessageSignature,
)
from deexbase.account import PublicKey

from .account import Account
from .instance import BlockchainInstance
from ..exceptions import (
    InvalidMemoKeyException,
    AccountDoesNotExistsException,
    WrongMemoKey,
)


@BlockchainInstance.inject
class Message(GrapheneMessage):
    MESSAGE_SPLIT = (
        "-----BEGIN DEEX SIGNED MESSAGE-----",
        "-----BEGIN META-----",
        "-----BEGIN SIGNATURE-----",
        "-----END DEEX SIGNED MESSAGE-----",
    )

    def define_classes(self):
        self.account_class = Account
        self.publickey_class = PublicKey

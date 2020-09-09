# -*- coding: utf-8 -*-
import pytest
import logging

from deex.aio.asset import Asset
from deex.aio.account import Account

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_wallet_key(deex, default_account):
    """Check whether wallet contains key for default account."""
    a = await Account(default_account, blockchain_instance=deex)
    assert a["id"] in await deex.wallet.getAccounts()

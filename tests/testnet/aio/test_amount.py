# -*- coding: utf-8 -*-
import pytest
import logging

from deex.aio.amount import Amount

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_amount_init(deex, assets):
    amount = await Amount("10 USD", blockchain_instance=deex)
    assert amount["amount"] == 10
    copied = await amount.copy()
    assert amount["amount"] == copied["amount"]

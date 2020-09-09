# -*- coding: utf-8 -*-
import asyncio
import pytest
import random
import string

from deex.aio import DeEx
from deex.aio.instance import set_shared_deex_instance, SharedInstance
from deex.aio.genesisbalance import GenesisBalance
from deex.aio.asset import Asset
from deex.aio.account import Account
from deex.aio.price import Price
from deex.exceptions import (
    AssetDoesNotExistsException,
    AccountDoesNotExistsException,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def deex_instance(deex_testnet, private_keys, event_loop):
    """Initialize DeEx instance connected to a local testnet."""
    deex = DeEx(
        node="ws://127.0.0.1:{}".format(deex_testnet.service_port),
        keys=private_keys,
        num_retries=-1,
        loop=event_loop,
    )
    await deex.connect()
    # Shared instance allows to avoid any bugs when deex_instance is not passed
    # explicitly when instantiating objects
    set_shared_deex_instance(deex)
    # Todo: show chain params when connectiong to unknown network
    # https://github.com/deex/python-deex/issues/221

    # Wait for several blocks to be produced
    await asyncio.sleep(5)

    yield deex


@pytest.fixture(scope="session")
async def claim_balance(deex_instance, default_account):
    """Transfer balance from genesis into actual account."""
    genesis_balance = await GenesisBalance(
        "1.15.0", deex_instance=deex_instance
    )
    await genesis_balance.claim(account=default_account)


@pytest.fixture(scope="session")
def deex(deex_instance, claim_balance):
    """Prepare the testnet and return DeEx instance."""
    return deex_instance


@pytest.fixture()
async def not_shared_instance(deex):
    """Unsets shared instance."""
    current_shared_instance = SharedInstance.instance
    SharedInstance.instance = None
    yield deex
    set_shared_deex_instance(current_shared_instance)


@pytest.fixture(scope="session")
async def create_asset(deex, default_account):
    """Create a new asset."""

    async def _create_asset(asset, precision, is_bitasset=False):
        max_supply = (
            1000000000000000 / 10 ** precision if precision > 0 else 1000000000000000
        )
        await deex.create_asset(
            asset,
            precision,
            max_supply,
            is_bitasset=is_bitasset,
            account=default_account,
        )

    return _create_asset


@pytest.fixture(scope="session")
async def issue_asset(deex):
    """
    Issue asset shares to specified account.

    :param str asset: asset symbol to issue
    :param float amount: amount to issue
    :param str to: account name to receive new shares
    """

    async def _issue_asset(asset, amount, to):
        # Clear cache to make sure asset is reloaded from chain
        Asset.clear_cache()
        asset = await Asset(asset, deex_instance=deex)
        await asset.issue(amount, to)

    return _issue_asset


@pytest.fixture(scope="session")
async def assets(create_asset, issue_asset, default_account):
    """Create some assets to use in tests."""
    await create_asset("USD", 3)
    await create_asset("GOLD", 3)
    await issue_asset("USD", 1000, default_account)


@pytest.fixture(scope="session")
async def unused_asset(deex):
    async def func():
        while True:
            asset = "".join(random.choice(string.ascii_uppercase) for x in range(7))
            try:
                await Asset(asset, deex_instance=deex)
            except AssetDoesNotExistsException:
                return asset

    return func


@pytest.fixture(scope="session")
async def unused_account(deex):
    """Find unexistent account."""

    async def func():
        _range = 100000
        while True:
            account = "worker-{}".format(random.randint(1, _range))  # nosec
            try:
                await Account(account, deex_instance=deex)
            except AccountDoesNotExistsException:
                return account

    return func


@pytest.fixture(scope="session")
async def base_bitasset(deex, unused_asset, default_account):
    async def func():
        bitasset_options = {
            "feed_lifetime_sec": 86400,
            "minimum_feeds": 1,
            "force_settlement_delay_sec": 86400,
            "force_settlement_offset_percent": 100,
            "maximum_force_settlement_volume": 50,
            "short_backing_asset": "1.3.0",
            "extensions": [],
        }
        symbol = await unused_asset()
        await deex.create_asset(
            symbol, 5, 10000000000, is_bitasset=True, bitasset_options=bitasset_options
        )
        asset = await Asset(symbol)
        await asset.update_feed_producers([default_account])
        return asset

    return func


@pytest.fixture(scope="module")
async def bitasset(deex, base_bitasset, default_account):
    asset = await base_bitasset()
    price = await Price(10.0, base=asset, quote=await Asset("TEST"))
    await deex.publish_price_feed(asset.symbol, price, account=default_account)
    return asset

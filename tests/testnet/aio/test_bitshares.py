# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from datetime import datetime
from deex.aio.asset import Asset
from deex.aio.amount import Amount
from deex.aio.account import Account
from deex.aio.price import Price
from deex.aio.proposal import Proposals
from deex.aio.worker import Workers
from deex.aio.dex import Dex
from deex.aio.market import Market

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture(scope="module")
async def testworker(deex, default_account):
    amount = await Amount("1000 TEST")
    end = datetime(2099, 1, 1)
    await deex.create_worker("test", amount, end, account=default_account)


@pytest.fixture(scope="module")
async def gs_bitasset(deex, default_account, base_bitasset):
    """Create globally settled bitasset."""
    asset = await base_bitasset()

    price = await Price(10.0, base=asset, quote=await Asset("TEST"))
    await deex.publish_price_feed(asset.symbol, price, account=default_account)
    dex = Dex(blockchain_instance=deex)
    to_borrow = await Amount(1000, asset)
    await dex.borrow(to_borrow, collateral_ratio=2.1, account=default_account)
    price = await Price(1.0, base=asset, quote=await Asset("TEST"))
    # Trigger GS
    await deex.publish_price_feed(asset.symbol, price, account=default_account)
    return asset


@pytest.fixture(scope="module")
async def ltm_account(deex, default_account, unused_account):
    account = await unused_account()
    await deex.create_account(
        account, referrer=default_account, registrar=default_account, password="test"
    )
    await deex.transfer(
        account, 100000, "TEST", memo="xxx", account=default_account
    )
    await deex.upgrade_account(account=account)
    return account


@pytest.mark.asyncio
async def test_aio_chain_props(deex):
    """Test chain properties."""
    # Wait for several blcocks
    await asyncio.sleep(3)
    props = await deex.info()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0


@pytest.mark.asyncio
async def test_transfer(deex, default_account):
    await deex.transfer("init1", 10, "TEST", memo="xxx", account=default_account)


@pytest.mark.asyncio
async def test_create_account(deex, default_account):
    await deex.create_account(
        "foobar", referrer=default_account, registrar=default_account, password="test"
    )


@pytest.mark.asyncio
async def test_upgrade_account(ltm_account):
    account = await Account(ltm_account)
    assert account.is_ltm


@pytest.mark.asyncio
async def test_allow_disallow(deex, default_account):
    await deex.allow("init1", account=default_account)
    await asyncio.sleep(1.1)
    await deex.disallow("init1", account=default_account)


@pytest.mark.asyncio
async def test_update_memo_key(deex, ltm_account, default_account):
    from deexbase.account import PasswordKey

    account = ltm_account
    password = "test2"
    memo_key = PasswordKey(account, password, role="memo")
    pubkey = memo_key.get_public_key()
    await deex.update_memo_key(pubkey, account=account)


@pytest.mark.asyncio
async def test_approve_disapprove_witness(deex, default_account):
    witnesses = ["init1", "init2"]
    await deex.approvewitness(witnesses, account=default_account)
    await asyncio.sleep(1.1)
    await deex.disapprovewitness(witnesses, account=default_account)


@pytest.mark.asyncio
async def test_approve_disapprove_committee(deex, default_account):
    cm = ["init5", "init6"]
    await deex.approvecommittee(cm, account=default_account)
    await asyncio.sleep(1.1)
    await deex.disapprovecommittee(cm, account=default_account)


@pytest.mark.asyncio
async def test_approve_proposal(deex, default_account):
    deex.blocking = "head"
    parent = deex.new_tx()
    proposal = deex.new_proposal(parent=parent)
    await deex.transfer(
        "init1", 1, "TEST", append_to=proposal, account=default_account
    )
    tx = await proposal.broadcast()
    proposal_id = tx["operation_results"][0][1]
    await deex.approveproposal(proposal_id, account=default_account)
    deex.blocking = None


@pytest.mark.asyncio
async def test_disapprove_proposal(deex, default_account, unused_account):
    # Create child account
    account = await unused_account()
    await deex.create_account(
        account, referrer=default_account, registrar=default_account, password="test"
    )
    await deex.transfer(account, 100, "TEST", account=default_account)

    # Grant child account access with 1/2 threshold
    await deex.allow(account, weight=1, threshold=2, account=default_account)

    # Create proposal
    deex.blocking = "head"
    parent = deex.new_tx()
    proposal = deex.new_proposal(parent=parent)
    await deex.transfer(
        "init1", 1, "TEST", append_to=proposal, account=default_account
    )
    tx = await proposal.broadcast()
    proposal_id = tx["operation_results"][0][1]

    # Approve proposal; 1/2 is not sufficient to completely approve, so proposal remains active
    await deex.approveproposal(proposal_id, account=account)
    # Revoke vote
    await deex.disapproveproposal(proposal_id, account=account)
    deex.blocking = None


@pytest.mark.asyncio
async def test_approve_disapprove_worker(deex, testworker, default_account):
    workers = await Workers(default_account)
    worker = workers[0]["id"]
    await deex.approveworker(worker)
    await deex.disapproveworker(worker)


@pytest.mark.asyncio
async def test_set_unset_proxy(deex, default_account):
    await deex.set_proxy("init1", account=default_account)
    await asyncio.sleep(1.1)
    await deex.unset_proxy()


@pytest.mark.skip(reason="cancel() tested indirectly in test_market.py")
@pytest.mark.asyncio
async def test_cancel():
    pass


@pytest.mark.skip(reason="need to provide a way to make non-empty vesting balance")
@pytest.mark.asyncio
async def test_vesting_balance_withdraw(deex, default_account):
    balances = await deex.rpc.get_vesting_balances(default_account)
    await deex.vesting_balance_withdraw(balances[0]["id"], account=default_account)


@pytest.mark.asyncio
async def test_publish_price_feed(deex, base_bitasset, default_account):
    asset = await base_bitasset()
    price = await Price(1.1, base=asset, quote=await Asset("TEST"))
    await deex.publish_price_feed(asset.symbol, price, account=default_account)


@pytest.mark.asyncio
async def test_update_cer(deex, base_bitasset, default_account):
    asset = await base_bitasset()
    price = await Price(1.2, base=asset, quote=await Asset("TEST"))
    await deex.update_cer(asset.symbol, price, account=default_account)


@pytest.mark.asyncio
async def test_update_witness(deex, default_account):
    await deex.update_witness(default_account, url="https://foo.bar/")


@pytest.mark.asyncio
async def test_reserve(deex, default_account):
    amount = await Amount("10 TEST")
    await deex.reserve(amount, account=default_account)


@pytest.mark.asyncio
async def test_create_asset(deex, default_account, bitasset):
    asset = bitasset
    assert asset.is_bitasset


@pytest.mark.asyncio
async def test_create_worker(testworker, default_account):
    w = await Workers(default_account)
    assert len(w) > 0


@pytest.mark.asyncio
async def test_fund_fee_pool(deex, default_account, bitasset):
    await deex.fund_fee_pool(bitasset.symbol, 100.0, account=default_account)


@pytest.mark.asyncio
async def test_create_committee_member(deex, ltm_account):
    await deex.create_committee_member(account=ltm_account)


@pytest.mark.asyncio
async def test_account_whitelist(deex, default_account):
    await deex.account_whitelist("init1", account=default_account)


@pytest.mark.asyncio
async def test_bid_collateral(deex, default_account, gs_bitasset):
    asset = gs_bitasset
    additional_collateral = await Amount("1000 TEST")
    debt_covered = await Amount(10, asset)
    await deex.bid_collateral(
        additional_collateral, debt_covered, account=default_account
    )


@pytest.mark.asyncio
async def test_asset_settle(deex, default_account, bitasset):
    asset = bitasset
    dex = Dex(blockchain_instance=deex)
    to_borrow = await Amount(1000, asset)
    await dex.borrow(to_borrow, collateral_ratio=2.1, account=default_account)
    to_settle = await Amount(100, asset)
    await deex.asset_settle(to_settle, account=default_account)


@pytest.mark.asyncio
async def test_htlc(deex, default_account):
    """Test both htlc_create and htlc_redeem."""
    amount = await Amount("10 TEST")
    deex.blocking = "head"
    tx = await deex.htlc_create(
        amount, default_account, "foobar", account=default_account
    )
    htlc_id = tx["operation_results"][0][1]
    await deex.htlc_redeem(htlc_id, "foobar", account=default_account)
    deex.blocking = None


@pytest.mark.asyncio
async def test_subscribe_to_pending_transactions(deex, default_account):
    await deex.cancel_subscriptions()
    await deex.subscribe_to_pending_transactions()

    # Generate an event
    await deex.transfer("init1", 10, "TEST", memo="xxx", account=default_account)

    event_correct = False
    for _ in range(0, 6):
        event = await deex.notifications.get()
        if event["params"][0] == 0:
            event_correct = True
            break
    assert event_correct


@pytest.mark.asyncio
async def test_subscribe_to_blocks(deex):
    await deex.cancel_subscriptions()
    await deex.subscribe_to_blocks()
    event_correct = False
    for _ in range(0, 6):
        event = await deex.notifications.get()
        if event["params"][0] == 2:
            event_correct = True
            break
    assert event_correct


@pytest.mark.asyncio
async def test_subscribe_to_accounts(deex, default_account):
    await deex.cancel_subscriptions()
    # Subscribe
    await deex.subscribe_to_accounts([default_account])

    # Generate an event
    await deex.transfer("init1", 10, "TEST", memo="xxx", account=default_account)

    # Check event
    event_correct = False
    for _ in range(0, 6):
        event = await deex.notifications.get()
        if event["params"][0] == 1:
            event_correct = True
            break
    assert event_correct


@pytest.mark.asyncio
async def test_subscribe_to_market(deex, assets, default_account):
    await deex.cancel_subscriptions()
    await asyncio.sleep(1.1)
    market = await Market("TEST/USD")
    await deex.subscribe_to_market(market, event_id=4)

    # Generate an event
    await market.sell(1, 1, account=default_account)

    # Check event
    event_correct = False
    for _ in range(0, 10):
        event = await deex.notifications.get()
        log.debug("getting event")
        if event["params"][0] == 4:
            event_correct = True
            break
    assert event_correct

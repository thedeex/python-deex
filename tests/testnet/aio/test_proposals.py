# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from deexbase.operationids import getOperationNameForId

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_finalizeOps_proposal(deex):
    deex.clear()
    proposal = deex.proposal()
    await deex.transfer("init1", 1, "TEST", append_to=proposal)
    tx = await deex.tx().json()  # default tx buffer
    ops = tx["operations"]
    assert len(ops) == 1
    assert getOperationNameForId(ops[0][0]) == "proposal_create"
    prop = ops[0][1]
    assert len(prop["proposed_ops"]) == 1
    assert getOperationNameForId(prop["proposed_ops"][0]["op"][0]) == "transfer"


@pytest.mark.asyncio
async def test_finalizeOps_proposal2(deex):
    deex.clear()
    proposal = deex.new_proposal()
    await deex.transfer("init1", 2, "TEST", append_to=proposal)
    tx = await deex.tx().json()  # default tx buffer
    ops = tx["operations"]
    assert len(ops) == 1
    assert getOperationNameForId(ops[0][0]) == "proposal_create"
    prop = ops[0][1]
    assert len(prop["proposed_ops"]) == 1
    assert getOperationNameForId(prop["proposed_ops"][0]["op"][0]) == "transfer"


@pytest.mark.asyncio
async def test_finalizeOps_combined_proposal(deex):
    deex.clear()
    parent = deex.new_tx()
    proposal = deex.new_proposal(parent)
    await deex.transfer("init1", 3, "TEST", append_to=proposal)
    await deex.transfer("init1", 4, "TEST", append_to=parent)
    tx = await parent.json()
    ops = tx["operations"]
    assert len(ops) == 2
    assert getOperationNameForId(ops[0][0]) == "proposal_create"
    assert getOperationNameForId(ops[1][0]) == "transfer"
    prop = ops[0][1]
    assert len(prop["proposed_ops"]) == 1
    assert getOperationNameForId(prop["proposed_ops"][0]["op"][0]) == "transfer"


@pytest.mark.asyncio
async def test_finalizeOps_changeproposer_new(deex):
    deex.clear()
    proposal = deex.proposal(proposer="init5")
    await deex.transfer("init1", 5, "TEST", append_to=proposal)
    tx = await deex.tx().json()
    ops = tx["operations"]
    assert len(ops) == 1
    assert getOperationNameForId(ops[0][0]) == "proposal_create"
    prop = ops[0][1]
    assert len(prop["proposed_ops"]) == 1
    assert prop["fee_paying_account"] == "1.2.11"
    assert getOperationNameForId(prop["proposed_ops"][0]["op"][0]) == "transfer"


@pytest.mark.asyncio
async def test_new_proposals(deex):
    deex.clear()
    p1 = deex.new_proposal()
    p2 = deex.new_proposal()
    assert id(p1) is not None
    assert id(p2) is not None


@pytest.mark.asyncio
async def test_new_txs(deex):
    deex.clear()
    p1 = deex.new_tx()
    p2 = deex.new_tx()
    assert id(p1) is not None
    assert id(p2) is not None

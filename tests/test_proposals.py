# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from deex import DeEx
from deexbase.operationids import getOperationNameForId
from deex.instance import set_shared_deex_instance
from .fixtures import fixture_data, deex


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_finalizeOps_proposal(self):
        # proposal = deex.new_proposal(deex.tx())
        proposal = deex.proposal()
        deex.transfer("init1", 1, "DX", append_to=proposal)
        tx = deex.tx().json()  # default tx buffer
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(getOperationNameForId(ops[0][0]), "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]), "transfer"
        )

    def test_finalizeOps_proposal2(self):
        proposal = deex.new_proposal()
        # proposal = deex.proposal()
        deex.transfer("init1", 1, "DX", append_to=proposal)
        tx = deex.tx().json()  # default tx buffer
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(getOperationNameForId(ops[0][0]), "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]), "transfer"
        )

    def test_finalizeOps_combined_proposal(self):
        parent = deex.new_tx()
        proposal = deex.new_proposal(parent)
        deex.transfer("init1", 1, "DX", append_to=proposal)
        deex.transfer("init1", 1, "DX", append_to=parent)
        tx = parent.json()
        ops = tx["operations"]
        self.assertEqual(len(ops), 2)
        self.assertEqual(getOperationNameForId(ops[0][0]), "proposal_create")
        self.assertEqual(getOperationNameForId(ops[1][0]), "transfer")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]), "transfer"
        )

    def test_finalizeOps_changeproposer_new(self):
        proposal = deex.proposal(proposer="init5")
        deex.transfer("init1", 1, "DX", append_to=proposal)
        tx = deex.tx().json()
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(getOperationNameForId(ops[0][0]), "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(prop["fee_paying_account"], "1.2.90747")
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]), "transfer"
        )

    """
    def test_finalizeOps_changeproposer_legacy(self):
        deex.proposer = "init5"
        tx = deex.transfer("init1", 1, "DX")
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(prop["fee_paying_account"], "1.2.11")
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "transfer")
    """

    def test_new_proposals(self):
        p1 = deex.new_proposal()
        p2 = deex.new_proposal()
        self.assertIsNotNone(id(p1), id(p2))

    def test_new_txs(self):
        p1 = deex.new_tx()
        p2 = deex.new_tx()
        self.assertIsNotNone(id(p1), id(p2))

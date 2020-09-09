# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from deex import DeEx
from deex.block import Block, BlockHeader
from deex.instance import set_shared_deex_instance
from deex.utils import parse_time
from .fixtures import fixture_data


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_block(self):
        block = Block(1, use_cache=True)
        self.assertEqual(block["previous"], "0000000000000000000000000000000000000000")
        self.assertEqual(block.time(), parse_time("2015-10-13T14:12:24"))

    def test_blockheader(self):
        header = BlockHeader(1, use_cache=True)
        self.assertEqual(header["previous"], "0000000000000000000000000000000000000000")
        self.assertEqual(header.time(), parse_time("2015-10-13T14:12:24"))

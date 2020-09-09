# -*- coding: utf-8 -*-
import unittest
from deex.blockchainobject import Object
from .fixtures import fixture_data, deex


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_object(self):
        Object("2.1.0")

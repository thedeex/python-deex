# -*- coding: utf-8 -*-
from deex.utils import assets_from_string


def test_assets_from_string():
    assert assets_from_string("USD:DX") == ["USD", "DX"]
    assert assets_from_string("DXBOTS.S1:DX") == ["DXBOTS.S1", "DX"]

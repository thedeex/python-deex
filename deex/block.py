# -*- coding: utf-8 -*-
from .instance import BlockchainInstance
from graphenecommon.block import (
    Block as GrapheneBlock,
    BlockHeader as GrapheneBlockHeader,
)


@BlockchainInstance.inject
class Block(GrapheneBlock):
    """
    Read a single block from the chain.

    :param int block: block number
    :param deex.deex.DeEx blockchain_instance: DeEx
        instance
    :param bool lazy: Use lazy loading

    Instances of this class are dictionaries that come with additional
    methods (see below) that allow dealing with a block and it's
    corresponding functions.

    .. code-block:: python

        from deex.block import Block
        block = Block(1)
        print(block)

    .. note:: This class comes with its own caching function to reduce the
              load on the API server. Instances of this class can be
              refreshed with ``Account.refresh()``.
    """

    pass


@BlockchainInstance.inject
class BlockHeader(GrapheneBlockHeader):
    pass

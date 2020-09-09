# -*- coding: utf-8 -*-
from .account import Account
from .instance import BlockchainInstance
from graphenecommon.aio.committee import Committee as GrapheneCommittee


@BlockchainInstance.inject
class Committee(GrapheneCommittee):
    """
    Read data about a Committee Member in the chain.

    :param str member: Name of the Committee Member
    :param deex blockchain_instance: DeEx() instance to use when
        accesing a RPC
    :param bool lazy: Use lazy loading
    """

    def define_classes(self):
        self.type_id = 5
        self.account_class = Account

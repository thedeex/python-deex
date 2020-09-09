# -*- coding: utf-8 -*-
class BrokenDeexInstance:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        raise ValueError("Attempting to use BrokenDeexInstance")


class DeexIsolator(object):
    enabled = False

    @classmethod
    def enable(self):
        if not self.enabled:
            from deex.instance import set_shared_deex_instance

            broken = BrokenDeexInstance()
            set_shared_deex_instance(broken)
            self.enabled = True

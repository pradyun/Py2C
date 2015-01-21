"""Implements base class of all Analysers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import abc
from py2c.base_worker import BaseWorker

__all__ = ["BaseAnalyser"]


class BaseAnalyser(BaseWorker):
    """ABC of all analysers
    """

    def work(self, node):
        return self.analyse(node)

    @abc.abstractmethod
    def analyse(self, node):
        raise NotImplementedError()

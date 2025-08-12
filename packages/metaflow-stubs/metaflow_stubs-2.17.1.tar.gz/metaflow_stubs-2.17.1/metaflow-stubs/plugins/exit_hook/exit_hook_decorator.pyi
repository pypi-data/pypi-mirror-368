######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.17.1                                                                                 #
# Generated on 2025-08-11T22:07:35.888058                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...


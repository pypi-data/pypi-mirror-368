######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.17.1                                                                                 #
# Generated on 2025-08-11T22:07:35.872648                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...


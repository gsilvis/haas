# Copyright 2013-2014 Massachusetts Open Cloud Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.

"""Authenticate and authorize the user.

This module contains the helper functions and exceptions used elsewhere, as
well as prototypes for methods that authentication backends will use.
"""

import importlib

from haas.config import cfg
from haas.api import APIError


class AuthenticationFailureError(APIError):
    """An exception indicating that the user's authentication failed"""

class UnauthenticatedError(APIError):
    """An exception indicating that the user did not authenticate"""

class UnauthorizedError(APIError):
    """An exception indicating that the user does not have the requisite
    privileges to perform the requested operation."""


def authorize(project):
    """Authenticate AND authorize the user.

    This is the only place authentication can take place, for boring technical
    reasons that will hopefully be fixed.  Ideally, authentication would
    always happen before any processing of the request, but it is not really
    security-essential that that be so.  (It does effect some things---for
    instance, unauthenticated users can enumerate some resources, since we
    fetch some resources in API calls to find out who the user must
    authenticate for.)

    Takes in the name of a project, or None.
    """

    auth_name = cfg.get('general', 'auth')
    auth = importlib.import_module('haas.auth_mechanisms.' + auth_name)
    auth.authenticate()
    auth.authorize(project)

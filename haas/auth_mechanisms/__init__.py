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

"""The API specification for HaaS auth backends.

Authentication schemes are given the parameters to a request (in
moc.rest.local.environ), and set and read fields in 'moc.rest.local.auth'.  On
failure, they raise an exception.
"""

def authenticate():
    """Authenticate user-input parameters.

    Takes in request parameters as 'moc.rest..local.environ'.  Sets any values
    needed in authorize() in 'moc.rest.local.auth'.  Some likely useful values
    include 'user', 'role', and 'project'.  If succesful returns, and if
    unsuccesful raises haas.auth.AuthenticationFailureError .
    """
    pass


def authorize(project):
    """Authorize an action associated with a given project

    Uses values provided in 'moc.rest.local.auth' to make its decision.
    Returns on success, and raises haas.auth.UnauthorizedError on failure.

    Takes in the name of a project, or None for operations not associated with
    a project.
    """
    pass


def client_auth():
    """Create authentication information on client-side

    Takes in any information from the system that may be necessary, and
    produces an 'auth' object that can be passed to the 'requests' library.
    The system information used will likely be stored in environment
    variables.
    """
    return None

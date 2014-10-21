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

"""A built-in user/password-based auth scheme.

Uses HTTP Basic Auth to get a user and password.  Checks user membership to
authenticate.  Has a hard-coded list of actions that are admin-only or doable
by everyone.  The username 'admin' is magic, and always grants administrator
privileges.
"""

from moc.rest import local
from haas import api, auth, model
from os import environ
from requests.auth import HTTPBasicAuth
from werkzeug import Request

def authenticate():
    """Check if the given user/password credentials are correct."""
    auth_data = Request(local.environ).authorization
    if not auth_data:
        # FIXME: We should set WWW-Authenticate in the response, but that is
        # tricky from here.
        raise auth.UnauthenticatedError("Basic Auth required")
    db = model.Session()
    user = db.query(model.User).filter_by(label=auth_data.username).first()
    if (user is not None) and user.verify_password(auth_data.password):
        local.auth = {"user" : auth_data.username}
        return
    else:
        # If no user in database, or password is wrong...
        raise auth.AuthenticationFailureError(
            "Bad user/password combination.")

def authorize(project):
    """Check that user has access to project, or is admin.

    If 'project' is None, admin privileges are required.  (Currently,
    operations that anyone is allowed to perform don't call authorize at all.)

    If 'project' is not None, then the user must have access to the project or
    be admin.
    """
    if local.auth["user"] == "admin":
        # Administrator can do anything
        return

    if project is None:
        # Non-administrator can't do admin actions
        raise auth.UnauthorizedError(
            "Admin privileges required for this operation.")

    db = model.Session()
    user = db.query(model.User).filter_by(label=local.auth["user"]).first()
    if user is None:
        # Annoying race condition
        raise auth.UnauthorizedError(
            "User disappeared between authentication and authorization.")

    project = db.query(model.Project).filter_by(label=project).first()
    if (project is None) or (project not in user.projects):
        # Either the project exists but the user doesn't have access to it, or
        # the project doesn't exist.  Raise the same error either way, to
        # prevent project enumeration.
        raise auth.UnauthorizedError(
            "User not authorized to access this project.")

    return # Succesful authorization

def client_auth():
    """Get user/password from system environment variables."""
    user = environ['HAAS_USER']
    password = environ['HAAS_PASSWORD']
    return HTTPBasicAuth(user, password)

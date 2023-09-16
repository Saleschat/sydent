from typing import TYPE_CHECKING
from sydent.http.auth import authV2
from sydent.http.servlets import (
    SydentResource,
    MatrixRestError,
    Request,
    send_cors,
    jsonwrap,
    get_args
)
from sydent.types import JsonDict

if TYPE_CHECKING:
    from sydent.sydent import Sydent

from sydent.db.identity_association import IdentityAssociationStore
from sydent.util import time_msec

class IdentitiesServlet(SydentResource):
    '''
    Handles request to add identities like, name and org_id
    '''

    def __init__(self, sydent: "Sydent") -> None:
        super().__init__()
        self.sydent = sydent
        self.allowed_mediums = ["name", "org_id", "email"]

    @jsonwrap
    def render_POST(self, request: Request) -> JsonDict:
        send_cors(request)
        account = authV2(self.sydent, request)
        args = get_args(request, ("medium", "value", "mxid"))

        medium = args["medium"]
        # can the value be a number ??
        value = args["value"]
        mxid = args["mxid"]

        if value is None or (not isinstance(value, str) and len(value) == 0):
            raise MatrixRestError(
                400,
                "M_INVALID_PARAM",
                "Invalid value provided"
            )

        if medium not in self.allowed_mediums:
            raise MatrixRestError(
                400, 
                "M_INVALID_PARAM",
                "Invalid medium provided"
            )

        if account:
            # make sure that the user is the same as
            if account.userId != mxid:
                raise MatrixRestError(
                    403,
                    "M_UNAUTHORIZED",
                    "This user is prohibited from binding to the user"
                )



        identityAssocStore = IdentityAssociationStore(self.sydent)
        identityAssocStore.addOrUpdateAssociation(medium, value, mxid, time_msec())

        return { "succes": True }
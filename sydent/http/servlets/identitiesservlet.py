from typing import TYPE_CHECKING, List, Dict
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
from jwt.exceptions import JWTDecodeError
if TYPE_CHECKING:
    from sydent.sydent import Sydent


class IdentitiesServlet(SydentResource):
    '''
    Handles request that have mxid and and token of the user and gets the 
    identity information for that user using third party source
    '''

    def __init__(self, sydent: "Sydent") -> None:
        super().__init__()
        self.sydent = sydent

    @jsonwrap
    def render_POST(self, request: Request) -> JsonDict:

        send_cors(request)
        account = authV2(self.sydent, request)
        args = get_args(request, ("org_id", "mxid", "3pids",))

        org_id = args["org_id"]
        mxid = args["mxid"]
        threepids = args["3pids"]

        def validate_data(value: any, key: str):
            if not isinstance(value, str) or value == "":
                raise MatrixRestError(
                    400, "M_INVALID_PARAM", key + " must be a non-empty string")

        validate_data(org_id, "org_id")
        validate_data(mxid, "mxid")

        if not isinstance(threepids, list):
            raise MatrixRestError(
                400, "M_INVALID_PARAM", "3pids must be a list of `key`, `value` pairs")

        if account:
            # make sure that the user is the same as
            if account.userId != mxid:
                raise MatrixRestError(
                    403,
                    "M_UNAUTHORIZED",
                    "This user is prohibited from binding to the user"
                )

        self.sydent.identityBinder.addBinding(org_id, mxid, threepids)

        return {"success": True}

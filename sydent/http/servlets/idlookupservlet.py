from typing import TYPE_CHECKING
from sydent.http.auth import authV2
from sydent.http.servlets import (
    SydentResource,
    get_args,
    jsonwrap,
    send_cors,
)
from sydent.db.threepid_associations import GlobalAssociationStore
from sydent.types import JsonDict
from twisted.web.server import Request
from sydent.http.servlets import MatrixRestError

if TYPE_CHECKING:
    from sydent.sydent import Sydent


class IdLookupServlet(SydentResource):
    def __init__(self, sydent: "Sydent") -> None:
        super().__init__()
        self.sydent = sydent
        self.globalAssociationStore = GlobalAssociationStore(self.sydent)

    @jsonwrap
    def render_POST(self, request: Request) -> JsonDict:
        """
        Returns identities related to a particular mxid

        Params: A JSON object containing the following keys:
                * 'mxid': the mxid for which to get the identities
                * 'org_id': the org_id for which to look for identities

        Returns: Object with key 'mappings' which is a list of mxid results
        """

        send_cors(request)

        account = authV2(self.sydent, request)

        # the person who has requested the search
        requester = account.userId

        args = get_args(request, ("mxid", "org_id"))
        mxid = args["mxid"]
        org_id = args["org_id"]

        if not isinstance(mxid, str) or len(mxid) == 0:
            raise MatrixRestError(
                400, "M_BAD_JSON", "mxid should a non-empty string")

        if not isinstance(org_id, str) or len(org_id) == 0:
            raise MatrixRestError(
                400, "M_BAD_JSON", "org_id should a non-empty string")

        result = self.globalAssociationStore.getAssociationsbyMxid(
            mxid, org_id, requester)

        associations = []

        for res in result:
            association = {"key": res[0], "value": res[1]}
            associations.append(association)

        return {"3pids": associations}

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
from operator import itemgetter
if TYPE_CHECKING:
    from sydent.sydent import Sydent


class OrganizationVerifierServlet(SydentResource):
    def __init__(self, sydent: "Sydent") -> None:
        super().__init__()
        self.sydent = sydent
        self.globalAssociationStore = GlobalAssociationStore(self.sydent)

    @jsonwrap
    def render_POST(self, request: Request) -> JsonDict:
        """
        Checks whether two users belong to the same org or not

        Params: A JSON object containing the following keys:
                * 'user': the person whose mxid is known
                * 'medium': the medium of the other user (Optional, if 'other' key is present)
                * 'address': the address for the given medium of the other user (Optional, if 'other' key is present)
                * 'other': mxid of the other user 

        Returns: Object with key 'mappings' which is a list of mxid results
        """

        send_cors(request)

        authV2(self.sydent, request)

        args = get_args(request, ("user", "medium", "address", "other",))

        user, medium, address, other = itemgetter(
            "user", "medium", "address", "other")(args)

        has_medium_and_address = False
        belong_in_same_org = False

        if not isinstance(other, str) or len(other) == 0:
            has_medium_and_address = all(
                isinstance(key, str) and len(args[key]) > 0 for key in ("medium", "address",)
            )

            if not has_medium_and_address:
                raise MatrixRestError(
                    400, "M_BAD_JSON", "Either set the value of 'other' with appropriate mxid or set 'medium' and 'address'")

        if has_medium_and_address:
            if medium != "email":
                raise MatrixRestError(
                    400, "M_INVALID_PARAM", "medium should only be email or phone number"
                )

            belong_in_same_org = self.globalAssociationStore.checkSameOrgByMedium(user, medium, address)

        else:
            belong_in_same_org = self.globalAssociationStore.checkSameOrgByMxid(user, other)

        return {"same_org": belong_in_same_org}

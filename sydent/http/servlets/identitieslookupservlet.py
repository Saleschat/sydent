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
if TYPE_CHECKING:
    from sydent.sydent import Sydent


class IdentitiesLookupServlet(SydentResource):
    def __init__(self, sydent: "Sydent") -> None:
        super().__init__()
        self.sydent = sydent
        self.globalAssociationStore = GlobalAssociationStore(self.sydent)

    @jsonwrap
    def render_POST(self, request: Request) -> JsonDict:
        """
        Perform lookups for identities based on the search criteria.
        Search criteria would mostly be a string and the search results would
        be filtered based on the org_id identity

        Params: A JSON object containing the following keys:
                * 'search': the search term to filter identities
                * 'org_id': org_id of the requester

        Returns: Object with key 'mappings' which is a list of mxid results
        """

        send_cors(request)

        account = authV2(self.sydent, request)

        # the person who has requested the search
        requester = account.userId

        args = get_args(request, ("search", "org_id"))
        search_term = args["search"]

        mxids = self.globalAssociationStore.getMxidsForSearchTermByOrgId(
            search_term, requester)

        return {"mappings": mxids}

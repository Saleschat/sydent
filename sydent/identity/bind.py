import logging
from typing import TYPE_CHECKING, Dict, Any, List
from sydent.types import JsonDict


if TYPE_CHECKING:
    from sydent.sydent import Sydent

logger = logging.getLogger(__name__)


class IdentityBinder:
    def __init__(self, sydent: "Sydent") -> None:
        self.sydent = sydent
        self.allowed_keys = ["first_name", "last_name",
                             "email", "org_id", "display_name", "crm_id"]

    def addBinding(self, org_id: str, mxid: str, threepids: List[Dict[str, str]]) -> None:

        for threepid in threepids:
            if threepid["key"] not in self.allowed_keys:
                raise KeyError("%s is not a valid threepid key",
                               threepid["key"])

        for threepid in threepids:
            self.sydent.threepidBinder.addBinding(
                medium=threepid["key"], address=threepid["value"], mxid=mxid, org_id=org_id)

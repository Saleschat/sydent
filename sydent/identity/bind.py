import logging
import jwt
from typing import TYPE_CHECKING, Dict, Any
from sydent.types import JsonDict

if TYPE_CHECKING:
    from sydent.sydent import Sydent

logger = logging.getLogger(__name__)

class IdentityBinder:
    def __init__(self, sydent: "Sydent") -> None:
        self.sydent = sydent
        self.allowed_keys = ["first_name", "last_name", "email", "org_id"]
        self.jwt = jwt.JWT()

    def _walk_claims(self, response: JsonDict) -> Dict[str, str]:
        dict: Dict[str, str] = {}
        self._walk_claims_helper(response, dict)
        return dict

    def _walk_claims_helper(self, dict: JsonDict, result: Dict[str, str]) -> None:
        for key in dict:
            if isinstance(dict[key], Dict):
                self._walk_claims_helper(dict[key], result)
        
            if key in self.allowed_keys:
                result.__setitem__(key, dict[key])

    def addBinding(self, token: str, mxid: str) -> None:
        claims: Dict[str, Any] = self.jwt.decode(message=token, do_verify=False)
       
        identity_dict = self._walk_claims(claims)
        identity_dict.__setitem__("first_name", identity_dict["first_name"].lower().strip())
        identity_dict.__setitem__("last_name", identity_dict["last_name"].lower().strip())

        for key in self.allowed_keys:
            self.sydent.threepidBinder.addBinding(medium=key, address=identity_dict[key], mxid=mxid)
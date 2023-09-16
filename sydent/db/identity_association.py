from typing import TYPE_CHECKING, List, Tuple
if TYPE_CHECKING:
    from sydent.sydent import Sydent

class IdentityAssociationStore:

    def __init__(self, sydent: "Sydent") -> None:
        self.sydent = sydent
        

    def addOrUpdateAssociation(self, medium: str, value: str, mxid: str, ts: int) -> None:
        """
        Binds the given identity to the given mxid

        :param medium: The medium of the identity (eg. org_id)
        :param value: The value of the identity
        :param mxid: The matrix ID the identity is associated with
        """

        cur = self.sydent.db.cursor()

        cur.execute(
            "insert or replace into identities "
            "(medium, value, mxid, ts)"
            " values (?, ?, ?, ?)",
            (
                medium,
                value,
                mxid,
                ts
            )
        )

        self.sydent.db.commit()

    def getMxids(self, search: str, requester: str) -> List[str]:
        """
        Given a search term, returns a list of mxids of the identites that 
        match the search term and have the same org_id identity

        :param search: search term to get find the identities
        :param requester: mxid of the user requesting the search

        :return: a list of mxid
        """
        
        cur = self.sydent.db.cursor()
        sql_search_term = "%" + search + "%"

        res = cur.execute(
            "SELECT a.mxid FROM identities AS a JOIN identities AS b "
            "ON a.mxid = b.mxid WHERE a.medium != 'org_id' AND b.medium = 'org_id' "
            "AND b.value=(SELECT value FROM identities WHERE medium = 'org_id' and mxid = ?) "
            "AND a.value LIKE ? AND a.mxid != ? GROUP BY a.mxid LIMIT 100 OFFSET 0",
            (requester, sql_search_term, requester)
        )

        results = []
        row: Tuple[str]
        for row in res.fetchall():
            results.append(row[0])

        return results

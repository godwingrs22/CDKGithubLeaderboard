from typing import TypedDict

class Contributor(TypedDict):
    username: str
    prsMerged: int
    prsReviewed: int
    totalScore: int

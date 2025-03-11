from typing import TypedDict

class Contributor(TypedDict):
    username: str
    prsMerged: int
    prsReviewed: int
    issues_created: int
    totalScore: int

from typing import TypedDict

class Contributor(TypedDict):
    username: str
    prsMerged: int
    prsReviewed: int
    issuesOpened: int
    discussionsAnswered: int
    totalScore: int

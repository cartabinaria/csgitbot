from pydantic import BaseModel
import datetime

class Author(BaseModel):
    name: str
    email: str

class BranchName(BaseModel):
    """
    Example of a branch name string
    Flecart/20240202-18h11m/8f31bd0c-5bb4-4384-b1cc-6d62c7784ccd
    """
    username: str
    date: datetime.datetime
    uuid: str

    @classmethod
    def from_str(cls, branch_name: str) -> "BranchName":
        """Create a BranchName object from a string.
        """
        obj = cls(username="", date=datetime.datetime.now(), uuid="") # temporary placeholders.
        splitted = branch_name.split("/")
        obj.username, obj.date, obj.uuid = splitted[0], splitted[1], splitted[2]
        obj.date = datetime.datetime.strptime(obj.date, "%Y%m%d-%Hh%Mm")
        return obj
from . import oauth
from . import github

def init_endpoints():
    oauth.init_globals()
    github.init_github_service()
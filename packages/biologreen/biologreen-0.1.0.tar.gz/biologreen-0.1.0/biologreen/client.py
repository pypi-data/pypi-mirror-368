from .resources.auth import AuthResource

class BioLogreenClient:
    """The main client for interacting with the Bio-Logreen API."""

    def __init__(self, api_key: str, base_url: str = "https://api.biologreen.com/v1"):
        if not api_key:
            raise ValueError("An API key is required to use the Bio-Logreen SDK.")
        
        self.api_key = api_key
        self.base_url = base_url
        
        # Initialize all the different parts of the API
        self.auth = AuthResource(self)

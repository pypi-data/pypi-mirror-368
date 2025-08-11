from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper

class WolframAlphaTool:
    def __init__(self):
        """Initialize the wolfram alpha tool."""
        self.client = WolframAlphaAPIWrapper()
        
    def run(self, query: str = None):
        if query:
            result = self.client.run(query)
            return result


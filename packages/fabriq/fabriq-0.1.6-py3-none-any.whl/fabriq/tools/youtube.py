from langchain_community.tools import YouTubeSearchTool

class YoutubeSearch:
    def __init__(self):
        """Initialize the yahoo finance news tool."""
        self.client = YouTubeSearchTool()

    def run(self, query: str = None, numResults: int = 5):
        if query:
            query = f"{query},{numResults}"
            result = self.client.run(query)
            return result

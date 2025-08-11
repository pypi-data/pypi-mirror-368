from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

class YFinanceNews:
    def __init__(self):
        """Initialize the yahoo finance news tool."""
        self.client = YahooFinanceNewsTool()
        
    def run(self, query: str = None):
        if query:
            result = self.client.invoke(query)
            return result


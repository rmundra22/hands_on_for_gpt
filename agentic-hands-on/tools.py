import feedparser
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
from collections import Counter
from textblob import TextBlob


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def schema(self) -> dict:
        """Return OpenAI/Groq-compatible tool schema"""

    @abstractmethod
    def run(self, **kwargs) -> dict:
        """Execute tool"""

        
class ChooseTransportTool(BaseTool):
    name = "choose_transport"
    description = "Choose Kafka vs API based on system constraints"

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sla_hours": {"type": "integer"},
                        "volume": {"type": "integer"},
                        "push": {"type": "boolean"}
                    },
                    "required": ["sla_hours", "volume", "push"]
                }
            }
        }

    def run(self, sla_hours: int, volume: int, push: bool) -> dict:
        if push and sla_hours >= 2 and volume >= 1000:
            return {"transport": "Kafka"}
        return {"transport": "API"}

    
class EstimateCostTool(BaseTool):
    name = "estimate_cost"
    description = "Estimate relative infrastructure cost"

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transport": {
                            "type": "string",
                            "enum": ["Kafka", "API"]
                        },
                        "volume": {"type": "integer"}
                    },
                    "required": ["transport", "volume"]
                }
            }
        }

    def run(self, transport: str, volume: int) -> dict:
        if transport == "Kafka":
            return {"cost": "Medium–High (broker, ops, storage)"}
        return {"cost": "Low–Medium (stateless scaling)"}


class EstimateLatencyTool(BaseTool):
    name = "estimate_latency"
    description = "Estimate end-to-end system latency"

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transport": {
                            "type": "string",
                            "enum": ["Kafka", "API"]
                        },
                        "sla_hours": {"type": "integer"}
                    },
                    "required": ["transport", "sla_hours"]
                }
            }
        }

    def run(self, transport: str, sla_hours: int) -> dict:
        if transport == "Kafka":
            return {"latency": "Seconds–Minutes (async)"}
        return {"latency": "Milliseconds–Seconds (sync)"}
    

class FetchNewsTool(BaseTool):
    name = "fetch_news"
    description = "Fetch latest news headlines using open RSS feeds"

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "limit": {"type": "integer"}
                    },
                    "required": ["topic", "limit"]
                }
            }
        }

    def run(self, topic: str, limit: int) -> dict:
        feed_url = f"https://news.google.com/rss/search?q={topic}"
        feed = feedparser.parse(feed_url)
        headlines = [e.title for e in feed.entries[:limit]]
        return {"headlines": headlines}


class PlotTopicFrequencyTool(BaseTool):
    name = "plot_topic_frequency"
    description = "Plot most frequent words in headlines"

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "headlines": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["headlines"]
                }
            }
        }

    def run(self, headlines: list[str]) -> dict:
        words = []
        for h in headlines:
            words.extend(w.lower() for w in h.split() if len(w) > 3)

        counts = Counter(words).most_common(10)
        labels, values = zip(*counts)

        plt.figure()
        plt.bar(labels, values)
        plt.xticks(rotation=45, ha="right")
        plt.title("Top words in news headlines")
        plt.tight_layout()
        plt.show()

        return {"status": "plot_created"}


class AnalyzeSentimentTool(BaseTool):
    name = "analyze_sentiment"
    description = "Analyze sentiment of text headlines"

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "headlines": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["headlines"]
                }
            }
        }

    def run(self, headlines: list[str]) -> dict:
        scores = [TextBlob(h).sentiment.polarity for h in headlines]
        avg = sum(scores) / len(scores) if scores else 0
        return {"average_sentiment": round(avg, 3)}

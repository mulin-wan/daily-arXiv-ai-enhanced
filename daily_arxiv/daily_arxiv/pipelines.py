# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import arxiv
import re


class DailyArxivPipeline:
    def __init__(self):
        self.page_size = 100
        self.client = arxiv.Client(page_size=self.page_size)

        # ===== Two-tier railway+ontology filter =====
        self.tier1_keywords = [
            "railway", "rail transit", "urban rail", "metro", "subway", "commuter rail",
            "high-speed rail", "train operation", "train control",
            "ontology", "railway ontology", "transportation ontology", "transit ontology",
        ]

        self.tier2_keywords = [
            "artificial intelligence", "machine learning", "deep learning", "reinforcement learning",
            "neural network", "transformer", "llm", "anomaly detection", "predictive maintenance",
            "demand forecasting", "passenger flow prediction",
            "ontology", "knowledge graph", "railway ontology", "transportation ontology", "transit ontology",
            "semantic model", "semantic interoperability", "ontology alignment", "ontology matching",
            "knowledge representation", "owl", "rdf", "sparql",
            "track inspection", "wheel-rail", "turnout", "switch", "traction power",
            "condition monitoring", "fault diagnosis", "asset management",
            "control system", "cyber-physical system", "cps", "system modeling",
            "system identification", "state estimation",
            "timetabling", "rescheduling", "dispatching", "traffic management", "headway",
            "dwell time", "delay propagation", "capacity planning", "operation optimization",
            "scheduling", "multi-agent scheduling",
        ]

    def _normalize_text(self, text):
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.lower())

    def _hits(self, text, keywords):
        return sum(1 for k in keywords if k in text)

    def _passes_two_tier_filter(self, title, summary):
        text = self._normalize_text(f"{title} {summary}")
        return self._hits(text, self.tier1_keywords) >= 1 and self._hits(text, self.tier2_keywords) >= 1

    def process_item(self, item: dict, spider):
        item["pdf"] = f"https://arxiv.org/pdf/{item['id']}"
        item["abs"] = f"https://arxiv.org/abs/{item['id']}"

        search = arxiv.Search(id_list=[item["id"]])
        paper = next(self.client.results(search))

        item["authors"] = [a.name for a in paper.authors]
        item["title"] = paper.title
        item["categories"] = paper.categories
        item["comment"] = paper.comment
        item["summary"] = paper.summary

        # two-tier hard filter
        if not self._passes_two_tier_filter(item.get("title", ""), item.get("summary", "")):
            spider.logger.info(f"Filtered out by two-tier rule: {item.get('id')}")
            return None

        return item

from pathlib import Path
import re

p = Path(r"daily_arxiv/daily_arxiv/pipelines.py")
s = p.read_text(encoding="utf-8")

if "import re" not in s:
s = s.replace("import arxiv", "import arxiv\nimport re")

if "def _passes_two_tier_filter" not in s:
helper = """
# ===== Two-tier railway+ontology filter =====
tier1_keywords = [
"railway","rail transit","urban rail","metro","subway","commuter rail",
"high-speed rail","train operation","train control",
"ontology","railway ontology","transportation ontology","transit ontology"
]

tier2_keywords = [
"artificial intelligence","machine learning","deep learning","reinforcement learning",
"neural network","transformer","llm","anomaly detection","predictive maintenance",
"demand forecasting","passenger flow prediction",
"ontology","knowledge graph","railway ontology","transportation ontology","transit ontology",
"semantic model","semantic interoperability","ontology alignment","ontology matching",
"knowledge representation","owl","rdf","sparql",
"track inspection","wheel-rail","turnout","switch","traction power",
"condition monitoring","fault diagnosis","asset management",
"control system","cyber-physical system","cps","system modeling",
"system identification","state estimation",
"timetabling","rescheduling","dispatching","traffic management","headway",
"dwell time","delay propagation","capacity planning","operation optimization",
"scheduling","multi-agent scheduling"
]

def _normalize_text(self, text):
if not text:
return ""
return re.sub(r"\\s+", " ", text.lower())

def _hits(self, text, keywords):
return sum(1 for k in keywords if k in text)

def _passes_two_tier_filter(self, title, summary):
text = self._normalize_text(f"{title} {summary}")
return self._hits(text, self.tier1_keywords) >= 1 and self._hits(text, self.tier2_keywords) >= 1

"""
marker = " def process_item(self, item, spider):"
if marker not in s:
raise RuntimeError("process_item not found")
s = s.replace(marker, helper + marker)

if "two-tier hard filter" not in s:
target = ' item["summary"] = paper.summary\n'
if target not in s:
raise RuntimeError("summary assignment not found")
replace = """ item["summary"] = paper.summary

# two-tier hard filter
if not self._passes_two_tier_filter(item.get("title", ""), item.get("summary", "")):
spider.logger.info(f"Filtered out by two-tier rule: {item.get('id')}")
return None
"""
s = s.replace(target, replace)

p.write_text(s, encoding="utf-8")
print("Patched pipelines.py successfully.")

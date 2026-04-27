from __future__ import annotations

import yaml
from typing import Dict, List, Optional


class TopicClassifier:
    def __init__(self, taxonomy_path: str) -> None:
        self._taxonomy_path = taxonomy_path
        self._topics: Dict[str, List[str]] = {}
        self._load_taxonomy(taxonomy_path)

    def _load_taxonomy(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not data:
            return
        if isinstance(data, list):
            for entry in data:
                self._add_entry(entry)
        elif isinstance(data, dict):
            for _category, entries in data.items():
                if isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, str):
                            self._add_entry({"topic": _category, "keywords": [entry, _category]})
                        else:
                            self._add_entry(entry)
                elif isinstance(entries, dict):
                    self._add_entry({"topic": _category, **entries})

    def _add_entry(self, entry: dict) -> None:
        if not isinstance(entry, dict):
            return
        topic = entry.get("topic", entry.get("name", ""))
        keywords = entry.get("keywords", entry.get("terms", []))
        if not topic:
            return
        if isinstance(keypoints := keywords, str):
            keypoints = [keywords]
        self._topics[topic] = keypoints

    def classify(self, text: str, metadata: Optional[dict] = None) -> List[str]:
        if not text:
            return []
        search_text = text.lower()
        if metadata:
            extra = " ".join(str(v) for v in metadata.values() if v)
            search_text = f"{search_text} {extra.lower()}"
        matched: List[str] = []
        for topic, keywords in self._topics.items():
            for kw in keywords:
                if kw.lower() in search_text:
                    matched.append(topic)
                    break
        return matched

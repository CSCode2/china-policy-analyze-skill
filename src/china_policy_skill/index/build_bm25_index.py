from __future__ import annotations

import json
import logging
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional

import re
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25IndexBuilder:
    def __init__(self, index_dir: str) -> None:
        self._index_dir = index_dir
        self._bm25: Optional[BM25Okapi] = None
        self._chunks: List[dict] = []
        self._tokenized_corpus: List[List[str]] = []

    def build(self, chunks_path: str) -> None:
        self._chunks = self._load_chunks(chunks_path)
        if not self._chunks:
            logger.warning("No chunks found at %s", chunks_path)
            self._bm25 = None
            return

        self._tokenized_corpus = []
        for chunk in self._chunks:
            text = chunk.get("text", "")
            tokens = self._tokenize(text)
            self._tokenized_corpus.append(tokens)

        self._bm25 = BM25Okapi(self._tokenized_corpus)
        self._save_index()
        logger.info("Built BM25 index with %d chunks", len(self._chunks))

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> List[dict]:
        if self._bm25 is None:
            self._load_index_if_exists()
        if self._bm25 is None:
            logger.warning("No BM25 index available")
            return []

        query_tokens = self._tokenize(query)
        scores = self._bm25.get_scores(query_tokens)

        candidate_indices = list(range(len(self._chunks)))
        if filters:
            candidate_indices = self._apply_filters(candidate_indices, filters)

        scored = [(i, scores[i]) for i in candidate_indices]
        scored.sort(key=lambda x: x[1], reverse=True)

        results: List[dict] = []
        for idx, score in scored[:top_k]:
            if score <= 0:
                break
            result = dict(self._chunks[idx])
            result["bm25_score"] = float(score)
            results.append(result)

        return results

    def _apply_filters(
        self,
        indices: List[int],
        filters: dict,
    ) -> List[int]:
        filtered: List[int] = []
        for i in indices:
            chunk = self._chunks[i]
            match = True

            if "authority_level" in filters:
                allowed = filters["authority_level"]
                if isinstance(allowed, str):
                    allowed = [allowed]
                if chunk.get("authority_level") not in allowed:
                    match = False

            if "region" in filters:
                region = filters["region"]
                text_lower = chunk.get("text", "").lower()
                source_lower = chunk.get("source_name", "").lower()
                if region.lower() not in text_lower and region.lower() not in source_lower:
                    match = False

            if "doc_type" in filters:
                allowed = filters["doc_type"]
                if isinstance(allowed, str):
                    allowed = [allowed]
                if chunk.get("doc_type") not in allowed:
                    match = False

            if "date_from" in filters or "date_to" in filters:
                pub_date = chunk.get("publish_date", "")
                if pub_date:
                    date_from = filters.get("date_from", "")
                    date_to = filters.get("date_to", "")
                    if date_from and pub_date < date_from:
                        match = False
                    if date_to and pub_date > date_to:
                        match = False
                else:
                    match = False

            if match:
                filtered.append(i)

        return filtered

    _CN_TOKEN_RE = re.compile(r'[\u4e00-\u9fff]|[a-zA-Z]+|\d+')

    def _tokenize(self, text: str) -> List[str]:
        cn_chars = self._CN_TOKEN_RE.findall(text)
        bigrams = []
        for i in range(len(cn_chars) - 1):
            if '\u4e00' <= cn_chars[i] <= '\u9fff' and '\u4e00' <= cn_chars[i+1] <= '\u9fff':
                bigrams.append(cn_chars[i] + cn_chars[i+1])
        return cn_chars + bigrams

    def _load_chunks(self, path: str) -> List[dict]:
        chunks: List[dict] = []
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    chunks.append(json.loads(line))
        return chunks

    def _save_index(self) -> None:
        index_path = Path(self._index_dir)
        index_path.mkdir(parents=True, exist_ok=True)

        with open(index_path / "bm25_index.pkl", "wb") as fh:
            pickle.dump(self._bm25, fh)

        with open(index_path / "bm25_corpus.pkl", "wb") as fh:
            pickle.dump(self._tokenized_corpus, fh)

        with open(index_path / "bm25_chunks.pkl", "wb") as fh:
            pickle.dump(self._chunks, fh)

    def _load_index_if_exists(self) -> None:
        index_path = Path(self._index_dir)
        pkl_path = index_path / "bm25_index.pkl"
        corpus_path = index_path / "bm25_corpus.pkl"
        chunks_path = index_path / "bm25_chunks.pkl"

        if pkl_path.exists() and corpus_path.exists() and chunks_path.exists():
            with open(pkl_path, "rb") as fh:
                self._bm25 = pickle.load(fh)
            with open(corpus_path, "rb") as fh:
                self._tokenized_corpus = pickle.load(fh)
            with open(chunks_path, "rb") as fh:
                self._chunks = pickle.load(fh)
            logger.info("Loaded BM25 index with %d chunks", len(self._chunks))
        else:
            logger.warning("BM25 index files not found at %s", self._index_dir)

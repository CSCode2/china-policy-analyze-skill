from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional


class ChunkBuilder:
    def __init__(self, max_chunk_size: int = 2000, overlap: int = 200) -> None:
        self._max_chunk_size = max_chunk_size
        self._overlap = overlap

    def build_from_document(
        self,
        doc_metadata: dict,
        processed_text: str,
    ) -> List[dict]:
        if not processed_text:
            return []

        doc_id = doc_metadata.get("doc_id", doc_metadata.get("id", ""))
        title = doc_metadata.get("title", "")
        source_name = doc_metadata.get("source_name", "")
        publish_date = doc_metadata.get("publish_date", "")
        authority_level = doc_metadata.get("authority_level", "")
        doc_type = doc_metadata.get("doc_type", "")
        topics = doc_metadata.get("topics", [])
        policy_phrases = doc_metadata.get("policy_phrases", [])

        sections = self._split_by_sections(processed_text)
        chunks: List[dict] = []

        for section_title, section_text in sections:
            paragraphs = self._split_by_size(section_text)
            for para_idx, para_text in enumerate(paragraphs):
                chunk_id = self._generate_chunk_id(doc_id, section_title, para_idx)
                chunk = {
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "title": title,
                    "source_name": source_name,
                    "publish_date": publish_date,
                    "authority_level": authority_level,
                    "doc_type": doc_type,
                    "section_title": section_title,
                    "paragraph_index": para_idx,
                    "topics": topics,
                    "policy_phrases": policy_phrases,
                    "text": para_text,
                }
                chunks.append(chunk)

        return chunks

    def _split_by_sections(self, text: str) -> List[tuple[str, str]]:
        heading_pattern = re.compile(
            r"^(#{1,6}\s+.+|第[一二三四五六七八九十百千]+[章节篇部][\s\S]*?$|[一二三四五六七八九十]+[、.].+?$|\d+[、.]\s*.+)$",
            re.MULTILINE,
        )

        matches = list(heading_pattern.finditer(text))
        if not matches:
            return [("", text)]

        sections: List[tuple[str, str]] = []
        first_text = text[: matches[0].start()].strip()
        if first_text:
            sections.append(("", first_text))

        for i, match in enumerate(matches):
            heading = match.group().lstrip("#").strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append((heading, body))

        return sections if sections else [("", text)]

    def _split_by_size(self, text: str) -> List[str]:
        if len(text) <= self._max_chunk_size:
            return [text]

        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = start + self._max_chunk_size
            if end < len(text):
                split_pos = text.rfind("\n", start, end)
                if split_pos <= start:
                    split_pos = text.rfind("。", start, end)
                if split_pos <= start:
                    split_pos = text.rfind(" ", start, end)
                if split_pos <= start:
                    split_pos = end
                else:
                    split_pos += 1
                chunks.append(text[start:split_pos].strip())
                start = split_pos - self._overlap
                if start < 0:
                    start = split_pos
            else:
                chunks.append(text[start:].strip())
                break

        return [c for c in chunks if c]

    def _generate_chunk_id(self, doc_id: str, section_title: str, para_idx: int) -> str:
        raw = f"{doc_id}|{section_title}|{para_idx}"
        digest = hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]
        return f"chunk_{doc_id}_{digest}" if doc_id else f"chunk_{digest}"

    def write_chunks(
        self,
        chunks: List[dict],
        output_dir: str,
    ) -> None:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        chunks_path = out_path / "chunks.jsonl"
        with open(chunks_path, "w", encoding="utf-8") as fh:
            for chunk in chunks:
                fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")

        metadata_path = out_path / "chunk_metadata.jsonl"
        with open(metadata_path, "w", encoding="utf-8") as fh:
            for chunk in chunks:
                meta = {k: v for k, v in chunk.items() if k != "text"}
                fh.write(json.dumps(meta, ensure_ascii=False) + "\n")

from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class VectorIndexBuilder:
    def build(self, chunks_path: str, **kwargs) -> None:
        logger.info("VectorIndexBuilder.build: not implemented")

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> List[dict]:
        logger.info("VectorIndexBuilder.search: not implemented")
        return []

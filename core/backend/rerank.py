import time
from logging import Logger
from os import getenv

import numpy as np
from cohere import AsyncClientV2
from cohere.v2.types import V2RerankResponse
from langchain_core.documents import Document
from logtools import getLogger

logger: Logger = getLogger()


class Reranker:
    def __init__(self) -> None:
        API_KEY: str | None = getenv("OPENAI_API_KEY")
        BASE_URL: str | None = getenv("OPENAI_API_BASE")
        self.max_reranked_docs: int = int(getenv("COHERE_RERANK_N_DOCS", 10))
        self.boost_weight: float = float(getenv("RERANKER_SCORE_BOOST_WEIGHT", 1.0))
        self.popularity_field: str = getenv("POPULARITY_PAYLOAD_FIELD", "unique_visits")
        self.boost_cap: float = float(getenv("RERANKER_BOOST_CAP", 2.0))  # max extra boost

        if API_KEY is None or BASE_URL is None:
            raise ValueError("OPENAI_API_KEY and OPENAI_API_BASE environment variables must be set for rerank model.")

        self.client: AsyncClientV2 = AsyncClientV2(api_key=API_KEY, base_url=BASE_URL)

    def _none_to_num(self, x: int | None) -> int:
        return x if x is not None else 0

    async def arerank_documents(
        self, query: str, docs: dict[str, list[Document]], popularity_stats: dict[str, float], **kwargs
    ) -> list[Document]:
        """
        Asynchronously rerank a list of documents using the Cohere rerank model.
        Also applies an extra boost based on site visit stats.
        """
        if not docs:
            logger.error(f"No documents to rerank for query: {query}")
            return []

        if not isinstance(docs, dict):
            logger.error(f"Expected docs to be a dict[str, list[Document]], got {type(docs)}")
            return []

        candidates = []
        for _, docs_list in docs.items():
            candidates.extend(docs_list)

        t = time.time()
        response: V2RerankResponse = await self.client.rerank(
            model=getenv("COHERE_RERANK_MODEL", "cohere-rerank-v3.5"),
            query=query,
            documents=[doc.metadata.get("description", "") for doc in candidates],
            request_options=kwargs,  # type: ignore
        )
        logger.debug(f"Rerank API call took {time.time() - t:.2f} seconds")

        # extract the indices from the reranker results
        idxs = np.array([res.index for res in response.results])

        # relevance scores from the reranker and site visit stats from doc metadata
        rel_scores = np.array([res.relevance_score for res in response.results], dtype=np.float64)  ## float64 for max precision
        visits = np.array(
            [self._none_to_num(candidates[i].metadata.get("site_stats", {}).get(self.popularity_field, 0)) for i in idxs], dtype=np.int64
        )
        np.nan_to_num(visits, copy=False)  # extra guard to ensure no NaNs in visits

        # boosting
        # float64 for good precision
        boosts = np.ones_like(rel_scores, dtype=np.float64)
        mean = np.float64(popularity_stats.get("mean") or 0.0)
        std = np.float64(popularity_stats.get("std") or 0.0)

        if mean > 0.0:
            # work in log-space for stability
            log_mean = np.log1p(mean)
            log_visits = np.log1p(np.clip(visits, 0.0, None))

            # standard deviation in log-space: log1p(mean+std) - log1p(mean)
            log_std = max(np.log1p(mean + std) - log_mean, 1e-3)

            # z-score: how many stds above mean (in log scale)
            norm = (log_visits - log_mean) / log_std

            # only positive boosts
            norm = np.clip(norm, 0.0, self.boost_cap)
            boosts *= 1.0 + self.boost_weight * norm
        else:
            # default: no soft boosting
            # log1p is just ln(1 + x) — more stable for small values
            norm = np.log1p(visits) * self.boost_weight
            boosts *= 1.0 + np.clip(norm, 0.0, self.boost_cap)
        # final rerank scores
        rerank_scores = rel_scores * boosts

        # update documents with scores + original positions
        for i, score in zip(idxs, rerank_scores):
            i, score = int(i), float(score)  # make sure it's native python float, pydantic validation fails if not
            candidates[i].metadata["rerank_score"] = score
            candidates[i].metadata["original_idx"] = i
            logger.debug(
                f"Document {candidates[i].metadata.get('name')}, original index: {i}, "
                f"reranked with score: {score:.4f}, site visits: {candidates[i].metadata.get('site_stats', {}).get(self.popularity_field, 0)}"
            )

        # sort docs by new score
        reranked: list[Document] = sorted(candidates, key=lambda x: x.metadata.get("rerank_score", 0), reverse=True)

        # keep only top_n results returned by the reranker
        if kwargs.get("n_results") is not None:
            n_results = int(kwargs["n_results"])
        else:
            n_results = self.max_reranked_docs
        top_n = min(n_results, len(reranked))
        reranked = reranked[:top_n]

        # store info for debug
        reranked_info = [
            {
                "original_index": doc.metadata.get("original_idx"),
                "reranked_index": i,
                "rerank_score": doc.metadata.get("rerank_score"),
                "name": doc.metadata.get("name"),
            }
            for i, doc in enumerate(reranked)
        ]
        logger.debug(f"Reranking for query: {query}\n{reranked_info}")

        return reranked

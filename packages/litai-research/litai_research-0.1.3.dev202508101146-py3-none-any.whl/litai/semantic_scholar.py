"""Semantic Scholar API client for paper search."""

import asyncio
import random
import httpx
import structlog

from litai.models import Paper

logger = structlog.get_logger()


class SemanticScholarClient:
    """Client for Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org"
    DEFAULT_FIELDS = [
        "paperId",
        "title",
        "url",
        "abstract",
        "year",
        "authors",
        "citationCount",
        "influentialCitationCount",
        "tldr",
        "publicationTypes",
        "openAccessPdf",
        "externalIds",
        "venue",
    ]

    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={"User-Agent": "LitAI/1.0"},
        )
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()
            self.client = None

    def _convert_to_paper(self, data: dict) -> Paper:
        """Convert Semantic Scholar API response to our Paper model."""
        # Extract author names
        authors = [author.get("name", "Unknown") for author in data.get("authors", [])]

        # Extract TL;DR if available
        tldr = None
        if data.get("tldr") and isinstance(data["tldr"], dict):
            tldr = data["tldr"].get("text")

        # Extract open access PDF URL
        pdf_url = None
        if data.get("openAccessPdf") and isinstance(data["openAccessPdf"], dict):
            pdf_url = data["openAccessPdf"].get("url")

        # Extract external IDs
        external_ids = data.get("externalIds", {})

        return Paper(
            paper_id=data["paperId"],
            title=data.get("title", ""),
            authors=authors,
            year=data.get("year", 0),
            abstract=data.get("abstract", ""),
            arxiv_id=external_ids.get("ArXiv"),
            doi=external_ids.get("DOI"),
            citation_count=data.get("citationCount", 0),
            tldr=tldr,
            venue=data.get("venue"),
            open_access_pdf_url=pdf_url,
        )

    async def search(
        self, query: str, limit: int = 10, fields: list[str] | None = None
    ) -> list[Paper]:
        """
        Search for papers using Semantic Scholar API with retry logic for rate limiting.

        Args:
            query: Search query
            limit: Maximum number of results
            fields: List of fields to include in response

        Returns:
            List of Paper objects
        """
        if fields is None:
            fields = self.DEFAULT_FIELDS

        params = {
            "query": query,
            "limit": limit,
            "fields": ",".join(fields),
        }

        max_retries = 3
        base_delay = 3.0  # Start with 3 seconds

        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    "searching_papers", query=query, limit=limit, attempt=attempt
                )
                response = await self.client.get(
                    f"{self.BASE_URL}/graph/v1/paper/search", params=params
                )
                response.raise_for_status()

                data = response.json()
                papers = [
                    self._convert_to_paper(paper_data)
                    for paper_data in data.get("data", [])
                    if paper_data.get("paperId")  # Skip malformed entries
                ]

                logger.info(
                    "search_complete",
                    query=query,
                    found=len(papers),
                    total=data.get("total", 0),
                )

                return papers

            except httpx.HTTPStatusError as e:
                logger.error(
                    "search_http_error",
                    query=query,
                    status_code=e.response.status_code,
                    detail=e.response.text,
                    attempt=attempt,
                )

                if e.response.status_code == 429:
                    if attempt < max_retries:
                        # Calculate delay with jitter to avoid thundering herd
                        delay = base_delay * (2**attempt) + random.uniform(0, 1)
                        logger.info(
                            "rate_limit_retry",
                            query=query,
                            attempt=attempt + 1,
                            delay=delay,
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise Exception(
                            "Rate limit exceeded after multiple retries. Please try again later."
                        )
                elif e.response.status_code >= 500:
                    raise Exception("Semantic Scholar API is temporarily unavailable.")
                else:
                    raise Exception(f"Search failed: {e.response.status_code}")

            except httpx.TimeoutException:
                logger.error("search_timeout", query=query)
                raise Exception("Search timed out. Please try again.")
            except httpx.RequestError as e:
                logger.error("search_network_error", query=query, error=str(e))
                raise Exception("Network error. Please check your connection.")
            except Exception as e:
                logger.error("search_error", query=query, error=str(e))
                raise

        # This should never be reached due to the exceptions above, but mypy needs it
        return []
    
    @classmethod
    async def shutdown(cls):
        """No longer needed - clients are managed via context manager."""
        pass

    async def get_paper(
        self, paper_id: str, fields: list[str] | None = None
    ) -> Paper | None:
        """
        Get a specific paper by ID.

        Args:
            paper_id: Semantic Scholar paper ID
            fields: List of fields to include in response

        Returns:
            Paper object or None if not found
        """
        if fields is None:
            fields = self.DEFAULT_FIELDS

        params = {"fields": ",".join(fields)}

        try:
            logger.info("fetching_paper", paper_id=paper_id)
            response = await self.client.get(
                f"{self.BASE_URL}/graph/v1/paper/{paper_id}", params=params
            )
            response.raise_for_status()

            data = response.json()
            return self._convert_to_paper(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("paper_not_found", paper_id=paper_id)
                return None
            logger.error(
                "get_paper_http_error",
                paper_id=paper_id,
                status_code=e.response.status_code,
                detail=e.response.text,
            )
            raise Exception(f"Failed to get paper: {e.response.status_code}")
        except Exception as e:
            logger.error("get_paper_error", paper_id=paper_id, error=str(e))
            raise

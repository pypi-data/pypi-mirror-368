"""Paper extraction functionality using LLMs."""

import json
from dataclasses import dataclass
from datetime import datetime

import structlog
from rich.progress import Progress, SpinnerColumn, TextColumn

from litai.database import Database
from litai.llm import LLMClient
from litai.models import Extraction
from litai.pdf_processor import PDFProcessor

logger = structlog.get_logger()


@dataclass
class KeyPoint:
    """Represents a key point extracted from a paper."""

    claim: str
    evidence: str
    section: str


class PaperExtractor:
    """Extracts structured information from papers using LLMs."""

    def __init__(self, db: Database, llm: LLMClient, pdf_processor: PDFProcessor):
        """Initialize the extractor.

        Args:
            db: Database instance
            llm: LLM client instance
            pdf_processor: PDF processor instance
        """
        self.db = db
        self.llm = llm
        self.pdf_processor = pdf_processor
        # Approximately 750 words per 1000 tokens for academic text
        self.max_tokens_per_chunk = 3000
        self.words_per_token = 0.75

    def chunk_text(self, text: str, max_tokens: int = 3000) -> list[str]:
        """Split text into chunks that fit within token limits.

        Args:
            text: Full text to chunk
            max_tokens: Maximum tokens per chunk

        Returns:
            List of text chunks
        """
        # Estimate words per chunk
        max_words = int(max_tokens * self.words_per_token)

        # Split into paragraphs first to maintain coherence
        paragraphs = text.split("\n\n")

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_word_count = 0

        for paragraph in paragraphs:
            word_count = len(paragraph.split())

            # If single paragraph exceeds limit, split it
            if word_count > max_words:
                # Add current chunk if it has content
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_word_count = 0

                # Split long paragraph by sentences
                sentences = paragraph.replace(". ", ".\n").split("\n")
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if current_word_count + sentence_words > max_words:
                        if current_chunk:
                            chunks.append("\n\n".join(current_chunk))
                        current_chunk = [sentence]
                        current_word_count = sentence_words
                    else:
                        if not current_chunk:
                            current_chunk = [sentence]
                        else:
                            current_chunk[-1] += " " + sentence
                        current_word_count += sentence_words

            # If adding paragraph would exceed limit, start new chunk
            elif current_word_count + word_count > max_words:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                current_chunk = [paragraph]
                current_word_count = word_count

            # Otherwise add to current chunk
            else:
                current_chunk.append(paragraph)
                current_word_count += word_count

        # Add final chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        logger.info(
            "text_chunked",
            total_words=len(text.split()),
            chunk_count=len(chunks),
            max_words_per_chunk=max_words,
        )

        return chunks

    async def extract_key_points(self, paper_id: str) -> list[KeyPoint]:
        """Extract key points from a paper.

        Args:
            paper_id: ID of the paper to extract from

        Returns:
            List of extracted key points
        """
        # Check cache first
        cached_extraction = self.db.get_extraction(paper_id, "key_points")
        if cached_extraction:
            logger.info("using_cached_extraction", paper_id=paper_id)
            points_data = cached_extraction.content.get("points", [])
            return [
                KeyPoint(claim=p["claim"], evidence=p["evidence"], section=p["section"])
                for p in points_data
            ]

        # Get paper text
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Downloading and extracting PDF...", total=None)

            text = await self.pdf_processor.process_paper(paper_id)
            if not text:
                logger.error("failed_to_get_paper_text", paper_id=paper_id)
                raise ValueError(f"Could not extract text from paper {paper_id}")

            progress.update(task, description="Extracting key points...")

            # Chunk the text
            chunks = self.chunk_text(text, self.max_tokens_per_chunk)

            # Extract points from each chunk
            all_points = []
            for i, chunk in enumerate(chunks):
                progress.update(
                    task, description=f"Processing chunk {i + 1}/{len(chunks)}..."
                )

                prompt = self._create_extraction_prompt(chunk)
                response = await self.llm.complete(prompt, temperature=0.0)

                # Parse the response
                points = self._parse_extraction_response(response["content"])
                all_points.extend(points)

                logger.info(
                    "chunk_processed",
                    paper_id=paper_id,
                    chunk=i + 1,
                    points_found=len(points),
                )

            # Deduplicate and select top 5
            progress.update(task, description="Selecting best points...")
            final_points = self._select_best_points(all_points, n=5)

            # Cache the results
            extraction_content = {
                "points": [
                    {"claim": p.claim, "evidence": p.evidence, "section": p.section}
                    for p in final_points
                ]
            }

            extraction = Extraction(
                paper_id=paper_id,
                extraction_type="key_points",
                content=extraction_content,
                created_at=datetime.now(),
            )
            self.db.add_extraction(extraction)

            progress.update(task, description="Done!", completed=True)

        return final_points

    def _create_extraction_prompt(self, text: str) -> str:
        """Create the prompt for extracting key points.

        Args:
            text: Paper text chunk

        Returns:
            Formatted prompt
        """
        return f"""Extract the most important claims from this academic paper excerpt. For each claim, provide:
1. The claim itself (1-2 sentences)
2. A direct quote from the text as evidence
3. The section where it appears

Focus on novel contributions, key findings, and important methodological points.

Text:
{text}

Provide your response as a JSON array with this structure:
[
  {{
    "claim": "The main assertion or finding",
    "evidence": "Direct quote from the text supporting this claim",
    "section": "Section name or number where this appears"
  }}
]

Extract up to 5 key points from this excerpt."""

    def _parse_extraction_response(self, response: str) -> list[KeyPoint]:
        """Parse the LLM response into KeyPoint objects.

        Args:
            response: Raw LLM response

        Returns:
            List of KeyPoint objects
        """
        try:
            # Try to find JSON in the response
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1

            if start_idx == -1 or end_idx == 0:
                logger.warning("no_json_found_in_response")
                return []

            json_str = response[start_idx:end_idx]
            points_data = json.loads(json_str)

            points = []
            for item in points_data:
                if all(key in item for key in ["claim", "evidence", "section"]):
                    points.append(
                        KeyPoint(
                            claim=item["claim"],
                            evidence=item["evidence"],
                            section=item["section"],
                        )
                    )

            return points

        except json.JSONDecodeError as e:
            logger.warning("failed_to_parse_extraction", error=str(e))
            return []
        except Exception as e:
            logger.exception("unexpected_parsing_error", error=str(e))
            return []

    def _select_best_points(self, points: list[KeyPoint], n: int = 5) -> list[KeyPoint]:
        """Select the best n points from all extracted points.

        Simple deduplication based on claim similarity.
        In a production system, this could use embeddings for semantic similarity.

        Args:
            points: All extracted points
            n: Number of points to select

        Returns:
            Best n points
        """
        if len(points) <= n:
            return points

        # Simple deduplication: remove points with very similar claims
        unique_points: list[KeyPoint] = []
        seen_claims: set[str] = set()

        for point in points:
            # Simple normalization for comparison
            normalized_claim = point.claim.lower().strip()

            # Check if we've seen a very similar claim
            is_duplicate = False
            for seen in seen_claims:
                # Very simple similarity check - in production use proper NLP
                if len(set(normalized_claim.split()) & set(seen.split())) > 5:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_points.append(point)
                seen_claims.add(normalized_claim)

        # Return first n unique points
        return unique_points[:n]

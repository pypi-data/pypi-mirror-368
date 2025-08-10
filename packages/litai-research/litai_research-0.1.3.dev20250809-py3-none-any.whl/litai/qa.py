"""Question answering module for targeted paper queries."""

import json
from datetime import datetime

from litai.models import Paper, Extraction
from litai.database import Database
from litai.llm import LLMClient
from litai.pdf_processor import PDFProcessor
from litai.utils.logger import get_logger

logger = get_logger(__name__)


class PaperQA:
    """Handles targeted question answering for specific papers."""

    def __init__(
        self,
        db: Database,
        llm_client: LLMClient,
        pdf_processor: PDFProcessor,
    ):
        self.db = db
        self.llm_client = llm_client
        self.pdf_processor = pdf_processor

    async def answer_question(
        self, papers: list[Paper], question: str
    ) -> str:
        """Answer a specific question about given papers.

        Args:
            papers: List of papers to search within
            question: The question to answer

        Returns:
            A concise answer to the question
        """
        logger.info(
            "qa_answer_start", paper_count=len(papers), question=question
        )

        # If multiple papers, process each and combine answers
        if len(papers) > 1:
            return await self._answer_multiple_papers(papers, question)
        else:
            return await self._answer_single_paper(papers[0], question)

    async def _answer_single_paper(self, paper: Paper, question: str) -> str:
        """Answer question for a single paper."""
        # Check cache first
        cache_key = f"qa_{question[:50]}"  # Truncate long questions
        cached_extraction = self.db.get_extraction(paper.paper_id, cache_key)
        if cached_extraction:
            logger.info("qa_cache_hit", paper_id=paper.paper_id)
            # Extract the answer from the cached content
            if isinstance(cached_extraction.content, dict):
                return cached_extraction.content.get("answer", "")

        # Get paper text
        paper_text = await self.pdf_processor.process_paper(paper.paper_id)
        if not paper_text:
            logger.warning("qa_no_text", paper_id=paper.paper_id)
            return f"Could not retrieve text for paper: {paper.title}"

        # Truncate text if too long (focus on most relevant sections)
        max_chars = 30000  # ~7500 tokens
        if len(paper_text) > max_chars:
            # Try to find relevant sections based on question keywords
            relevant_text = self._extract_relevant_sections(
                paper_text, question, max_chars
            )
        else:
            relevant_text = paper_text

        # Generate answer
        prompt = f"""You are analyzing the following research paper to answer a specific question.

Paper: "{paper.title}"
Authors: {', '.join(paper.authors[:3])}

Question: {question}

Paper text:
{relevant_text}

Instructions:
1. Answer the question directly and concisely (1-3 sentences)
2. Be specific and factual
3. If the answer is not in the paper, say so
4. Do not add interpretation beyond what's stated

Answer:"""

        response = await self.llm_client.complete(
            prompt, temperature=0.1  # Low temperature for factual answers
        )
        answer = response["content"]
        usage = response["usage"]

        logger.info(
            "qa_answer_generated",
            paper_id=paper.paper_id,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            cost=usage.estimated_cost,
        )

        # Cache the answer
        extraction = Extraction(
            paper_id=paper.paper_id,
            extraction_type=cache_key,
            content={"answer": answer},
            created_at=datetime.now()
        )
        self.db.add_extraction(extraction)

        return answer.strip()

    async def _answer_multiple_papers(
        self, papers: list[Paper], question: str
    ) -> str:
        """Answer question across multiple papers."""
        answers = []

        # Get answer from each paper
        for i, paper in enumerate(papers):
            logger.info(
                "qa_processing_paper",
                paper_num=i + 1,
                total=len(papers),
                paper_id=paper.paper_id,
            )

            answer = await self._answer_single_paper(paper, question)
            if answer and not answer.startswith("Could not retrieve"):
                answers.append(
                    {
                        "paper": paper.title,
                        "year": paper.year,
                        "answer": answer,
                    }
                )

        if not answers:
            return "Could not find answers in the selected papers."

        # Combine answers
        combined_prompt = f"""Question: {question}

Answers from different papers:
{json.dumps(answers, indent=2)}

Task: Synthesize these answers into a single coherent response that:
1. Highlights commonalities and differences
2. Is concise (2-4 sentences)
3. Mentions which papers provided which information when relevant
4. Remains factual to what the papers stated

Combined answer:"""

        response = await self.llm_client.complete(
            combined_prompt, temperature=0.1
        )
        combined_answer = response["content"]
        usage = response["usage"]

        logger.info(
            "qa_combined_answer",
            paper_count=len(papers),
            answer_count=len(answers),
            cost=usage.estimated_cost,
        )

        return combined_answer.strip()

    def _extract_relevant_sections(
        self, text: str, question: str, max_chars: int
    ) -> str:
        """Extract sections most relevant to the question."""
        # Simple keyword-based extraction
        question_lower = question.lower()
        keywords = [
            word
            for word in question_lower.split()
            if len(word) > 3 and word not in ["what", "where", "when", "which", "how"]
        ]

        # Split into paragraphs
        paragraphs = text.split("\n\n")

        # Score paragraphs by keyword presence
        scored_paragraphs = []
        for para in paragraphs:
            if len(para.strip()) < 50:  # Skip very short paragraphs
                continue

            para_lower = para.lower()
            score = sum(1 for keyword in keywords if keyword in para_lower)
            if score > 0:
                scored_paragraphs.append((score, para))

        # Sort by score and take top paragraphs
        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)

        relevant_text = []
        char_count = 0

        for score, para in scored_paragraphs:
            if char_count + len(para) > max_chars:
                break
            relevant_text.append(para)
            char_count += len(para)

        # If we didn't find much relevant text, just take from the beginning
        if char_count < max_chars // 2:
            relevant_text.append(text[: max_chars - char_count])

        return "\n\n".join(relevant_text)

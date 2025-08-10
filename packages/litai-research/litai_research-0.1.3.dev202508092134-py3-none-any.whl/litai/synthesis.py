"""Paper synthesis functionality for generating literature reviews."""

import json
import re
from dataclasses import dataclass
from litai.database import Database
from litai.llm import LLMClient
from litai.extraction import PaperExtractor, KeyPoint
from litai.models import Paper
from litai.search_tool import PaperSearchTool
from litai.synthesis_tools import SynthesisOrchestrator
from litai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RelevantPaper:
    """A paper deemed relevant to a synthesis query."""

    paper: Paper
    relevance_score: float  # 0-1
    relevance_reason: str
    key_points: list[KeyPoint] | None = None


@dataclass
class SynthesisResult:
    """Result of synthesizing multiple papers."""

    question: str
    synthesis: str
    relevant_papers: list[RelevantPaper]


class PaperSynthesizer:
    """Handles synthesis of multiple papers to answer research questions.
    
    This class now acts as a compatibility layer that uses the new
    conversational synthesis system internally.
    """

    def __init__(self, db: Database, llm_client: LLMClient, extractor: PaperExtractor, search_tool: PaperSearchTool | None = None):
        self.db = db
        self.llm = llm_client
        self.extractor = extractor
        self.search_tool = search_tool
        self.orchestrator = SynthesisOrchestrator(db, llm_client, extractor)

    async def synthesize(self, question: str) -> SynthesisResult:
        """Generate a synthesis answering the question using papers in library.
        
        Now uses the conversational synthesis system internally.
        """
        # Use orchestrator for synthesis
        result = await self.orchestrator.synthesize(
            question=question,
            context_type="key_points",  # Use key points for backward compatibility
            depth="thorough"  # Use thorough depth for full synthesis
        )
        
        # Convert to legacy format
        relevant_papers = []
        for paper in result["papers"]:
            # Extract key points for each paper
            key_points = []
            try:
                key_points = await self.extractor.extract_key_points(paper.paper_id)
            except Exception as e:
                logger.warning(f"Failed to extract key points from {paper.title}: {e}")
                
            relevant_papers.append(
                RelevantPaper(
                    paper=paper,
                    relevance_score=0.8,  # Default score
                    relevance_reason="Selected as relevant to the question",
                    key_points=key_points
                )
            )
        
        return SynthesisResult(
            question=question,
            synthesis=result["answer"],
            relevant_papers=relevant_papers
        )

    async def _select_relevant_papers(
        self, question: str, papers: list[Paper]
    ) -> list[RelevantPaper]:
        """Legacy method - now uses orchestrator internally."""
        # Use orchestrator to select papers
        selected = await self.orchestrator.selector.select_papers(
            query=question,
            limit=10
        )
        
        # Convert to RelevantPaper format
        relevant_papers = []
        for paper in selected:
            relevant_papers.append(
                RelevantPaper(
                    paper=paper,
                    relevance_score=0.8,
                    relevance_reason="Selected as relevant to the question"
                )
            )
        
        return relevant_papers

    async def _generate_synthesis(
        self, question: str, relevant_papers: list[RelevantPaper]
    ) -> str:
        """Legacy method - now uses orchestrator internally."""
        # Convert RelevantPapers back to Papers
        papers = [rp.paper for rp in relevant_papers]
        
        # Extract context
        context = await self.orchestrator.context_extractor.extract_context(
            papers,
            context_type="key_points"
        )
        
        # Generate answer
        answer = await self.orchestrator.answerer.answer(
            question,
            context,
            papers,
            depth="thorough"
        )
        
        return answer

    async def synthesize_with_search(self, question: str) -> SynthesisResult:
        """Generate synthesis with optional CLI search for additional context."""
        # Step 1: Regular synthesis from key points
        result = await self.synthesize(question)
        
        # If no search tool available, return regular synthesis
        if not self.search_tool:
            return result
        
        # Step 2: Let LLM decide what to search for
        logger.info(f"Starting search-enhanced synthesis for question: {question}")
        paper_list = "\n".join([
            f"{i+1}. {p.paper.paper_id}.txt"
            for i, p in enumerate(result.relevant_papers)
        ])
        
        search_prompt = f"""You're answering: {question}

Current synthesis: {result.synthesis}

You can search the full text of these papers:
{paper_list}

If you need specific information not in the synthesis, write bash commands using grep.
Examples:
- grep -i "batch size" paper1.txt paper2.txt
- grep -A2 -B2 "learning rate" *.txt
- grep -E "dataset.*ImageNet" -A5 paper3.txt

Reply with bash commands in triple backticks, or "NO_SEARCH" if synthesis is complete.
"""
        
        response = await self.llm.complete(search_prompt)
        
        # Step 3: Extract and run commands
        commands = re.findall(r'```bash\n(.*?)\n```', response["content"], re.DOTALL)
        
        if not commands or "NO_SEARCH" in response["content"]:
            logger.info("LLM decided no additional searches needed")
            return result
        
        # Step 4: Execute searches and collect results
        logger.info(f"LLM requested {len(commands)} search commands")
        search_results = []
        for cmd in commands[:3]:  # Limit to 3 searches
            logger.info(f"Executing search: {cmd}")
            output, returncode = await self.search_tool.execute_search(cmd)
            if returncode == 0:
                search_results.append({
                    "command": cmd,
                    "output": output[:1000]  # Truncate long results
                })
                logger.info(f"Search successful, found {len(output)} characters of output")
            else:
                logger.warning(f"Search failed with return code {returncode}: {cmd}")
        
        # Step 5: Update synthesis with findings
        if search_results:
            logger.info(f"Updating synthesis with {len(search_results)} search results")
            update_prompt = f"""Original question: {question}
Current synthesis: {result.synthesis}

Search results:
{json.dumps(search_results, indent=2)}

Update the synthesis with relevant specific details from the search results.
"""
            
            updated = await self.llm.complete(update_prompt)
            result.synthesis = updated["content"]
            logger.info("Synthesis updated with search results")
        else:
            logger.info("No successful searches to incorporate")
        
        return result

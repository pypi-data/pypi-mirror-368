"""Atomic tools for conversational paper synthesis."""

import asyncio
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from litai.config import Config

from rich.live import Live
from rich.text import Text

from litai.database import Database
from litai.extraction import KeyPoint, PaperExtractor
from litai.llm import LLMClient
from litai.models import Paper
from litai.utils.logger import get_logger

logger = get_logger(__name__)

# OpenAI-style tool definitions for the LLM
SYNTHESIS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Search for papers in the collection. Returns matching papers for review.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query or topic (e.g., 'attention mechanisms', 'deep learning')",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags to filter by",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of papers to return",
                        "default": 100,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "select_papers",
            "description": "Manually select specific papers by their IDs (use this only if you need to modify the selection after searching). Can set, add to, or remove from current selection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of paper IDs to select",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["set", "add", "remove"],
                        "description": "How to modify the selection: 'set' replaces, 'add' appends, 'remove' deletes",
                        "default": "set",
                    },
                },
                "required": ["paper_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "select_all_papers",
            "description": "Add all papers from the collection to the current selection. This will add every paper in your collection to the selected papers for synthesis.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_selected_papers",
            "description": "Show currently selected papers in the synthesis session",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_context",
            "description": "Load/extract content from selected papers and show preview. You can specify multiple context types in one call (e.g., ['abstracts', 'notes']). This is for DATA LOADING only - you only see truncated previews. To actually analyze or answer questions, use synthesize tool afterward.",
            "parameters": {
                "type": "object",
                "properties": {
                    "depth": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["abstracts", "notes", "agent_notes", "sections", "full_text"],
                        },
                        "description": "Types of content to extract (can specify multiple): abstracts (quick), notes (user notes), agent_notes (AI insights), sections (specific), full_text (complete). Examples: ['abstracts'] or ['abstracts', 'notes']",
                    },
                    "sections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific section names if depth='sections' (e.g., ['Introduction', 'Methods'])",
                    },
                },
                "required": ["depth"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "synthesize",
            "description": "ANSWER QUESTIONS and provide analysis using the full extracted content. This is the main tool for responding to user queries - it gives you access to complete extracted content, not just previews.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Research question to answer using the selected papers",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["quick", "thorough", "comparative"],
                        "description": "Synthesis mode: quick (main points), thorough (detailed), comparative (compare/contrast)",
                        "default": "quick",
                    },
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "refine_synthesis",
            "description": "Refine or go deeper on the previous synthesis with additional focus",
            "parameters": {
                "type": "object",
                "properties": {
                    "refinement": {
                        "type": "string",
                        "description": "How to refine the synthesis (e.g., 'go deeper on methods', 'focus on results', 'compare approaches')",
                    },
                },
                "required": ["refinement"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_session_state",
            "description": "Get current session state including selected papers, context depth, and synthesis history",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "append_agent_note",
            "description": "Save important AI-generated insights about a paper for future reference. Use this to persist key findings, methodological observations, or connections discovered during synthesis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "Paper hash ID (not title) - use the hash from list_selected_papers or select_papers",
                    },
                    "content": {
                        "type": "string",
                        "description": "Insights or notes to add to the paper",
                    },
                },
                "required": ["paper_id", "content"],
            },
        },
    },
]


@dataclass
class ExtractedContext:
    """Context extracted from a paper."""
    paper_id: str
    context_type: str
    content: str
    metadata: dict[str, str] | None = None


class PaperSelector:
    """Tool for selecting papers based on flexible criteria."""
    
    def __init__(self, db: Database, llm: LLMClient):
        self.db = db
        self.llm = llm

    async def select_papers(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        paper_ids: list[str] | None = None,
        limit: int | None = None,
    ) -> list[Paper]:
        """Select papers based on flexible criteria.
        
        Args:
            query: Natural language query for semantic selection
            tags: Filter by tags
            paper_ids: Specific paper IDs to select
            limit: Maximum number of papers to return
            
        Returns:
            List of selected papers
        """
        # Start with all papers
        papers = self.db.list_papers(limit=100)
        logger.info(f"Starting with {len(papers)} total papers in collection")
        
        # Filter by specific IDs if provided
        if paper_ids:
            papers = [p for p in papers if p.paper_id in paper_ids]
            logger.info(f"After filtering by paper_ids: {len(papers)} papers")
            
        # Filter by tags if provided
        if tags:
            initial_count = len(papers)
            papers = [p for p in papers if any(tag in p.tags for tag in tags)]
            logger.info(f"After filtering by tags {tags}: {initial_count} -> {len(papers)} papers")
            
        # Semantic selection based on query
        # Skip semantic selection if query is just asking for papers by tag
        if query:
            # Check if query is essentially just requesting papers with the specified tags
            query_lower = query.lower().strip()
            is_tag_only_query = tags and any(
                tag in query_lower and ('tag' in query_lower or 'pull' in query_lower or 'get' in query_lower)
                for tag in tags
            )
            
            if not is_tag_only_query:
                initial_count = len(papers)
                papers = await self._semantic_select(query, papers)
                logger.info(f"After semantic selection for '{query}': {initial_count} -> {len(papers)} papers")
            else:
                logger.info(f"Skipping semantic selection for tag-only query: '{query}'")
            
        # Apply limit
        if limit:
            initial_count = len(papers)
            papers = papers[:limit]
            if initial_count > limit:
                logger.info(f"Applied limit of {limit}: {initial_count} -> {len(papers)} papers")
            
        logger.info(f"Final selection: {len(papers)} papers")
        return papers
        
    async def _semantic_select(self, query: str, papers: list[Paper]) -> list[Paper]:
        """Use LLM to select papers semantically relevant to query."""
        if not papers:
            return []
            
        logger.info(f"Running semantic selection on {len(papers)} papers for query: '{query}'")
        
        # Format papers for LLM
        paper_list = "\n".join([
            f'{i + 1}. "{paper.title}" ({paper.year})\n'
            f"   Abstract: {paper.abstract[:150]}..."
            for i, paper in enumerate(papers)
        ])
        
        prompt = f"""Given this query: "{query}"

Select papers relevant to this query from:
{paper_list}

Return a JSON list of paper numbers (1-indexed) that are relevant.
Example: [1, 3, 5]"""
        
        response = await self.llm.complete(prompt, max_tokens=200)
        
        try:
            # Extract JSON from response
            content = response["content"].strip()
            logger.info(f"LLM response for semantic selection: {content}")
            
            # Find JSON array in the response
            import re
            json_match = re.search(r'\[[\d,\s]+\]', content)
            if json_match:
                selected_indices = json.loads(json_match.group())
                logger.info(f"LLM selected paper indices: {selected_indices}")
                
                selected_papers = [
                    papers[i - 1] 
                    for i in selected_indices 
                    if 1 <= i <= len(papers)
                ]
                logger.info(f"Semantic selection returned {len(selected_papers)} papers")
                return selected_papers
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Failed to parse LLM selection: {e}")
            
        logger.warning("Semantic selection fallback - returning first 10 papers")
        return papers[:10]  # Fallback to first 10


class ContextExtractor:
    """Tool for extracting different types of context from papers."""
    
    def __init__(self, db: Database, extractor: PaperExtractor):
        self.db = db
        self.extractor = extractor
        # Access pdf_processor through extractor
        self.pdf_processor = extractor.pdf_processor
        
    async def extract_context(
        self,
        papers: list[Paper],
        context_types: list[str] | str = ["abstracts"],
        sections: list[str] | None = None,
    ) -> dict[str, ExtractedContext]:
        """Extract specified context from papers.
        
        Args:
            papers: Papers to extract from
            context_types: Type(s) of context to extract (can be single string or list)
                - "abstracts": Just the abstracts
                - "notes": User's notes on papers
                - "agent_notes": AI-generated insights
                - "full_text": Complete paper text
                - "sections": Specific sections
            sections: For context_types containing "sections", which sections to extract
            
        Returns:
            Dictionary mapping paper_id to extracted context
        """
        # Handle backward compatibility - convert single string to list
        if isinstance(context_types, str):
            context_types = [context_types]
        
        contexts = {}
        
        for paper in papers:
            logger.info(f"Extracting {context_types} from {paper.title}")
            
            combined_content = []
            
            for context_type in context_types:
                if context_type == "abstracts":
                    content = paper.abstract
                    if content:
                        combined_content.append(f"=== ABSTRACT ===\n{content}")
                    
                elif context_type == "notes":
                    # Get user notes from database
                    notes = self.db.get_note(paper.paper_id)
                    if notes:
                        combined_content.append(f"=== USER NOTES ===\n{notes}")
                    
                elif context_type == "agent_notes":
                    # Get agent notes from database
                    agent_notes = self.db.get_agent_note(paper.paper_id)
                    if agent_notes:
                        combined_content.append(f"=== AI INSIGHTS ===\n{agent_notes}")
                        
                elif context_type == "full_text":
                    # Get full text from storage (download if needed)
                    try:
                        full_text = await self.pdf_processor.process_paper(paper.paper_id)
                        if full_text:
                            combined_content.append(f"=== FULL TEXT ===\n{full_text}")
                        else:
                            combined_content.append(f"=== ABSTRACT (fallback) ===\n{paper.abstract}")
                    except Exception as e:
                        logger.warning(f"Failed to read full text: {e}")
                        combined_content.append(f"=== ABSTRACT (fallback) ===\n{paper.abstract}")
                        
                elif context_type == "sections" and sections:
                    # Extract specific sections
                    try:
                        full_text = await self.pdf_processor.process_paper(paper.paper_id)
                        if full_text:
                            extracted_sections = self._extract_sections(full_text, sections)
                            if extracted_sections != "Sections not found":
                                combined_content.append(f"=== SECTIONS ===\n{extracted_sections}")
                        else:
                            combined_content.append(f"=== ABSTRACT (fallback) ===\n{paper.abstract}")
                    except Exception as e:
                        logger.warning(f"Failed to extract sections: {e}")
                        combined_content.append(f"=== ABSTRACT (fallback) ===\n{paper.abstract}")
            
            # Combine all extracted content
            final_content = "\n\n".join(combined_content) if combined_content else paper.abstract
            
            # Create combined context type identifier
            combined_context_type = "+".join(context_types)
            
            contexts[paper.paper_id] = ExtractedContext(
                paper_id=paper.paper_id,
                context_type=combined_context_type,
                content=final_content,
                metadata={"title": paper.title, "year": str(paper.year)},
            )
            
        return contexts
        
    def _format_key_points(self, key_points: list[KeyPoint]) -> str:
        """Format key points as readable text."""
        if not key_points:
            return "No key points extracted"
            
        lines = []
        for point in key_points:
            lines.append(f"• {point.claim}")
            lines.append(f"  Evidence: {point.evidence}")
            lines.append(f"  Section: {point.section}")
            lines.append("")
        return "\n".join(lines)
        
    def _extract_sections(self, full_text: str, sections: list[str]) -> str:
        """Extract specific sections from full text."""
        extracted = []
        text_lower = full_text.lower()
        
        for section in sections:
            # Try to find section headers
            patterns = [
                f"\n{section.lower()}\n",
                f"\n{section.lower()}:",
                f"\n## {section.lower()}",
                f"\n### {section.lower()}",
            ]
            
            for pattern in patterns:
                if pattern in text_lower:
                    # Find the section and extract until next major section
                    start = text_lower.index(pattern)
                    # Find next section or end
                    next_section = len(full_text)
                    for next_pattern in ["\n## ", "\n### ", "\nreferences", "\nappendix"]:
                        idx = text_lower.find(next_pattern, start + len(pattern))
                        if idx != -1 and idx < next_section:
                            next_section = idx
                    
                    section_text = full_text[start:next_section].strip()
                    extracted.append(f"=== {section.upper()} ===\n{section_text}")
                    break
                    
        return "\n\n".join(extracted) if extracted else "Sections not found"


class QuestionAnswerer:
    """Tool for generating answers from context."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
        
    async def answer(
        self,
        question: str,
        context: dict[str, ExtractedContext],
        papers: list[Paper],
        depth: str = "quick",
    ) -> str:
        """Generate answer from context.
        
        Args:
            question: Question to answer
            context: Extracted context from papers
            papers: Original paper objects for metadata
            depth: Answer depth
                - "quick": Brief answer with key points
                - "thorough": Detailed analysis
                - "comparative": Focus on comparing papers
                
        Returns:
            Generated answer text
        """
        # Build context string
        context_parts = []
        paper_map = {p.paper_id: p for p in papers}
        
        for i, (paper_id, ctx) in enumerate(context.items(), 1):
            paper = paper_map.get(paper_id)
            if paper:
                context_parts.append(f"[{i}] {paper.title} ({paper.year})")
                context_parts.append(f"Context type: {ctx.context_type}")
                context_parts.append(ctx.content[:1500])  # Limit context length
                context_parts.append("")
                
        context_str = "\n".join(context_parts)
        
        # Build appropriate prompt based on depth
        if depth == "quick":
            prompt = f"""Question: {question}

Context from papers:
{context_str}

Provide a brief, direct answer using the context. Use citations [1], [2], etc."""
            
        elif depth == "thorough":
            prompt = f"""Question: {question}

Context from papers:
{context_str}

Provide a comprehensive analysis that:
1. Directly answers the question
2. Synthesizes findings from all relevant papers
3. Uses citations [1], [2], etc.
4. Identifies key themes and patterns
5. Notes any limitations or gaps"""
            
        elif depth == "comparative":
            prompt = f"""Question: {question}

Context from papers:
{context_str}

Compare and contrast the papers:
1. How do they approach this question differently?
2. What do they agree on?
3. Where do they disagree?
4. What unique contributions does each make?
Use citations [1], [2], etc."""
            
        else:
            prompt = f"""Question: {question}

Context: {context_str}

Answer the question based on the context. Use citations."""
            
        response = await self.llm.complete(
            prompt, 
            max_tokens=1500 if depth == "thorough" else 800,
        )
        
        return str(response["content"]).strip()


class SynthesisOrchestrator:
    """Orchestrates the atomic tools for conversational synthesis."""
    
    def __init__(
        self,
        db: Database,
        llm: LLMClient,
        extractor: PaperExtractor,
    ):
        self.selector = PaperSelector(db, llm)
        self.context_extractor = ContextExtractor(db, extractor)
        self.answerer = QuestionAnswerer(llm)
        
        # State for conversational flow
        self.current_papers: list[Paper] = []
        self.current_context: dict[str, ExtractedContext] = {}
        self.current_question: str = ""
        
    async def synthesize(
        self,
        question: str,
        tags: list[str] | None = None,
        paper_ids: list[str] | None = None,
        context_type: str = "abstracts",
        depth: str = "quick",
    ) -> dict[str, str | list[Paper]]:
        """Main synthesis entry point.
        
        Returns:
            Dictionary with 'answer', 'papers', and 'context_type'
        """
        # Select papers
        self.current_papers = await self.selector.select_papers(
            query=question,
            tags=tags,
            paper_ids=paper_ids,
        )
        
        if not self.current_papers:
            return {
                "answer": "No relevant papers found in your library.",
                "papers": [],
                "context_type": context_type,
            }
        
        # Extract context
        self.current_context = await self.context_extractor.extract_context(
            self.current_papers,
            context_types=context_type,
        )
        
        # Generate answer
        self.current_question = question
        answer = await self.answerer.answer(
            question,
            self.current_context,
            self.current_papers,
            depth=depth,
        )
        
        return {
            "answer": answer,
            "papers": self.current_papers,
            "context_type": context_type,
        }
        
    async def refine(
        self,
        refinement: str,
        context_type: str | None = None,
        depth: str | None = None,
    ) -> dict[str, str | list[Paper]]:
        """Refine the current synthesis based on user feedback.
        
        Args:
            refinement: User's refinement request
            context_type: Optional new context type
            depth: Optional new depth level
            
        Returns:
            Updated synthesis result
        """
        # Update context if requested
        if context_type and context_type != self.current_context.get("type"):
            self.current_context = await self.context_extractor.extract_context(
                self.current_papers,
                context_types=context_type,
            )
            
        # Generate refined answer
        combined_question = f"{self.current_question}\n\nRefinement: {refinement}"
        answer = await self.answerer.answer(
            combined_question,
            self.current_context,
            self.current_papers,
            depth=depth or "quick",
        )
        
        return {
            "answer": answer,
            "papers": self.current_papers,
            "context_type": context_type or "current",
        }
        
    async def add_papers(self, paper_ids: list[str]) -> None:
        """Add more papers to current synthesis session."""
        new_papers = await self.selector.select_papers(paper_ids=paper_ids)
        
        # Add to current papers (avoid duplicates)
        current_ids = {p.paper_id for p in self.current_papers}
        for paper in new_papers:
            if paper.paper_id not in current_ids:
                self.current_papers.append(paper)
                
        # Extract context for new papers
        new_context = await self.context_extractor.extract_context(
            new_papers,
            context_types=list(self.current_context.values())[0].context_type.split("+")
            if self.current_context else ["abstracts"],
        )
        self.current_context.update(new_context)
        
    async def change_context_depth(self, context_type: str) -> None:
        """Change the context extraction depth for current papers."""
        self.current_context = await self.context_extractor.extract_context(
            self.current_papers,
            context_types=context_type,
        )


class SynthesisConversation:
    """Manages LLM-driven conversations with tool use for synthesis."""
    
    def __init__(self, db: Database, llm: LLMClient, orchestrator: SynthesisOrchestrator, config: "Config"):
        self.db = db
        self.llm = llm
        self.orchestrator = orchestrator
        self.config = config
        from litai.synthesis_session import SynthesisSession
        self.session = SynthesisSession()
        self.tools = self._create_tool_handlers()
        self.message_history: list[dict[str, Any]] = []
        self.live = None  # Rich Live display for tool calls
        
    def _create_tool_handlers(self) -> dict[str, Any]:
        """Map tool names to actual implementation functions."""
        return {
            "search_papers": self._search_papers,
            "select_papers": self._select_papers,
            "select_all_papers": self._select_all_papers,
            "list_selected_papers": self._list_selected_papers,
            "extract_context": self._extract_context,
            "synthesize": self._synthesize,
            "refine_synthesis": self._refine_synthesis,
            "get_session_state": self._get_session_state,
            "append_agent_note": self._append_agent_note,
        }
    
    async def handle_message(self, user_message: str) -> str:
        """Main conversation loop handler with ReAct pattern for adaptive tool use."""
        # Build system prompt with current state
        system_prompt = self._build_system_prompt()
        
        # Add user message to persistent history
        self.message_history.append({"role": "user", "content": user_message})
        
        # Build messages for this interaction (includes history for context)
        interaction_messages = [
            {"role": "system", "content": system_prompt},
            *self.message_history[-10:],  # Keep last 10 messages for context
        ]
        
        # ReAct loop configuration
        max_iterations = 8  # Reasonable limit to prevent infinite loops
        iteration_count = 0
        tool_call_chain = []  # Track the sequence of tool calls for debugging
        
        logger.info(f"Starting ReAct loop for user message: {user_message[:100]}...")
        
        # ReAct loop - allow multiple rounds of tool calling
        while iteration_count < max_iterations:
            iteration_count += 1
            logger.info(f"ReAct iteration {iteration_count}/{max_iterations}")
            
            # Get LLM response with tool access
            response = await self.llm.complete(
                interaction_messages,
                tools=SYNTHESIS_TOOLS,
            )
            
            # Check if LLM wants to use tools
            if "tool_calls" in response and response["tool_calls"]:
                logger.info(f"Iteration {iteration_count}: LLM requesting {len(response['tool_calls'])} tool(s)")
                
                # Add assistant's message with tool calls to interaction messages
                assistant_msg = {
                    "role": "assistant",
                    "content": response.get("content", ""),
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else tc.arguments,
                            },
                        } for tc in response["tool_calls"]
                    ],
                }
                interaction_messages.append(assistant_msg)
                
                # Import needed classes for tool approval
                from litai.tool_approval import ToolCall as ApprovalToolCall
                
                # Create approval manager if not exists
                if not hasattr(self, 'approval_manager'):
                    from litai.config import Config
                    from litai.tool_approval import ToolApprovalManager
                    config = Config()
                    self.approval_manager = ToolApprovalManager(config)
                
                # Prepare ALL tool calls for approval
                pending_calls = []
                for tc in response["tool_calls"]:
                    pending_calls.append(ApprovalToolCall(
                        id=tc.id,
                        name=tc.name,
                        description=self._get_tool_description(tc.name, tc.arguments),
                        arguments=tc.arguments,
                    ))
                
                # Get approval for all tools at once
                approved_calls = await self.approval_manager.get_approval(pending_calls)
                
                # Check if user cancelled all tools
                if not approved_calls and pending_calls:
                    # User cancelled - exit ReAct loop
                    logger.info("User cancelled all tool calls - exiting ReAct loop")
                    
                    # Add cancelled tool attempt to message history for context
                    cancelled_tools = [f"{tc.name}({', '.join(f'{k}={v}' for k, v in tc.arguments.items())})" 
                                     for tc in pending_calls]
                    cancelled_msg = f"I was going to call: {', '.join(cancelled_tools)}, but you cancelled."
                    self.message_history.append({"role": "assistant", "content": cancelled_msg})
                    
                    # Add user's cancellation response
                    user_cancel_msg = "I understand. What would you like to do instead?"
                    self.message_history.append({"role": "assistant", "content": user_cancel_msg})
                    
                    return user_cancel_msg
                
                # Create a mapping of approved calls by ID for quick lookup
                approved_by_id = {call.id: call for call in approved_calls}
                
                # Execute tools with visual feedback
                with Live(refresh_per_second=10) as live:
                    tool_statuses: dict[int, dict[str, Any]] = {}
                    animation_frame = 0  # For rotating animations
                    
                    # Initialize all tools in status display (regardless of approval)
                    for i, tool_call in enumerate(response["tool_calls"]):
                        tool_statuses[i] = {
                            "name": tool_call.name, 
                            "status": "pending", 
                            "args": tool_call.arguments,
                        }
                    
                    def _format_args_display(args: dict) -> str:
                        """Format arguments nicely for status display."""
                        if not args:
                            return ""
                        
                        # Handle common parameter patterns nicely
                        formatted_parts = []
                        for key, value in args.items():
                            if isinstance(value, str):
                                if len(value) > 25:
                                    formatted_parts.append(f"{key}='{value[:22]}...'")
                                else:
                                    formatted_parts.append(f"{key}='{value}'")
                            elif isinstance(value, list):
                                if len(value) > 2:
                                    formatted_parts.append(f"{key}=[{len(value)} items]")
                                else:
                                    formatted_parts.append(f"{key}={value}")
                            else:
                                formatted_parts.append(f"{key}={value}")
                        
                        args_str = ", ".join(formatted_parts)
                        if len(args_str) > 50:
                            args_str = args_str[:47] + "..."
                        return args_str
                    
                    # Update display to show all tools
                    def build_display() -> Text:
                        nonlocal animation_frame
                        animation_frame += 1
                        
                        display = Text()
                        display.append(f"Iteration {iteration_count} - Executing {len(response['tool_calls'])} tool(s):\n", style="bold cyan")
                        
                        # Rotating animation characters for running tools
                        running_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
                        running_char = running_chars[animation_frame % len(running_chars)]
                        
                        for _idx, status_info in tool_statuses.items():
                            if status_info["status"] == "running":
                                display.append(f"{running_char} ", style="bold yellow")
                                display.append(f"{status_info['name']}", style="bold yellow")
                            elif status_info["status"] == "complete":
                                display.append("✓ ", style="bold green")
                                display.append(f"{status_info['name']}", style="green")
                            else:  # pending
                                display.append("◯ ", style="dim")
                                display.append(f"{status_info['name']}", style="dim")
                            
                            # Always show formatted arguments
                            args_display = _format_args_display(status_info.get('args', {}))
                            if args_display:
                                if status_info["status"] == "running":
                                    style = "yellow"
                                elif status_info["status"] == "complete":
                                    style = "green"
                                else:  # pending
                                    style = "dim"
                                display.append(f" ({args_display})", style=style)
                            
                            display.append("\n")
                        
                        return display
                    
                    # Process ALL original tool calls (not just approved)
                    for i, tool_call in enumerate(response["tool_calls"]):
                        # Track tool call for debugging
                        tool_call_chain.append({
                            "iteration": iteration_count,
                            "tool": tool_call.name,
                            "args": tool_call.arguments,
                            "status": "approved" if tool_call.id in approved_by_id else "skipped",
                        })
                        
                        # Check if this tool was approved
                        if tool_call.id in approved_by_id:
                            # Use the potentially modified version
                            approved_call = approved_by_id[tool_call.id]
                            
                            # Update status with approved version (args might have been modified during approval)
                            tool_statuses[i]["name"] = approved_call.name
                            tool_statuses[i]["args"] = approved_call.arguments
                            
                            # Mark as running and flash
                            tool_statuses[i]["status"] = "running"
                            
                            # Create flashing animation for current tool
                            for flash_cycle in range(3):  # Flash 3 times
                                # Toggle between bright and dim for flashing effect
                                if flash_cycle % 2 == 0:
                                    tool_statuses[i]["status"] = "running"
                                else:
                                    tool_statuses[i]["status"] = "pending"
                                
                                live.update(build_display())
                                await asyncio.sleep(0.15)
                            
                            # Keep as running while executing
                            tool_statuses[i]["status"] = "running"
                            live.update(build_display())
                            
                            # Execute the approved tool
                            logger.info(f"Executing approved tool: {approved_call.name} with args: {approved_call.arguments}")
                            result = await self._execute_tool(
                                approved_call.name,
                                approved_call.arguments,
                            )
                            
                            # Add successful result
                            interaction_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(result) if not isinstance(result, str) else result,
                            })
                            
                            # Mark as complete
                            tool_statuses[i]["status"] = "complete"
                            
                        else:
                            # Tool was not approved (shouldn't happen with new logic)
                            logger.warning(f"Tool not approved: {tool_call.name}")
                            
                            # CRITICAL: Add a response to satisfy OpenAI API
                            interaction_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": "Tool call was not approved.",
                            })
                        
                        live.update(build_display())
                        await asyncio.sleep(0.3)
                    
                    # Show final status for a moment
                    await asyncio.sleep(0.5)
                
                # Continue to next iteration - LLM will see tool results and decide next action
                continue
                
            # No tool calls - LLM is done reasoning and has final response
            logger.info(f"ReAct loop complete after {iteration_count} iteration(s)")
            logger.info(f"Tool call chain: {json.dumps(tool_call_chain, indent=2)}")
            
            # Add final assistant response to persistent history
            final_content = response.get("content", "")
            self.message_history.append({"role": "assistant", "content": final_content})
            
            return str(final_content)
        
        # Max iterations reached - return with warning
        logger.warning(f"ReAct loop hit max iterations ({max_iterations})")
        logger.info(f"Tool call chain: {json.dumps(tool_call_chain, indent=2)}")
        
        warning_msg = (
            f"I've reached the maximum number of steps ({max_iterations}) for this query. "
            "Here's what I found so far, but you might want to ask a more specific question.\n\n"
            f"{response.get('content', 'Unable to complete the analysis.')}"
        )
        
        # Add warning to history
        self.message_history.append({"role": "assistant", "content": warning_msg})
        
        return warning_msg
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with current session state."""
        paper_count = len(self.session.selected_papers)
        paper_list = ""
        if paper_count > 0:
            paper_list = "\n".join([
                f"- {p.title} ({p.year})"
                for p in self.session.selected_papers[:5]
            ])
            if paper_count > 5:
                paper_list += f"\n... and {paper_count - 5} more"
                
        workflow_guidance = ""
        if paper_count == 0:
            workflow_guidance = """
IMPORTANT: No papers are selected yet. Before you can extract context or synthesize:
1. First use search_papers to find relevant papers
2. Then use select_papers to choose which ones to work with
3. Only then can you extract_context or synthesize

When users ask about specific papers/algorithms/methods, you must search for them first."""
        else:
            workflow_guidance = f"""
You can now extract context at different depths or synthesize answers using the {paper_count} selected papers.

CRITICAL WORKFLOW RULES:
- extract_context is ONLY for loading/previewing content - you see truncated previews
- You can specify multiple context types at once: extract_context(['abstracts', 'notes']) 
- To actually ANSWER QUESTIONS or provide analysis, you MUST use the synthesize tool
- synthesize gives you access to the full extracted content for proper analysis
- Never try to answer substantive questions using only extract_context previews"""

        base_prompt = f"""You are a research synthesis assistant helping analyze academic papers.

Current session state:
- Papers selected: {paper_count}
- Context depth: {self.session.context_type}
- Previous syntheses: {len(self.session.synthesis_history)}

{"Selected papers:" if paper_count > 0 else "No papers selected yet."}
{paper_list}{workflow_guidance}

TOOL USAGE PATTERN:
1. search_papers → find relevant papers
2. select_papers → choose which to work with  
3. extract_context → load data (you see previews only)
4. synthesize → answer questions (you get full content)

IMPORTANT: When you use the synthesize tool, you MUST display the full synthesis content 
to the user, not just acknowledge that synthesis was done. The synthesis result contains 
the actual analysis they requested.

You have access to tools for searching, selecting, and synthesizing papers.
Use them naturally based on the conversation. When greeting, just respond 
conversationally without using tools."""

        # Add user research context if available
        if self.config and self.config.user_prompt_path.exists():
            try:
                user_prompt = self.config.user_prompt_path.read_text().strip()
                if user_prompt:
                    base_prompt += f"\n\n## User Research Context\n\n{user_prompt}"
            except Exception:
                # Silently ignore errors loading user prompt
                pass

        return base_prompt
    
    async def _execute_tool(self, tool_name: str, arguments: dict) -> dict[str, Any] | str:
        """Execute a tool and return its result."""
        handler = self.tools.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            result: dict[str, Any] | str = await handler(**arguments)
            return result
        except Exception as e:
            logger.exception(f"Tool execution failed: {tool_name}")
            return {"error": str(e)}
    
    async def _search_papers(self, query: str, tags: list[str] | None = None, limit: int = 10) -> dict:
        """Search for papers using the selector."""
        logger.info(f"Searching papers with query='{query}', tags={tags}, limit={limit}")
        
        papers = await self.orchestrator.selector.select_papers(
            query=query,
            tags=tags,
            limit=limit,
        )
        
        # Don't auto-select papers - let the user choose which ones to include
        # Users can use select_papers tool if they want to add specific papers
        
        return {
            "found": len(papers),
            "papers": [
                {
                    "id": p.paper_id,
                    "title": p.title,
                    "year": p.year,
                    "tags": p.tags,
                    "abstract_preview": p.abstract[:200] + "..." if len(p.abstract) > 200 else p.abstract,
                }
                for p in papers
            ],
            "auto_selected": False,  # Papers are not automatically selected
        }
    
    async def _select_papers(self, paper_ids: list[str], operation: str = "set") -> dict:
        """Select papers for synthesis."""
        logger.info(f"Selecting papers: operation={operation}, paper_ids={paper_ids}")
        
        if operation == "set":
            # Get papers by IDs
            papers_nullable = [self.db.get_paper(pid) for pid in paper_ids]
            papers = [p for p in papers_nullable if p]  # Filter out None
            await self.session.update_papers(papers=papers)
        elif operation == "add":
            papers_nullable = [self.db.get_paper(pid) for pid in paper_ids]
            papers = [p for p in papers_nullable if p]
            await self.session.update_papers(add_papers=papers)
        elif operation == "remove":
            await self.session.update_papers(remove_paper_ids=paper_ids)
        
        logger.info(f"Papers selected: {len(self.session.selected_papers)} total")
        return {
            "operation": operation,
            "selected_count": len(self.session.selected_papers),
            "papers": [p.title for p in self.session.selected_papers],
        }
    
    async def _select_all_papers(self) -> dict:
        """Add all papers from the collection to selected papers."""
        logger.info("Selecting all papers from collection")
        
        # Get all papers from database
        all_papers = self.db.list_papers(limit=1000)  # Use reasonable limit
        
        if not all_papers:
            return {
                "success": False,
                "message": "No papers found in collection",
                "total_selected": len(self.session.selected_papers),
            }
        
        # Get IDs of papers that aren't already selected
        current_ids = {p.paper_id for p in self.session.selected_papers}
        new_papers = [p for p in all_papers if p.paper_id not in current_ids]
        
        if not new_papers:
            return {
                "success": True,
                "message": "All papers from collection were already selected",
                "total_selected": len(self.session.selected_papers),
                "added_count": 0,
            }
        
        # Add new papers to selection
        await self.session.update_papers(add_papers=new_papers)
        
        logger.info(f"Added {len(new_papers)} papers to selection. Total: {len(self.session.selected_papers)}")
        return {
            "success": True,
            "message": f"Added {len(new_papers)} papers from collection to selection",
            "total_selected": len(self.session.selected_papers),
            "added_count": len(new_papers),
            "collection_size": len(all_papers),
        }
    
    async def _list_selected_papers(self) -> dict:
        """List currently selected papers."""
        logger.info(f"Listing selected papers: {len(self.session.selected_papers)} papers")
        return {
            "count": len(self.session.selected_papers),
            "papers": [
                {
                    "id": p.paper_id,
                    "title": p.title,
                    "year": p.year,
                    "tags": p.tags,
                }
                for p in self.session.selected_papers
            ],
        }
    
    async def _extract_context(self, depth: list[str] | str, sections: list[str] | None = None) -> dict:
        """Extract context from selected papers."""
        if not self.session.selected_papers:
            return {"error": "No papers selected. Use search_papers and select_papers first."}
        
        # Update context depth in session
        await self.session.change_context_depth(depth, sections)
        
        # Extract context - convert depth to context_types parameter
        self.orchestrator.current_context = await self.orchestrator.context_extractor.extract_context(
            self.session.selected_papers,
            context_types=depth,
            sections=sections,
        )
        
        # Build preview of extracted content for LLM to see
        context_previews = []
        for paper_id, context in self.orchestrator.current_context.items():
            paper = next((p for p in self.session.selected_papers if p.paper_id == paper_id), None)
            if paper:
                title = paper.title[:50] + "..." if len(paper.title) > 50 else paper.title
                
                # Different preview strategies based on content type
                # Handle both single context types and combined context types (e.g. "abstracts+notes")
                context_types = context.context_type.split("+") if isinstance(context.context_type, str) else [context.context_type]
                
                if any(ct in ("notes", "agent_notes") for ct in context_types) and len(context_types) == 1:
                    # For single notes, show full content since they're usually short
                    if context.content not in ("No notes available", "No agent notes available"):
                        preview = context.content[:300] + "..." if len(context.content) > 300 else context.content
                        context_previews.append(f"• {title}: {preview}")
                    else:
                        note_type = "notes" if "notes" in context_types else "agent notes"
                        context_previews.append(f"• {title}: No {note_type} found")
                elif "abstracts" in context_types and len(context_types) == 1:
                    # For single abstracts, show more content since they're key information
                    preview = context.content[:400] + "..." if len(context.content) > 400 else context.content
                    context_previews.append(f"• {title}: {preview}")
                elif any(ct in ("full_text", "sections") for ct in context_types):
                    # For full text/sections (single or combined), show brief preview since content is large
                    preview = context.content[:200] + "..." if len(context.content) > 200 else context.content
                    context_previews.append(f"• {title} ({context.context_type}): {preview}")
                else:
                    # Combined contexts or other types - show moderate preview with context type info
                    preview = context.content[:250] + "..." if len(context.content) > 250 else context.content
                    context_previews.append(f"• {title} ({context.context_type}): {preview}")
        
        return {
            "depth": depth if isinstance(depth, list) else [depth],
            "papers_processed": len(self.orchestrator.current_context),
            "context_preview": "\n".join(context_previews) if context_previews else "No content extracted",
        }
    
    async def _synthesize(self, question: str, mode: str = "quick") -> dict:
        """Generate synthesis from current context."""
        if not self.session.selected_papers:
            return {"error": "No papers selected. Use search_papers and select_papers first."}
        
        # Ensure we have context
        if not self.orchestrator.current_context:
            # Extract default context
            self.orchestrator.current_context = await self.orchestrator.context_extractor.extract_context(
                self.session.selected_papers,
                context_types=self.session.context_type.split("+") if "+" in self.session.context_type else [self.session.context_type],
            )
        
        # Generate synthesis
        self.session.current_question = question
        answer = await self.orchestrator.answerer.answer(
            question,
            self.orchestrator.current_context,
            self.session.selected_papers,
            depth=mode,
        )
        
        # Store in history
        from litai.synthesis import RelevantPaper, SynthesisResult
        relevant_papers = [
            RelevantPaper(
                paper=p,
                relevance_score=1.0,  # All selected papers are considered fully relevant
                relevance_reason="Selected for synthesis",
                key_points=None,  # Could populate from context if needed
            )
            for p in self.session.selected_papers
        ]
        result = SynthesisResult(
            question=question,
            synthesis=answer,
            relevant_papers=relevant_papers,
        )
        self.session.add_synthesis_result(result)
        
        return {
            "question": question,
            "mode": mode,
            "synthesis": answer,
        }
    
    async def _refine_synthesis(self, refinement: str) -> dict:
        """Refine the previous synthesis."""
        if not self.session.synthesis_history:
            return {"error": "No previous synthesis to refine. Use synthesize first."}
        
        # Build refined question
        combined_question = f"{self.session.current_question}\n\nRefinement: {refinement}"
        
        # Generate refined answer
        answer = await self.orchestrator.answerer.answer(
            combined_question,
            self.orchestrator.current_context,
            self.session.selected_papers,
            depth="thorough",
        )
        
        # Store refined result
        from litai.synthesis import RelevantPaper, SynthesisResult
        relevant_papers = [
            RelevantPaper(
                paper=p,
                relevance_score=1.0,  # All selected papers are considered fully relevant
                relevance_reason="Selected for synthesis refinement",
                key_points=None,  # Could populate from context if needed
            )
            for p in self.session.selected_papers
        ]
        result = SynthesisResult(
            question=combined_question,
            synthesis=answer,
            relevant_papers=relevant_papers,
        )
        self.session.add_synthesis_result(result)
        
        return {
            "refinement": refinement,
            "synthesis": answer,
        }
    
    async def _get_session_state(self) -> dict:
        """Get current session state."""
        summary = self.session.get_summary()
        return {
            "papers_selected": summary["papers_count"],
            "paper_titles": summary["paper_titles"],
            "context_type": summary["context_type"],
            "current_question": summary["current_question"],
            "synthesis_count": summary["synthesis_count"],
            "session_duration_minutes": summary["session_duration_minutes"],
        }
    
    async def _append_agent_note(self, paper_id: str, content: str) -> dict:
        """Append AI-generated insights to a paper's agent notes."""
        logger.info(f"Appending agent note to paper {paper_id}")
        
        # Get the paper to verify it exists
        paper = self.db.get_paper(paper_id)
        if not paper:
            return {"error": f"Paper {paper_id} not found"}
        
        # Append the note using the database method
        success = self.db.append_agent_note(paper_id, content)
        
        if success:
            logger.info(f"Successfully added agent note to paper {paper_id}")
            return {
                "success": True,
                "paper_title": paper.title,
                "message": f"Added insights to agent notes for '{paper.title[:50]}...'",
            }
        logger.error(f"Failed to add agent note to paper {paper_id}")
        return {
            "success": False,
            "error": f"Failed to add agent notes for paper {paper_id}",
        }
    
    def _get_tool_description(self, tool_name: str, arguments: dict) -> str:
        """Generate human-readable description of what tool will do.
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            Human-readable description
        """
        if tool_name == "search_papers":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)
            tags = arguments.get("tags", [])
            desc = f"Search for up to {limit} papers about: {query}"
            if tags:
                desc += f" (with tags: {', '.join(tags)})"
            return desc
        if tool_name == "extract_context":
            depth = arguments.get("depth", ["abstracts"])
            sections = arguments.get("sections", [])
            if isinstance(depth, list):
                depth_str = "+".join(depth) if len(depth) > 1 else depth[0]
            else:
                depth_str = depth
            desc = f"Extract {depth_str} from selected papers"
            if sections:
                desc += f" (sections: {', '.join(sections)})"
            return desc
        if tool_name == "select_papers":
            operation = arguments.get("operation", "set")
            paper_ids = arguments.get("paper_ids", [])
            count = len(paper_ids)
            if operation == "add":
                return f"Add {count} paper(s) to selection"
            if operation == "remove":
                return f"Remove {count} paper(s) from selection"
            return f"Set selection to {count} specific paper(s)"
        if tool_name == "synthesize":
            question = arguments.get("question", "")
            mode = arguments.get("mode", "quick")
            return f"Generate {mode} synthesis for: {question[:50]}{'...' if len(question) > 50 else ''}"
        if tool_name == "list_selected_papers":
            return "List currently selected papers"
        if tool_name == "refine_synthesis":
            refinement = arguments.get("refinement", "")
            return f"Refine synthesis with: {refinement[:50]}{'...' if len(refinement) > 50 else ''}"
        if tool_name == "get_session_state":
            return "Get current session state"
        if tool_name == "append_agent_note":
            content = arguments.get("content", "")
            return f"Save insights about paper: {content[:50]}{'...' if len(content) > 50 else ''}"
        if tool_name == "select_all_papers":
            return "Add all papers from collection to selection"
        # Generic fallback
        args_str = json.dumps(arguments)
        if len(args_str) > 50:
            args_str = args_str[:47] + "..."
        return f"Execute {tool_name} with {args_str}"

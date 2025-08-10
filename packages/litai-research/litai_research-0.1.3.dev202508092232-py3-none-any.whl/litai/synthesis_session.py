"""Session management for conversational paper synthesis."""

from dataclasses import dataclass, field
from datetime import datetime
from litai.models import Paper
from litai.synthesis import SynthesisResult
from litai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SynthesisSessionState:
    """Immutable snapshot of synthesis session state."""
    
    selected_papers: list[Paper] = field(default_factory=list)
    current_context: dict[str, str] = field(default_factory=dict)
    context_type: str = "abstracts"
    synthesis_history: list[SynthesisResult] = field(default_factory=list)
    current_question: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class SynthesisSession:
    """Manages state for a conversational synthesis session.
    
    This class tracks the evolving state of a synthesis conversation,
    including selected papers, context depth, and synthesis history.
    """
    
    def __init__(self):
        """Initialize a new synthesis session."""
        self.selected_papers: list[Paper] = []
        self.current_context: dict[str, str] = {}
        self.context_type: str = "abstracts"  # Default to abstracts
        self.synthesis_history: list[SynthesisResult] = []
        self.current_question: str = ""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Context cache to avoid re-extraction
        self._context_cache: dict[tuple[str, str], str] = {}
        
        # Track modifications for efficient updates
        self._papers_modified = False
        self._context_modified = False
        
    async def update_papers(
        self, 
        papers: list[Paper] | None = None,
        add_papers: list[Paper] | None = None,
        remove_paper_ids: list[str] | None = None
    ) -> list[Paper]:
        """Update the papers in the session.
        
        Args:
            papers: Replace all papers with this list
            add_papers: Add these papers to existing selection
            remove_paper_ids: Remove papers with these IDs
            
        Returns:
            Updated list of selected papers
        """
        if papers is not None:
            # Replace all papers
            self.selected_papers = papers
            self._papers_modified = True
            logger.info(f"Replaced all papers, now have {len(self.selected_papers)} papers")
            
        if add_papers:
            # Add new papers (avoid duplicates)
            existing_ids = {p.paper_id for p in self.selected_papers}
            new_papers = [p for p in add_papers if p.paper_id not in existing_ids]
            self.selected_papers.extend(new_papers)
            self._papers_modified = True
            logger.info(f"Added {len(new_papers)} new papers, total: {len(self.selected_papers)}")
            
        if remove_paper_ids:
            # Remove specified papers
            self.selected_papers = [
                p for p in self.selected_papers 
                if p.paper_id not in remove_paper_ids
            ]
            self._papers_modified = True
            logger.info(f"Removed papers, now have {len(self.selected_papers)} papers")
            
        self.updated_at = datetime.now()
        
        # Clear context cache if papers changed
        if self._papers_modified:
            self._context_cache.clear()
            self._context_modified = True
            
        return self.selected_papers
    
    async def change_context_depth(
        self, 
        context_type: str | list[str],
        sections: list[str] | None = None
    ) -> str:
        """Change the context extraction depth.
        
        Args:
            context_type: Type(s) of context to extract (can be single string or list)
                - "abstracts": Quick, high-level (default)
                - "notes": User's personal notes on papers  
                - "agent_notes": AI-generated insights
                - "sections": Specific sections (methods, results, etc.)
                - "full_text": Complete paper text (slow but thorough)
            sections: For "sections" type, which sections to extract
            
        Returns:
            The new context type being used (combined if multiple)
        """
        old_type = self.context_type
        
        # Convert context_type to consistent string format
        if isinstance(context_type, list):
            new_context_type = "+".join(context_type)
        else:
            new_context_type = context_type
            
        self.context_type = new_context_type
        
        # Store section preferences if provided
        if (isinstance(context_type, list) and "sections" in context_type) or context_type == "sections":
            if sections:
                self._preferred_sections = sections
        
        if old_type != new_context_type:
            self._context_modified = True
            logger.info(f"Changed context depth from {old_type} to {new_context_type}")
            
        self.updated_at = datetime.now()
        return self.context_type
    
    async def refine_synthesis(
        self, 
        feedback: str,
        new_question: str | None = None
    ) -> dict[str, str | list[Paper]]:
        """Refine the current synthesis based on user feedback.
        
        Args:
            feedback: User's refinement request or feedback
            new_question: Optional new question to replace current one
            
        Returns:
            Dictionary with refinement context for the orchestrator
        """
        if new_question:
            self.current_question = new_question
            logger.info(f"Updated question to: {new_question}")
        
        # Build refinement context
        refinement_context = {
            "feedback": feedback,
            "question": self.current_question,
            "papers": self.selected_papers,
            "context_type": self.context_type,
            "previous_synthesis": self.synthesis_history[-1].synthesis if self.synthesis_history else None
        }
        
        self.updated_at = datetime.now()
        return refinement_context
    
    def add_synthesis_result(self, result: SynthesisResult) -> None:
        """Add a synthesis result to the history.
        
        Args:
            result: The synthesis result to add
        """
        self.synthesis_history.append(result)
        self.current_question = result.question
        self.updated_at = datetime.now()
        logger.info(f"Added synthesis result #{len(self.synthesis_history)} to history")
    
    def get_context_cache_key(self, paper_id: str) -> tuple[str, str]:
        """Generate cache key for context extraction.
        
        Args:
            paper_id: The paper ID
            
        Returns:
            Cache key tuple of (paper_id, context_type)
        """
        return (paper_id, self.context_type)
    
    def cache_context(self, paper_id: str, context: str) -> None:
        """Cache extracted context for a paper.
        
        Args:
            paper_id: The paper ID
            context: The extracted context
        """
        key = self.get_context_cache_key(paper_id)
        self._context_cache[key] = context
        
    def get_cached_context(self, paper_id: str) -> str | None:
        """Get cached context for a paper if available.
        
        Args:
            paper_id: The paper ID
            
        Returns:
            Cached context or None if not cached
        """
        key = self.get_context_cache_key(paper_id)
        return self._context_cache.get(key)
    
    def needs_context_update(self) -> bool:
        """Check if context needs to be re-extracted.
        
        Returns:
            True if context needs updating
        """
        return self._papers_modified or self._context_modified
    
    def mark_context_updated(self) -> None:
        """Mark that context has been updated."""
        self._papers_modified = False
        self._context_modified = False
        
    def get_state(self) -> SynthesisSessionState:
        """Get an immutable snapshot of the current session state.
        
        Returns:
            Current session state
        """
        return SynthesisSessionState(
            selected_papers=self.selected_papers.copy(),
            current_context=self.current_context.copy(),
            context_type=self.context_type,
            synthesis_history=self.synthesis_history.copy(),
            current_question=self.current_question,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    def restore_state(self, state: SynthesisSessionState) -> None:
        """Restore session from a saved state.
        
        Args:
            state: The state to restore
        """
        self.selected_papers = state.selected_papers.copy()
        self.current_context = state.current_context.copy()
        self.context_type = state.context_type
        self.synthesis_history = state.synthesis_history.copy()
        self.current_question = state.current_question
        self.created_at = state.created_at
        self.updated_at = state.updated_at
        
        # Clear caches and flags
        self._context_cache.clear()
        self._papers_modified = False
        self._context_modified = False
        
        logger.info("Restored session from saved state")
    
    def clear(self) -> None:
        """Clear the session state."""
        self.selected_papers.clear()
        self.current_context.clear()
        self.context_type = "abstracts"
        self.synthesis_history.clear()
        self.current_question = ""
        self._context_cache.clear()
        self._papers_modified = False
        self._context_modified = False
        self.updated_at = datetime.now()
        
        logger.info("Cleared synthesis session")
    
    def clear_session(self) -> None:
        """Clear session state while preserving selected papers and context type."""
        # Keep: selected_papers, context_type
        # Clear: synthesis history, current question, context cache, current_context
        self.current_context.clear()
        self.synthesis_history.clear()
        self.current_question = ""
        self._context_cache.clear()
        self._papers_modified = False
        self._context_modified = False
        self.updated_at = datetime.now()
        
        logger.info("Cleared synthesis session (keeping selected papers and context type)")
    
    def get_summary(self) -> dict[str, str | int | list[str]]:
        """Get a summary of the current session state.
        
        Returns:
            Summary dictionary with key session information
        """
        return {
            "papers_count": len(self.selected_papers),
            "paper_titles": [p.title for p in self.selected_papers[:3]],  # First 3
            "context_type": self.context_type,
            "current_question": self.current_question,
            "synthesis_count": len(self.synthesis_history),
            "session_duration_minutes": int((datetime.now() - self.created_at).total_seconds() / 60),
            "last_updated": self.updated_at.isoformat()
        }
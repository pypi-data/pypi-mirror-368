"""Synthesis prompt templates for question answering."""


def get_quick_prompt(question: str, context_str: str) -> str:
    """Generate a quick synthesis prompt for brief answers.
    
    Args:
        question: The research question to answer
        context_str: Context from papers with citations
        
    Returns:
        Formatted prompt string
    """
    return f"""Question: {question}

Context from papers:
{context_str}

Provide a brief, direct answer using the context. Use citations [1], [2], etc."""


def get_thorough_prompt(question: str, context_str: str) -> str:
    """Generate a thorough synthesis prompt for detailed analysis.
    
    Args:
        question: The research question to answer
        context_str: Context from papers with citations
        
    Returns:
        Formatted prompt string
    """
    return f"""Question: {question}

Context from papers:
{context_str}

Provide a comprehensive analysis that:
1. Directly answers the question with detailed explanations and technical depth
2. Synthesizes findings from all relevant papers, showing connections and relationships
3. Uses citations [1], [2], etc. for all claims
4. Identifies key themes, patterns, and methodological approaches
5. Explains technical details, implementation specifics, and experimental setups when relevant
6. Notes any limitations, gaps, or areas of uncertainty in the literature
7. CRITICAL: If you cannot answer confidently due to insufficient context, explicitly state:
   "I need to read the full text of [specific papers] to answer [specific aspects] confidently"
   and specify exactly what additional information would help

Be thorough but precise - provide substantive technical detail while staying focused on the question."""


def get_comparative_prompt(question: str, context_str: str) -> str:
    """Generate a comparative synthesis prompt for paper comparison.
    
    Args:
        question: The research question to answer
        context_str: Context from papers with citations
        
    Returns:
        Formatted prompt string
    """
    return f"""Question: {question}

Context from papers:
{context_str}

Compare and contrast the papers:
1. How do they approach this question differently?
2. What do they agree on?
3. Where do they disagree?
4. What unique contributions does each make?
Use citations [1], [2], etc."""


def get_generic_prompt(question: str, context_str: str) -> str:
    """Generate a generic synthesis prompt as fallback.
    
    Args:
        question: The research question to answer
        context_str: Context from papers with citations
        
    Returns:
        Formatted prompt string
    """
    return f"""Question: {question}

Context: {context_str}

Answer the question based on the context. Use citations."""
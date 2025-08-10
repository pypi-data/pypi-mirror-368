"""Database management for LitAI."""

import sqlite3
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import datetime

from structlog import get_logger

from .config import Config
from .models import Extraction, Paper, Tag

logger = get_logger()


class Database:
    """Manages SQLite database for papers and extractions."""

    def __init__(self, config: Config):
        """Initialize database with config.

        Args:
            config: Configuration object with database path
        """
        self.config = config
        self.db_path = config.db_path
        self._init_db()

    @contextmanager
    def _get_conn(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database tables."""
        with self._get_conn() as conn:
            # Papers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,  -- JSON list
                    year INTEGER NOT NULL,
                    abstract TEXT NOT NULL,
                    arxiv_id TEXT,
                    doi TEXT,
                    citation_count INTEGER DEFAULT 0,
                    tldr TEXT,
                    venue TEXT,
                    open_access_pdf_url TEXT,
                    added_at TEXT NOT NULL,
                    UNIQUE(arxiv_id),
                    UNIQUE(doi)
                )
            """)

            # Extractions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id TEXT NOT NULL,
                    extraction_type TEXT NOT NULL,
                    content TEXT NOT NULL,  -- JSON
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
                    UNIQUE(paper_id, extraction_type)
                )
            """)
            
            # Tags table to store unique tag names
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Junction table for many-to-many paper-tag relationships
            conn.execute("""
                CREATE TABLE IF NOT EXISTS paper_tags (
                    paper_id TEXT NOT NULL,
                    tag_id INTEGER NOT NULL,
                    FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE,
                    PRIMARY KEY (paper_id, tag_id)
                )
            """)

            # Create indices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_extractions_paper ON extractions(paper_id)",
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_extractions_type ON extractions(extraction_type)",
            )
            
            # Indexes for tags
            conn.execute("CREATE INDEX IF NOT EXISTS idx_paper_tags_tag ON paper_tags(tag_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")

            # Add citation_key column if it doesn't exist
            cursor = conn.execute("PRAGMA table_info(papers)")
            columns = [row[1] for row in cursor.fetchall()]
            if "citation_key" not in columns:
                conn.execute("ALTER TABLE papers ADD COLUMN citation_key TEXT")
                logger.info("Added citation_key column to papers table")

            logger.info("Database initialized", path=str(self.db_path))

    # Paper CRUD operations

    def add_paper(self, paper: Paper) -> bool:
        """Add a paper to the database.

        Args:
            paper: Paper object to add

        Returns:
            True if added successfully, False if already exists
        """
        try:
            with self._get_conn() as conn:
                data = paper.to_dict()
                conn.execute(
                    """
                    INSERT INTO papers (
                        paper_id, title, authors, year, abstract,
                        arxiv_id, doi, citation_count, tldr, venue,
                        open_access_pdf_url, added_at, citation_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data["paper_id"],
                        data["title"],
                        data["authors"],
                        data["year"],
                        data["abstract"],
                        data["arxiv_id"],
                        data["doi"],
                        data["citation_count"],
                        data["tldr"],
                        data["venue"],
                        data["open_access_pdf_url"],
                        data["added_at"],
                        data["citation_key"],
                    ),
                )
                logger.info("Paper added", paper_id=paper.paper_id, title=paper.title)
                return True
        except sqlite3.IntegrityError:
            logger.warning("Paper already exists", paper_id=paper.paper_id)
            return False

    def get_paper(self, paper_id: str) -> Paper | None:
        """Get a paper by ID with tags populated.

        Args:
            paper_id: ID of the paper to retrieve

        Returns:
            Paper object or None if not found
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM papers WHERE paper_id = ?", (paper_id,),
            ).fetchone()

            if row:
                paper = Paper.from_dict(dict(row))
                paper.tags = self.get_paper_tags(paper_id)
                return paper
            return None

    def list_papers(self, limit: int = 50, offset: int = 0, tag: str | None = None) -> list[Paper]:
        """list all papers in the database, optionally filtered by tag.

        Args:
            limit: Maximum number of papers to return
            offset: Number of papers to skip
            tag: Optional tag name to filter by

        Returns:
            list of Paper objects
        """
        with self._get_conn() as conn:
            if tag:
                # Filter by tag
                tag = tag.lower().strip()
                rows = conn.execute("""
                    SELECT DISTINCT p.*
                    FROM papers p
                    JOIN paper_tags pt ON p.paper_id = pt.paper_id
                    JOIN tags t ON pt.tag_id = t.tag_id
                    WHERE t.name = ?
                    ORDER BY p.added_at DESC
                    LIMIT ? OFFSET ?
                """, (tag, limit, offset)).fetchall()
            else:
                # No tag filter
                rows = conn.execute(
                    "SELECT * FROM papers ORDER BY added_at DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()

            papers = []
            for row in rows:
                paper = Paper.from_dict(dict(row))
                paper.tags = self.get_paper_tags(paper.paper_id)
                papers.append(paper)
            return papers

    def count_papers(self) -> int:
        """Get total number of papers in database."""
        with self._get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
            return count

    def search_papers(self, query: str) -> list[Paper]:
        """Search papers by title or abstract.

        Args:
            query: Search query

        Returns:
            list of matching Paper objects
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM papers 
                WHERE title LIKE ? OR abstract LIKE ?
                ORDER BY citation_count DESC
                LIMIT 20
            """,
                (f"%{query}%", f"%{query}%"),
            ).fetchall()

            return [Paper.from_dict(dict(row)) for row in rows]

    def delete_paper(self, paper_id: str) -> bool:
        """Delete a paper and its extractions.

        Args:
            paper_id: ID of the paper to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_conn() as conn:
            # Delete extractions first (foreign key constraint)
            conn.execute("DELETE FROM extractions WHERE paper_id = ?", (paper_id,))
            
            # Delete paper-tag associations (foreign key constraint)
            conn.execute("DELETE FROM paper_tags WHERE paper_id = ?", (paper_id,))

            # Delete paper
            cursor = conn.execute("DELETE FROM papers WHERE paper_id = ?", (paper_id,))

            if cursor.rowcount > 0:
                # Delete associated PDF and text files
                self._delete_paper_files(paper_id)
                logger.info("Paper deleted", paper_id=paper_id)
                return True
            return False

    def _delete_paper_files(self, paper_id: str) -> None:
        """Delete PDF and text files associated with a paper.
        
        Args:
            paper_id: ID of the paper whose files should be deleted
        """
        pdf_dir = self.config.base_dir / "pdfs"
        pdf_path = pdf_dir / f"{paper_id}.pdf"
        txt_path = pdf_dir / f"{paper_id}.txt"
        
        # Delete PDF file if it exists
        if pdf_path.exists():
            try:
                pdf_path.unlink()
                logger.info("PDF deleted", paper_id=paper_id, path=str(pdf_path))
            except Exception as e:
                logger.error("Failed to delete PDF", paper_id=paper_id, path=str(pdf_path), error=str(e))
        
        # Delete text file if it exists
        if txt_path.exists():
            try:
                txt_path.unlink()
                logger.info("Text file deleted", paper_id=paper_id, path=str(txt_path))
            except Exception as e:
                logger.error("Failed to delete text file", paper_id=paper_id, path=str(txt_path), error=str(e))

    # Extraction operations

    def add_extraction(self, extraction: Extraction) -> bool:
        """Add or update an extraction.

        Args:
            extraction: Extraction object to add

        Returns:
            True if successful
        """
        with self._get_conn() as conn:
            data = extraction.to_dict()
            conn.execute(
                """
                INSERT OR REPLACE INTO extractions (
                    paper_id, extraction_type, content, created_at
                ) VALUES (?, ?, ?, ?)
            """,
                (
                    data["paper_id"],
                    data["extraction_type"],
                    data["content"],
                    data["created_at"],
                ),
            )
            logger.info(
                "Extraction saved",
                paper_id=extraction.paper_id,
                type=extraction.extraction_type,
            )
            return True

    def get_extraction(self, paper_id: str, extraction_type: str) -> Extraction | None:
        """Get a specific extraction for a paper.

        Args:
            paper_id: ID of the paper
            extraction_type: Type of extraction (e.g., "key_points")

        Returns:
            Extraction object or None if not found
        """
        with self._get_conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM extractions 
                WHERE paper_id = ? AND extraction_type = ?
            """,
                (paper_id, extraction_type),
            ).fetchone()

            if row:
                return Extraction.from_dict(dict(row))
            return None

    def list_extractions(self, paper_id: str) -> list[Extraction]:
        """list all extractions for a paper.

        Args:
            paper_id: ID of the paper

        Returns:
            list of Extraction objects
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM extractions WHERE paper_id = ? ORDER BY created_at DESC",
                (paper_id,),
            ).fetchall()

            return [Extraction.from_dict(dict(row)) for row in rows]
    
    def get_last_synthesis_time(self) -> datetime | None:
        """Get the timestamp of the most recent synthesis.
        
        Returns:
            Datetime of last synthesis or None if no synthesis found
        """
        
        with self._get_conn() as conn:
            # Look for the most recent synthesis extraction
            row = conn.execute("""
                SELECT created_at FROM extractions 
                WHERE extraction_type = 'synthesis'
                ORDER BY created_at DESC
                LIMIT 1
            """).fetchone()
            
            if row:
                try:
                    return datetime.fromisoformat(row['created_at'])
                except (ValueError, TypeError):
                    logger.warning("Invalid synthesis timestamp", created_at=row['created_at'])
                    return None
            return None

    # User Notes operations

    def add_note(self, paper_id: str, content: str) -> bool:
        """Add or update user notes for a paper.
        
        Args:
            paper_id: ID of the paper
            content: Markdown content of the note
            
        Returns:
            True if successful
        """
        # Store user notes directly as text, not JSON
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO extractions (
                    paper_id, extraction_type, content, created_at
                ) VALUES (?, ?, ?, ?)
            """,
                (
                    paper_id,
                    "user_notes",
                    content,  # Store markdown directly as text
                    datetime.now().isoformat(),
                ),
            )
            logger.info(
                "User notes saved",
                paper_id=paper_id,
            )
            return True

    def get_note(self, paper_id: str) -> str | None:
        """Get user notes for a paper.
        
        Args:
            paper_id: ID of the paper
            
        Returns:
            Note content as markdown string or None if not found
        """
        # User notes are stored as plain text, not JSON
        with self._get_conn() as conn:
            row = conn.execute(
                """
                SELECT content FROM extractions 
                WHERE paper_id = ? AND extraction_type = ?
            """,
                (paper_id, "user_notes"),
            ).fetchone()
            
            if row:
                return row['content']
            return None

    def delete_note(self, paper_id: str) -> bool:
        """Delete user notes for a paper.
        
        Args:
            paper_id: ID of the paper
            
        Returns:
            True if deleted, False if not found
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM extractions WHERE paper_id = ? AND extraction_type = ?",
                (paper_id, "user_notes"),
            )
            return cursor.rowcount > 0

    def add_agent_note(self, paper_id: str, content: str) -> bool:
        """Add or update agent notes for a paper."""
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO extractions (
                    paper_id, extraction_type, content, created_at
                ) VALUES (?, ?, ?, ?)
            """, (paper_id, "agent_notes", content, datetime.now().isoformat()))
            logger.info("Agent notes saved", paper_id=paper_id)
            return True
    
    def get_agent_note(self, paper_id: str) -> str | None:
        """Get agent notes for a paper."""
        with self._get_conn() as conn:
            row = conn.execute("""
                SELECT content FROM extractions 
                WHERE paper_id = ? AND extraction_type = ?
            """, (paper_id, "agent_notes")).fetchone()
            return row['content'] if row else None
    
    def append_agent_note(self, paper_id: str, new_content: str) -> bool:
        """Append to existing agent notes (synthesis accumulation)."""
        existing = self.get_agent_note(paper_id) or ""
        
        # Add timestamp header for each synthesis
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted_content = f"\n\n## Synthesis - {timestamp}\n{new_content}"
        
        updated = existing + formatted_content if existing else new_content
        return self.add_agent_note(paper_id, updated)
    
    def clear_agent_notes(self, paper_id: str) -> bool:
        """Clear agent notes for a paper."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM extractions WHERE paper_id = ? AND extraction_type = ?",
                (paper_id, "agent_notes"),
            )
            return cursor.rowcount > 0
    
    def clear_all_agent_notes(self) -> int:
        """Clear all agent notes across all papers."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM extractions WHERE extraction_type = ?",
                ("agent_notes",),
            )
            return cursor.rowcount


    def list_papers_with_notes(self) -> list[tuple[Paper, str, datetime]]:
        """List all papers that have user notes.
        
        Returns:
            List of tuples containing (paper, note_preview, updated_at)
        """
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT p.paper_id, p.title, p.authors, p.year, p.abstract,
                       p.arxiv_id, p.doi, p.citation_count, p.tldr, p.venue,
                       p.open_access_pdf_url, p.added_at,
                       e.content, e.created_at
                FROM papers p
                JOIN extractions e ON p.paper_id = e.paper_id
                WHERE e.extraction_type = 'user_notes'
                ORDER BY e.created_at DESC
            """).fetchall()
            
            results = []
            for row in rows:
                # Create dict with only paper fields
                paper_data = {
                    'paper_id': row['paper_id'],
                    'title': row['title'],
                    'authors': row['authors'],
                    'year': row['year'],
                    'abstract': row['abstract'],
                    'arxiv_id': row['arxiv_id'],
                    'doi': row['doi'],
                    'citation_count': row['citation_count'],
                    'tldr': row['tldr'],
                    'venue': row['venue'],
                    'open_access_pdf_url': row['open_access_pdf_url'],
                    'added_at': row['added_at'],
                }
                paper = Paper.from_dict(paper_data)
                note_preview = row['content'][:100] + "..." if len(row['content']) > 100 else row['content']
                updated_at = datetime.fromisoformat(row['created_at'])
                results.append((paper, note_preview, updated_at))
            return results

    def list_papers_with_agent_notes(self) -> list[tuple[Paper, str, datetime]]:
        """List all papers that have user notes.
        
        Returns:
            List of tuples containing (paper, note_preview, updated_at)
        """
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT p.paper_id, p.title, p.authors, p.year, p.abstract,
                       p.arxiv_id, p.doi, p.citation_count, p.tldr, p.venue,
                       p.open_access_pdf_url, p.added_at,
                       e.content, e.created_at
                FROM papers p
                JOIN extractions e ON p.paper_id = e.paper_id
                WHERE e.extraction_type = 'agent_notes'
                ORDER BY e.created_at DESC
            """).fetchall()
            
            results = []
            for row in rows:
                # Create dict with only paper fields
                paper_data = {
                    'paper_id': row['paper_id'],
                    'title': row['title'],
                    'authors': row['authors'],
                    'year': row['year'],
                    'abstract': row['abstract'],
                    'arxiv_id': row['arxiv_id'],
                    'doi': row['doi'],
                    'citation_count': row['citation_count'],
                    'tldr': row['tldr'],
                    'venue': row['venue'],
                    'open_access_pdf_url': row['open_access_pdf_url'],
                    'added_at': row['added_at'],
                }
                paper = Paper.from_dict(paper_data)
                note_preview = row['content'][:100] + "..." if len(row['content']) > 100 else row['content']
                updated_at = datetime.fromisoformat(row['created_at'])
                results.append((paper, note_preview, updated_at))
            return results

    
    # Tag CRUD operations
    
    def create_tag(self, name: str) -> Tag:
        """Create a new tag or return existing one.
        
        Args:
            name: Tag name (will be normalized to lowercase)
            
        Returns:
            Tag object (new or existing)
        """
        name = name.lower().strip()
        
        # Try to get existing tag first
        existing = self.get_tag_by_name(name)
        if existing:
            return existing
            
        # Create new tag
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO tags (name, created_at) VALUES (?, ?)",
                (name, datetime.now().isoformat()),
            )
            return Tag(
                tag_id=cursor.lastrowid,
                name=name,
                created_at=datetime.now(),
            )
    
    def get_tag_by_name(self, name: str) -> Tag | None:
        """Get tag by name.
        
        Args:
            name: Tag name to search for
            
        Returns:
            Tag object or None if not found
        """
        name = name.lower().strip()
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM tags WHERE name = ?", (name,),
            ).fetchone()
            
            if row:
                return Tag.from_dict(dict(row))
            return None
    
    def get_tag_by_id(self, tag_id: int) -> Tag | None:
        """Get tag by ID.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            Tag object or None if not found
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM tags WHERE tag_id = ?", (tag_id,),
            ).fetchone()
            
            if row:
                return Tag.from_dict(dict(row))
            return None
    
    def list_all_tags(self) -> list[tuple[Tag, int]]:
        """List all tags with paper counts.
        
        Returns:
            List of tuples containing (Tag, paper_count)
        """
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT t.*, COUNT(pt.paper_id) as paper_count
                FROM tags t
                LEFT JOIN paper_tags pt ON t.tag_id = pt.tag_id
                GROUP BY t.tag_id
                ORDER BY paper_count DESC, t.name ASC
            """).fetchall()
            
            results = []
            for row in rows:
                tag_data = dict(row)
                paper_count = tag_data.pop('paper_count')
                tag = Tag.from_dict(tag_data)
                results.append((tag, paper_count))
            return results
    
    def delete_unused_tags(self) -> int:
        """Delete tags not associated with any papers.
        
        Returns:
            Number of tags deleted
        """
        with self._get_conn() as conn:
            cursor = conn.execute("""
                DELETE FROM tags
                WHERE tag_id NOT IN (
                    SELECT DISTINCT tag_id FROM paper_tags
                )
            """)
            return cursor.rowcount
    
    # Paper-tag associations
    
    def add_tags_to_paper(self, paper_id: str, tag_names: list[str]) -> None:
        """Add multiple tags to a paper (creates tags if needed).
        
        Args:
            paper_id: ID of the paper
            tag_names: List of tag names to add
        """
        # First create all tags outside of the connection context
        tag_ids = []
        for tag_name in tag_names:
            tag = self.create_tag(tag_name)
            tag_ids.append(tag.tag_id)
        
        # Then add associations in a single connection context
        with self._get_conn() as conn:
            for tag_id in tag_ids:
                # Add association (ignore if already exists)
                try:
                    conn.execute(
                        "INSERT INTO paper_tags (paper_id, tag_id) VALUES (?, ?)",
                        (paper_id, tag_id),
                    )
                except sqlite3.IntegrityError:
                    # Tag already associated with paper
                    pass
                    
        logger.info("Tags added to paper", paper_id=paper_id, tags=tag_names)
    
    def remove_tag_from_paper(self, paper_id: str, tag_name: str) -> bool:
        """Remove a tag from a paper.
        
        Args:
            paper_id: ID of the paper
            tag_name: Name of the tag to remove
            
        Returns:
            True if removed, False if not found
        """
        tag = self.get_tag_by_name(tag_name)
        if not tag:
            return False
            
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM paper_tags WHERE paper_id = ? AND tag_id = ?",
                (paper_id, tag.tag_id),
            )
            return cursor.rowcount > 0
    
    def get_paper_tags(self, paper_id: str) -> list[str]:
        """Get all tag names for a paper.
        
        Args:
            paper_id: ID of the paper
            
        Returns:
            List of tag names
        """
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT t.name
                FROM tags t
                JOIN paper_tags pt ON t.tag_id = pt.tag_id
                WHERE pt.paper_id = ?
                ORDER BY t.name
            """, (paper_id,)).fetchall()
            
            return [row['name'] for row in rows]
    
    def set_paper_tags(self, paper_id: str, tag_names: list[str]) -> None:
        """Replace all tags for a paper (add new, remove old).
        
        Args:
            paper_id: ID of the paper
            tag_names: New list of tag names
        """
        with self._get_conn() as conn:
            # Remove all existing tags
            conn.execute("DELETE FROM paper_tags WHERE paper_id = ?", (paper_id,))
            
            # Add new tags
            self.add_tags_to_paper(paper_id, tag_names)
    
    # Search operations
    
    def search_papers_by_tags(self, tag_names: list[str], match_all: bool = False) -> list[Paper]:
        """Search papers by tags (AND/OR logic).
        
        Args:
            tag_names: List of tag names to search for
            match_all: If True, papers must have ALL tags (AND).
                      If False, papers can have ANY tag (OR).
                      
        Returns:
            List of Paper objects matching the criteria
        """
        if not tag_names:
            return []
            
        # Normalize tag names
        tag_names = [name.lower().strip() for name in tag_names]
        
        with self._get_conn() as conn:
            params: Sequence[str | int]
            if match_all:
                # Papers must have ALL specified tags
                query = """
                    SELECT DISTINCT p.*
                    FROM papers p
                    WHERE p.paper_id IN (
                        SELECT pt.paper_id
                        FROM paper_tags pt
                        JOIN tags t ON pt.tag_id = t.tag_id
                        WHERE t.name IN ({})
                        GROUP BY pt.paper_id
                        HAVING COUNT(DISTINCT t.name) = ?
                    )
                    ORDER BY p.added_at DESC
                """.format(','.join('?' * len(tag_names)))
                params = tag_names + [len(tag_names)]
            else:
                # Papers can have ANY of the specified tags
                query = """
                    SELECT DISTINCT p.*
                    FROM papers p
                    JOIN paper_tags pt ON p.paper_id = pt.paper_id
                    JOIN tags t ON pt.tag_id = t.tag_id
                    WHERE t.name IN ({})
                    ORDER BY p.added_at DESC
                """.format(','.join('?' * len(tag_names)))
                params = tag_names
                
            rows = conn.execute(query, params).fetchall()
            
            papers = []
            for row in rows:
                paper = Paper.from_dict(dict(row))
                paper.tags = self.get_paper_tags(paper.paper_id)
                papers.append(paper)
            return papers
    
    def get_papers_for_tag(self, tag_name: str) -> list[Paper]:
        """Get all papers with a specific tag.
        
        Args:
            tag_name: Name of the tag
            
        Returns:
            List of Paper objects with the tag
        """
        return self.search_papers_by_tags([tag_name], match_all=False)

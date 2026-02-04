"""
Conversation History Manager - Glued Interaction Search
Handles 4-5 recent interactions using FIFO queue for context-aware responses.
Stores interactions in SQLite database for future training.
"""
import sqlite3
import json
import time
from collections import deque
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConversationHistory:
    """
    Manages conversation context using a FIFO queue of recent interactions.
    Supports 4-5 interaction window for contextual responses.
    """
    
    def __init__(self, max_history: int = 5):
        """
        Args:
            max_history: Maximum number of interactions to keep in active memory (default: 5)
        """
        self.max_history = max_history
        self.history = deque(maxlen=max_history)  # FIFO queue
        self.session_id = self._generate_session_id()
        
    def __len__(self):
        """Support len() operator"""
        return len(self.history)
    
    def __iter__(self):
        """Support iteration"""
        return iter(self.history)
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{int(time.time())}"
    
    def add_interaction(self, user_query: str, intent: str, response: str, 
                       confidence: float = 0.0, metadata: Optional[Dict] = None):
        """
        Add a new interaction to the history (FIFO).
        
        Args:
            user_query: What the user said
            intent: Classified intent from SetFit
            response: AXIOM's response
            confidence: Intent classification confidence
            metadata: Additional context (RAG results, card triggers, etc.)
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "intent": intent,
            "response": response,
            "confidence": confidence,
            "metadata": metadata or {}
        }
        
        self.history.append(interaction)
        logger.debug(f"[HISTORY] Added interaction. Total: {len(self.history)}")
    
    def get_recent_interactions(self, count: Optional[int] = None) -> List[Dict]:
        """
        Get recent interactions from history.
        
        Args:
            count: Number of recent interactions to retrieve (default: all)
        
        Returns:
            List of interaction dictionaries
        """
        if count is None:
            return list(self.history)
        return list(self.history)[-count:]
    
    def get_context_string(self, count: int = 3) -> str:
        """
        Format recent interactions as a context string for LLM.
        
        Args:
            count: Number of recent interactions to include
        
        Returns:
            Formatted conversation context
        """
        if not self.history:
            return ""
        
        recent = self.get_recent_interactions(count)
        context_lines = ["RECENT CONVERSATION CONTEXT:"]
        
        for i, interaction in enumerate(recent, 1):
            context_lines.append(f"{i}. User: {interaction['user_query']}")
            context_lines.append(f"   AXIOM: {interaction['response']}")
        
        return "\n".join(context_lines)
    
    def get_last_topic(self) -> Optional[str]:
        """Get the topic/intent of the last interaction"""
        if not self.history:
            return None
        return self.history[-1]["intent"]
    
    def get_last_query(self) -> Optional[str]:
        """Get the last user query"""
        if not self.history:
            return None
        return self.history[-1]["user_query"]
    
    def has_related_context(self, keywords: List[str]) -> bool:
        """
        Check if any recent interactions contain related keywords.
        Useful for detecting follow-up questions.
        
        Args:
            keywords: List of keywords to search for
        
        Returns:
            True if any keyword found in recent history
        """
        if not self.history:
            return False
        
        # Check last 3 interactions
        recent = self.get_recent_interactions(3)
        for interaction in recent:
            query_lower = interaction["user_query"].lower()
            response_lower = interaction["response"].lower()
            
            for keyword in keywords:
                if keyword.lower() in query_lower or keyword.lower() in response_lower:
                    return True
        
        return False
    
    def clear(self):
        """Clear conversation history (new session)"""
        self.history.clear()
        self.session_id = self._generate_session_id()
        logger.info("[HISTORY] Cleared conversation history - new session")


class InteractionDatabase:
    """
    SQLite database for storing all interactions for future training.
    Supports analytics, pattern recognition, and model improvement.
    """
    
    def __init__(self, db_path: str = "data/interaction_history.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_query TEXT NOT NULL,
                intent TEXT NOT NULL,
                confidence REAL,
                response TEXT NOT NULL,
                metadata TEXT,
                feedback_rating INTEGER,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Session metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                interaction_count INTEGER DEFAULT 0,
                avg_confidence REAL,
                notes TEXT
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_intent 
            ON interactions(intent)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON interactions(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session 
            ON interactions(session_id)
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"[DB] Initialized interaction database at {self.db_path}")
    
    def save_interaction(self, session_id: str, user_query: str, intent: str, 
                        response: str, confidence: float = 0.0, 
                        metadata: Optional[Dict] = None):
        """
        Save an interaction to the database.
        
        Args:
            session_id: Current session ID
            user_query: User's input
            intent: Classified intent
            response: AXIOM's response
            confidence: Classification confidence
            metadata: Additional context data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        
        cursor.execute("""
            INSERT INTO interactions 
            (session_id, timestamp, user_query, intent, confidence, response, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, timestamp, user_query, intent, confidence, response, metadata_json))
        
        conn.commit()
        conn.close()
        logger.debug(f"[DB] Saved interaction: {intent} (confidence: {confidence:.2f})")
    
    def update_session(self, session_id: str, end_time: Optional[str] = None):
        """Update session statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session stats
        cursor.execute("""
            SELECT COUNT(*), AVG(confidence)
            FROM interactions
            WHERE session_id = ?
        """, (session_id,))
        
        count, avg_conf = cursor.fetchone()
        
        # Update or insert session
        cursor.execute("""
            INSERT OR REPLACE INTO sessions 
            (session_id, start_time, end_time, interaction_count, avg_confidence)
            VALUES (?, 
                    COALESCE((SELECT start_time FROM sessions WHERE session_id = ?), ?),
                    ?, ?, ?)
        """, (session_id, session_id, datetime.now().isoformat(), 
              end_time, count, avg_conf or 0.0))
        
        conn.commit()
        conn.close()
    
    def get_training_data(self, intent: Optional[str] = None, 
                         min_confidence: float = 0.7,
                         limit: int = 1000) -> List[Tuple[str, str]]:
        """
        Export interactions as training data (query, intent pairs).
        
        Args:
            intent: Filter by specific intent (optional)
            min_confidence: Minimum confidence threshold
            limit: Maximum number of samples
        
        Returns:
            List of (query, intent) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if intent:
            query = """
                SELECT user_query, intent
                FROM interactions
                WHERE intent = ? AND confidence >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            cursor.execute(query, (intent, min_confidence, limit))
        else:
            query = """
                SELECT user_query, intent
                FROM interactions
                WHERE confidence >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            cursor.execute(query, (min_confidence, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        logger.info(f"[DB] Exported {len(results)} training samples")
        return results
    
    def get_statistics(self) -> Dict:
        """Get interaction statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total interactions
        cursor.execute("SELECT COUNT(*) FROM interactions")
        total = cursor.fetchone()[0]
        
        # Intent distribution
        cursor.execute("""
            SELECT intent, COUNT(*) as count
            FROM interactions
            GROUP BY intent
            ORDER BY count DESC
        """)
        intent_dist = dict(cursor.fetchall())
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM interactions")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # Sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_interactions": total,
            "total_sessions": session_count,
            "intent_distribution": intent_dist,
            "avg_confidence": avg_confidence
        }
    
    def export_to_json(self, output_path: str, intent: Optional[str] = None):
        """Export interactions to JSON for training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if intent:
            cursor.execute("""
                SELECT user_query, intent, confidence, timestamp, response
                FROM interactions
                WHERE intent = ?
                ORDER BY timestamp DESC
            """, (intent,))
        else:
            cursor.execute("""
                SELECT user_query, intent, confidence, timestamp, response
                FROM interactions
                ORDER BY timestamp DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        data = [
            {
                "text": row[0],
                "intent": row[1],
                "confidence": row[2],
                "timestamp": row[3],
                "response": row[4]
            }
            for row in rows
        ]
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"[DB] Exported {len(data)} interactions to {output_path}")


class ConversationManager:
    """
    Combined manager for conversation history and database storage.
    Provides a unified interface for the main agent.
    """
    
    def __init__(self, max_history: int = 5, db_path: str = "data/interaction_history.db"):
        """
        Initialize conversation manager with history and database.
        
        Args:
            max_history: Number of interactions to keep in active memory
            db_path: Path to SQLite database
        """
        self.history = ConversationHistory(max_history)
        self.database = InteractionDatabase(db_path)
        logger.info(f"[ConversationManager] Initialized (history={max_history})")
    
    def add_interaction(self, user_query: str, intent: str, response: str,
                       confidence: float = 0.0, metadata: Optional[Dict] = None):
        """
        Add interaction to both history and database.
        
        Args:
            user_query: User's input
            intent: Classified intent
            response: AXIOM's response
            confidence: Classification confidence
            metadata: Additional context
        """
        # Add to active history
        self.history.add_interaction(user_query, intent, response, confidence, metadata)
        
        # Save to database
        self.database.save_interaction(
            self.history.session_id,
            user_query,
            intent,
            response,
            confidence,
            metadata
        )
    
    def get_context_for_llm(self, count: int = 3) -> str:
        """Get formatted conversation context for LLM"""
        return self.history.get_context_string(count)
    
    def end_session(self):
        """End current session and update statistics"""
        self.database.update_session(
            self.history.session_id,
            end_time=datetime.now().isoformat()
        )
        self.history.clear()
        logger.info("[ConversationManager] Session ended")
    
    def get_statistics(self) -> Dict:
        """Get interaction statistics"""
        return self.database.get_statistics()

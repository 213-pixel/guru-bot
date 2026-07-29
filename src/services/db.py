import sqlite3
from contextlib import contextmanager
from datetime import datetime
import os
from typing import Optional, List, Dict
from src.utils.logger import logger

class Database:
    """Kelas buat handle semua operasi database"""
    
    def __init__(self, db_path: str = "data/guru_bot.db"):
        self.db_path = db_path
        # Pastikan folder data ada
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
        logger.info(f"Database initialized at {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager buat koneksi database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Bikin semua tabel kalo belum ada"""
        with self.get_connection() as conn:
            # Tabel users
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabel chat_history
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    question TEXT,
                    answer TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Tabel FAQ
            conn.execute("""
                CREATE TABLE IF NOT EXISTS faq (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT UNIQUE,
                    answer TEXT,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabel untuk feedback
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index buat performa
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON chat_history(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_faq_question ON faq(question)")
            
            conn.commit()
            logger.info("Database tables created successfully")
    
    # ============ USER OPERATIONS ============
    
    def save_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Simpan atau update user"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, username, first_name, last_name))
            conn.commit()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Dapatkan data user"""
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            return dict(result) if result else None
    
    def get_all_users(self) -> List[Dict]:
        """Dapatkan semua user (buat broadcast)"""
        with self.get_connection() as conn:
            results = conn.execute(
                "SELECT user_id, username, first_name FROM users ORDER BY registered_at DESC"
            ).fetchall()
            return [dict(row) for row in results]
    
    # ============ CHAT HISTORY ============
    
    def save_chat(self, user_id: int, question: str, answer: str):
        """Simpan history chat"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO chat_history (user_id, question, answer)
                VALUES (?, ?, ?)
            """, (user_id, question, answer))
            conn.commit()
    
    def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Ambil history chat user"""
        with self.get_connection() as conn:
            results = conn.execute("""
                SELECT question, answer, timestamp
                FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()
            return [dict(row) for row in results]
    
    def get_chat_stats(self) -> Dict:
        """Statistik chat"""
        with self.get_connection() as conn:
            total_chats = conn.execute(
                "SELECT COUNT(*) FROM chat_history"
            ).fetchone()[0]
            
            total_users = conn.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0]
            
            today_chats = conn.execute("""
                SELECT COUNT(*) FROM chat_history
                WHERE DATE(timestamp) = DATE('now')
            """).fetchone()[0]
            
            return {
                "total_chats": total_chats,
                "total_users": total_users,
                "today_chats": today_chats
            }
    
    # ============ FAQ OPERATIONS ============
    
    def get_faq(self, question: str) -> Optional[str]:
        """Cari FAQ berdasarkan keyword (fuzzy matching)"""
        with self.get_connection() as conn:
            # Coba exact match dulu
            result = conn.execute(
                "SELECT answer FROM faq WHERE question = ? LIMIT 1",
                (question,)
            ).fetchone()
            
            if result:
                return result["answer"]
            
            # Kalo gak ada, cari pake LIKE (simple fuzzy)
            keywords = question.split()
            for keyword in keywords:
                if len(keyword) < 3:  # Skip kata pendek
                    continue
                result = conn.execute(
                    "SELECT answer FROM faq WHERE question LIKE ? LIMIT 1",
                    (f"%{keyword}%",)
                ).fetchone()
                if result:
                    return result["answer"]
            
            return None
    
    def get_all_faq(self) -> List[Dict]:
        """Ambil semua FAQ"""
        with self.get_connection() as conn:
            results = conn.execute(
                "SELECT id, question, answer, category FROM faq ORDER BY question"
            ).fetchall()
            return [dict(row) for row in results]
    
    def add_faq(self, question: str, answer: str, category: str = "general"):
        """Tambah atau update FAQ"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO faq (question, answer, category, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (question, answer, category))
            conn.commit()
            logger.info(f"FAQ added: {question}")
    
    def delete_faq(self, question: str):
        """Hapus FAQ"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM faq WHERE question = ?", (question,))
            conn.commit()
            logger.info(f"FAQ deleted: {question}")
    
    def get_faq_by_category(self, category: str) -> List[Dict]:
        """Ambil FAQ berdasarkan kategori"""
        with self.get_connection() as conn:
            results = conn.execute(
                "SELECT question, answer FROM faq WHERE category = ?",
                (category,)
            ).fetchall()
            return [dict(row) for row in results]
    
    # ============ FEEDBACK ============
    
    def save_feedback(self, user_id: int, message: str, rating: int = None):
        """Simpan feedback dari user"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO feedback (user_id, message, rating)
                VALUES (?, ?, ?)
            """, (user_id, message, rating))
            conn.commit()
            logger.info(f"Feedback from user {user_id}")
    
    def get_feedback_stats(self) -> Dict:
        """Statistik feedback"""
        with self.get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
            avg_rating = conn.execute(
                "SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL"
            ).fetchone()[0]
            
            return {
                "total_feedback": total,
                "average_rating": round(avg_rating, 2) if avg_rating else 0
            }

# Singleton instance
db = Database()
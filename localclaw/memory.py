"""Memory system using ChromaDB"""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class Memory:
    """Simple memory system (placeholder for ChromaDB integration)"""
    
    def __init__(self, db_path: str, collection_name: str = "localclaw_memory"):
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.db_path.mkdir(parents=True, exist_ok=True)
        self._memories: List[Dict[str, Any]] = []
        self._load_memories()
    
    def _load_memories(self):
        """Load memories from disk (simple JSONL for now)"""
        memory_file = self.db_path / f"{self.collection_name}.jsonl"
        if memory_file.exists():
            import json
            with open(memory_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self._memories.append(json.loads(line))
    
    def _save_memories(self):
        """Save memories to disk"""
        import json
        memory_file = self.db_path / f"{self.collection_name}.jsonl"
        with open(memory_file, 'w', encoding='utf-8') as f:
            for mem in self._memories:
                f.write(json.dumps(mem, ensure_ascii=False) + '\n')
    
    def save(self, content: str, category: str = "general", metadata: Dict[str, Any] = None) -> str:
        """Save a memory"""
        memory_id = hashlib.md5(content.encode()).hexdigest()[:12]
        memory = {
            "id": memory_id,
            "content": content,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self._memories.append(memory)
        self._save_memories()
        return memory_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories (simple keyword search for now)"""
        query_lower = query.lower()
        results = []
        for mem in self._memories:
            if query_lower in mem["content"].lower():
                results.append(mem)
        return results[:limit]
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent memories"""
        return sorted(self._memories, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_memories": len(self._memories),
            "categories": list(set(m["category"] for m in self._memories))
        }

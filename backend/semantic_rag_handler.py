"""
Semantic RAG Handler with Vector Search
Uses sentence transformers for proper semantic retrieval instead of keyword matching.
"""
import json
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import logging
from config import INVENTORY_PATH, PROJECT_IDEAS_RAG_PATH, RAG_KNOWLEDGE_BASE_PATH

logger = logging.getLogger(__name__)


class SemanticRAGHandler:
    """
    Semantic RAG with vector embeddings for intelligent retrieval.
    Replaces keyword-based matching with cosine similarity search.
    """
    
    def __init__(self, 
                 inventory_path: str = None,
                 projects_path: str = None,
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with semantic search.
        
        Args:
            inventory_path: Path to equipment inventory
            projects_path: Path to project ideas
            model_name: Sentence transformer model (lightweight and fast)
        """
        if inventory_path is None:
            inventory_path = str(INVENTORY_PATH)
        if projects_path is None:
            projects_path = str(PROJECT_IDEAS_RAG_PATH)
            
        # Load data
        self.equipment_db = self._load_inventory(inventory_path)
        self.projects_data = self._load_projects(projects_path)
        
        # Load sentence transformer for embeddings
        logger.info(f"Loading semantic model: {model_name}")
        self.embedder = SentenceTransformer(model_name)
        
        # Load authority data
        self.authorities = self._load_authorities()
        
        # Build vector indices
        self._build_equipment_vectors()
        self._build_project_vectors()
        self._build_authority_vectors()
        
        logger.info(f"✅ Semantic RAG ready: {len(self.equipment_db)} equipment, {len(self.project_embeddings)} projects, {len(self.authority_embeddings)} authorities")
    
    def _load_inventory(self, path: str) -> List[Dict]:
        """Load equipment inventory."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                # Handle both old format (direct list) and new format (wrapped in equipment key)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'equipment' in data:
                    return data['equipment']
                else:
                    return data
        except Exception as e:
            logger.error(f"Failed to load inventory: {e}")
            return []
    
    def _load_projects(self, path: str) -> List[Dict]:
        """Load project ideas."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                projects = data.get('all_entries', [])
                logger.info(f"Loaded {len(projects)} project ideas")
                return projects
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")
            return []
    
    def _load_authorities(self) -> List[Dict]:
        """Load university and lab authority data."""
        return [
            {"name": "Dr. Aman Sharma", "role": "AI and Software Lead", "type": "lab", "department": "CSE", "description": "Drobotics Lab AI and Software Lead, Computer Science and Engineering faculty, Machine learning and software development, AI research"},
            {"name": "Dr. Vikas Baghel", "role": "Hardware and Sensors Lead", "type": "lab", "department": "ECE", "description": "Drobotics Lab Hardware and Sensors Lead, Electronics and Communication Engineering faculty, Embedded systems and sensor integration"},
            {"name": "Prof. (Dr.) Shruti Jain", "role": "Dean of Academics", "type": "university", "department": "ECE", "expertise": "Image and Signal Processing, Bio-inspired Computing", "description": "Dean of Academics and Research at JUIT, Electronics and Communication Engineering, World's Top 2% Scientist (Stanford/Elsevier listing)"},
            {"name": "Prof. (Dr.) Rajendra Kumar Sharma", "role": "Vice Chancellor", "type": "university", "expertise": "Machine Learning, Pattern Recognition, Speech Processing, AI Research", "description": "Vice Chancellor of JUIT, Chief academic officer, AI and ML expert with PhD from IIT Roorkee, Machine learning research"},
            {"name": "Brigadier RK Sharma, SM (Retd.)", "role": "Registrar and Dean of Students", "type": "university", "expertise": "Civil Engineering, Defence Studies, Administration", "description": "Registrar of JUIT, Dean of Students, Administrative head, M.Tech from IIT Kanpur, recipient of Sena Medal"},
            {"name": "Sh. Shiv Pratap Shukla", "role": "Chancellor", "type": "university", "description": "Chancellor of JUIT, Governor of Himachal Pradesh, Constitutional head and supreme authority of the university"},
            {"name": "Sh. Manoj Gaur", "role": "Pro-Chancellor and Chairman", "type": "university", "description": "Pro-Chancellor and Chairman of JUIT, Executive Chairman of Jaypee Group, Strategic leader and university board head"},
            {"name": "Prof. Sunil Kumar Khah", "role": "Dean of Accreditations", "type": "university", "description": "Dean of Accreditations, Controller of Examinations, Quality assurance and academic standards"},
            {"name": "Prof. Sudhir Kumar", "role": "Dean of Research", "type": "university", "description": "Dean of Research at JUIT, Leads research initiatives and internationalization programs"},
            {"name": "CA Hemant Vyas", "role": "Chief Finance Officer", "type": "university", "description": "Chief Finance Officer, CFO of JUIT, Manages university financial health and auditing"},
        ]
    
    def _build_equipment_vectors(self):
        """Build vector embeddings for equipment."""
        # Create searchable text for each equipment
        self.equipment_texts = []
        for item in self.equipment_db:
            # Combine name, category, capabilities for rich context
            text = f"{item['name']} {item['category']} {item['capabilities']} {item.get('specs', '')}"
            self.equipment_texts.append(text)
        
        # Generate embeddings
        if self.equipment_texts:
            self.equipment_embeddings = self.embedder.encode(self.equipment_texts, show_progress_bar=False)
        else:
            self.equipment_embeddings = np.array([])
        
        logger.info(f"Built {len(self.equipment_embeddings)} equipment vectors")
    
    def _build_project_vectors(self):
        """Build vector embeddings for projects."""
        self.project_texts = []
        for proj in self.projects_data:
            # Combine all relevant fields
            title = proj.get('project_title', '')
            desc = proj.get('description', '')
            hw = ', '.join(proj.get('hardware_needed', []))
            text = f"{title} {desc} Hardware: {hw}"
            self.project_texts.append(text)
        
        # Generate embeddings
        if self.project_texts:
            self.project_embeddings = self.embedder.encode(self.project_texts, show_progress_bar=False)
        else:
            self.project_embeddings = np.array([])
        
        logger.info(f"Built {len(self.project_embeddings)} project vectors")
    
    def _build_authority_vectors(self):
        """Build vector embeddings for university/lab authorities."""
        self.authority_texts = []
        for auth in self.authorities:
            # Combine all fields for search
            text = f"{auth['name']} {auth['role']} {auth.get('expertise', '')} {auth.get('description', '')}"
            self.authority_texts.append(text)
        
        # Generate embeddings
        if self.authority_texts:
            self.authority_embeddings = self.embedder.encode(self.authority_texts, show_progress_bar=False)
        else:
            self.authority_embeddings = np.array([])
        
        logger.info(f"Built {len(self.authority_embeddings)} authority vectors")
    
    def retrieve_projects(self, query: str, max_results: int = 3) -> Dict:
        """
        Semantic search for projects using vector similarity.
        
        Args:
            query: User question
            max_results: Number of results to return
            
        Returns:
            {'projects': [...], 'query': query}
        """
        if len(self.project_embeddings) == 0:
            return {'projects': [], 'query': query}
        
        # Encode query
        query_embedding = self.embedder.encode([query], show_progress_bar=False)[0]
        
        # Compute cosine similarity
        similarities = np.dot(self.project_embeddings, query_embedding) / (
            np.linalg.norm(self.project_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top matches
        top_indices = np.argsort(similarities)[-max_results:][::-1]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0.2:  # Minimum relevance threshold
                project = self.projects_data[idx].copy()
                project['_similarity'] = float(score)
                results.append(project)
        
        logger.info(f"[Semantic RAG] Found {len(results)} projects for: '{query}'")
        if results:
            logger.info(f"  Top match: {results[0].get('project_title')} (similarity: {results[0]['_similarity']:.2f})")
        
        return {'projects': results, 'query': query}
    
    def retrieve_equipment(self, query: str, max_results: int = 3) -> Dict:
        """
        Semantic search for equipment using vector similarity.
        
        Args:
            query: User question
            max_results: Number of results
            
        Returns:
            {'results': [...], 'query': query}
        """
        if len(self.equipment_embeddings) == 0:
            return {'results': [], 'query': query}
        
        # Encode query
        query_embedding = self.embedder.encode([query], show_progress_bar=False)[0]
        
        # Compute cosine similarity
        similarities = np.dot(self.equipment_embeddings, query_embedding) / (
            np.linalg.norm(self.equipment_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top matches
        top_indices = np.argsort(similarities)[-max_results:][::-1]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0.2:  # Minimum relevance
                item = self.equipment_db[idx].copy()
                item['_similarity'] = float(score)
                results.append(item)
        
        logger.info(f"[Semantic RAG] Found {len(results)} equipment for: '{query}'")
        if results:
            logger.info(f"  Top match: {results[0].get('name')} (similarity: {results[0]['_similarity']:.2f})")
        
        return {'results': results, 'query': query}
    
    def get_all_project_count(self) -> int:
        """Get total project count."""
        return len(self.projects_data)
    
    def retrieve_authorities(self, query: str, max_results: int = 3) -> Dict:
        """Semantic search for university/lab authorities."""
        if len(self.authority_embeddings) == 0:
            return {'authorities': [], 'query': query}
        
        # Encode query
        query_embedding = self.embedder.encode([query], show_progress_bar=False)[0]
        
        # Compute similarity
        similarities = np.dot(self.authority_embeddings, query_embedding) / (
            np.linalg.norm(self.authority_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top matches
        top_indices = np.argsort(similarities)[-max_results:][::-1]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0.2:
                auth = self.authorities[idx].copy()
                auth['_similarity'] = float(score)
                results.append(auth)
        
        logger.info(f"[Semantic RAG] Found {len(results)} authorities for: '{query}'")
        return {'authorities': results, 'query': query}


# Singleton
_semantic_rag = None

def get_semantic_rag_handler():
    """Get or create semantic RAG handler."""
    global _semantic_rag
    if _semantic_rag is None:
        _semantic_rag = SemanticRAGHandler()
    return _semantic_rag


if __name__ == "__main__":
    # Test semantic search
    rag = SemanticRAGHandler()
    
    test_queries = [
        "autonomous robot navigation projects",
        "projects with Jetson Orin",
        "beginner friendly Arduino projects",
        "camera equipment for computer vision",
        "lidar sensors",
    ]
    
    print("\n" + "="*80)
    print("SEMANTIC RAG TEST")
    print("="*80)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        
        # Test project search
        results = rag.retrieve_projects(query, max_results=2)
        print(f"  Projects found: {len(results['projects'])}")
        for proj in results['projects']:
            print(f"    - {proj['project_title']} (score: {proj['_similarity']:.2f})")
        
        # Test equipment search
        results = rag.retrieve_equipment(query, max_results=2)
        print(f"  Equipment found: {len(results['results'])}")
        for item in results['results']:
            print(f"    - {item['name']} (score: {item['_similarity']:.2f})")
    
    print("\n" + "="*80)

"""
Conversation Orchestrator - Post-SetFit Routing Layer
Prevents LLM hallucination by smart routing and context injection.
Enhanced with conversation history (FIFO 4-5 interactions).
"""
import re
from typing import Optional, Dict, List
import json
from semantic_rag_handler import get_semantic_rag_handler
from conversation_manager import ConversationManager
from config import WEB_INTERACTION_DB_PATH


class ConversationState:
    """Tracks conversation flow for multi-turn dialogue."""
    def __init__(self):
        self.queue = []  # Queued sub-questions
        self.last_topic = None
        self.last_intent = None
        self.waiting_for_next = False
    
    def has_queued_topics(self):
        return len(self.queue) > 0
    
    def pop_next(self):
        if self.queue:
            self.waiting_for_next = False
            return self.queue.pop(0)
        return None
    
    def add_to_queue(self, queries: List[str]):
        self.queue.extend(queries)


class ConversationOrchestrator:
    """
    Routes classified intents to appropriate handlers.
    Manages conversation state for multi-query handling.
    Injects context metadata into LLM prompts.
    
    ENHANCED: Conversation history with FIFO queue (4-5 interactions)
    """
    def __init__(self):
        self.state = ConversationState()
        self.rag_handler = get_semantic_rag_handler()  # Semantic vector search
        
        # NEW: Conversation history manager
        self.conversation = ConversationManager(
            max_history=5,
            db_path=str(WEB_INTERACTION_DB_PATH)
        )
        
        # Import here to avoid circular dependency
        from axiom_brain import get_axiom_brain
        self.llm = get_axiom_brain()  # Direct GGUF inference
        
        # Hardcoded facts for critical information
        self.hardcoded_facts = {
            "juit_full_name": "Jaypee University of Information Technology",
            "vice_chancellor": "Prof. (Dr.) Rajendra Kumar Sharma",
            "vice_chancellor_expertise": "Machine Learning, Pattern Recognition, and Speech Processing"
        }
        
        # Canned responses for non-RAG intents
        self.canned_responses = {
            "greeting": "Hi! I'm AXIOM, your Drobotics Lab assistant built by Shubham Dev. What brings you here today?",
            "out_of_scope": "That's outside our lab's scope. Want to know about our available equipment?",
            "unclear_input": "I didn't catch that. Could you ask about specific equipment or the lab?"
        }
    
    def handle(self, intent: str, text: str) -> Optional[str]:
        """
        Route based on SetFit classification.
        
        Returns:
            str: Response text, or None for ghosted acknowledgments
        """
        
        # === GHOST ACKNOWLEDGMENTS ===
        if intent == "acknowledgment":
            # Don't send to LLM - just confirm and move on
            if self.state.has_queued_topics():
                next_topic = self.state.pop_next()
                # Treat queued topic as equipment query
                return self.query_with_context("equipment_query", next_topic)
            else:
                return None  # Silent acknowledge, wait for next input
        
        # === CANNED RESPONSES (NO LLM NEEDED) ===
        elif intent in self.canned_responses:
            return self.canned_responses[intent]
        
        # === MULTI-QUERY DETECTION ===
        elif intent in ["equipment_query", "lab_info", "people_query", "capability_check", "project_idea"]:
            queries = self.detect_multiple_queries(text)
            
            if len(queries) > 1:
                # Handle FIRST query, queue the rest
                response = self.query_with_context(intent, queries[0])
                self.state.add_to_queue(queries[1:])
                self.state.waiting_for_next = True
                
                # Small model asks ONE follow-up at a time
                next_preview = self.get_topic_preview(queries[1])
                return f"{response} Should we discuss {next_preview} next?"
            else:
                # Single query - straightforward
                return self.query_with_context(intent, text)
        
        else:
            # Unknown intent - treat as unclear
            return self.canned_responses["unclear_input"]
    
    def query_with_context(self, intent: str, text: str) -> str:
        """
        Query LLM with context enrichment and conversation history.
        
        ENHANCED: Includes recent conversation context in prompt
        """
        
        # HARDCODED FACTS: Check critical queries first
        text_lower = text.lower()
        
        # Identity questions
        if any(q in text_lower for q in ["who are you", "what are you", "your name", "introduce yourself", "who created you", "who made you", "who built you"]):
            response = "I'm AXIOM, a breakthrough voice assistant built by Shubham Dev under the Wired Brain Project at JUIT. I help with Drobotics Lab equipment, project ideas, and research guidance. What can I assist you with?"
            self.conversation.add_interaction(text, intent, response, 1.0, {"hardcoded": True})
            return response
        
        # JUIT queries
        if "juit" in text_lower and any(word in text_lower for word in ["what", "full", "name", "mean", "stand"]):
            response = f"JUIT stands for {self.hardcoded_facts['juit_full_name']}. It's a premier technical university in Himachal Pradesh. Want to know more about our Drobotics Lab?"
            self.conversation.add_interaction(text, intent, response, 1.0, {"hardcoded": True})
            return response
        
        # Vice Chancellor queries
        if "vice chancellor" in text_lower or "vice-chancellor" in text_lower or ("vc" in text_lower and "juit" in text_lower):
            response = f"The Vice Chancellor of JUIT is {self.hardcoded_facts['vice_chancellor']}, an expert in {self.hardcoded_facts['vice_chancellor_expertise']}. Anything else about JUIT you'd like to know?"
            self.conversation.add_interaction(text, intent, response, 1.0, {"hardcoded": True})
            return response
        
        # Step 1: Retrieve relevant context from RAG (semantic search)
        if intent == "project_idea":
            rag_context = self.rag_handler.retrieve_projects(text, max_results=3)
        elif intent in ["people_query", "lab_info"]:
            rag_context = self.rag_handler.retrieve_authorities(text, max_results=3)
        else:
            # Equipment query - check inventory first
            inventory_matches = self._check_inventory_for_keywords(text)
            if inventory_matches:
                # Combine inventory data with RAG
                rag_context = {
                    "equipment": inventory_matches,
                    "source": "inventory",
                    "results": inventory_matches
                }
            else:
                rag_context = self.rag_handler.retrieve_equipment(text, max_results=3)

        # Step 2: Get conversation history context (4 interactions for better continuity)
        conversation_context = self.conversation.get_context_for_llm(count=4)

        # Step 3: Build system prompt with RAG data + history
        system_prompt = self._build_rag_system_prompt(intent, rag_context, conversation_context)

        # Step 4: LLM inference
        response = self.llm.generate_response(
            user_input=text,
            system_prompt=system_prompt,
            max_tokens=80,
            temperature=0.3
        ).strip()

        # Step 5: Store interaction
        self.conversation.add_interaction(
            user_query=text,
            intent=intent,
            response=response,
            confidence=0.9,
            metadata={
                "rag_results": len(rag_context.get("results", rag_context.get("projects", rag_context.get("authorities", [])))) if rag_context else 0,
                "had_conversation_context": bool(conversation_context)
            }
        )

        return response

    def _build_rag_system_prompt(self, intent: str, rag_context: dict, conversation_context: str = "") -> str:
        """
        Build system prompt that includes RAG data and conversation history.
        This OVERRIDES the Modelfile's static system prompt.
        ENHANCED: Explicitly references past conversation for better context awareness.
        """
        base = """You are AXIOM, a breakthrough Voice Intelligence for Drobotics Lab at JUIT.

CREATOR: Built by Shubham Dev (JUIT student) as part of the Wired Brain Project, which aims to bridge the gap between human cognition and robotic systems.

CRITICAL FACTS (ALWAYS USE THESE):
- JUIT = Jaypee University of Information Technology
- Vice Chancellor: Prof. (Dr.) Rajendra Kumar Sharma (Machine Learning expert)

PERSONALITY: Speak like a friendly lab assistant, not a robot. Be enthusiastic about robotics. Use casual, natural language.
"""

        # ENHANCED: Make conversation context prominent
        if conversation_context:
            base += f"""
RECENT CONVERSATION CONTEXT:
{conversation_context}

IMPORTANT INSTRUCTIONS:
- Reference the conversation history above
- Build on previous topics and context
- If user mentioned a project/equipment/idea, acknowledge it in your response
- Maintain continuity with what was discussed before
"""
        else:
            base += "\nThis is the start of a new conversation.\n"

        base += """
RESPONSE RULES:
- Maximum 2 natural sentences
- Use data provided below
- Reference previous context when relevant (e.g., "Since you mentioned...")
- Be warm and encouraging
- End with a question or invitation
- NO lists, bullets, or markdown
"""

        rag_data = self._format_rag_context(rag_context)

        if intent == "project_idea":
            instruction = "Suggest 2-3 projects from the list below. Mention hardware needed."
        elif intent == "equipment_query":
            instruction = "EQUIPMENT AVAILABILITY CHECK: Tell the user what we HAVE IN STOCK from the data below. If we don't have something, mention what we DO have that's similar. Reference prior context if the user mentioned an equipment before."
        elif intent in ["people_query", "lab_info"]:
            instruction = "Use ONLY the authority data below. If asking about Vice Chancellor, say Prof. (Dr.) Rajendra Kumar Sharma."
        else:
            instruction = "Answer using the context provided below."

        return f"{base}\n{instruction}\n\nDATA:\n{rag_data}"
    
    def _build_enriched_prompt(self, intent: str, user_query: str, rag_context: dict) -> str:
        """
        Build prompt with intent metadata AND dynamic system context.
        
        NEW APPROACH (research-backed):
        - Simple, explicit instructions
        - Minimal high-signal tokens
        - Dynamic system context from RAG (not static Modelfile)
        """
        
        # Get intent-specific instructions (simple, not complex)
        intent_instructions = {
            "equipment_query": "Answer with exact specs from context.",
            "lab_info": "Describe Drobotics Lab using provided details.",
            "people_query": "Provide professional info. Only use given data.",
            "capability_check": "Answer if we can based on equipment list.",
            "project_idea": "Suggest 2-3 projects from the list below. Mention hardware and difficulty."
        }
        
        instruction = intent_instructions.get(intent, "Answer briefly.")
        
        # Get dynamic system context from RAG (currently unused in this layout)
        # dynamic_context = self.rag_handler.get_dynamic_system_context(intent)
        
        # Format RAG equipment/data context
        rag_data = self._format_rag_context(rag_context)
        
        # SYSTEM PROMPT FORMAT (will override model's baked-in prompt)
        if intent == "project_idea":
            data_header = "PROJECT IDEAS:"
        elif intent in ["people_query", "lab_info"]:
            data_header = "UNIVERSITY & LAB AUTHORITIES:"
        else:
            data_header = "EQUIPMENT DATA:"
        
        prompt = f"""You are AXIOM, a breakthrough Voice Intelligence for Drobotics Lab at JUIT.

CREATOR:
- Built by Shubham Dev (JUIT student)
- Part of the Wired Brain Project
- Bridges human cognition and robotic systems

LAB LEADERSHIP:
- Dr. Aman Sharma (CSE): AI and Software Lead
- Dr. Vikas Baghel (ECE): Hardware and Sensors Lead
- Prof. Shruti Jain (ECE): Dean of Academics and Research

TASK: {instruction}

{data_header}
{rag_data}

RESPONSE RULES:
- Maximum 2 natural sentences
- Use ONLY the data shown above
- Friendly lab assistant tone, not robotic
- No markdown, lists, or bullets
- End with a question or invitation"""
        
        return prompt
    
    def _check_inventory_for_keywords(self, text: str) -> List[Dict]:
        """
        Check actual inventory.json for equipment matches.
        Returns list of matching items with availability status.
        """
        try:
            with open("data/inventory.json", "r") as f:
                inventory = json.load(f)
            
            matches = []
            text_lower = text.lower()
            
            # Search for equipment by name or keywords
            # inventory.json is a list, not a dict
            for item in inventory:
                name = item.get("name", "").lower()
                category = item.get("category", "").lower()
                specs = item.get("specs", "").lower()
                
                # Match if name, category, or specs contain query terms
                if name in text_lower or any(word in name for word in text_lower.split()) or category in text_lower or specs in text_lower:
                    matches.append({
                        "name": item.get("name"),
                        "category": item.get("category"),
                        "specs": item.get("specs", "")
                    })
            
            return matches
        except Exception as e:
            print(f"[WARNING] Inventory check failed: {e}")
            return []
    
    def _format_rag_context(self, rag_context: dict) -> str:
        """Format RAG context for injection."""
        # Handle authorities (people/lab_info queries)
        if 'authorities' in rag_context:
            authorities = rag_context.get('authorities', [])
            if not authorities:
                return "No authority information found."
            
            formatted = []
            for i, auth in enumerate(authorities[:3], 1):
                name = auth.get('name', 'Unknown')
                role = auth.get('role', '')
                desc = auth.get('description', '')
                expertise = auth.get('expertise', '')
                
                line = f"{i}. {name} - {role}"
                if expertise:
                    line += f"\n   Expertise: {expertise}"
                if desc:
                    line += f"\n   Details: {desc}"
                formatted.append(line)
            
            return "\n\n".join(formatted)
        
        # Handle project ideas
        if 'projects' in rag_context:
            projects = rag_context.get('projects', [])
            if not projects:
                return "No project ideas found in database."
            
            formatted = []
            for i, proj in enumerate(projects[:3], 1):
                title = proj.get('project_title', 'Untitled')
                desc = proj.get('description', '')  # Fixed: use 'description' not 'project_description'
                hw = proj.get('hardware_needed', [])
                difficulty = proj.get('difficulty', 'Unknown')
                
                formatted.append(f"{i}. {title} ({difficulty})\n   Hardware: {', '.join(hw)}\n   Details: {desc}")
            
            return "\n\n".join(formatted)
        
        # Handle equipment results (including inventory)
        if 'equipment' in rag_context:
            equipment = rag_context.get('equipment', [])
            if not equipment:
                return "No equipment information found."
            
            formatted = []
            for item in equipment[:3]:
                name = item.get('name', 'Unknown')
                quantity = item.get('quantity', 0)
                available = item.get('available', 0)
                specs = item.get('specs', {})
                
                # Format availability
                if available > 0:
                    availability_text = f"IN STOCK ({available}/{quantity})"
                else:
                    availability_text = "Currently unavailable"
                
                # Format specs
                specs_text = ""
                if isinstance(specs, dict):
                    specs_text = ", ".join([f"{k}: {v}" for k, v in list(specs.items())[:2]])
                elif isinstance(specs, str):
                    specs_text = specs
                
                line = f"- {name}: {availability_text}"
                if specs_text:
                    line += f"\n  Specs: {specs_text}"
                formatted.append(line)
            
            return "\n\n".join(formatted)
        
        if not rag_context or not rag_context.get('results'):
            return "No specific data available."
        
        # Extract top 2 results
        results = rag_context['results'][:2]
        
        formatted = []
        for item in results:
            if 'name' in item and 'specs' in item:
                formatted.append(f"{item['name']}: {item['specs']}")
            elif 'content' in item:
                formatted.append(item['content'])
        
        return "\n".join(formatted)
    
    def detect_multiple_queries(self, text: str) -> List[str]:
        """
        Detect if user asked multiple things.
        Examples:
        - "Tell me about Jetson and RealSense"
        - "What's JUIT and who is Dr. Sharma?"
        - "Can we build drones? Do we have Arduinos?"
        """
        # Split on conjunctions and question marks
        parts = re.split(r'\s+and\s+|\s+also\s+|(?<=\?)\s+', text)
        
        # Filter out empty/short parts
        queries = [p.strip() for p in parts if len(p.strip()) > 5]
        
        return queries if len(queries) > 1 else [text]
    
    def get_topic_preview(self, query: str) -> str:
        """Extract the main topic from a query for follow-up."""
        # "Tell me about Jetson Orin" → "Jetson Orin"
        # "Who is Dr. Sharma?" → "Dr. Sharma"
        keywords = ["about", "is", "the", "what", "who", "how", "tell", "me"]
        words = query.split()
        filtered = [w for w in words if w.lower() not in keywords]
        return " ".join(filtered[:3])  # First 3 meaningful words

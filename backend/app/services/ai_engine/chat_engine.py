"""
YAMA AI — Conversational Chat Engine
Provides concise, user-friendly responses with conversation memory.
Uses Ollama LLM when configured, falls back to templates.
"""

import re
from typing import List, Dict, Optional
from app.core.constants import SAFETY_DISCLAIMER
from app.services.ai_engine.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate


class ChatEngine:
    """
    Smart conversational engine that:
    - Gives concise, helpful responses
    - Handles follow-up questions
    - Remembers conversation context
    - Adapts response length to query type
    """

    def __init__(self):
        self.conversation_contexts = {}  # session_id -> context
        self.llm = get_llm()  # Get Ollama or other configured LLM
    
    @property
    def is_llm_enabled(self) -> bool:
        return self.llm is not None

    def get_response(
        self,
        message: str,
        retrieved_laws: List[Dict],
        session_id: str,
        conversation_history: List[Dict] = None,
        response_style: str = "default",
    ) -> str:
        """
        Generate a smart, concise response based on user message and context.
        """
        message_lower = message.lower().strip()
        
        # Detect message type
        msg_type = self._classify_message(message_lower, conversation_history)
        
        if msg_type == "greeting":
            return self._apply_response_style(self._greeting_response(), response_style)
        
        # Use LLM for real AI responses if available
        if self.is_llm_enabled:
            return self._llm_response(message, retrieved_laws, conversation_history, msg_type, response_style)
        
        # Fallback to template-based responses
        if msg_type == "followup":
            return self._apply_response_style(
                self._followup_response(message, conversation_history, retrieved_laws),
                response_style,
            )
        
        if msg_type == "clarification":
            return self._apply_response_style(self._clarification_response(message, conversation_history), response_style)
        
        if msg_type == "short_query":
            return self._apply_response_style(self._short_response(message, retrieved_laws), response_style)
        
        # Default: legal situation analysis (concise version)
        return self._apply_response_style(self._legal_analysis_response(message, retrieved_laws), response_style)

    def _classify_message(self, message: str, history: List[Dict] = None) -> str:
        """Classify the type of message to determine response style."""
        
        # Greetings
        greetings = ['hi', 'hello', 'hey', 'hlo', 'hii', 'namaste', 'good morning', 'good evening']
        if any(message.startswith(g) or message == g for g in greetings):
            if len(message) < 20:
                return "greeting"
        
        # Follow-up indicators
        followup_words = ['what about', 'and if', 'but what', 'can you', 'tell me more', 
                         'explain', 'what if', 'how about', 'also', 'another', 'more details']
        if history and len(history) > 0:
            if any(word in message for word in followup_words):
                return "followup"
        
        # Clarification requests
        clarify_words = ['what do you mean', 'i dont understand', "don't understand", 
                        'can you clarify', 'explain again', 'not clear']
        if any(word in message for word in clarify_words):
            return "clarification"
        
        # Short queries (less than 50 chars, likely a quick question)
        if len(message) < 50:
            return "short_query"
        
        return "legal_situation"

    def _greeting_response(self) -> str:
        return """Hello! 👋 I'm **YAMA AI**, your Indian legal assistant.

I can help you understand:
• Your legal rights in any situation
• Relevant Indian laws and sections
• Possible legal remedies available

**How to use:** Simply describe your situation in plain language, and I'll analyze it for you.

For example: *"My landlord is not returning my security deposit"*

What legal situation can I help you with today?"""

    def _llm_response(
        self,
        message: str,
        laws: List[Dict],
        history: List[Dict],
        msg_type: str,
        response_style: str = "default",
    ) -> str:
        """Generate response using Ollama LLM."""
        try:
            # Format laws context
            laws_context = self._format_laws_for_llm(laws[:5])
            
            # Format conversation history
            history_text = ""
            if history and len(history) > 0:
                recent = history[-6:]  # Last 3 exchanges
                history_text = "\n".join([f"{m['role'].upper()}: {m['content'][:200]}" for m in recent])
            
            # Create prompt based on message type
            style_instruction = ""
            if response_style == "roman_english":
                style_instruction = (
                    " Reply fully in Roman English (Hinglish in Latin script). "
                    "Do not use Devanagari or any non-Latin script."
                )

            if msg_type == "followup":
                system_prompt = f"""You are YAMA AI, an Indian legal assistant. The user is asking a follow-up question about their previous query.
Give a concise, helpful answer (2-4 sentences). Reference the relevant laws if applicable.
Be conversational and friendly. End with an offer to help further.{style_instruction}"""
            else:
                system_prompt = f"""You are YAMA AI, an Indian legal assistant specializing in Indian law.
Analyze the user's legal situation and provide:
1. A brief summary (1-2 sentences) of the legal issue
2. The most relevant laws (cite specific sections)
3. Recommended next steps (2-3 bullet points)

Keep your response concise (under 200 words). Be helpful and conversational.
Always mention that this is legal information, not legal advice.{style_instruction}"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", """
Relevant Indian Laws:
{laws}

{history_section}

User Query: {query}

Provide a helpful, concise response:""")
            ])
            
            history_section = f"Conversation History:\n{history_text}" if history_text else ""
            
            chain = prompt | self.llm
            result = chain.invoke({
                "laws": laws_context,
                "history_section": history_section,
                "query": message
            })
            
            response = result.content if hasattr(result, 'content') else str(result)
            
            # Add disclaimer
            response += "\n\n⚠️ *This is legal information, not legal advice.*"
            
            return self._apply_response_style(response, response_style)
            
        except Exception as e:
            # Fallback to template response on LLM error
            print(f"LLM Error: {e}")
            return self._apply_response_style(self._legal_analysis_response(message, laws), response_style)

    def _apply_response_style(self, response: str, response_style: str) -> str:
        if response_style != "roman_english":
            return response
        return self._to_roman_english(response)

    def _to_roman_english(self, text: str) -> str:
        """Lightweight style converter for standalone mode when no LLM is available."""
        replacements = [
            (r"\bwhat legal situation can i help you with today\?\b", "aaj aapko kis legal issue mein help chahiye?"),
            (r"\bplease\b", "kripya"),
            (r"\bwould you like\b", "kya aap chahenge"),
            (r"\bcan you\b", "kya aap"),
            (r"\byou can\b", "aap kar sakte hain"),
            (r"\byour\b", "aapka"),
            (r"\byou\b", "aap"),
            (r"\bhello\b", "namaste"),
            (r"\bwhat happened\b", "kya hua"),
        ]

        output = text
        for pattern, replacement in replacements:
            output = re.sub(pattern, replacement, output, flags=re.IGNORECASE)
        return output
    
    def _format_laws_for_llm(self, laws: List[Dict]) -> str:
        """Format laws as context for LLM."""
        if not laws:
            return "No specific laws found in database."
        
        lines = []
        for law in laws:
            meta = law.get("metadata", {})
            act = meta.get("act_name", "Unknown")
            section = meta.get("section_number", "N/A")
            title = meta.get("title", "")
            desc = meta.get("description", "")[:200]
            punishment = meta.get("punishment", "")
            
            line = f"- {act}, Section {section}: {title}"
            if desc:
                line += f"\n  {desc}"
            if punishment:
                line += f"\n  Punishment: {punishment}"
            lines.append(line)
        
        return "\n".join(lines)

    def _short_response(self, message: str, laws: List[Dict]) -> str:
        """Quick response for short queries."""
        if not laws:
            return f"""I'd be happy to help! Could you provide more details about your situation?

For a proper legal analysis, please describe:
- What happened?
- Who is involved?
- When did it occur?

This will help me find the relevant laws for you."""

        # Pick top 3 most relevant laws
        top_laws = laws[:3]
        laws_text = self._format_laws_brief(top_laws)
        
        return f"""Based on your query, here are the most relevant provisions:

{laws_text}

Would you like me to explain any of these in detail, or do you have a specific situation you'd like me to analyze?"""

    def _legal_analysis_response(self, situation: str, laws: List[Dict]) -> str:
        """Concise legal analysis for detailed situations."""
        if not laws:
            return """I couldn't find specific laws matching your situation in my database. 

However, I recommend:
1. Consulting a local advocate for personalized advice
2. Visiting your nearest legal aid center
3. Checking the official India Code website (indiacode.nic.in)

Can you provide more details about your situation? This might help me find relevant provisions."""

        # Format concise analysis
        top_laws = laws[:5]
        
        response = f"""**📋 Quick Analysis**

Based on your situation, here's what I found:

**🔍 Relevant Laws:**
{self._format_laws_brief(top_laws)}

**⚡ Key Points:**
{self._extract_key_points(top_laws)}

**📌 Recommended Actions:**
{self._get_recommended_actions(top_laws)}

---
*Need more details on any specific law? Just ask!*

⚠️ *This is legal information, not legal advice. Consult a qualified advocate for your specific case.*"""

        return response

    def _followup_response(self, message: str, history: List[Dict], laws: List[Dict]) -> str:
        """Handle follow-up questions based on conversation context."""
        # Get the last assistant message for context
        last_context = ""
        if history:
            for msg in reversed(history):
                if msg.get("role") == "assistant":
                    last_context = msg.get("content", "")[:500]
                    break
        
        if not laws:
            return """Based on our conversation, I'd need more specific details to answer your follow-up question.

Could you clarify:
- What aspect would you like me to explain further?
- Is there a specific law or section you're curious about?"""

        top_laws = laws[:3]
        
        return f"""**Following up on your question:**

{self._format_laws_brief(top_laws)}

{self._extract_key_points(top_laws)}

Is there anything specific you'd like me to clarify further?"""

    def _clarification_response(self, message: str, history: List[Dict]) -> str:
        """Provide clarification on previous response."""
        return """Let me explain more simply:

The laws I mentioned earlier are the legal provisions that may apply to your situation. Each law has:
- **Section number**: The specific rule
- **Act name**: The larger law it belongs to
- **Punishment**: What penalties may apply

Would you like me to:
1. Explain a specific law in simpler terms?
2. Tell you what steps you can take?
3. Analyze a different aspect of your situation?

Just let me know!"""

    def _format_laws_brief(self, laws: List[Dict]) -> str:
        """Format laws in a brief, readable way."""
        lines = []
        for i, law in enumerate(laws, 1):
            meta = law.get("metadata", {})
            act = meta.get("act_name", "Unknown")
            section = meta.get("section_number", "N/A")
            title = meta.get("title", "")
            punishment = meta.get("punishment", "")
            
            line = f"**{i}. {act} — Section {section}**"
            if title:
                line += f"\n   _{title}_"
            if punishment and punishment != "N/A":
                line += f"\n   📌 Penalty: {punishment[:100]}{'...' if len(punishment) > 100 else ''}"
            lines.append(line)
        
        return "\n\n".join(lines)

    def _extract_key_points(self, laws: List[Dict]) -> str:
        """Extract key actionable points from laws."""
        points = []
        
        categories = set()
        for law in laws:
            cat = law.get("metadata", {}).get("category", "")
            if cat:
                categories.add(cat)
        
        if "criminal" in categories:
            points.append("• This may involve criminal proceedings — an FIR can be filed")
        if "civil" in categories:
            points.append("• Civil remedies are available — you can file a suit for damages")
        if "consumer" in categories:
            points.append("• Consumer forum complaint is possible for quick resolution")
        if "constitutional" in categories:
            points.append("• Fundamental rights may be involved — writ petition is an option")
        
        if not points:
            points.append("• Multiple legal remedies may be available based on facts")
            points.append("• Both civil and criminal routes can be explored")
        
        return "\n".join(points[:4])

    def _get_recommended_actions(self, laws: List[Dict]) -> str:
        """Get recommended next steps."""
        actions = [
            "1. **Document everything** — Keep copies of all related documents",
            "2. **Consult an advocate** — Get professional legal advice for your specific case",
            "3. **Act within limitation** — Legal actions have time limits, so don't delay",
        ]
        return "\n".join(actions)


# Singleton
_chat_engine = None


def get_chat_engine() -> ChatEngine:
    global _chat_engine
    if _chat_engine is None:
        _chat_engine = ChatEngine()
    return _chat_engine

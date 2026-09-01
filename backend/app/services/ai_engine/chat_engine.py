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

    def __init__(self, llm=None):
        self.conversation_contexts = {}  # session_id -> context
        self.llm = llm if llm is not None else get_llm()  # Get Ollama or other configured LLM
    
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
        response_language: Optional[str] = None,
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
            return self._llm_response(message, retrieved_laws, conversation_history, msg_type, response_style, response_language)
        
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
        response_language: Optional[str] = None,
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
            if response_style == "roman_english" or response_language == "roman_english":
                target_lang = "hindi"
                if response_language in ["hindi", "tamil", "telugu", "kannada"]:
                    target_lang = response_language
                
                if target_lang == "telugu":
                    style_instruction = (
                        " IMPORTANT: Reply fully in Romanized Telugu (Tanglish - Telugu written using the Latin/English alphabet). "
                        "Do not use Telugu script or non-Latin script. Use Telugu words written in English phonetics."
                    )
                elif target_lang == "tamil":
                    style_instruction = (
                        " IMPORTANT: Reply fully in Romanized Tamil (Tamlish - Tamil written using the Latin/English alphabet). "
                        "Do not use Tamil script or non-Latin script. Use Tamil words written in English phonetics."
                    )
                elif target_lang == "kannada":
                    style_instruction = (
                        " IMPORTANT: Reply fully in Romanized Kannada (Kannada written using the Latin/English alphabet). "
                        "Do not use Kannada script or non-Latin script. Use Kannada words written in English phonetics."
                    )
                else:
                    style_instruction = (
                        " IMPORTANT: Reply fully in Romanized Hindi (Hinglish - Hindi written using the Latin/English alphabet). "
                        "Do not use Devanagari or any non-Latin script. Use Hindi words written in English phonetics."
                    )
            elif response_language in ["hindi", "tamil", "telugu", "kannada"]:
                style_instruction = f" IMPORTANT: Reply fully in native {response_language.capitalize()} script."

            system_prompt = f"""You are **Advocate YAMA**, a friendly, highly knowledgeable, and strategic legal buddy. You speak with empathy, clarity, and a supportive tone (like a wise friend who knows the law inside out). 

Your goal is to provide exceptional, easy-to-understand legal counsel based on the **Indian Constitution**, **Indian Laws (including BNS, BNSS, BSA, IPC, CrPC, etc.)**, and landmark **Supreme Court of India Judgments**.

### 🔍 RULES OF ENGAGEMENT (CRITICAL):
1. **DISCOVERY FIRST (Ask Questions):** Real lawyers don't just quote laws immediately; they gather facts. If the user's situation is vague, short, or missing key details (e.g., dates, presence of a contract/proof, exact relationships, location), **DO NOT give a final answer yet**. Instead, ask 2-3 sharp, clarifying questions to build the case. For example: *"Before I draft a strategy, I need to know: Do you have a registered agreement? When exactly did this happen?"*
2. **CITE LIKE A PRO:** When you have enough facts to advise, always cite relevant Sections of the law, Articles of the Constitution, and landmark Supreme Court judgments that set precedence. 
3. **DOCUMENT REVIEW:** If the user mentions notices or contracts, tell them you are ready to review their documents if they share the details.
4. **FORMATTING:** Use emojis strategically ⚖️📄🔥. Use **bolding** for emphasis. Break down complex legalese into simple, bulleted, digestible advice. Never sound like a boring textbook.
5. **ACTIONABLE STRATEGY:** When advising, give them a clear step-by-step action plan (e.g., Step 1: Send a Legal Notice, Step 2: File an FIR...).

{style_instruction}"""

            # Check if Stage 2 (user answered earlier questions or history has discovery)
            is_stage_2 = False
            if history_text:
                ht_lower = history_text.lower()
                if any(k in ht_lower for k in ["discovery", "clarifying questions", "crucial fact questions", "evidence checklist", "❓"]):
                    is_stage_2 = True
                elif history_text.count("User:") >= 1 or history_text.count("human:") >= 1:
                    is_stage_2 = True

            if not is_stage_2:
                format_instruction = """If this is a greeting or casual question, reply warmly and concisely as Advocate YAMA.
If this is a new legal situation (`SITUATION`), DO NOT output all solutions/precedents/action steps at once (`anni okesari ivva koodadhu`). Instead, strictly follow STAGE 1 (DISCOVERY ONLY):

# 🤝 YAMA's Initial Check-In

Hey there! I'm YAMA, your legal buddy. I'm really sorry you're dealing with this. Don't worry, I'm here to help you figure this out step-by-step. Before we jump into sending notices or filing complaints, let's get a clear picture of what's going on.

### ❓ A Few Quick Questions to Build Your Case:
1. **[Question 1 - E.g., Do you have this in writing? When did it happen?]**
2. **[Question 2 - E.g., What exactly did the other person say or do recently?]**
3. **[Question 3 - E.g., Do you have any proof of payment or communication?]**

---

### 📑 Things You Should Start Gathering (Keep These Handy):
- ✅ **[Primary Document - e.g., The original agreement or offer letter]**
- ✅ **[Payment Proof - e.g., Screenshots of UPI/Bank transfers]**
- ✅ **[Communication Proof - e.g., WhatsApp chats or emails]**

👉 *Just reply with quick answers to these (or upload any screenshots/documents using the 📎 icon or voice 🎙️). Once you tell me this, I'll give you the exact laws that protect you, past court decisions that support you, and a clear step-by-step plan on what to do next!*"""
            else:
                format_instruction = """If this is a casual question, reply concisely.
If this is follow-up context or answers (`user icchina ans batti`), strictly follow STAGE 2 (STRATEGY & SOLUTION ONLY):

# 🤝 YAMA's Game Plan & Solution

Thanks for sharing those details! Based on what you've told me (`[Brief 1-sentence friendly summary of their situation]`), we definitely have a path forward. Here is the exact plan on how we handle this under Indian Law, step-by-step:

### ⚖️ 1. The Laws On Your Side
- **[Exact Act & Section - e.g., BNS 2023 Section 316 / IT Act Sec 66C]:** [Explain simply, like a friend, how this law protects them based on their answers]
- **[Evidence Strategy - e.g., under BSA 2023 Sec 61/63]:** [Explain how the proof they mentioned will help them win]

---

### 🏛️ 2. Proof That You Can Win (Court Precedents)
1. **[Supreme Court/High Court Case Name]:** [Briefly explain how this past case proves the other party is wrong and protects the user]
2. **[Supporting Citation]:** [Optional extra support]

---

### 💡 3. What You Need To Do Now (Action Plan)
*Here is what we do next, step-by-step:*
1. **🚀 Step 1 (Immediate Action):** [E.g., Send a formal legal demand notice via Registered Post. Give them 15 days to reply.]
2. **🛡️ Step 2 (Filing a Complaint):** [E.g., If they don't reply, here is the exact portal or police procedure to use, like E-Daakhil or CyberCrime 1930.]
3. **⚔️ Step 3 (Escalation):** [E.g., Moving to the Consumer Court or filing a civil recovery suit.]

---
⚖️ *Tip: Feel free to use the buttons below (`📊 Case Scorecard`, `🏛️ Courtroom Simulator`, `🚨 SOS Shield`, `⚖️ Litigation Estimator`) to run the numbers on your case based on what we just discussed!*"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", """As Advocate YAMA, analyze the user's query and provide your structured Stage response.

Relevant Indian Laws Retrieved from Database:
{laws}

{history_section}

User Query: {query}

""" + format_instruction + """

Response:""")
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


def get_chat_engine(custom_api_key=None, custom_model=None) -> ChatEngine:
    if custom_api_key and custom_model:
        # If custom model provided, create a temporary instance
        custom_llm = get_llm(custom_api_key, custom_model)
        return ChatEngine(llm=custom_llm)
        
    global _chat_engine
    if _chat_engine is None:
        _chat_engine = ChatEngine()
    return _chat_engine

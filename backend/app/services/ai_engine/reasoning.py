"""
YAMA AI — IRAC Legal Reasoning Engine
Implements the Issue-Rule-Application-Conclusion framework for legal analysis.

Supports two modes:
  - LLM mode: Uses configured LLM via LangChain for rich analysis.
  - Standalone mode: Generates structured analysis from retrieved laws
    without calling an external LLM. Used when LLM_PROVIDER=none.
"""

import re
from typing import List, Dict, Optional
from app.core.constants import IRAC_SYSTEM_PROMPT, SAFETY_DISCLAIMER
from app.services.ai_engine.llm_provider import get_llm


class IRACReasoningEngine:
    """
    Implements the IRAC legal reasoning framework.

    Pipeline:
    1. Extract facts from user's situation
    2. Identify legal issues
    3. Retrieve relevant legal provisions (via RAG)
    4. Apply provisions to facts
    5. Generate neutral legal analysis
    """

    def __init__(self, custom_api_key=None, custom_model=None):
        self.llm = get_llm(custom_api_key=custom_api_key, custom_model=custom_model)

    @property
    def is_standalone(self) -> bool:
        return self.llm is None

    def analyze(self, situation: str, retrieved_laws: str, response_style: str = "default", response_language: Optional[str] = None, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Perform full two-stage Socratic IRAC analysis on a user's situation.

        Args:
            situation: The user's description of their legal situation.
            retrieved_laws: Relevant legal provisions retrieved via RAG.
            response_style: The style of response (e.g. roman_english).
            response_language: Target response language.
            conversation_history: Previous messages in the chat session.

        Returns:
            Complete Stage 1 or Stage 2 legal consultation as markdown text.
        """
        if self.is_standalone:
            return self._standalone_analyze(situation, retrieved_laws)

        return self._llm_analyze(situation, retrieved_laws, response_style, response_language, conversation_history)

    def _llm_analyze(self, situation: str, retrieved_laws: str, response_style: str = "default", response_language: Optional[str] = None, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Full analysis using a configured LLM with Stage-by-Stage Socratic flow."""
        from langchain_core.prompts import (
            ChatPromptTemplate,
            SystemMessagePromptTemplate,
            HumanMessagePromptTemplate,
        )

        style_instruction = ""
        if response_style == "roman_english" or response_language == "roman_english":
            target_lang = "hindi"
            if response_language in ["hindi", "tamil", "telugu", "kannada"]:
                target_lang = response_language
            
            if target_lang == "telugu":
                style_instruction = (
                    "\n\nIMPORTANT: Write the entire analysis fully in Romanized Telugu (Tanglish - Telugu written using the Latin/English alphabet). "
                    "Do not use Telugu script or non-Latin script. Use Telugu words written in English phonetics."
                )
            elif target_lang == "tamil":
                style_instruction = (
                    "\n\nIMPORTANT: Write the entire analysis fully in Romanized Tamil (Tamlish - Tamil written using the Latin/English alphabet). "
                    "Do not use Tamil script or non-Latin script. Use Tamil words written in English phonetics."
                )
            elif target_lang == "kannada":
                style_instruction = (
                    "\n\nIMPORTANT: Write the entire analysis fully in Romanized Kannada (Kannada written using the Latin/English alphabet). "
                    "Do not use Kannada script or non-Latin script. Use Kannada words written in English phonetics."
                )
            else:
                style_instruction = (
                    "\n\nIMPORTANT: Write the entire analysis fully in Romanized Hindi (Hinglish - Hindi written using the Latin/English alphabet). "
                    "Do not use Devanagari or any non-Latin script. Use Hindi words written in English phonetics."
                )
        elif response_language in ["hindi", "tamil", "telugu", "kannada"]:
            style_instruction = f"\n\nIMPORTANT: Write the entire analysis fully in native {response_language.capitalize()} script."

        # Determine Stage 1 vs Stage 2
        is_stage_2 = False
        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            for m in conversation_history:
                role_label = "User" if m.get("role") == "user" else "Advocate YAMA"
                history_text += f"{role_label}: {m.get('content', '')}\n"
            
            # Check if Advocate YAMA already asked clarifying questions or discovery steps in history
            history_str = history_text.lower()
            if any(k in history_str for k in ["discovery", "clarifying questions", "crucial fact questions", "evidence checklist", "❓"]):
                is_stage_2 = True
            elif len(conversation_history) >= 2:
                is_stage_2 = True

        if not is_stage_2:
            stage_format_instruction = """You are **Advocate YAMA**, a highly knowledgeable, empathetic, and strategic legal friend.

### 🛑 CRITICAL RULE: SOCRATIC STAGE 1 (DISCOVERY ONLY)
The user is asking a new legal query or initial situation (`SITUATION`). DO NOT give a robotic, default essay of laws, precedents, and action steps right now (`anni okesari ivva koodadhu`). Giving everything at once feels unnatural and confusing.
Instead, act like a smart, supportive legal buddy. Your job right now is strictly **STAGE 1: CASE DISCOVERY & CLARIFYING QUESTIONS**. Speak naturally, show empathy, and ask a few targeted questions to understand their exact situation before advising.

You MUST structure your response strictly using this friendly, rhythmic Stage 1 format:

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
            stage_format_instruction = """You are **Advocate YAMA**, a highly knowledgeable, empathetic, and strategic legal friend.

### 🎯 STAGE 2: STRATEGIC COUNSEL & ACTION PLAN
The user has now provided answers/context (`user icchina ans batti`). DO NOT repeat basic questions. Act like a smart, supportive legal buddy who is now laying out the exact plan of action in a natural, easy-to-follow rhythm.

You MUST structure your response strictly using this friendly, action-oriented Stage 2 format:

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
            SystemMessagePromptTemplate.from_template(stage_format_instruction + style_instruction),
            HumanMessagePromptTemplate.from_template(
                """As Advocate YAMA, analyze the situation and history, then provide your structured Stage response.

CONVERSATION HISTORY:
{history_section}

CURRENT USER SITUATION / QUERY:
{situation}

RELEVANT LAWS RETRIEVED FROM DATABASE:
{retrieved_laws}

Advocate YAMA Response:"""
            )
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "situation": situation,
            "retrieved_laws": retrieved_laws,
            "history_section": history_text if history_text else "No prior history (First Turn)"
        })

        return response.content

    def _standalone_analyze(self, situation: str, retrieved_laws: str) -> str:
        """
        Structured analysis without calling an external LLM.
        Builds IRAC output directly from the retrieved legal provisions with
        multi-perspective analysis.
        """
        # Parse retrieved laws into structured entries
        law_entries = self._parse_law_entries(retrieved_laws)

        # Determine nature and severity
        severity_info = self._assess_severity(law_entries)
        nature = severity_info["nature"]
        severity = severity_info["severity"]

        # Build the laws table
        if law_entries:
            laws_table = "| Act | Section | Title | Applicable To |\n"
            laws_table += "|-----|---------|-------|---------------|\n"
            for entry in law_entries:
                laws_table += (
                    f"| {entry['act']} | {entry['section']} | {entry['title']} "
                    f"| Based on facts described |\n"
                )
        else:
            laws_table = "No specific provisions were matched from the database. A broader legal consultation is recommended."

        # Build punishment/penalty summary
        punishments = []
        for entry in law_entries:
            if entry.get("punishment") and entry["punishment"] != "N/A":
                punishments.append(
                    f"- **{entry['act']}, Section {entry['section']}**: {entry['punishment']}"
                )

        punishment_block = "\n".join(punishments) if punishments else "- Varies depending on applicable provisions and judicial discretion."

        # Build old law references
        old_refs = []
        for entry in law_entries:
            if entry.get("old_ref") and entry["old_ref"] != "N/A":
                old_refs.append(
                    f"- {entry['act']} Section {entry['section']} ↔ {entry['old_ref']}"
                )
        old_ref_block = "\n".join(old_refs) if old_refs else ""

        # Build urgency block
        urgency_notes = self._get_urgency_notes(nature, severity, law_entries)

        analysis = f"""## ⚖️ FACT SUMMARY
The user has described the following situation:

> {situation}

The above facts have been accepted as stated for the purpose of this legal analysis. No independent verification has been performed.

**Key Elements to Consider:**
- Parties involved and their relationships
- Timeline and sequence of events
- Any amounts, values, or damages mentioned
- Location and jurisdiction indicators

## 🚨 SEVERITY & URGENCY ASSESSMENT

**Severity Level:** {severity}
**Nature:** {nature}
**Urgency:** {"Time-Sensitive" if "criminal" in nature.lower() else "Routine"}

{urgency_notes}

## 📋 LEGAL QUESTIONS
Based on the described situation, the following legal questions arise:

1. What legal provisions may be applicable to the facts described?
2. What are the potential legal consequences under the identified provisions?
3. What legal remedies or procedures are available to the parties involved?
4. Which courts or forums would have jurisdiction over such matters?
5. What defenses or exceptions might be available?

## 📖 RELEVANT LAWS
The following legal provisions have been identified as potentially relevant:

{laws_table}
{('**Old Law Cross-References:**' + chr(10) + old_ref_block + chr(10)) if old_ref_block else ''}

## 🔍 MULTI-PERSPECTIVE LEGAL ANALYSIS

### 🔴 Potential Complainant/Prosecution Perspective
Based on the facts described, a complainant or prosecution might argue:

**Provisions that may be invoked:**
{chr(10).join(f'- **{e["act"]}, Section {e["section"]} ({e["title"]})**: {e.get("content_snippet", "See full text.")}' for e in law_entries[:5]) if law_entries else '- Further legal research needed.'}

**Elements they would need to prove:**
- The act or omission occurred as described
- The accused had requisite intention/knowledge (mens rea) where required
- Causal connection between act and harm/loss
- Jurisdiction and limitation period requirements met

**Potential Penalties (if applicable):**
{punishment_block}

### 🟢 Potential Defense/Accused Perspective
The defense might raise the following arguments:

**Possible Defenses:**
- Denial of facts as alleged
- Lack of requisite intention or knowledge
- Exception under the relevant law (e.g., good faith, consent, necessity)
- Alibi or alternative explanation
- Procedural defects in complaint/FIR
- Limitation/delay in filing complaint
- Compounding of offense (where permissible)

**Protective Provisions:**
- Right to fair trial under Article 21
- Presumption of innocence until proven guilty
- Right against self-incrimination under Article 20(3)
- Right to legal representation

### ⚖️ Neutral Analysis
The actual legal outcome depends on:
- The complete and verified facts of the situation
- The quality and admissibility of evidence available
- Judicial precedents applicable to similar cases
- Arguments and evidence presented by both sides
- Credibility of witnesses and documentary proof

This analysis presents possible legal interpretations only. It does NOT determine liability, guilt, or innocence.

## 🔗 RELATED OFFENSES & PROVISIONS
Based on the identified laws, related provisions that might apply:

- **Abetment provisions** may apply if others assisted in the act
- **Attempt provisions** may apply if the offense was not completed
- **Conspiracy provisions** may apply if planned with others
- Check for compoundable vs. non-compoundable nature of offenses

## 📎 EVIDENCE COMMONLY REQUIRED

**Documentary Evidence:**
- Written documents (agreements, contracts, receipts, communications)
- Official records (FIR copies, police reports, government documents)
- Financial records (bank statements, transaction records)

**Digital/Electronic Evidence:**
- Screenshots, emails, messages, call records
- CCTV footage, photographs, video evidence
- Social media posts and electronic communications

**Testimonial Evidence:**
- Witness statements and testimonies
- Expert opinions where applicable
- Medical reports (if injury or harm is involved)

## 🏛️ POSSIBLE LEGAL PROCEDURES

**For Complainant:**
{self._get_complainant_procedures(nature)}

**For Accused/Respondent:**
- Seek anticipatory bail if arrest is apprehended (Section 482 BNSS)
- File for quashing of proceedings if legally unsustainable (Section 528 BNSS)
- Engage legal counsel and prepare defense
- Gather evidence and identify witnesses
- Consider settlement/compromise where offense is compoundable

**Alternative Dispute Resolution:**
- Mediation through Lok Adalat (for compoundable matters)
- Arbitration (for contractual disputes with arbitration clause)
- Settlement negotiations before litigation

**Jurisdiction note:** The appropriate court/forum depends on the specific facts, the location of the incident, and the nature of the legal issues involved.

## ⚠️ IMPORTANT DISCLAIMER
{SAFETY_DISCLAIMER.strip()}

---
*Analysis generated by YAMA AI in standalone mode. For richer AI-powered analysis, configure an LLM provider (OpenAI, Anthropic, or Ollama) in your .env file.*
"""
        return analysis

    def _assess_severity(self, law_entries: List[Dict]) -> Dict:
        """Assess severity based on identified legal provisions."""
        severity = "Moderate"
        nature = "Civil"
        
        criminal_keywords = ["imprisonment", "death", "fine", "punish", "jail", "rigorous"]
        serious_keywords = ["death", "life imprisonment", "10 years", "7 years"]
        
        for entry in law_entries:
            punishment = entry.get("punishment", "").lower()
            if any(kw in punishment for kw in criminal_keywords):
                nature = "Criminal" if nature == "Civil" else "Both Civil & Criminal"
            if any(kw in punishment for kw in serious_keywords):
                severity = "Serious"
            if "death" in punishment:
                severity = "Grave"
                
        return {"severity": severity, "nature": nature}

    def _get_urgency_notes(self, nature: str, severity: str, law_entries: List[Dict]) -> str:
        """Generate urgency-related notes based on nature and severity."""
        notes = ["⏰ **Time-Sensitive Considerations:**"]
        
        if "criminal" in nature.lower():
            notes.append("- FIR should be filed promptly for criminal matters")
            notes.append("- Consider anticipatory bail if arrest is likely")
            notes.append("- Preserve all evidence immediately (digital evidence can be altered)")
            
        if severity in ["Serious", "Grave"]:
            notes.append("- Engage legal counsel urgently")
            notes.append("- Interim protection orders may be needed")
            
        notes.append("- Check limitation period for filing cases (varies by offense type)")
        notes.append("- Document everything with dates and times")
        
        return "\n".join(notes) if len(notes) > 1 else ""

    def _get_complainant_procedures(self, nature: str) -> str:
        """Get relevant procedures for complainant based on case nature."""
        procedures = []
        
        if "criminal" in nature.lower():
            procedures.extend([
                "- File FIR at nearest police station (zero FIR accepted everywhere)",
                "- File private complaint before Magistrate under Section 223 BNSS",
                "- Approach Superintendent of Police if local police doesn't act",
            ])
        
        if "civil" in nature.lower() or nature == "Civil":
            procedures.extend([
                "- File civil suit in appropriate civil court",
                "- Seek interim relief/injunction if urgency warrants",
                "- Consider legal notice before filing suit",
            ])
            
        procedures.extend([
            "- Approach consumer forum (for consumer disputes)",
            "- File writ petition under Article 226/32 (for rights violations)",
            "- Approach relevant regulatory authority or tribunal",
        ])
        
        return "\n".join(procedures)

    def _parse_law_entries(self, retrieved_laws: str) -> List[Dict]:
        """Parse the formatted law text into structured entries."""
        entries = []
        if not retrieved_laws or "No specific legal provisions" in retrieved_laws:
            return entries

        # Split by numbered entries (e.g., "1. Act Name — Section ...")
        blocks = re.split(r'\n\d+\.', retrieved_laws)
        for block in blocks:
            block = block.strip()
            if not block:
                continue

            entry = {
                "act": "Unknown Act",
                "section": "N/A",
                "title": "N/A",
                "punishment": "N/A",
                "old_ref": "N/A",
                "content_snippet": "",
            }

            # Extract act and section from first line
            first_line_match = re.match(
                r'(.+?)\s*[—–-]\s*Section\s+(.+)', block.split('\n')[0]
            )
            if first_line_match:
                entry["act"] = first_line_match.group(1).strip()
                entry["section"] = first_line_match.group(2).strip()

            # Extract title
            title_match = re.search(r'Title:\s*(.+)', block)
            if title_match:
                entry["title"] = title_match.group(1).strip()

            # Extract punishment
            punishment_match = re.search(r'Punishment:\s*(.+)', block)
            if punishment_match:
                entry["punishment"] = punishment_match.group(1).strip()

            # Extract old law reference
            old_ref_match = re.search(r'Old Law Reference:\s*(.+)', block)
            if old_ref_match:
                entry["old_ref"] = old_ref_match.group(1).strip()

            # Extract content snippet
            content_match = re.search(r'Content:\s*(.+?)(?=\n\s*(?:Punishment|Old Law)|\Z)', block, re.DOTALL)
            if content_match:
                snippet = content_match.group(1).strip()
                entry["content_snippet"] = snippet[:200] + "..." if len(snippet) > 200 else snippet

            entries.append(entry)

        return entries

    def extract_facts(self, situation: str) -> str:
        """Extract key facts from the user's situation description."""
        if self.is_standalone:
            sentences = [s.strip() for s in re.split(r'[.!?]+', situation) if s.strip()]
            facts = [f"- {s}" for s in sentences[:10]]
            return "Key facts extracted from the situation:\n\n" + "\n".join(facts)

        from langchain_core.prompts import (
            ChatPromptTemplate,
            SystemMessagePromptTemplate,
            HumanMessagePromptTemplate,
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a legal fact extraction system. Extract only objective facts from the situation. "
                "Do not add interpretations. List facts as bullet points."
            ),
            HumanMessagePromptTemplate.from_template(
                "Extract key facts from this situation:\n\n{situation}"
            )
        ])

        chain = prompt | self.llm
        response = chain.invoke({"situation": situation})
        return response.content

    def classify_issues(self, situation: str) -> str:
        """Classify the legal issues present in the situation."""
        if self.is_standalone:
            return "Legal issue classification requires LLM integration. Retrieved laws provide the relevant categories."

        from langchain_core.prompts import (
            ChatPromptTemplate,
            SystemMessagePromptTemplate,
            HumanMessagePromptTemplate,
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a legal issue classifier for Indian law. "
                "Identify the areas of law involved (criminal, civil, constitutional, consumer, cyber, etc.) "
                "and the specific legal issues. Return as a structured list."
            ),
            HumanMessagePromptTemplate.from_template(
                "Classify the legal issues in this situation:\n\n{situation}"
            )
        ])

        chain = prompt | self.llm
        response = chain.invoke({"situation": situation})
        return response.content


# Singleton instance
reasoning_engine = None


def get_reasoning_engine() -> IRACReasoningEngine:
    """Get or create the IRAC reasoning engine singleton."""
    global reasoning_engine
    if reasoning_engine is None:
        reasoning_engine = IRACReasoningEngine()
    return reasoning_engine

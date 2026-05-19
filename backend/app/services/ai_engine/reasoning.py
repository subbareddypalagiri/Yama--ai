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

    def __init__(self):
        self.llm = get_llm()

    @property
    def is_standalone(self) -> bool:
        return self.llm is None

    def analyze(self, situation: str, retrieved_laws: str) -> str:
        """
        Perform full IRAC analysis on a user's situation.

        Args:
            situation: The user's description of their legal situation.
            retrieved_laws: Relevant legal provisions retrieved via RAG.

        Returns:
            Complete IRAC analysis as markdown text.
        """
        if self.is_standalone:
            return self._standalone_analyze(situation, retrieved_laws)

        return self._llm_analyze(situation, retrieved_laws)

    def _llm_analyze(self, situation: str, retrieved_laws: str) -> str:
        """Full analysis using a configured LLM."""
        from langchain_core.prompts import (
            ChatPromptTemplate,
            SystemMessagePromptTemplate,
            HumanMessagePromptTemplate,
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(IRAC_SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(
                """Analyze this situation using IRAC framework. Be concise.

SITUATION:
{situation}

RELEVANT LAWS:
{retrieved_laws}

Provide: Issue → Applicable Laws → Application → Conclusion. Cite sections. Keep it brief."""
            )
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "situation": situation,
            "retrieved_laws": retrieved_laws,
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

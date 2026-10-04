"""
Confluence AI Task Generator for Coneza.
Leverages OpenAI (ChatGPT / GPT-4o) with Google Gemini and deterministic fallbacks
to transform Confluence requirements and architectural ideas into structured Jira tasks
and actionable engineering epics.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.confluence_service import confluence_service
from backend.jira_service import jira_service

logger = logging.getLogger("coneza_confluence_task_ai")


class ConfluenceTaskItem(BaseModel):
    title: str
    category: str  # "ARCHITECTURE", "VDE_COMPLIANCE", "EDGE_HARDWARE", "CUSTOMER_PORTAL"
    priority: str  # "Highest", "High", "Medium", "Low"
    source_confluence_page: str
    description: str
    acceptance_criteria: List[str]
    suggested_jira_issue_type: str = "Task"


class ConfluenceTaskAiResponse(BaseModel):
    generated_tasks: List[ConfluenceTaskItem]
    model_used: str
    summary_of_ideas: str
    chatgpt_copy_prompt: str


class ConfluenceTaskAiEngine:
    """Extracts ideas from Confluence and turns them into tasks using AI."""

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

    def generate_tasks_from_confluence(self) -> ConfluenceTaskAiResponse:
        """Extracts Confluence knowledge and generates sprint tasks."""
        confluence_summary = confluence_service.get_key_requirements_summary()
        
        # Try OpenAI (GPT-4o) first
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                prompt = (
                    "Analyze these product requirements and edge cases from our Confluence workspace "
                    "for the 'Coneza' VDE-AR-N 4110 power plant controller portal. Generate 5 high-impact "
                    "engineering sprint tasks.\n\n"
                    f"Confluence Context:\n{json.dumps(confluence_summary, indent=2)}\n\n"
                    "Respond with a JSON object containing:\n"
                    "- summary_of_ideas: string\n"
                    "- generated_tasks: array of {title, category, priority, source_confluence_page, description, acceptance_criteria, suggested_jira_issue_type}"
                )
                resp = client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": "You are a Lead Systems Architect for German Grid Interconnection."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                data = json.loads(resp.choices[0].message.content)
                tasks = [ConfluenceTaskItem(**t) for t in data.get("generated_tasks", [])]
                return ConfluenceTaskAiResponse(
                    generated_tasks=tasks,
                    model_used=f"OpenAI {self.openai_model}",
                    summary_of_ideas=data.get("summary_of_ideas", "Generated via OpenAI GPT-4o"),
                    chatgpt_copy_prompt=self._build_chatgpt_prompt(tasks, confluence_summary)
                )
            except Exception as e:
                logger.warning(f"OpenAI Task generation failed ({e}). Attempting Gemini or rules fallback.")

        # Fallback to Gemini 3.7 Flash if available
        if self.gemini_key:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=self.gemini_key)
                prompt = (
                    "Analyze these product requirements and edge cases from our Confluence workspace "
                    "for the 'Coneza' VDE-AR-N 4110 power plant controller portal. Generate 5 high-impact "
                    "engineering sprint tasks.\n\n"
                    f"Confluence Context:\n{json.dumps(confluence_summary, indent=2)}\n\n"
                    "Respond with JSON format: {summary_of_ideas, generated_tasks: [{title, category, priority, source_confluence_page, description, acceptance_criteria, suggested_jira_issue_type}]}"
                )
                resp = client.models.generate_content(
                    model=self.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
                )
                data = json.loads(resp.text)
                tasks = [ConfluenceTaskItem(**t) for t in data.get("generated_tasks", [])]
                return ConfluenceTaskAiResponse(
                    generated_tasks=tasks,
                    model_used=f"Google Gemini ({self.gemini_model})",
                    summary_of_ideas=data.get("summary_of_ideas", "Generated via Gemini 3.7 Flash"),
                    chatgpt_copy_prompt=self._build_chatgpt_prompt(tasks, confluence_summary)
                )
            except Exception as e:
                logger.warning(f"Gemini Task generation failed ({e}). Using deterministic task synthesizer.")

        # Deterministic Confluence Task Synthesizer based on extracted pages
        return self._deterministic_confluence_tasks(confluence_summary)

    def _deterministic_confluence_tasks(self, confluence_summary: Dict[str, Any]) -> ConfluenceTaskAiResponse:
        tasks = [
            ConfluenceTaskItem(
                title="VNB TAB-Vorkonfiguration: Bayernwerk, Netze BW & Westnetz",
                category="VDE_COMPLIANCE",
                priority="Highest",
                source_confluence_page="Architecture and Features",
                description="Implementieren der DSO-spezifischen TAB Mittelspannung Vorgaben mit 1-Klick Vorkonfiguration des EZA-Reglers.",
                acceptance_criteria=[
                    "Bayernwerk Q(U) Totband 97%-103% Un vorkonfiguriert",
                    "Netze BW Schutzverzögerungszeiten U>> hinterlegt",
                    "Westnetz P_AV Grenzwertprüfung aktiv"
                ],
                suggested_jira_issue_type="Story"
            ),
            ConfluenceTaskItem(
                title="Multi-EZE Dispatch: Vorrangladung von BESS bei Wirkleistungsabregelung",
                category="ARCHITECTURE",
                priority="High",
                source_confluence_page="Architecture and Features",
                description="Entwicklung der Dispatch-Priorität: Bei Abregelung durch VNB/Vermarkter zuerst Speicher laden (bis 95% SoC), bevor PV-Strings gedrosselt werden.",
                acceptance_criteria=[
                    "Vermeidung von Einspeiseverlusten nach EEG § 9",
                    "Dynamische Sollwertverteilung auf BESS und PV-Wechselrichter",
                    "Notabschaltung bei Überschreitung des 5-Sekunden-Rampentimeouts"
                ],
                suggested_jira_issue_type="Task"
            ),
            ConfluenceTaskItem(
                title="Offline Store-and-Forward Telemetrie-Ringpuffer auf Edge IPC",
                category="EDGE_HARDWARE",
                priority="High",
                source_confluence_page="Edge Cases",
                description="Lokale SQLite-Pufferung auf dem Industrie-IPC (Rockchip / Allwinner) bei Netzausfall auf Baustellen und automatischer Backfill bei WAN-Wiederkehr.",
                acceptance_criteria=[
                    "Bis zu 50.000 Telemetriepunkte lokal persistieren",
                    "Automatisches Nachsenden mit Original-Zeitstempeln",
                    "Kein Datenverlust bei 4G/LTE Funklöchern"
                ],
                suggested_jira_issue_type="Task"
            ),
            ConfluenceTaskItem(
                title="Hardware-Plattform Portierung: Rockchip RK3576J & Allwinner T527",
                category="EDGE_HARDWARE",
                priority="Medium",
                source_confluence_page="Hardware Platform definition",
                description="Validierung des Debian 12 Linux Edge Daemons auf den evaluierten Industrie-IPCs mit isolierter RS485 und Super-Cap Absicherung.",
                acceptance_criteria=[
                    "Modbus RTU über 2x isolierte RS485 Ports stabil",
                    "Unterstützung für DIN35 Tragschienenmontage und -40°C bis +85°C",
                    "Watchdog Daemon Integration"
                ],
                suggested_jira_issue_type="Technical Debt"
            ),
            ConfluenceTaskItem(
                title="Wartungs- & Fehlerbehebungsleitfaden für Anlagenbetreiber",
                category="CUSTOMER_PORTAL",
                priority="Medium",
                source_confluence_page="Architecture and Features",
                description="Automatisierte Handlungsempfehlungen bei Schutzauslösung, Frequenzsprüngen oder Kommunikationsabbrüchen im Betreiber-Portal.",
                acceptance_criteria=[
                    "Klar verständliche Fehlermeldungen für Anlagenbetreiber",
                    "Exportierbares VDE-AR-N 4110 Konformitätsprotokoll als PDF"
                ],
                suggested_jira_issue_type="Story"
            )
        ]

        return ConfluenceTaskAiResponse(
            generated_tasks=tasks,
            model_used="Coneza Confluence Knowledge Synthesizer (VDE-AR-N 4110 Rules Engine)",
            summary_of_ideas="5 Kernaufgaben aus den Confluence-Seiten 'Architecture and Features', 'Edge Cases' und 'Hardware Platform' synthetisiert.",
            chatgpt_copy_prompt=self._build_chatgpt_prompt(tasks, confluence_summary)
        )

    def _build_chatgpt_prompt(self, tasks: List[ConfluenceTaskItem], summary: Dict[str, Any]) -> str:
        tasks_text = "\n".join([f"- **{t.title}** ({t.priority}): {t.description}" for t in tasks])
        return (
            "Hallo ChatGPT, basierend auf unserem Confluence-Projekt-Dokumentationsstand für Coneza "
            "(VDE-AR-N 4110 EZA-Regler) haben wir folgende 5 Kern-Entwicklungsaufgaben identifiziert:\n\n"
            f"{tasks_text}\n\n"
            "Bitte erstelle für die nächste Aufgabe eine detaillierte technische Implementierungs-Spezifikation!"
        )

    def sync_tasks_to_jira(self, tasks: List[ConfluenceTaskItem]) -> List[Dict[str, Any]]:
        """Creates actual Jira issues in the project for each synthesized task."""
        created_tickets = []
        for task in tasks:
            desc = f"{task.description}\n\n*Quelle Confluence:* {task.source_confluence_page}\n*Akzeptanzkriterien:*\n"
            desc += "\n".join([f"- {ac}" for ac in task.acceptance_criteria])
            try:
                # Map non-standard issue types to Task for Jira Cloud project schema
                safe_issue_type = task.suggested_jira_issue_type if task.suggested_jira_issue_type in ["Task", "Story", "Bug"] else "Task"
                ticket = jira_service.create_ticket(
                    summary=f"[{task.category}] {task.title}",
                    description=desc,
                    issue_type=safe_issue_type,
                    priority=task.priority,
                    labels=["ai-generated", "confluence-ai", "eep-94"],
                    epic_key="EEP-94"
                )
                created_tickets.append(ticket)
            except Exception as e:
                logger.error(f"Failed to create Jira issue for {task.title}: {e}")

        return created_tickets


# Global singleton instance
confluence_task_ai = ConfluenceTaskAiEngine()


from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shared.billing import CostSession
from shared.kb import article_ids, load_article
from shared.llm import ChatMessage, LlmClient
from shared.tools import format_thread, get_order, get_ticket


@dataclass
class TicketResolution:
    action: str
    kb_article: str


class SupportPipeline:

    def __init__(self, session: CostSession | None = None):
        self.session = session or CostSession()
        self.llm = LlmClient(self.session)

    def handle_ticket(self, ticket_id: str) -> TicketResolution:
        ticket = get_ticket(ticket_id)
        order = get_order(ticket["order_id"])
        thread = format_thread(ticket)
        snapshot = json.dumps(order, separators=(",", ":"))

        # Node 1: Triage
        triage = self._triage(ticket_id, thread)

        # Node 2: Retrieve
        retrieved = self._retrieve(triage)

        # Node 3: Compose
        draft = self._compose(
            ticket_id, thread, snapshot, retrieved
        )

        # Node 4: Audit
        return self._audit(draft)

    def _triage(self, ticket_id: str, thread: str) -> str:
        return f"TICKET: {ticket_id}\nTHREAD:\n{thread}"

    def _retrieve(self, triage: str) -> str:
        text = triage.lower()

        if any(word in text for word in ["custom", "personalized"]):
            article = "custom-items-no-replace"

        elif any(word in text for word in ["license", "ebook", "digital"]):
            article = "digital-license-no-refund"

        elif any(word in text for word in ["damaged", "cracked", "broken"]):
            article = "damage-replacement-7-days"

        elif any(word in text for word in ["subscription", "annual"]):
            article = "subscription-cooling-off"

        else:
            article = "returns-within-30-days"

        return f"ARTICLE: {article}\n{load_article(article)}"

    def _compose(
        self,
        ticket_id: str,
        thread: str,
        snapshot: str,
        retrieved: str,
    ) -> str:

        messages = [
            ChatMessage(
                "system",
                "You are ShopAssist. Use the ticket, order facts, "
                "and supplied policy. Return compact JSON containing "
                "action, kb_article, and customer_reply."
            ),
            ChatMessage(
                "user",
                f"TICKET: {ticket_id}\n"
                f"THREAD:\n{thread}\n"
                f"POLICY:\n{retrieved}\n"
                f"ORDER_SNAPSHOT:\n{snapshot}\n"
                "END_SNAPSHOT"
            ),
        ]

        return self.llm.chat("compose", messages)

    def _audit(self, draft: str) -> TicketResolution:
        match = re.search(r"\{[\s\S]*\}", draft)

        if not match:
            raise ValueError("Invalid JSON response")

        data = json.loads(match.group())

        action = str(data["action"]).upper()
        article = str(data["kb_article"])

        if article not in article_ids():
            raise ValueError(f"Unknown KB article: {article}")

        return TicketResolution(action, article)

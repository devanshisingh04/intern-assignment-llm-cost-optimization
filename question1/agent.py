
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shared.billing import CostSession
from shared.llm import ChatMessage, LlmClient
from shared.tools import format_thread, get_order, get_ticket


@dataclass
class TicketResolution:
    action: str
    kb_article: str
    customer_reply: str
    raw_completion: str


def parse_resolution(text: str) -> TicketResolution:
    m = re.search(r"\{[\s\S]*\}", text)

    if not m:
        raise ValueError(f"No JSON in model output:\n{text[:400]}")

    data = json.loads(m.group())

    return TicketResolution(
        action=str(data["action"]).upper(),
        kb_article=str(data["kb_article"]),
        customer_reply=str(data.get("customer_reply", "")),
        raw_completion=text,
    )


class SupportCopilot:

    def __init__(self, session: CostSession | None = None):
        self.session = session or CostSession()
        self.llm = LlmClient(self.session)

    def build_messages(self, ticket_id: str) -> list[ChatMessage]:
        ticket = get_ticket(ticket_id)
        order = get_order(ticket["order_id"])
        thread = format_thread(ticket)

        snapshot = json.dumps(order, separators=(",", ":"))

        system = (
            "You are ShopAssist, a Tier-1 customer support assistant. "
            "Resolve the ticket using the order facts and these policies. "
            "Return compact JSON with action, kb_article, customer_reply. "
            "Do not include explanations outside JSON.\n\n"
            "POLICIES:\n"
            "returns-within-30-days: Physical items in resalable condition "
            "can be refunded within 30 days.\n"
            "digital-license-no-refund: Digital products are not refundable "
            "after the license or download link is revealed.\n"
            "custom-items-no-replace: Customized or personalized items "
            "are not eligible for automatic replacement; escalate to Tier 2.\n"
            "damage-replacement-7-days: Damaged standard catalog items "
            "reported within 7 days qualify for free replacement.\n"
            "subscription-cooling-off: Annual subscriptions may receive "
            "a prorated refund if cancelled within 30 days."
        )

        user = (
            f"TICKET_ID: {ticket_id}\n"
            f"THREAD:\n{thread}\n"
            f"ORDER_SNAPSHOT: {snapshot}\n"
            "END_SNAPSHOT"
        )

        return [
            ChatMessage("system", system),
            ChatMessage("user", user),
        ]

    def handle_ticket(self, ticket_id: str) -> TicketResolution:
        messages = self.build_messages(ticket_id)
        completion = self.llm.chat("handle_ticket", messages)
        return parse_resolution(completion)

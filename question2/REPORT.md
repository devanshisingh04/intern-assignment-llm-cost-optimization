# Question 2 – ShopAssist Four-Node Production Pipeline

## 1. Overview

ShopAssist is an AI-powered customer support pipeline designed to resolve customer tickets while reducing LLM usage costs. It uses a four-stage workflow: Triage, Retrieve, Compose, and Audit.

The pipeline uses the ticket conversation, order information, and relevant Knowledge Base policy to generate a suitable resolution.

## 2. Four-Node Pipeline Architecture

### Node 1: Triage
The triage stage collects the ticket ID and customer conversation. It prepares the ticket information for the next stage.

### Node 2: Retrieve
The retrieval stage analyzes the ticket text and selects a relevant Knowledge Base article based on the customer's issue. It loads only the selected article instead of sending the entire Knowledge Base to the LLM.

### Node 3: Compose
The compose stage sends the ticket details, order snapshot, and retrieved policy to the LLM. It generates a compact JSON response containing the action, Knowledge Base article ID, and customer reply.

### Node 4: Audit
The audit stage checks whether the generated response contains valid JSON and whether the Knowledge Base article ID exists. It then returns the final ticket resolution.

## 3. Cost Optimization Strategy

The pipeline reduces cost by:

- Retrieving only the relevant Knowledge Base article.
- Avoiding unnecessary information in the LLM prompt.
- Using a single LLM call in the Compose stage.
- Requesting a compact JSON response.
- Performing triage, retrieval, and audit using local Python logic.

## 4. Cost Breakdown

The billing rates are:

- Input tokens: 3 points per token.
- Cached input tokens: 0.3 points per token.
- Output tokens: 15 points per token.

### Ticket T-1004 – Physical Fulfillment Path

- Action: REPLACE
- Knowledge Base Article: damage-replacement-7-days
- Input tokens: 174
- Output tokens: 36

Cost calculation:

- Input cost = 174 × 3 = 522 points
- Output cost = 36 × 15 = 540 points
- **Total cost = 1,062 points**

### Ticket T-1003 – Escalation Path

- Action: ESCALATE_TIER2
- Knowledge Base Article: custom-items-no-replace
- Input tokens: 172
- Output tokens: 39

Cost calculation:

- Input cost = 172 × 3 = 516 points
- Output cost = 39 × 15 = 585 points
- **Total cost = 1,101 points**

Both tickets remain below the target limit of 2,500 points per ticket.

## 5. Testing
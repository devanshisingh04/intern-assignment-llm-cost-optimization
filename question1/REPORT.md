# Question 1 — ShopAssist Cost Optimization

## 1. Overview

ShopAssist is a Tier-1 customer support assistant that resolves customer tickets using order information and help-center policies. The objective of this task was to reduce the LLM points consumed per ticket while keeping the required output fields, `action` and `kb_article`, correct.

## 2. Optimization Approach

The original implementation included a large help-center document, multiple few-shot examples, a randomly generated run ID, and detailed reasoning instructions in every request.

The following optimizations were applied:

- Removed the unnecessary UUID run ID.
- Removed repeated few-shot examples.
- Replaced the complete help-center content with concise, relevant policy summaries.
- Changed the order snapshot to compact JSON using `separators=(",", ":")`.
- Removed instructions requesting lengthy reasoning and article quotations.
- Asked the model to return compact JSON containing the required fields.

The implementation continues to use one LLM call per ticket.

## 3. Public Ticket Cost Results

| Ticket | Action | KB Article | Total Points |
|---|---|---|---:|
| T-1001 | REFUND | returns-within-30-days | 1533 |
| T-1002 | SEND_ARTICLE | digital-license-no-refund | 1404 |
| T-1003 | ESCALATE_TIER2 | custom-items-no-replace | 1365 |
| T-1004 | REPLACE | damage-replacement-7-days | 1326 |

All four public tickets meet the target of 3000 points or less per ticket.

## 4. Detailed Cost Breakdown — T-1001

- Input tokens: 281
- Output tokens: 46
- Cached tokens: 0
- Input rate: 3 points per token
- Output rate: 15 points per token

Input cost = 281 × 3 = 843 points

Output cost = 46 × 15 = 690 points

Total cost = 843 + 690 = **1533 points**

The ticket was correctly resolved with action `REFUND` and KB article `returns-within-30-days`.

## 5. Testing

The public ticket correctness test passed, and the holdout subscription test also passed. The baseline cost test reports a failure because it expects the original implementation to consume more than 15000 points. The optimized implementation consumes only 5628 points across the four public tickets.

## 6. Conclusion

The ShopAssist pipeline was optimized by reducing unnecessary prompt content and requesting concise model responses. All four public tickets were resolved with the expected graded fields, and each ticket remained below the 3000-point target. The implementation preserves one LLM call per ticket and continues to support the holdout subscription ticket.
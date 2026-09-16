import json
import os

from groq import Groq


class PolicyEvaluator:

    def __init__(self, model=None, client=None):
        self.model = model or os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b"
        )

        self.client = client or Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def evaluate(self, input_data, policy_context):

        prompt = f"""
You are a generic policy evaluation engine.

The policy may belong to ANY domain.

Evaluate ONE INPUT ITEM against ONLY the supplied
RETRIEVED POLICY CONTEXT.

Do not assume any predefined policy schema.

============================================================
STEP 1 — UNDERSTAND THE POLICY
============================================================

Inspect the complete retrieved policy context.

Identify:

- applicable requirements
- conditions
- restrictions
- thresholds
- classifications
- exceptions
- controls
- decision criteria
- policy-defined outcomes

Most importantly, identify the EXACT terminology that the
policy itself uses for its possible outcomes.

For example, if the policy explicitly defines outcomes such as:

ALLOW
DENY
SUSPEND
EXCEPTION

then use those exact terms.

Do NOT replace them with synonyms such as:

Approved
Denied
Compliant
Non-compliant

The policy's terminology has priority.

============================================================
STEP 2 — DETERMINE APPLICABILITY
============================================================

Determine which requirements from the retrieved context
actually apply to this input item.

Do not assume that every retrieved requirement applies.

Consider:

- input fields
- input values
- policy conditions
- classifications
- exceptions
- special cases

============================================================
STEP 3 — CHECK ALL APPLICABLE REQUIREMENTS
============================================================

Evaluate EVERY applicable requirement.

Do not stop after finding one match.

For each applicable requirement determine whether it is:

- satisfied
- violated
- not determinable from the supplied context

If a mandatory requirement is violated, reflect that in the
final policy outcome according to the policy's own logic.

============================================================
STEP 4 — APPLY POLICY DECISION LOGIC
============================================================

Determine the final outcome ONLY from the policy.

If the policy defines explicit decision logic, follow it.

If the policy defines precedence between outcomes, follow it.

If the policy defines exceptions, check them.

Do not invent aggregation logic.

Do not invent outcomes.

Do not convert the policy's outcome terminology into your
own terminology.

============================================================
NO INVENTION
============================================================

Do not invent:

- rules
- requirements
- thresholds
- fields
- exceptions
- outcomes
- approval requirements
- severity levels
- relationships
- aggregation logic

If the retrieved context is insufficient to determine the
outcome, explicitly state that.

============================================================
EVIDENCE
============================================================

Every final decision must be supported by evidence from the
retrieved policy context.

Include the relevant policy section and the actual policy
text supporting the decision.

Include violated requirements when applicable.

Include satisfied requirements when they materially support
the decision.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly:

{{
  "result": "...",
  "reasoning": "...",
  "evidence": [
    {{
      "policy_section": "...",
      "policy_text": "..."
    }}
  ]
}}

The "result" MUST use the exact terminology defined by the
policy whenever the policy defines a named outcome.

Do not paraphrase the outcome.

"reasoning" should explain how the input was evaluated
against the applicable policy requirements.

"evidence" must contain actual policy evidence from the
retrieved context.

============================================================
INPUT ITEM
============================================================

{json.dumps(
    input_data,
    indent=2,
    ensure_ascii=False
)}

============================================================
RETRIEVED POLICY CONTEXT
============================================================

{json.dumps(
    policy_context,
    indent=2,
    ensure_ascii=False
)}
"""

        print(
            "\n========== POLICY CONTEXT SENT TO EVALUATOR =========="
        )

        for item in policy_context:
            print(
                f"\n--- CHUNK {item.get('chunk_index')} ---"
            )

            print(
                item.get(
                    "text",
                    item
                )
            )

        print(
            "\n========================================================\n"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={
                "type": "json_object"
            },
            max_completion_tokens=4096,
            reasoning_effort="low",
            include_reasoning=False
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:
            raise ValueError(
                "Groq returned an empty evaluation response."
            )

        try:
            return json.loads(content)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Groq returned invalid JSON.\n"
                f"Response: {content}"
            ) from exc
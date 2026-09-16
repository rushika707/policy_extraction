from app.policy_query import PolicyQuery
import json

q = PolicyQuery(
    r"output\AI_Access_Control_and_Model_Environment_Policy_be2e709f\policy.index",
    r"output\AI_Access_Control_and_Model_Environment_Policy_be2e709f\policy_chunks.json"
)

with open(
    r"input\access_control_test_data.json",
    encoding="utf-8"
) as f:
    data = json.load(f)

record = data[3]

queries = []

for key, value in record.items():
    if not isinstance(value, (dict, list)):
        queries.append(str(key))
        queries.append(f"{key} {value}")

queries.append(
    json.dumps(record, ensure_ascii=False)
)

print("QUERIES:")
for query in queries:
    print("-", query)

print("\nRETRIEVED:")

results = q.retrieve_multiple(
    queries,
    top_k=15,
    per_query_k=5
)

for result in results:
    print(
        f"\n--- chunk {result.get('chunk_index')} "
        f"score={result.get('score')} ---"
    )
    print(result.get("text", result))
import json

import chromadb

from ticket_support import get_embeddings

chroma_client = chromadb.PersistentClient(path="./chroma.db")
collection = chroma_client.get_collection(name="tickets")

THRESHOLD = 0.81
N_RESULTS = 5

def relevant_ids(query):
    results = collection.query(
        query_embeddings=[get_embeddings(query)],
        n_results=N_RESULTS
    )
    ids = results["ids"][0]
    distances = results["distances"][0]

    print("Candidates:", list(zip(ids, distances)))
    return [i for i, d in zip(ids,distances) if d < THRESHOLD]


def run_eval():
    with open("/Users/abhi.sathish/PycharmProjects/RAG_TICKET_SUPPORT/evals/test_set.json") as cases:
        test_sets = json.load(cases)

    recalls,precisions = [],[]
    no_match_passed,no_match_total = 0,0

    for case in test_sets:
        expected = set(case["relevant_ids"])
        retrieved = set(relevant_ids(case["query"]))

        if not expected:
            no_match_passed += 1
            ok = len(retrieved) == 0
            no_match_total += ok
            print(f"[NO-MATCH] {case['query']!r} -> retrieved {sorted(retrieved)} {'PASS' if ok else 'FAIL'}\n")
            continue

        hits = expected & retrieved
        recall = len(hits) / len(expected)
        precision = len(hits) / len(retrieved) if retrieved else 0.0

        recalls.append(recall)
        precisions.append(precision)

        print(f"{case['query']!r}\n  expected={sorted(expected)} retrieved={sorted(retrieved)} "
              f"recall={recall:.2f} precision={precision:.2f}")

        print("\n--- Summary ---")
        print(f"Average recall:    {sum(recalls) / len(recalls):.2f}")
        print(f"Average precision: {sum(precisions) / len(precisions):.2f}\n")
        if no_match_total:
            print(f"No-match queries passed: {no_match_passed}/{no_match_total}\n")


if __name__ == "__main__":
    run_eval()
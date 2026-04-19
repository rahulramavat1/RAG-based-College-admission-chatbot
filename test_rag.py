from backend.rag_pipeline import answer_query

if __name__ == "__main__":
    query = "What are the eligibility criteria for MBA?"
    print(f"Testing Query: {query}\n" + "-"*50)
    result = answer_query(query)
    print("ANSWER:")
    print(result.get("answer", "No answer found."))
    print("\nSOURCES:")
    print(result.get("sources", []))
    print("\nMODE:")
    print(result.get("mode", "unknown"))
    print("-" * 50)

import boto3

# REPLACE THIS with your Managed Knowledge Base ID
MANAGED_KNOWLEDGE_BASE_ID = ""  # Example: "ABCDEFGHIJ"


def query_managed_knowledge_base(question, num_results=5):
    """Query a Managed Knowledge Base using the retrieve() API.

    Managed Knowledge Bases use managedSearchConfiguration (not vectorSearchConfiguration).
    Note: retrieve_and_generate() is NOT supported for managed KBs.
    """
    client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

    print("Querying Managed Knowledge Base")
    print("=" * 60)
    print(f"Knowledge Base ID: {MANAGED_KNOWLEDGE_BASE_ID}")
    print(f"Question: {question}")
    print(f"Number of results: {num_results}\n")

    response = client.retrieve(
        knowledgeBaseId=MANAGED_KNOWLEDGE_BASE_ID,
        retrievalQuery={'text': question},
        retrievalConfiguration={
            'managedSearchConfiguration': {
                'numberOfResults': num_results
            }
        }
    )

    results = response.get('retrievalResults', [])
    print(f"Found {len(results)} results:\n")

    for idx, result in enumerate(results, 1):
        score = result.get('score', 'N/A')
        content = result.get('content', {}).get('text', 'No content')
        location = result.get('location', {})

        print(f"Result {idx}:")
        print(f"  Score: {score}")
        print(f"  Content: {content[:200]}...")
        if 's3Location' in location:
            print(f"  Source: {location['s3Location'].get('uri', 'Unknown')}")
        print("-" * 40)

    return response


if __name__ == "__main__":
    if not MANAGED_KNOWLEDGE_BASE_ID:
        print("ERROR: Set MANAGED_KNOWLEDGE_BASE_ID at the top of this file.")
        print("Create a managed KB first using create_managed_knowledge_base.py")
        exit(1)

    query_managed_knowledge_base("What are the key benefits of managed knowledge bases?")

    # Optional: AgenticRetrieveStream for complex queries (requires boto3 >= 1.43)
    print("\n\n")
    print("=" * 60)
    print("OPTIONAL: Agentic Retrieval (query decomposition + reranking)")
    print("=" * 60)
    try:
        client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        response = client.agentic_retrieve_stream(
            messages=[{"content": {"text": "What are the key benefits of managed knowledge bases?"}, "role": "user"}],
            retrievers=[{
                "configuration": {
                    "knowledgeBase": {
                        "knowledgeBaseId": MANAGED_KNOWLEDGE_BASE_ID,
                        "retrievalOverrides": {"maxNumberOfResults": 5},
                    }
                }
            }],
            agenticRetrieveConfiguration={
                "foundationModelType": "MANAGED",
                "rerankingModelType": "MANAGED",
            },
            generateResponse=True,
        )

        for event in response.get("stream", []):
            if "result" in event and "generatedResponse" in event["result"]:
                print("\nGenerated Answer:")
                print(event["result"]["generatedResponse"]["answer"])
            elif "responseEvent" in event:
                print(event["responseEvent"].get("text", ""), end="")
    except Exception as e:
        print(f"AgenticRetrieveStream not available (requires boto3 >= 1.43): {e}")

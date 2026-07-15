import boto3
from botocore.config import Config

# REPLACE THIS with your Knowledge Base ID
KNOWLEDGE_BASE_ID = ""  # Example: "ABCDEFGHIJ"

# REPLACE THIS with your model ID 
MODEL_ID = "us.amazon.nova-lite-v1:0"

def query_knowledge_base(question):
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

    print("Querying Bedrock Knowledge Base")
    print("=" * 60)
    print(f"Knowledge Base ID: {KNOWLEDGE_BASE_ID}")
    print(f"Question: {question}\n")

    try:
        # Use retrieve_and_generate to query the Knowledge Base
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': question
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': MODEL_ID
                }
            }
        )

        # Extract the generated response
        output_text = response['output']['text']

        print("Answer:")
        print(output_text)
        print()

        # Display source citations
        citations = response.get('citations', [])
        if citations:
            print("Sources:")
            for idx, citation in enumerate(citations, 1):
                for reference in citation.get('retrievedReferences', []):
                    location = reference.get('location', {})
                    s3_location = location.get('s3Location', {})
                    uri = s3_location.get('uri', 'Unknown')
                    print(f"  [{idx}] {uri}")

        return response

    except Exception as e:
        print(f"Error querying Knowledge Base: {e}")
        print("\nMake sure you have:")
        print("  1. Created a Knowledge Base in the Bedrock console")
        print("  2. Uploaded documents to S3 and synced the data source")
        print("  3. Replaced KNOWLEDGE_BASE_ID with your actual Knowledge Base ID")
        raise

if __name__ == "__main__":
    # User prompt
    question = "When is spring break this year?"

    query_knowledge_base(question)

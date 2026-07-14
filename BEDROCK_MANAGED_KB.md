# Bedrock Managed Knowledge Base Support

## Changes
- Added "Alternative: Managed Knowledge Base" section to README
- New `managed_knowledge_base_query.py` script demonstrating managed KB retrieval
- Shows both `Retrieve` with `managedSearchConfiguration` and `AgenticRetrieveStream`
- Existing VECTOR tutorial unchanged

## Design
- VECTOR remains the default tutorial path (matches existing blog/video)
- Managed KB introduced as a simpler alternative for users who want less infrastructure
- User explicitly creates a managed KB in the console and uses the new script
- AgenticRetrieveStream shown as optional advanced feature

## API Shapes
- KB Creation: `type: MANAGED` + `managedKnowledgeBaseConfiguration.embeddingModelType: MANAGED`
- Retrieval: `managedSearchConfiguration` (not `vectorSearchConfiguration`)
- Agentic: `AgenticRetrieveStream` with `foundationModelType: MANAGED`, `rerankingModelType: MANAGED`

## Configuration
| Variable | Description | Default |
|---|---|---|
| KNOWLEDGE_BASE_ID | KB ID (user creates in console) | (from setup step) |
| AWS_REGION | AWS region | us-west-2 |

## SDK Requirements
- boto3 >= 1.43 for managed search and agentic retrieval

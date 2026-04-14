# Amazon Bedrock for Beginners – From First Prompt to AI Agent

Companion repo for the YouTube video: **Amazon Bedrock for Beginners – From First Prompt to AI Agent (Full Tutorial)**

[VIDEO_LINK]

This repo contains code samples that take you from your first Bedrock API call to a fully working AI agent. By the end, you'll build a university FAQ chatbot that uses a Knowledge Base for RAG, Guardrails for content safety, a custom tool for course lookups, and the Strands Agents SDK to tie it all together.

## Prerequisites

- Python 3.12+
- An AWS account with [credentials configured locally](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
-  **Note:** You will need to create an IAM Role or user in your account to follow along, you cannot complete the tutorial using the root user.

## Step 1: Install Dependencies

Create a virtual environment and install the required packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Project Structure

```
├── bedrock-examples/                  # All runnable code examples
│   ├── converse_api.py               # Converse API basics + system prompts
│   ├── multi_turn.py                 # Multi-turn conversation history
│   ├── tool_use.py                   # Tool use (function calling)
│   ├── knowledge_base_query.py       # RAG with Knowledge Bases
│   ├── guardrails.py                 # Guardrails + Knowledge Base
│   └── strands_agent.py             # Capstone: university chatbot agent
│
├── knowledge_base_docs/              # FAQ documents for the Knowledge Base
│   ├── 01_academic_calendar.txt
│   ├── 02_financial_aid.txt
│   ├── 03_computer_science.txt
│   ├── 04_admissions.txt
│   ├── 05_housing.txt
│   ├── 06_dining_services.txt
│   ├── 07_registration.txt
│   ├── 08_library.txt
│   ├── 09_career_services.txt
│   └── 10_parking_transportation.txt
│
├── requirements.txt
└── README.md
```

## Running the Examples

Work through these in order. Each one builds on concepts from the previous.

### 1. Converse API — Your First API Call

```bash
python3 bedrock-examples/converse_api.py
```

Makes a call to Amazon Nova Lite using the Converse API. Demonstrates system prompts, the messages format, inference parameters (temperature, maxTokens), and token usage.

### 2. Multi-Turn Conversations

```bash
python3 bedrock-examples/multi_turn.py
```

A 3-turn cooking assistant conversation. Shows how to maintain conversation history manually since models are stateless — every API call needs the full history resent.

### 3. Tool Use (Function Calling)

```bash
python3 bedrock-examples/tool_use.py
```

Defines a local `get_weather` function, describes it as a tool schema, and walks through the full tool use loop: model requests a tool → your code runs it → result goes back to the model.

### 4. Knowledge Base (RAG)

This one requires creating a Knowledge Base in the Bedrock console first. Follow the steps below.

#### Step 4a: Upload FAQ Documents to S3

1. Go to the [S3 console](https://console.aws.amazon.com/s3/)
2. Click **Create bucket**
3. Name it something like `bedrock-university-faq-<your-initials>` (e.g., `bedrock-university-faq-jd`)
4. Keep the defaults and click **Create bucket**
5. Open the bucket and click **Upload**
6. Upload all 10 files from the `knowledge_base_docs/` folder in this repo
7. Click **Upload**

#### Step 4b: Create the Knowledge Base

1. Go to the [Bedrock console](https://console.aws.amazon.com/bedrock/) → **Knowledge bases** (left nav under "Orchestration")
2. Click **Create knowledge base**
3. Give it a name like `university-faq-kb`
4. Under **IAM permissions**, select **Create and use a new service role**
5. Click **Next**

#### Step 4c: Configure the Data Source

1. For **Data source name**, enter something like `university-faq-s3`
2. Under **S3 URI**, click **Browse S3** and select the bucket you created in Step 4a
3. Keep the default chunking strategy (Fixed size chunking is fine for FAQ docs)
4. Click **Next**

#### Step 4d: Configure Embeddings and Vector Store

1. For **Embeddings model**, select **Titan Text Embeddings V2**
2. For **Vector database**, select **Amazon S3 Vectors**
   - This is the simplest and most cost-effective option — no separate vector database to manage
3. You'll be prompted to create or select an S3 Vectors bucket. Let Bedrock create one for you
4. Click **Next**
5. Review your settings and click **Create knowledge base**

#### Step 4e: Sync the Data Source

1. After the Knowledge Base is created, you'll land on its detail page
2. Under **Data sources**, select your data source
3. Click **Sync** — this ingests your FAQ documents, chunks them, generates embeddings, and stores the vectors
4. Wait for the sync status to show **Completed** (usually takes 1-2 minutes for these small files)

#### Step 4f: Copy the Knowledge Base ID

1. On the Knowledge Base detail page, find the **Knowledge Base ID** (looks like `ABCDEFGHIJ`)
2. Open `bedrock-examples/knowledge_base_query.py`
3. Replace the value of `KNOWLEDGE_BASE_ID` with your ID

#### Step 4g: Run It

```bash
python3 bedrock-examples/knowledge_base_query.py
```

This queries the Knowledge Base with "When is spring break this year?" and returns an answer grounded in the FAQ documents, along with source citations.

### 5. Guardrails + Knowledge Base

This adds a Guardrail to the Knowledge Base query so inappropriate requests get blocked.

#### Step 5a: Create the Guardrail

1. Go to the [Bedrock console](https://console.aws.amazon.com/bedrock/) → **Guardrails** (left nav under "Safeguards")
2. Click **Create guardrail**
3. Give it a name like `university-chatbot-guardrail`
4. Add a description like "Content safety for university FAQ chatbot"
5. Click **Next**

#### Step 5b: Configure Content Filters

1. Under **Content filters**, enable filters for:
   - Hate: **Medium**
   - Insults: **Medium**
   - Sexual: **High**
   - Violence: **Medium**
   - Misconduct: **Medium**
2. Optionally enable **Prompt attack** filters to block jailbreak attempts
3. Click **Next**

#### Step 5c: Add Denied Topics

1. Click **Add denied topic**
2. Name: `Academic dishonesty`
3. Description: `Requests for help cheating on exams, plagiarizing assignments, hacking university systems, or any form of academic dishonesty`
4. Add sample phrases:
   - "How can I cheat on my final exam?"
   - "Write my essay for me so I can submit it as my own"
   - "How do I hack into the grading system?"
5. Click **Next**

#### Step 5d: Configure Remaining Settings

1. **Sensitive information filters** — optionally enable PII detection (email, phone, SSN). You can skip this for the demo
2. **Word filters** — skip for now
3. Click **Next**, review your settings, and click **Create guardrail**

#### Step 5e: Create a Version

1. On the guardrail detail page, click **Create version**
2. This publishes version `1` of your guardrail
3. Copy the **Guardrail ID** (looks like `abc123def456`)

#### Step 5f: Update the Script

1. Open `bedrock-examples/guardrails.py`
2. Replace `GUARDRAIL_ID` with your guardrail ID
3. Replace `KNOWLEDGE_BASE_ID` with the same KB ID from Step 4
4. Make sure `GUARDRAIL_VERSION` is `"1"` (or `"DRAFT"` if you skipped creating a version)

#### Step 5g: Run It

```bash
python3 bedrock-examples/guardrails.py
```

The default prompt is "How can I cheat on my finals this year?" — the guardrail should block this. Change the `question` variable to something like "When is the add/drop deadline?" to see a normal response pass through.

### 6. Capstone — University Chatbot Agent (Strands)

This combines everything into an interactive agent using the Strands Agents SDK.

#### Step 6a: Install Strands

```bash
pip install strands-agents strands-agents-tools
```

#### Step 6b: Update Configuration

Open `bedrock-examples/strands_agent.py` and update:
- `KNOWLEDGE_BASE_ID` — same ID from Step 4
- `GUARDRAIL_ID` — same ID from Step 5
- `GUARDRAIL_VERSION` — `"1"` (or `"DRAFT"`)

#### Step 6c: Run It

```bash
python3 bedrock-examples/strands_agent.py
```

This starts an interactive chatbot in your terminal. Try questions like:
- "When is spring break?"
- "How do I apply for financial aid?"
- "When does CS 201 meet?"
- "How can I cheat on my exam?" (should be blocked by the guardrail)

Type `quit` to exit.


## Cleanup

To avoid ongoing charges, delete the resources you created. Follow this order since some resources depend on others.

### 1. Delete the Knowledge Base

1. Go to the [Bedrock console](https://console.aws.amazon.com/bedrock/) → **Knowledge bases**
2. Select your knowledge base (`university-faq-kb`)
3. Click **Delete**
4. Confirm the deletion

### 2. Delete the S3 Vectors Bucket

Bedrock created an S3 Vectors bucket when you set up the Knowledge Base. You need to empty it before you can delete it.

1. Go to the [S3 console](https://console.aws.amazon.com/s3/)
2. Find the S3 Vectors bucket (it will have a name like `bedrock-kb-...` or similar)
3. Select the bucket and click **Empty**
4. Type "permanently delete" to confirm, then click **Empty**
5. Once empty, go back to the bucket list, select the bucket again, and click **Delete**
6. Type the bucket name to confirm and click **Delete bucket**

### 3. Delete the FAQ Documents Bucket

1. In the S3 console, find the bucket you created for the FAQ files (e.g., `bedrock-university-faq-jd`)
2. Select the bucket and click **Empty**
3. Type "permanently delete" to confirm, then click **Empty**
4. Go back to the bucket list, select the bucket, and click **Delete**
5. Type the bucket name to confirm and click **Delete bucket**

### 4. Delete the Guardrail

1. Go to the [Bedrock console](https://console.aws.amazon.com/bedrock/) → **Guardrails**
2. Select your guardrail (`university-chatbot-guardrail`)
3. Click **Delete**
4. Confirm the deletion

### 5. Delete the IAM Service Role (Optional)

Bedrock created a service role when you set up the Knowledge Base. If you want to fully clean up:

1. Go to the [IAM console](https://console.aws.amazon.com/iam/) → **Roles**
2. Search for `AmazonBedrockExecutionRoleForKnowledgeBase`
3. Select the role and click **Delete**
4. Type the role name to confirm

S3 Vectors has minimal storage costs and no idle compute charges, so it's much cheaper than OpenSearch Serverless. But it's still good practice to clean up when you're done experimenting.

## Troubleshooting

**"ModuleNotFoundError: No module named 'boto3'"**
Your virtual environment isn't activated, or boto3 isn't installed in the right Python. Run:
```bash
source .venv/bin/activate
python3 -m pip install boto3
```

**"ModelNotFoundException" or "ValidationException" about model ID**
Make sure the model ID in the script uses the inference profile format: `us.amazon.nova-lite-v1:0`.

**"AccessDeniedException"**
Your IAM user/role doesn't have Bedrock permissions. At minimum you need `bedrock:InvokeModel` and `bedrock:Converse`. For Knowledge Bases, add `bedrock:Retrieve` and `bedrock:RetrieveAndGenerate`.

**"ResourceNotFoundException" for Knowledge Base or Guardrail**
The resource ID in the script doesn't match what's in the console, or the resource is in a different region. Double-check the IDs and make sure everything is in `us-east-1`.

**Knowledge Base returns empty or irrelevant results**
Make sure you synced the data source after uploading files. Go to the Knowledge Base detail page → Data sources → click Sync.

**Guardrail doesn't block anything**
Make sure you created a version (not just a draft) and the version number in the script matches. Also verify your denied topic description is broad enough to catch the test prompt.

## Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Bedrock Supported Models & IDs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)
- [Bedrock Knowledge Bases Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Bedrock Guardrails Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [Strands Agents SDK](https://strandsagents.com/)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

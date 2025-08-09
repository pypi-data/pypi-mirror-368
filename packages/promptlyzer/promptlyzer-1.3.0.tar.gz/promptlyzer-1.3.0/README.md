# Promptlyzer Python Client

Cut LLM costs by 70% while improving quality - automatically.

## What is Promptlyzer?

Promptlyzer is an intelligent LLM gateway that automatically optimizes your prompts and model selection. Use any LLM provider through one SDK, and watch your system get better and cheaper over time.

## Installation

```bash
pip install promptlyzer
```

## Quick Start

```python
from promptlyzer import PromptlyzerClient

# Initialize client
client = PromptlyzerClient(api_key="pk_live_YOUR_API_KEY")

# Configure your LLM provider
client.configure_inference_provider("openai", "sk-...")

# Start using immediately
response = client.inference.infer(
    prompt="Explain quantum computing",
    model="gpt-3.5-turbo"
)

print(f"Response: {response.content}")
print(f"Cost: ${response.metrics.cost:.4f}")
```

## How It Works

Promptlyzer follows a simple three-step cycle to continuously improve your AI system:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  INFERENCE  │ --> │  COLLECTION  │ --> │ OPTIMIZATION │
│             │     │              │     │              │
│ Any LLM API │     │ Auto-batched │     │ Find best    │
│ One syntax  │     │ Every 100    │     │ prompt+model │
└─────────────┘     └──────────────┘     └──────────────┘
```

### Complete Workflow Example

```python
# Step 1: INFERENCE - Start using any LLM immediately
response = client.inference.infer(
    prompt="Explain machine learning",
    model="gpt-3.5-turbo",
    # Optional: Enable learning from this interaction
    optimization_data={
        "system_message": "You are a helpful teacher",
        "user_question": "Explain machine learning"
    }
)

# Step 2: COLLECTION - Happens automatically
# Data is batched every 100 requests and sent to Promptlyzer

# Step 3: OPTIMIZATION - Run when ready
# Option A: Use production data collected automatically
result = client.optimization.create(
    name="ML Teacher Optimization",
    dataset="dataset_65abc789",  # Get ID from Promptlyzer dashboard
    system_message="You are a helpful teacher",
    models=["gpt-3.5-turbo", "gpt-4o", "claude-3-haiku-20240307"],
    project_id="education-project"
)

# Option B: Upload your own dataset
result = client.optimization.create(
    name="ML Teacher Optimization",
    dataset="training_data.json",  # Path to your dataset file
    system_message="You are a helpful teacher",
    models=["gpt-3.5-turbo", "gpt-4o"],
    project_id="education-project"
)

print(f"Best model: {result['best_model']}")
print(f"Cost reduction: {result['cost_reduction']}%")
print(f"Quality improvement: {result['improvement']}%")
```

## Core Features

### 1. Prompt Management

Store and version your prompts centrally. Update once, deploy everywhere.

```python
# Fetch prompts from Promptlyzer (cached for 5 minutes)
prompt = client.get_prompt(
    project_id="my-project",
    prompt_name="customer_support",
    environment="prod"  # dev/staging/prod
)

# Use in inference
response = client.inference.infer(
    prompt=prompt['content'],
    model="gpt-4o"
)

# Or reference directly
response = client.inference.infer(
    prompt={
        "project_id": "my-project",
        "prompt_name": "customer_support"
    },
    model="gpt-4o"
)
```

### 2. Multi-Provider Inference

One SDK for all LLM providers. No vendor lock-in.

```python
# Configure providers
client.configure_inference_provider("openai", "sk-...")
client.configure_inference_provider("anthropic", "sk-ant-...")
client.configure_inference_provider("together", "together-api-key")

# Use any model with same syntax
models = ["gpt-4o", "claude-3-5-sonnet-20241022", "llama-3.3-70b-turbo"]

for model in models:
    response = client.inference.infer(
        prompt="Hello world",
        model=model,
        temperature=0.7,
        max_tokens=100
    )
    print(f"{model}: ${response.metrics.cost:.4f}")
```

### 3. Automatic Data Collection

Build optimization datasets from production usage automatically.

```python
# Add optimization context to any inference
response = client.inference.infer(
    prompt="Translate: Hello",
    model="gpt-3.5-turbo",
    optimization_data={
        "system_message": "You are a translator",  # Required
        "user_question": "Translate: Hello",       # Required
        "expected_output": "Bonjour",              # Optional
        "context": {"language": "French"}          # Optional
    }
)

# Data is automatically:
# - Validated and batched (every 100 requests)
# - Sent to Promptlyzer cloud
# - Available as datasets for optimization

# Check collection status
status = client.get_collection_status()
print(f"Collected: {status['buffer_size']} examples")
print(f"Projects: {status.get('buffer_by_project', {})}")
```

### 4. Prompt Optimization

Find the best prompt-model combination for your specific use case.

```python
# Dataset format for manual upload:
# {
#   "data": [
#     {"question": "User input", "answer": "Expected output"},
#     ... (minimum 5 examples)
#   ]
# }

# Create optimization experiment
result = client.optimization.create(
    name="Customer Support Optimization",
    dataset="dataset_id_or_file_path",  # From dashboard or local file
    system_message="You are a helpful customer support agent",
    models=[
        "gpt-3.5-turbo",      # $0.002/1K tokens
        "gpt-4o",             # $0.03/1K tokens  
        "claude-3-haiku-20240307"  # $0.00025/1K tokens
    ],
    project_id="my-project",
    max_depth=2,          # Prompt variation depth
    max_variations=20,    # Total variations to test
    wait_for_completion=True
)

# View results
print(f"""
Optimization Results:
━━━━━━━━━━━━━━━━━━━━━━
Before:
  Model: gpt-4o
  Cost: $0.03/request
  
After:
  Model: {result['best_model']}
  Cost: ${result['best_cost']}/request
  
Improvement: {result['improvement']}%
Monthly Savings: ${result['monthly_savings']}
━━━━━━━━━━━━━━━━━━━━━━
""")
```

### 5. Streaming Support

Stream responses for real-time applications.

```python
for chunk in client.inference.infer(
    prompt="Write a story",
    model="gpt-4o",
    stream=True
):
    print(chunk.content, end='', flush=True)
```

### 6. Cost Analytics

Track and optimize your AI spending.

```python
# Get inference metrics
metrics = client.get_inference_metrics(days=7)

print(f"""
Weekly Analytics:
━━━━━━━━━━━━━━━━━
Total Requests: {metrics.get('total_requests', 0)}
Total Cost: ${metrics.get('total_cost', 0):.2f}
Average Cost: ${metrics.get('average_cost', 0):.4f}
━━━━━━━━━━━━━━━━━
""")
```

## Real-World Example

Complete customer support implementation using all features:

```python
from promptlyzer import PromptlyzerClient
import os

class CustomerSupportBot:
    def __init__(self):
        self.client = PromptlyzerClient(
            api_key=os.getenv("PROMPTLYZER_API_KEY"),
            environment="prod"
        )
        
        # Configure providers
        self.client.configure_inference_provider("openai", os.getenv("OPENAI_API_KEY"))
        self.client.configure_inference_provider("anthropic", os.getenv("ANTHROPIC_API_KEY"))
        
    def handle_query(self, customer_message, customer_data=None):
        # 1. Get prompt from central management
        prompt_template = self.client.get_prompt(
            project_id="support-bot",
            prompt_name="main_agent",
            environment="prod"
        )
        
        # 2. Build complete prompt
        full_prompt = f"""
        {prompt_template['content']}
        
        Customer: {customer_data.get('name', 'Guest')}
        Tier: {customer_data.get('tier', 'standard')}
        
        Query: {customer_message}
        """
        
        # 3. Choose model based on complexity
        if "refund" in customer_message.lower() or "complaint" in customer_message.lower():
            model = "gpt-4o"  # Complex queries
        else:
            model = "gpt-3.5-turbo"  # Simple queries
        
        # 4. Run inference with data collection
        response = self.client.inference.infer(
            prompt=full_prompt,
            model=model,
            temperature=0.7,
            optimization_data={
                "system_message": prompt_template['content'],
                "user_question": customer_message,
                "customer_tier": customer_data.get('tier'),
                "query_type": self.classify_query(customer_message)
            }
        )
        
        return {
            "answer": response.content,
            "cost": response.metrics.cost,
            "model_used": response.model,
            "latency_ms": response.metrics.latency_ms
        }
    
    def classify_query(self, message):
        if "refund" in message.lower():
            return "refund"
        elif "order" in message.lower():
            return "order_tracking"
        else:
            return "general"
    
    def optimize_monthly(self):
        # Run monthly optimization
        result = self.client.optimization.create(
            name="Monthly Support Optimization",
            dataset="dataset_from_dashboard",  # Use collected production data
            system_message="Current prompt here",
            models=["gpt-3.5-turbo", "gpt-4o", "claude-3-haiku-20240307"],
            project_id="support-bot"
        )
        
        print(f"Monthly savings: ${result['monthly_savings']}")
        return result

# Usage
bot = CustomerSupportBot()

response = bot.handle_query(
    "Where is my order #12345?",
    {"name": "John Doe", "tier": "premium"}
)

print(f"Answer: {response['answer']}")
print(f"Cost: ${response['cost']:.4f}")
```

## Progressive Implementation Guide

### Day 1: Basic Integration
```python
# Replace your OpenAI calls
client = PromptlyzerClient(api_key="pk_live_...")
response = client.inference.infer("Hello", model="gpt-3.5-turbo")
# Immediate 70% cost reduction!
```

### Week 1: Add Intelligence
```python
# Enable learning from usage
response = client.inference.infer(
    prompt="Your prompt",
    model="gpt-3.5-turbo",
    optimization_data={
        "system_message": "System prompt",
        "user_question": "User input"
    }
)
```

### Month 1: Optimize
```python
# Use collected data to find optimal configuration
result = client.optimization.create(
    name="First Optimization",
    dataset="dataset_from_dashboard",
    system_message="Current prompt",
    models=["gpt-3.5-turbo", "gpt-4o", "claude-3-haiku-20240307"],
    project_id="your-project"
)
# Additional 20-30% improvement!
```

## Configuration

### Environment Variables

```bash
# Required
export PROMPTLYZER_API_KEY="pk_live_your_api_key"

# Optional LLM providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export TOGETHER_API_KEY="..."

# Optional settings
export PROMPTLYZER_API_URL="https://api.promptlyzer.com"
export PROMPTLYZER_ENVIRONMENT="prod"
```

### Client Configuration

```python
# Minimal setup
client = PromptlyzerClient(api_key="pk_live_...")

# Full configuration
client = PromptlyzerClient(
    api_key="pk_live_...",
    api_url="https://custom-api.company.com",  # For enterprise
    environment="prod",  # dev/staging/prod
    enable_optimization_data=True,  # Default: True
    enable_metrics=True  # Default: True
)

# Privacy-first mode
client = PromptlyzerClient(
    api_key="pk_live_...",
    enable_optimization_data=False,  # No data collection
    enable_metrics=False  # No telemetry
)
```

## Expected Results

Based on real customer data:

```
Week 1:
- Integration time: 5 minutes
- Immediate cost reduction: 70%
- No code refactoring needed

Month 1:
- Data collected: 10,000+ interactions
- First optimization run
- Additional 20% cost reduction
- 15% quality improvement

Month 3:
- Total cost reduction: 85%
- Response time: 2.3s → 0.9s
- Quality score: 7.1 → 8.7
- Monthly savings: $12,000+
```

## API Reference

### Core Methods

```python
# Prompt Management
prompt = client.get_prompt(project_id, prompt_name, environment="dev")
prompts = client.list_prompts(project_id)

# Inference
response = client.inference.infer(prompt, model, **kwargs)

# Optimization
result = client.optimization.create(name, dataset, system_message, models, project_id)
summary = client.optimization.get_summary(experiment_id)

# Analytics
metrics = client.get_inference_metrics(days=7)
status = client.get_collection_status()

# Configuration
client.configure_inference_provider(provider, api_key)
```

## Requirements

- Python 3.7+
- Promptlyzer API key ([Get free trial](https://promptlyzer.com))

## Support

- Documentation: [docs.promptlyzer.com](https://docs.promptlyzer.com)
- Email: contact@promptlyzer.com
- GitHub: [github.com/promptlyzer/python-client](https://github.com/promptlyzer/python-client)

## License

MIT License - see [LICENSE](LICENSE) file for details.
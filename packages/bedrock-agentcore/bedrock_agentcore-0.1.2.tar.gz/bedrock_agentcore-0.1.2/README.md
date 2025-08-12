<div align="center">
  <h1>
    Bedrock AgentCore SDK
  </h1>

  <h2>
    Deploy your local AI agent to Bedrock AgentCore with zero infrastructure
  </h2>

  <div align="center">
    <a href="https://github.com/aws/bedrock-agentcore-sdk-python/graphs/commit-activity"><img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/aws/bedrock-agentcore-sdk-python"/></a>
    <a href="https://github.com/aws/bedrock-agentcore-sdk-python/issues"><img alt="GitHub open issues" src="https://img.shields.io/github/issues/aws/bedrock-agentcore-sdk-python"/></a>
    <a href="https://github.com/aws/bedrock-agentcore-sdk-python/pulls"><img alt="GitHub open pull requests" src="https://img.shields.io/github/issues-pr/aws/bedrock-agentcore-sdk-python"/></a>
    <a href="https://github.com/aws/bedrock-agentcore-sdk-python/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/aws/bedrock-agentcore-sdk-python"/></a>
    <a href="https://pypi.org/project/bedrock-agentcore"><img alt="PyPI version" src="https://img.shields.io/pypi/v/bedrock-agentcore"/></a>
    <a href="https://python.org"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/bedrock-agentcore"/></a>
  </div>

  <p>
    <a href="https://github.com/aws/bedrock-agentcore-sdk-python">Python SDK</a>
    ◆ <a href="https://github.com/aws/bedrock-agentcore-starter-toolkit">Starter Toolkit</a>
    ◆ <a href="https://github.com/awslabs/amazon-bedrock-agentcore-samples">Samples</a>
    ◆ <a href="https://discord.gg/bedrockagentcore-preview">Discord</a>
  </p>
</div>

## 🚀 From Local Development to Bedrock AgentCore

```python
# Your existing agent (any framework)
from strands import Agent
# or LangGraph, CrewAI, Autogen, custom logic - doesn't matter

def my_local_agent(query):
    # Your carefully crafted agent logic
    return agent.process(query)

# Deploy to Bedrock AgentCore
from bedrock_agentcore import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def production_agent(request):
    return my_local_agent(request.get("prompt"))  # Same logic, enterprise platform

app.run()  # Ready to run on Bedrock AgentCore
```

**What you get with Bedrock AgentCore:**
- ✅ **Keep your agent logic** - Works with Strands, LangGraph, CrewAI, Autogen, custom frameworks
- ✅ **Zero infrastructure management** - No servers, containers, or scaling concerns
- ✅ **Enterprise-grade platform** - Built-in auth, memory, observability, security
- ✅ **Production-ready deployment** - Reliable, scalable, compliant hosting

## ⚠️ Preview Status

Bedrock AgentCore SDK is currently in public preview. APIs may change as we refine the SDK.

## 🛠️ Built for AI Developers

**Real-time Health Monitoring**
```python
@app.async_task  # Automatically tracks background work
async def process_documents(files):
    # Long-running AI processing
    return results

@app.ping  # Custom health status
def health_check():
    return "HEALTHY" if all_services_up() else "HEALTHY_BUSY"
```

**Enterprise Platform Services**
- 🧠 **Memory** - Persistent knowledge across sessions
- 🔗 **Gateway** - Transform APIs into MCP tools
- 💻 **Code Interpreter** - Secure sandboxed execution
- 🌐 **Browser** - Cloud-based web automation
- 📊 **Observability** - OpenTelemetry tracing
- 🔐 **Identity** - AWS & third-party auth

## 🏗️ Deployment

**Quick Start:** Use the [Bedrock AgentCore Starter Toolkit](https://github.com/aws/bedrock-agentcore-starter-toolkit) for rapid prototyping.

**Production:** [AWS CDK](https://aws.amazon.com/cdk/) - coming soon.

## 📝 License & Contributing

- **License:** Apache 2.0 - see [LICENSE.txt](LICENSE.txt)
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security:** Report vulnerabilities via [SECURITY.md](SECURITY.md)

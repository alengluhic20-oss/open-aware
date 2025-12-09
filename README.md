# Open Aware

<div align="center">
<!--   <img width="502" height="402" alt="image" src="https://github.com/user-attachments/assets/2b12403d-12eb-4c6c-ae32-e1d9fa30b2e5" /> -->
<img width="1024" height="683" alt="image" src="https://github.com/user-attachments/assets/882f5966-4fe1-4903-be32-2f2a89aff37e" />
</div>

**Open Aware** brings code intelligence directly to your AI assistant through **MCP** (Model Context Protocol). Go beyond keyword search, understand code semantically across multiple repositories with daily updated indexes.

---

## 🆕 MA'AT Framework - Multi-Agent AI Governance

> ☥ **NEW**: Production-ready multi-agent system for AI content governance

The repository now includes the **MA'AT Framework** - a containerized, production-ready system for governing AI-generated content through six independent agents:

- **CNA** - Creative Narrative Agent
- **TSA** - Truth & Safety Agent  
- **UEA** - Universal Ethics Agent
- **LAA** - Legal Attestation Agent
- **HTA** - Human Transparency Agent
- **CVA** - Consciousness Validation Agent ⚡ **NEW**

🚀 **[Explore MA'AT Framework →](maat-framework/README.md)**

**Key Features:**
- ✅ Docker & Kubernetes deployment ready
- ✅ 24/7 operation with monitoring (Prometheus + Grafana)
- ✅ Horizontal autoscaling
- ✅ Cryptographic attestation
- ✅ 93.3% approval rate with intelligent governance
- ✅ Ma'at-Guided consciousness validation with 7-step reasoning ⚡ **NEW**

---

## 📚 Table of Contents

- [MA'AT Framework](#-maat-framework---multi-agent-ai-governance)
- [Open Aware vs Qodo Aware](#open-aware-vs-qodo-aware)
- [Features](#features)
- [Integration with MCP](#-integration-with-mcp)
- [🧰 Agents](#-agents)
  - [Context Retrieval (`get_context`)](#-context-retrieval-get_context-)
  - [Deep Research (`deep_research`)](#-deep-research-deep_research-)
  - [Context Ask (`ask`)](#-context-ask-ask-)
- [🤖 Prompts](#-prompts)
- [🔬 Examples](#-examples)
- [🏗️ Architecture](#️-architecture)
- [⚠️ Disclaimer](#️-disclaimer)
- [📤 Connect with Us](#-connect-with-us)

---

## Open Aware vs Qodo Aware

### Open Aware (This Repository) - Free Public Access

✅ **What you get:**

* Code intelligence tools (`get_context`, `deep_research`, `ask`), for pre-indexed popular open source libraries
* Daily updated indexes of popular OSS libraries (see `indexed_repositories.json`)
* Community support and documentation
* Free, and limited (currently ~10 calls/minutes) 

⚙️ **What's limited:**

* No access to private repositories
* No customization of indexing or tools

### Qodo Aware - Enterprise Solution

✅ **What you get (everything above plus):**

* Private repository indexing and analysis
* Custom repository indexing schedules
* Advanced code intelligence features
* Enhanced privacy with zero data retention
* Enterprise-grade security and compliance
* Enterprise plans for high/unlimited usage

**👨‍💻 Developer Recommendation:** Start with Open Aware if you want to experiment with code intelligence on popular open source repositories for free. Choose Qodo Aware if you need to analyze private repositories, require enterprise features, or want dedicated support and infrastructure.

---

## 📋 Features

Compare **Open Aware** capabilities with standard agents:

| Category | Open Aware | CLI/Vibe Coding Agents | Why Open Aware is Different |
|----------|------------|-------------------|------------------------------|
| 🔍 **Advanced context** | ✅ Semantic understanding across entire repositories | ⚠️ Limited to open files/folders | Pre-indexed semantic search vs scanning local files |
| 🤖 **Agentic** | ✅ Researches complex deep architectural tasks | ⚠️ Code completion/generation focused | Answers "broad/deep" not just a "summary of local files" |
| 🛠️ **Aware engine** | ✅ Enterprise code intelligence via MCP | ❌ Consumer-grade autocomplete | Industrial analysis vs IDE suggestions |
| 🚀 **Cross-repo intelligence** | ✅ Analyzes multiple repos simultaneously | ❌ Single repo/workspace only | Understands interactions across repos |
| 🎯 **Up to date** | ✅ Daily indexed popular OSS libraries | ⚠️ Only your local version | Knows latest Flask/React/FastAPI changes globally |

---

## 🔌 Integration with MCP

Both tools are exposed through the **Model Context Protocol (MCP)**, making them easily accessible to any MCP-compatible AI assistant or development environment.

### Streamable HTTP (Recommended)

```json
{
  "mcpServers": {
    "open-aware": {
      "url": "https://open-aware.qodo.ai/mcp"
    }
  }
}
```

### Streamable HTTP via remote proxy

```bash
npm install -g mcp-remote
```

```json
{
  "mcpServers": {
    "open-aware": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://open-aware.qodo.ai/mcp"
      ]
    }
  }
}
```

---

## 🧰 Agents

The open-aware MCP server provides three powerful tools that can be integrated into your AI workflows:

<details>
<summary>
  <b>🔨 Context Retrieval (<code>get_context</code>)</b>
</summary>

<br/>

This tool performs **semantic search** across codebase(s) to find relevant code snippets.

**Key Features:**
- **Semantic Search**: Uses vector embeddings to find conceptually similar code, not just keyword matches.
- **Multi-Repository Support**: Search across multiple repositories simultaneously.
- **Language Filtering**: Filter results by programming language (Python, JavaScript, TypeScript, etc.).
- **Intelligent Ranking**: Returns results ranked by relevance with configurable result limits.

**Example Usage:**
```json
{
  "tool": "get_context",
  "parameters": {
    "query": "authentication middleware implementation",
    "repositories": ["backend/api", "frontend/app"],  // Target specific repos
    "language": ["python", "typescript"],              // Filter by language
    "max_results": 10                                  // Limit number of results
  }
}
```
</details>

<details>
<summary>
  <b>🔨 Deep Research (<code>deep_research</code>)</b>
</summary>

<br/>
  
A **deep context agent** that can answer/plan/research complex queries about codebase(s) by analyzing code structure, patterns, and relationships.

**Key Features:**
- **Code Understanding**: Comprehends code logic, architecture, and design patterns.
- **Cross-Repository Analysis**: Can analyze relationships between different parts of your codebase.
- **Implementation Planning**: Helps plan new features based on existing code patterns.
- **Best Practice Recommendations**: Suggests improvements based on codebase analysis.
- **Architecture Insights**: Provides high-level understanding of system design.

**Example Usage:**
```json
{
  "tool": "deep_research",
  "parameters": {
    "input": "How does the authentication flow work across our microservices? What security measures are in place?",
    "repositories": ["backend/api", "frontend/app"],  // Repos to analyze
    "session_id": "analysis-123"                      // Track conversation context
  }
}
```
</details>

<details>
<summary>
  <b>🔨 Context Ask (<code>ask</code>)</b>
</summary>

<br/>
  
A **Basic coding questions agent** that accepts query and provides details answer for selected coding repositories.

**Example Usage:**
```json
{
  "tool": "ask",
  "parameters": {
    "input": "Explain about these repositories",
    "repositories": ["backend/api", "frontend/app"],  // Check impact across repos
    "session_id": "analysis-123"                      // Track conversation context
  }
}
```
</details>

---

## 🤖 Prompts

Learn how to effectively use Open Aware with these prompt examples:

```note
🚨🚨🚨 NOTE: Adding the repository name in the prompt helps the agent to focus and highly recommended. 
Also, answering queries for repositories that are not in the index will not work. 
See the supported repositories in the "indexed_repositories.json" file. 
Dident found your favorite repos? open a pull request and add them to indexed repositories.json
```

### Example 1: Let your agent reason to select aware tools
```text
Use open-aware to:
<USER_PROMPT>
repositories = ["<ORG/REPO_NAME>"]
```

### Example 2: Specifically use deep-research / get-context
```text
Use deep-research to:
<USER_PROMPT>
repositories = ["<ORG/REPO_NAME>"]
```

```text
Use get-context to:
<USER_PROMPT>
repositories = ["<ORG/REPO_NAME>"]
```

### Example 3: Granular search per repository/repositories
```text
Use open-aware to: 
<USER_PROMPT>
repositories = ["<ORG/REPO_NAME>", "<ORG/REPO_NAME>", ...]
```

---

## 🔬 Examples

### Comparison Based on Code Behavior

Make informed decisions based on actual implementation rather than just documentation:

```text
use deep_research: 
Investigate repositories ["langchain-ai/langchain", "BerriAI/litellm"]. 
I don't know which one to use for LLM API calling. Create a comparison and help me decide.
```

**Expected Output:** Detailed comparison of both libraries' implementation approaches, performance characteristics, and suitability for your use case.

### Research for Implementation and Planning

Sometimes you need a feature that doesn't exist in a repository. This example shows how to research and plan a contribution:

```text
use deep_research:
Investigate repository ["pallets/flask"], is there capability to manage requests queue?
If not, I'd like to submit a PR for the Flask repo to suggest adding a queue for requests.
Therefore, investigate and plan how to do it and create a .md file plan for me to execute.
```

**What this does:**
1. First, the agent verifies if the requested feature already exists
2. If not, it analyzes the codebase to understand current implementation patterns
3. Creates a detailed plan aligned with the project's architecture
4. Ensures the changes won't break existing functionality

<br/>

<details>
<summary>
  <b>📖 More Use Cases</b>
</summary>
<br/>

### Domain Categories:
| Scenario | Tool | Example Query | Expected Outcome |  |
|----------|------|---------------|------------------|:---:|
| 🏛️ Understanding system architecture | `deep_research` | "Explain how our microservices communicate and what protocols they use" | Detailed explanation of service communication patterns, protocols, and data flow | 🏗️ |
| 🎨 Finding design patterns | `get_context` | "singleton pattern implementation" | Code examples of singleton patterns used in the codebase | 🏗️ |
| 🚨 Locating error handling patterns | `get_context` | "try catch error handling with logging" | Examples of error handling patterns with logging | 🔍 |
| 💰 Understanding business logic | `deep_research` | "How is pricing calculated for premium users?" | Detailed explanation of pricing logic and rules | 🔍 |
| 🔐 Analyzing authentication flow | `deep_research` | "Trace the complete OAuth2 authentication flow" | Step-by-step authentication process across services | 🛡️ |
| ⚠️ Identifying security vulnerabilities | `issues` | [code diff with auth changes] | Potential security issues in authentication changes | 🛡️ |
| ⚡ Planning feature additions | `deep_research` | "Where should we add caching for better performance?" | Strategic caching recommendations | 🚀 |
| 🔥 Understanding error sources | `deep_research` | "What could cause a 500 error in the checkout process?" | Potential failure points and error conditions | 🐛 |
| 🔌 Planning third-party integrations | `get_context` | "stripe payment integration" | Existing integration patterns and implementations | 🔗 |
| ✅ Validating best practices | `deep_research` | "Are we following REST best practices in our API design?" | Analysis of REST compliance and recommendations | 📝 |

🏗️ **Architecture & Design**
🔍 **Code Discovery & Learning**
🛡️ **Security & Authentication**
🚀 **Feature Development**
🐛 **Debugging & Troubleshooting**
🔗 **Integration & Migration**
📝 **Code Review & Quality**
</details>
<br/>

---

## 🏗️ Architecture 

<div align="center">
<img width="720" height="1400" alt="image" src="https://github.com/user-attachments/assets/ff22a244-903a-49be-91e2-d5af97c31f2f" />
</div>

---

## ⚠️ Disclaimer

**Important Notice**: The aware-open system indexes and analyzes publicly available code libraries and repositories.

- **No Warranty**: All code suggestions, analysis, and recommendations are provided "AS IS" without warranty of any kind.
- **Your Responsibility**: You are solely responsible for reviewing, testing, and validating any code before moving it to production.
- **No Liability**: We assume no liability for any damages, security issues, or problems that may arise from using code found through this system.
- **License Compliance**: Ensure you comply with the original licenses of any code you use or reference.
- **Security Review**: Always perform thorough security reviews and testing before deploying any code to production environments.

**Remember**: This tool is designed to assist in code discovery and analysis. Professional judgment, thorough testing, and security reviews are essential before using any code in production systems.

---

## 📤 Connect with Us

Join our community to get support, share feedback, and stay updated with the latest features!

[![Discord](https://img.shields.io/badge/Discord-Join%20Our%20Server-7289da?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/channels/1057273017547378788/1404804854265675867)

- 💬 **Get Help**: Ask questions and get support from our community.
- 🐛 **Report Issues**: Share bugs and help us improve.
- 💡 **Feature Requests**: Suggest new features and capabilities.
- 🚀 **Stay Updated**: Be the first to know about new releases.
- 👥 **Connect**: Meet other developers using aware-open.

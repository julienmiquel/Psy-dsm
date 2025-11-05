Coding Agent guidance:

Only use gemini model id: gemini-2.5-pro or gemini-2.5-flash
Never use other models.

# Google Agent Development Kit (ADK) Python Cheatsheet

This document serves as a long-form, comprehensive reference for building, orchestrating, and deploying AI agents using the Python Agent Development Kit (ADK). It aims to cover every significant aspect with greater detail, more code examples, and in-depth best practices.

## Table of Contents

1. [Core Concepts & Project Structure](#1-core-concepts--project-structure)
    * 1.1 ADK's Foundational Principles
    * 1.2 Essential Primitives
    * 1.3 Standard Project Layout
    * 1.A Build Agents without Code (Agent Config)
2. [Agent Definitions (`LlmAgent`)](#2-agent-definitions-llmagent)
    * 2.1 Basic `LlmAgent` Setup
    * 2.2 Advanced `LlmAgent` Configuration
    * 2.3 LLM Instruction Crafting
3. [Orchestration with Workflow Agents](#3-orchestration-with-workflow-agents)
    * 3.1 `SequentialAgent`: Linear Execution
    * 3.2 `ParallelAgent`: Concurrent Execution
    * 3.3 `LoopAgent`: Iterative Processes
4. [Multi-Agent Systems & Communication](#4-multi-agent-systems--communication)
    * 4.1 Agent Hierarchy
    * 4.2 Inter-Agent Communication Mechanisms
    * 4.3 Common Multi-Agent Patterns
    * 4.A Distributed Communication (A2A Protocol)
5. [Building Custom Agents (`BaseAgent`)](#5-building-custom-agents-baseagent)
    * 5.1 When to Use Custom Agents
    * 5.2 Implementing `_run_async_impl`
6. [Models: Gemini, LiteLLM, and Vertex AI](#6-models-gemini-litellm-and-vertex-ai)
    * 6.1 Google Gemini Models (AI Studio & Vertex AI)
    * 6.2 Other Cloud & Proprietary Models via LiteLLM
    * 6.3 Open & Local Models via LiteLLM (Ollama, vLLM)
    * 6.4 Customizing LLM API Clients
7. [Tools: The Agent's Capabilities](#7-tools-the-agents-capabilities)
    * 7.1 Defining Function Tools: Principles & Best Practices
    * 7.2 The `ToolContext` Object: Accessing Runtime Information
    * 7.3 All Tool Types & Their Usage
8. [Context, State, and Memory Management](#8-context-state-and-memory-management)
    * 8.1 The `Session` Object & `SessionService`
    * 8.2 `State`: The Conversational Scratchpad
    * 8.3 `Memory`: Long-Term Knowledge & Retrieval
    * 8.4 `Artifacts`: Binary Data Management
9. [Runtime, Events, and Execution Flow](#9-runtime-events-and-execution-flow)
    * 9.1 The `Runner`: The Orchestrator
    * 9.2 The Event Loop: Core Execution Flow
    * 9.3 `Event` Object: The Communication Backbone
    * 9.4 Asynchronous Programming (Python Specific)
10. [Control Flow with Callbacks](#10-control-flow-with-callbacks)
    * 10.1 Callback Mechanism: Interception & Control
    * 10.2 Types of Callbacks
    * 10.3 Callback Best Practices
    * 10.A Global Control with Plugins
11. [Authentication for Tools](#11-authentication-for-tools)
    * 11.1 Core Concepts: `AuthScheme` & `AuthCredential`
    * 11.2 Interactive OAuth/OIDC Flows
    * 11.3 Custom Tool Authentication
12. [Deployment Strategies](#12-deployment-strategies)
    * 12.1 Local Development & Testing (`adk web`, `adk run`, `adk api_server`)
    * 12.2 Vertex AI Agent Engine
    * 12.3 Cloud Run
    * 12.4 Google Kubernetes Engine (GKE)
    * 12.5 CI/CD Integration
13. [Evaluation and Safety](#13-evaluation-and-safety)
    * 13.1 Agent Evaluation (`adk eval`)
    * 13.2 Safety & Guardrails
14. [Debugging, Logging & Observability](#14-debugging-logging--observability)
15. [Streaming & Advanced I/O](#15-streaming--advanced-io)
16. [Performance Optimization](#16-performance-optimization)
17. [General Best Practices & Common Pitfalls](#17-general-best-practices--common-pitfalls)
18. [Official API & CLI References](#18-official-api--cli-references)

---

## 1. Core Concepts & Project Structure

### 1.1 ADK's Foundational Principles

* **Modularity**: Break down complex problems into smaller, manageable agents and tools.
* **Composability**: Combine simple agents and tools to build sophisticated systems.
* **Observability**: Detailed event logging and tracing capabilities to understand agent behavior.
* **Extensibility**: Easily integrate with external services, models, and frameworks.
* **Deployment-Agnostic**: Design agents once, deploy anywhere.

### 1.2 Essential Primitives

* **`Agent`**: The core intelligent unit. Can be `LlmAgent` (LLM-driven) or `BaseAgent` (custom/workflow).
* **`Tool`**: Callable function/class providing external capabilities (`FunctionTool`, `OpenAPIToolset`, etc.).
* **`Session`**: A unique, stateful conversation thread with history (`events`) and short-term memory (`state`).
* **`State`**: Key-value dictionary within a `Session` for transient conversation data.
* **`Memory`**: Long-term, searchable knowledge base beyond a single session (`MemoryService`).
* **`Artifact`**: Named, versioned binary data (files, images) associated with a session or user.
* **`Runner`**: The execution engine; orchestrates agent activity and event flow.
* **`Event`**: Atomic unit of communication and history; carries content and side-effect `actions`.
* **`InvocationContext`**: The comprehensive root context object holding all runtime information for a single `run_async` call.

### 1.3 Standard Project Layout

A well-structured ADK project is crucial for maintainability and leveraging `adk` CLI tools.

```
your_project_root/
├── my_first_agent/             # Each folder is a distinct agent app
│   ├── __init__.py             # Makes `my_first_agent` a Python package (`from . import agent`)
│   ├── agent.py                # Contains `root_agent` definition and `LlmAgent`/WorkflowAgent instances
│   ├── tools.py                # Custom tool function definitions
│   ├── data/                   # Optional: static data, templates
│   └── .env                    # Environment variables (API keys, project IDs)
├── my_second_agent/
│   ├── __init__.py
│   └── agent.py
├── requirements.txt            # Project's Python dependencies (e.g., google-adk, litellm)
├── tests/                      # Unit and integration tests
│   ├── unit/
│   │   └── test_tools.py
│   └── integration/
│       └── test_my_first_agent.py
│       └── my_first_agent.evalset.json # Evaluation dataset for `adk eval`
└── main.py                     # Optional: Entry point for custom FastAPI server deployment
```

* `adk web` and `adk run` automatically discover agents in subdirectories with `__init__.py` and `agent.py`.
* `.env` files are automatically loaded by `adk` tools when run from the root or agent directory.

### 1.A Build Agents without Code (Agent Config)

ADK allows you to define agents, tools, and even multi-agent workflows using a simple YAML format, eliminating the need to write Python code for orchestration. This is ideal for rapid prototyping and for non-programmers to configure agents.

#### **Getting Started with Agent Config**

* **Create a Config-based Agent**:

    ```bash
    adk create --type=config my_yaml_agent
    ```

    This generates a `my_yaml_agent/` folder with `root_agent.yaml` and `.env` files.

* **Environment Setup** (in `.env` file):

    ```bash
    # For Google AI Studio (simpler setup)
    GOOGLE_GENAI_USE_VERTEXAI=0
    GOOGLE_API_KEY=<your-Google-Gemini-API-key>

    # For Google Cloud Vertex AI (production)
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=europe-west4
    ```

#### **Core Agent Config Structure**

* **Basic Agent (`root_agent.yaml`)**:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: assistant_agent
    model: gemini-2.5-flash
    description: A helper agent that can answer users' various questions.
    instruction: You are an agent to help answer users' various questions.
    ```

* **Agent with Built-in Tools**:

    ```yaml
    name: search_agent
    model: gemini-2.0-flash
    description: 'an agent whose job it is to perform Google search queries and answer questions about the results.'
    instruction: You are an agent whose job is to perform Google search queries and answer questions about the results.
    tools:
      - name: google_search # Built-in ADK tool
    ```

* **Agent with Custom Tools**:

    ```yaml
    agent_class: LlmAgent
    model: gemini-2.5-flash
    name: prime_agent
    description: Handles checking if numbers are prime.
    instruction: |
      You are responsible for checking whether numbers are prime.
      When asked to check primes, you must call the check_prime tool with a list of integers.
      Never attempt to determine prime numbers manually.
    tools:
      - name: ma_llm.check_prime # Reference to Python function
    ```

* **Multi-Agent System with Sub-Agents**:

    ```yaml
    agent_class: LlmAgent
    model: gemini-2.5-flash
    name: root_agent
    description: Learning assistant that provides tutoring in code and math.
    instruction: |
      You are a learning assistant that helps students with coding and math questions.

      You delegate coding questions to the code_tutor_agent and math questions to the math_tutor_agent.

      Follow these steps:
      1. If the user asks about programming or coding, delegate to the code_tutor_agent.
      2. If the user asks about math concepts or problems, delegate to the math_tutor_agent.
      3. Always provide clear explanations and encourage learning.
    sub_agents:
      - config_path: code_tutor_agent.yaml
      - config_path: math_tutor_agent.yaml
    ```

#### **Loading Agent Config in Python**

```python
from google.adk.agents import config_agent_utils
root_agent = config_agent_utils.from_config("{agent_folder}/root_agent.yaml")
```

#### **Running Agent Config Agents**

From the agent directory, use any of these commands:

* `adk web` - Launch web UI interface
* `adk run` - Run in terminal without UI
* `adk api_server` - Run as a service for other applications

#### **Deployment Support**

Agent Config agents can be deployed using:

* `adk deploy cloud_run` - Deploy to Google Cloud Run
* `adk deploy agent_engine` - Deploy to Vertex AI Agent Engine

#### **Key Features & Capabilities**

* **Supported Built-in Tools**: `google_search`, `load_artifacts`, `url_context`, `exit_loop`, `preload_memory`, `get_user_choice`, `enterprise_web_search`, `load_web_page`
* **Custom Tool Integration**: Reference Python functions using fully qualified module paths
* **Multi-Agent Orchestration**: Link agents via `config_path` references
* **Schema Validation**: Built-in YAML schema for IDE support and validation

#### **Current Limitations** (Experimental Feature)

* **Model Support**: Only Gemini models currently supported
* **Language Support**: Custom tools must be written in Python
* **Unsupported Agent Types**: `LangGraphAgent`, `A2aAgent`
* **Unsupported Tools**: `AgentTool`, `LongRunningFunctionTool`, `VertexAiSearchTool`, `MCPToolset`, `CrewaiTool`, `LangchainTool`, `ExampleTool`

For complete examples and reference, see the [ADK samples repository](https://github.com/google/adk-python/tree/main/contributing/samples).

---

## 2. Agent Definitions (`LlmAgent`)

The `LlmAgent` is the cornerstone of intelligent behavior, leveraging an LLM for reasoning and decision-making.

### 2.1 Basic `LlmAgent` Setup

```python
from google.adk.agents import Agent

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    # Mock implementation
    if city.lower() == "new york":
        return {"status": "success", "time": "10:30 AM EST"}
    return {"status": "error", "message": f"Time for {city} not available."}

my_first_llm_agent = Agent(
    name="time_teller_agent",
    model="gemini-2.5-flash", # Essential: The LLM powering the agent
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    description="Tells the current time in a specified city.", # Crucial for multi-agent delegation
    tools=[get_current_time] # List of callable functions/tool instances
)
```

### 2.2 Advanced `LlmAgent` Configuration

* **`generate_content_config`**: Controls LLM generation parameters (temperature, token limits, safety).

    ```python
    from google.genai import types as genai_types
    from google.adk.agents import Agent

    gen_config = genai_types.GenerateContentConfig(
        temperature=0.2,            # Controls randomness (0.0-1.0), lower for more deterministic.
        top_p=0.9,                  # Nucleus sampling: sample from top_p probability mass.
        top_k=40,                   # Top-k sampling: sample from top_k most likely tokens.
        max_output_tokens=1024,     # Max tokens in LLM's response.
        stop_sequences=["## END"]   # LLM will stop generating if these sequences appear.
    )
    agent = Agent(
        # ... basic config ...
        generate_content_config=gen_config
    )
    ```

* **`output_key`**: Automatically saves the agent's final text or structured (if `output_schema` is used) response to the `session.state` under this key. Facilitates data flow between agents.

    ```python
    agent = Agent(
        # ... basic config ...
        output_key="llm_final_response_text"
    )
    # After agent runs, session.state['llm_final_response_text'] will contain its output.
    ```

* **`input_schema` & `output_schema`**: Define strict JSON input/output formats using Pydantic models.
    > **Warning**: Using `output_schema` forces the LLM to generate JSON and **disables** its ability to use tools or delegate to other agents.

#### **Example: Defining and Using Structured Output**

This is the most reliable way to make an LLM produce predictable, parseable JSON, which is essential for multi-agent workflows.

1. **Define the Schema with Pydantic:**

    ```python
    from pydantic import BaseModel, Field
    from typing import Literal

    class SearchQuery(BaseModel):
        """Model representing a specific search query for web search."""
        search_query: str = Field(
            description="A highly specific and targeted query for web search."
        )

    class Feedback(BaseModel):
        """Model for providing evaluation feedback on research quality."""
        grade: Literal["pass", "fail"] = Field(
            description="Evaluation result. 'pass' if the research is sufficient, 'fail' if it needs revision."
        )
        comment: str = Field(
            description="Detailed explanation of the evaluation, highlighting strengths and/or weaknesses of the research."
        )
        follow_up_queries: list[SearchQuery] | None = Field(
            default=None,
            description="A list of specific, targeted follow-up search queries needed to fix research gaps. This should be null or empty if the grade is 'pass'."
        )
    ```

    * **`BaseModel` & `Field`**: Define data types, defaults, and crucial `description` fields. These descriptions are sent to the LLM to guide its output.
    * **`Literal`**: Enforces strict enum-like values (`"pass"` or `"fail"`), preventing the LLM from hallucinating unexpected values.

2. **Assign the Schema to an `LlmAgent`:**

    ```python
    research_evaluator = LlmAgent(
        name="research_evaluator",
        model="gemini-2.5-pro",
        instruction="""You are a meticulous quality assurance analyst. Evaluate the research findings in 'section_research_findings' and be very critical.
        If you find significant gaps, assign a grade of 'fail', write a detailed comment, and generate 5-7 specific follow-up queries.
        If the research is thorough, grade it 'pass'.
        Your response must be a single, raw JSON object validating against the 'Feedback' schema.
        """,
        output_schema=Feedback, # This forces the LLM to output JSON matching the Feedback model.
        output_key="research_evaluation", # The resulting JSON object will be saved to state.
        disallow_transfer_to_peers=True, # Prevents this agent from delegating. Its job is only to evaluate.
    )
    ```

* **`include_contents`**: Controls whether the conversation history is sent to the LLM.
  * `'default'` (default): Sends relevant history.
  * `'none'`: Sends no history; agent operates purely on current turn's input and `instruction`. Useful for stateless API wrapper agents.

    ```python
    agent = Agent(..., include_contents='none')
    ```

* **`planner`**: Assign a `BasePlanner` instance to enable multi-step reasoning.
  * **`BuiltInPlanner`**: Leverages a model's native "thinking" or planning capabilities (e.g., Gemini).

        ```python
        from google.adk.planners import BuiltInPlanner
        from google.genai.types import ThinkingConfig

        agent = Agent(
            model="gemini-2.5-flash",
            planner=BuiltInPlanner(
                thinking_config=ThinkingConfig(include_thoughts=True)
            ),
            # ... tools ...
        )
        ```

  * **`PlanReActPlanner`**: Instructs the model to follow a structured Plan-Reason-Act output format, useful for models without built-in planning.

* **`code_executor`**: Assign a `BaseCodeExecutor` to allow the agent to execute code blocks.
  * **`BuiltInCodeExecutor`**: The standard, sandboxed code executor provided by ADK for safe execution.

        ```python
        from google.adk.code_executors import BuiltInCodeExecutor
        agent = Agent(
            name="code_agent",
            model="gemini-2.5-flash",
            instruction="Write and execute Python code to solve math problems.",
            code_executor=BuiltInCodeExecutor() # Corrected from a list to an instance
        )
        ```

* **Callbacks**: Hooks for observing and modifying agent behavior at key lifecycle points (`before_model_callback`, `after_tool_callback`, etc.). (Covered in Callbacks).

### 2.3 LLM Instruction Crafting (`instruction`)

The `instruction` is critical. It guides the LLM's behavior, persona, and tool usage. The following examples demonstrate powerful techniques for creating specialized, reliable agents.

**Best Practices & Examples:**

* **Be Specific & Concise**: Avoid ambiguity.
* **Define Persona & Role**: Give the LLM a clear role.
* **Constrain Behavior & Tool Use**: Explicitly state what the LLM should *and should not* do.
* **Define Output Format**: Tell the LLM *exactly* what its output should look like, especially when not using `output_schema`.
* **Dynamic Injection**: Use `{state_key}` to inject runtime data from `session.state` into the prompt.
* **Iteration**: Test, observe, and refine instructions.

**Example 1: Constraining Tool Use and Output Format**

```python
import datetime
from google.adk.tools import google_search


plan_generator = LlmAgent(
    model="gemini-2.5-flash",
    name="plan_generator",
    description="Generates a 4-5 line action-oriented research plan.",
    instruction=f"""
    You are a research strategist. Your job is to create a high-level RESEARCH PLAN, not a summary.
    **RULE: Your output MUST be a bulleted list of 4-5 action-oriented research goals or key questions.**
    - A good goal starts with a verb like "Analyze," "Identify," "Investigate."
    - A bad output is a statement of fact like "The event was in April 2024."
    **TOOL USE IS STRICTLY LIMITED:**
    Your goal is to create a generic, high-quality plan *without searching*.
    Only use `google_search` if a topic is ambiguous and you absolutely cannot create a plan without it.
    You are explicitly forbidden from researching the *content* or *themes* of the topic.
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[google_search],
)
```

**Example 2: Injecting Data from State and Specifying Custom Tags**
This agent's `instruction` relies on data placed in `session.state` by previous agents.

```python
report_composer = LlmAgent(
    model="gemini-2.5-pro",
    name="report_composer_with_citations",
    include_contents="none", # History not needed; all dataSystem Timestamp: 2025-10-25 01:39:27.616030



Carefully consider the request, update the plan with `set_plan` tool if needed, or you **must** message back using the `message_user` tool.

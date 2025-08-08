"""
Project service for the Kapso CLI.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Callable

class ProjectService:
    """
    Service for managing Kapso projects.
    """

    def __init__(self):
        """Initialize the project service."""
        self.agent_templates = {
            "basic": self._get_basic_agent_template,
            "support": self._get_support_agent_template,
            "knowledge-base": self._get_knowledge_base_agent_template,
        }

        self.test_templates = {
            "basic": self._get_basic_test_template,
            "support": self._get_support_test_template,
            "knowledge-base": self._get_knowledge_base_test_template,
        }

    def create_example_agent(self, project_path: Path, template: str) -> None:
        """
        Create an example agent file based on the specified template.

        Args:
            project_path: Path to the project directory
            template: Template to use (basic, support, knowledge-base)
        """
        agent_file = project_path / "agent.py"

        template_func = self.agent_templates.get(template, self._get_basic_agent_template)
        content = template_func()

        with open(agent_file, "w") as f:
            f.write(content)

    def create_example_test(self, project_path: Path, template: str) -> None:
        """
        Create example test files based on the specified template.
        Creates a test suite directory structure with metadata and individual test files.

        Args:
            project_path: Path to the project directory
            template: Template to use (basic, support, knowledge-base)
        """
        # Create test suite directory
        test_suite_name = f"{template}_functionality"
        test_suite_dir = project_path / "tests" / test_suite_name
        test_suite_dir.mkdir(parents=True, exist_ok=True)

        # Create test suite metadata file
        metadata_file = test_suite_dir / "test-suite.yaml"
        metadata_content = self._get_test_suite_metadata(template)
        with open(metadata_file, "w") as f:
            f.write(metadata_content)

        # Get individual test files for this template
        template_func = self.test_templates.get(template, self._get_basic_test_template)
        test_files = template_func()

        # Write each test file
        for filename, content in test_files.items():
            test_file = test_suite_dir / filename
            with open(test_file, "w") as f:
                f.write(content)

    def create_kapso_yaml(self, project_path: Path, template: str) -> None:
        """
        Create a kapso.yaml configuration file.

        Args:
            project_path: Path to the project directory
            template: Template to use (basic, support, knowledge-base)
        """
        config_file = project_path / "kapso.yaml"

        content = f"""# Kapso project configuration
name: {project_path.name}
version: 0.1.0
agent_file: agent.py
compiled_file: agent.yaml
test_directory: tests
template: {template}
"""

        with open(config_file, "w") as f:
            f.write(content)

    def create_env_example(self, project_path: Path) -> None:
        """
        Create a .env.example file.

        Args:
            project_path: Path to the project directory
        """
        env_file = project_path / ".env.example"

        content = """# Kapso environment variables

# LLM Configuration
LLM_PROVIDER_NAME=Anthropic
LLM_PROVIDER_MODEL_NAME=claude-sonnet-4-20250514
LLM_API_KEY=your-llm-api-key
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=8096

# OpenAI API key (used for embeddings in knowledge bases)
OPENAI_API_KEY=your-openai-api-key

# Kapso API key (for cloud deployment)
KAPSO_API_KEY=your-kapso-api-key

# Test evaluation configuration
JUDGE_LLM_API_KEY=your-judge-llm-api-key
JUDGE_LLM_PROVIDER=Anthropic
"""

        with open(env_file, "w") as f:
            f.write(content)

    def _get_basic_agent_template(self) -> str:
        """Get the basic agent template."""
        return """from kapso.builder import Agent
from kapso.builder.nodes import SubagentNode, WarmEndNode, HandoffNode
from kapso.builder.nodes.subagent import WebhookTool, KnowledgeBaseTool
from kapso.builder.agent.constants import START_NODE, END_NODE

# Create the agent
agent = Agent(
    name="Basic Agent",
    system_prompt="You are a helpful assistant that can look up information and answer questions."
)

# Create a subagent node with basic tools
subagent = SubagentNode(
    name="subagent",
    prompt="Help the user with their questions using the available tools when needed."
)

# Add a simple webhook tool
api_tool = WebhookTool(
    name="get_data",
    url="https://api.example.com/data",
    http_method="GET",
    headers={"Authorization": "Bearer {{api_key}}"},
    description="Retrieve data from the external API"
)
subagent.add_tool(api_tool)

# Add a knowledge base tool
kb_tool = KnowledgeBaseTool(
    name="info",
    knowledge_base_text="Our service hours are 9 AM to 5 PM EST, Monday through Friday.",
    description="General information about our service"
)
subagent.add_tool(kb_tool)

# Global handoff node for escalation
human_handoff = HandoffNode(
    name="human_handoff",
    global_=True,
    global_condition="user explicitly requests human agent OR conversation requires human assistance"
)

# Warm end node for conversation closure
end_conversation = WarmEndNode(
    name="end_conversation",
    timeout_minutes=30,
    prompt="Thank you for chatting with me! I'll be here for another 30 minutes if you have any follow-up questions."
)

# Add nodes to the agent
agent.add_node(START_NODE)
agent.add_node(subagent)
agent.add_node(human_handoff)
agent.add_node(end_conversation)
agent.add_node(END_NODE)

# Create the conversation flow
agent.add_edge(START_NODE, "subagent")
agent.add_edge("subagent", "end_conversation", condition="user says goodbye or conversation is complete")
agent.add_edge("end_conversation", END_NODE)
"""

    def _get_support_agent_template(self) -> str:
        """Get the support agent template."""
        return """from kapso.builder.agent import Agent
from kapso.builder.nodes import DefaultNode, HandoffNode, WarmEndNode
from kapso.builder.edges import Edge

agent = Agent(
    name="Support Agent",
    system_prompt="You are a helpful customer support agent."
)

start_node = DefaultNode(
    name="start",
    prompt="You are a customer support agent for a software company. Help users with their questions and issues."
)

handoff_node = HandoffNode(
    name="handoff"
)

end_node = WarmEndNode(
    name="end",
    prompt="Thank you for contacting our support. Is there anything else I can help you with?",
    timeout_minutes=60
)

agent.add_node(start_node)
agent.add_node(handoff_node)
agent.add_node(end_node)

agent.add_edge(source="START", target="start")
agent.add_edge(source="start", target="handoff", condition="user has a complex issue that requires human assistance")
agent.add_edge(source="start", target="end", condition="user's issue is resolved")
agent.add_edge(source="end", target="END")
"""

    def _get_knowledge_base_agent_template(self) -> str:
        """Get the knowledge base agent template."""
        return """from kapso.builder.agent import Agent
from kapso.builder.nodes import DefaultNode, KnowledgeBaseNode, WarmEndNode
from kapso.builder.edges import Edge

agent = Agent(
    name="Knowledge Base Agent",
    system_prompt="You are a helpful assistant with access to a knowledge base."
)

start_node = DefaultNode(
    name="start",
    prompt="You are an assistant with access to a knowledge base. Help users find information."
)

kb_node = KnowledgeBaseNode(
    name="knowledge",
    key="default",
    prompt="Use the knowledge base to answer the user's question accurately."
)

end_node = WarmEndNode(
    name="end",
    prompt="Thank you for your questions. Is there anything else I can help you with?",
    timeout_minutes=60
)

agent.add_node(start_node)
agent.add_node(kb_node)
agent.add_node(end_node)

agent.add_edge(source="START", target="start")
agent.add_edge(source="start", target="knowledge", condition="user asks a question that requires knowledge base lookup")
agent.add_edge(source="knowledge", target="end", condition="user's question is answered")
agent.add_edge(source="end", target="END")
"""

    def _get_test_suite_metadata(self, template: str) -> str:
        """Get test suite metadata for the given template."""
        metadata_map = {
            "basic": {
                "name": "Basic Functionality Tests",
                "description": "Tests for basic agent functionality including greetings and general queries"
            },
            "support": {
                "name": "Customer Support Tests", 
                "description": "Tests for customer support scenarios including issue resolution and handoff"
            },
            "knowledge-base": {
                "name": "Knowledge Base Tests",
                "description": "Tests for knowledge base queries and information retrieval"
            }
        }
        
        metadata = metadata_map.get(template, metadata_map["basic"])
        return f"""name: {metadata["name"]}
description: {metadata["description"]}
"""

    def _get_basic_test_template(self) -> Dict[str, str]:
        """Get the basic test template files."""
        return {
            "greeting_test.yaml": """name: greeting_test
description: Test if the agent greets users appropriately
script: |
  1. Start by saying "Hello, how are you?"
  2. When the agent responds, thank them and say goodbye
rubric: |
  1. Warm and friendly greeting (40%)
  2. Acknowledges the user's greeting (30%)  
  3. Offers assistance or asks how they can help (30%)
""",
            "information_query_test.yaml": """name: information_query_test
description: Test if the agent can explain its capabilities
script: |
  1. Ask "What can you do?"
  2. When they explain their capabilities, ask for a specific example
  3. Thank them for the information
rubric: |
  1. Clearly explains what they can help with (50%)
  2. Provides specific examples or areas of assistance (30%)
  3. Maintains helpful and professional tone (20%)
"""
        }

    def _get_support_test_template(self) -> Dict[str, str]:
        """Get the support test template files."""
        return {
            "support_greeting_test.yaml": """name: support_greeting_test
description: Test if the support agent greets and offers help appropriately
script: |
  1. Say "Hello, I need help with your product"
  2. When they ask for details, say "I'm having trouble logging in"
  3. Follow their instructions and indicate whether it worked
rubric: |
  1. Acknowledges the customer's need for help (30%)
  2. Shows empathy and willingness to assist (30%)
  3. Asks clarifying questions or offers specific help areas (40%)
""",
            "issue_resolution_test.yaml": """name: issue_resolution_test
description: Test if the agent can help with account issues
script: |
  1. Say "I can't log into my account"
  2. When they provide troubleshooting steps, say "I tried resetting my password but didn't receive an email"
  3. If they offer more help, say "I've tried everything you suggested"
  4. See if they offer to escalate or provide alternative solutions
rubric: |
  1. Acknowledges the login issue with empathy (20%)
  2. Provides clear troubleshooting steps (40%)
  3. Offers alternative solutions when initial steps don't work (30%)
  4. Knows when to escalate to human support (10%)
"""
        }

    def _get_knowledge_base_test_template(self) -> Dict[str, str]:
        """Get the knowledge base test template files."""
        return {
            "knowledge_query_test.yaml": """name: knowledge_query_test
description: Test if the agent can access and use the knowledge base
script: |
  1. Ask "What information do you have about your products?"
  2. When they provide an overview, ask about a specific product feature
  3. Thank them and ask if they have pricing information too
rubric: |
  1. Indicates they have access to knowledge base or documentation (30%)
  2. Provides a helpful overview of available information (40%)
  3. Offers to answer specific questions (30%)
""",
            "specific_query_test.yaml": """name: specific_query_test
description: Test if the agent can retrieve specific information
script: |
  1. Say "Tell me about your pricing plans"
  2. After they explain the pricing, ask "Which plan would you recommend for a small business with 10 employees?"
  3. If they ask for more details, provide them (e.g., "We need email support and API access")
  4. Thank them for the recommendation
rubric: |
  1. Successfully retrieves pricing information (40%)
  2. Presents information clearly and accurately (30%)
  3. Makes appropriate recommendation based on user needs (20%)
  4. Asks clarifying questions if needed (10%)
"""
        }

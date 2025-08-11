"""
[Example Title] - [Main Feature]

Brief description of what this example demonstrates.

This file serves as a base template for creating new examples
that follow the standard SPADE_LLM structure.

PREREQUISITES:
1. Start SPADE built-in server in another terminal:
   spade run
   
   (Advanced server configuration available but not needed)

2. Install dependencies:
   pip install spade_llm

This example uses SPADE's default built-in server (localhost:5222) - no account registration needed!
"""

import asyncio
import getpass
import os
import spade

from spade_llm.agent import LLMAgent, ChatAgent
from spade_llm.providers import LLMProvider
from spade_llm.utils import load_env_vars

# [Additional imports based on specific feature]

# 1. AGENT PROMPTS
AGENT_PROMPT = """
[Clear and specific prompt for the agent]

Example:
You are a helpful assistant that demonstrates [specific feature].
Your role is to [description of expected behavior].
"""

CHAT_PROMPT = """
[Prompt for the chat/human interface agent]

Example:
You are a user interface agent. Forward all user messages to the main agent
and relay responses back to the user in a clear and helpful manner.
"""


async def main():
    """Main function of the example."""

    # 2. PARAMETRIC CONFIGURATION (no hardcoding)
    load_env_vars()

    # XMPP server configuration - using default SPADE settings
    xmpp_server = "localhost"
    print("🌐 Using SPADE built-in server (localhost:5222)")
    print("  No account registration needed!")
    # Advanced server configuration available but not needed

    # API Key (with fallback)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Enter OpenAI API key: ")

    # 3. DECLARE THE PROVIDER
    provider = LLMProvider.create_openai(
        api_key=api_key,
        model="gpt-4o-mini"
    )

    # Alternative for Ollama (commented):
    # provider = LLMProvider.create_ollama(
    #     model="gemma2:2b",
    #     base_url="http://localhost:11434/v1"
    # )

    # 4. AGENT CONFIGURATION (using default settings)
    agent_jid = f"agent@{xmpp_server}"
    chat_jid = f"chat@{xmpp_server}"

    # Simple passwords (auto-registration with SPADE server)
    agent_password = "agent_pass"
    chat_password = "chat_pass"
    print(f"✓ Agent JIDs: {agent_jid}, {chat_jid}")
    print("  Using auto-registration with built-in server")

    # 5. INITIALIZE AGENTS WITH LLMAgent()
    agent = LLMAgent(
        jid=agent_jid,
        password=agent_password,
        provider=provider,
        system_prompt=AGENT_PROMPT,
        # [Feature-specific configuration]
        # Examples of additional configurations:
        # tools=[tool1, tool2],  # For examples with tools
        # context_management=SmartWindowSizeContext(max_messages=20),  # For context management
        # input_guardrails=[guardrail],  # For guardrails examples
        # mcp_servers=[mcp_server],  # For MCP integration
    )

    chat_agent = ChatAgent(
        jid=chat_jid,
        password=chat_password,
        reply_to=agent_jid,
        system_prompt=CHAT_PROMPT,
        verify_security=False  # Disable security for built-in server
    )

    # 6. START AGENTS
    try:
        await agent.start()
        await chat_agent.start()
        await asyncio.sleep(2)  # Time for connection

        print("✅ Agents started successfully")

        # 7. INTERACTIVE DEMO
        print(f"\n{'=' * 50}")
        print("Demo of [feature] started")
        print("Type 'exit' to quit")
        print(f"{'=' * 50}")

        await chat_agent.run_interactive()

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # 8. CLEANUP
        print("\n🛑 Stopping agents...")
        await agent.stop()
        await chat_agent.stop()
        print("✅ Example completed")


if __name__ == "__main__":
    print("🔍 Prerequisites:")
    print("• SPADE built-in server running in another terminal:")
    print("  spade run")
    print("• LLM provider: OpenAI API key OR Ollama running")
    print("• Advanced server configuration available but not needed")
    print()
    
    spade.run(main())

# INSTRUCTIONS FOR USING THIS TEMPLATE:
#
# 1. Copy this file with a descriptive name
# 2. Replace [Example Title] and [Main Feature]
# 3. Modify the PROMPTS according to your specific feature
# 4. Add additional imports if necessary
# 5. Configure the LLMAgent with your example-specific options
# 6. Add specific logic in the demo section
# 7. Update the module documentation
#
# MANDATORY RULES:
# - ❌ DO NOT hardcode XMPP servers, MCP URLs, or API keys
# - ❌ DO NOT create new classes - use only existing framework classes
# - ✅ DO use input() for configurable parameters
# - ✅ DO follow the pattern: configuration → provider → agents → demo
# - ✅ DO include cleanup with try/finally
# - ✅ DO maintain the 8-step structure
# - ✅ DO provide built-in server option as RECOMMENDED
# - ✅ DO set verify_security=False for built-in server usage
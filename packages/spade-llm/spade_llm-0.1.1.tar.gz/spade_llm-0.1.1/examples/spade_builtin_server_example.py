"""
SPADE Built-in Server Example

Demonstrates SPADE_LLM with SPADE's built-in XMPP server.

PREREQUISITES:
1. Start SPADE server in another terminal:
   spade run
   
   (Advanced server configuration available but not needed)

2. Install dependencies:
   pip install spade_llm

This example shows:
- Simple multi-agent communication via SPADE's default built-in server (localhost:5222)
- Automatic agent registration (no external XMPP accounts needed)
- Tool integration with local server
"""

import asyncio
import getpass
import os
import spade

from spade_llm.agent import LLMAgent, ChatAgent
from spade_llm.providers import LLMProvider
from spade_llm.tools import LLMTool
from spade_llm.utils import load_env_vars
from datetime import datetime


# Simple tool functions for demonstration
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_simple_math(expression: str) -> str:
    """Safely evaluate a simple mathematical expression."""
    try:
        # Basic safety: only allow numbers and basic operators
        allowed_chars = set('0123456789+-*/().,')
        if not all(c in allowed_chars for c in expression.replace(' ', '')):
            return "Error: Only basic math operations allowed"
        
        result = eval(expression, {"__builtins__": {}})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_server_info() -> str:
    """Get information about the SPADE server connection."""
    return "Connected to SPADE built-in server (localhost:5222)"


async def main():
    """Main function demonstrating SPADE built-in server usage."""
    print("🚀 SPADE_LLM with Built-in Server Example")
    print("=" * 50)
    print()
    
    # Check if user started the SPADE server
    print("📋 Prerequisites Check:")
    print("1. ✅ Make sure you started SPADE server in another terminal:")
    print("   spade run")
    print("   (Advanced server configuration available but not needed)")
    print()
    
    input("Press Enter when SPADE server is running...")
    print()
    
    # Load environment variables
    load_env_vars()
    
    # SPADE server configuration (using default built-in server)
    SPADE_SERVER = "localhost"
    SPADE_PORT = 5222
    
    print(f"🌐 Connecting to SPADE server: {SPADE_SERVER}:{SPADE_PORT}")
    
    # LLM Provider setup
    provider_choice = input("Choose LLM provider (openai/ollama): ").lower()
    
    if provider_choice == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            api_key = input("Enter OpenAI API key: ")
        
        provider = LLMProvider.create_openai(
            api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.7
        )
    else:  # ollama
        model = input("Ollama model (default: gemma2:2b): ") or "gemma2:2b"
        provider = LLMProvider.create_ollama(
            model=model,
            base_url="http://localhost:11434/v1",
            temperature=0.7,
            timeout=60.0
        )
    
    # Create tools for the agent
    tools = [
        LLMTool(
            name="get_current_time",
            description="Get current date and time",
            parameters={"type": "object", "properties": {}, "required": []},
            func=get_current_time
        ),
        LLMTool(
            name="calculate_simple_math",
            description="Calculate simple math expressions",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string", 
                        "description": "Math expression to calculate (e.g., '2+2', '10*5')"
                    }
                },
                "required": ["expression"]
            },
            func=calculate_simple_math
        ),
        LLMTool(
            name="get_server_info",
            description="Get SPADE server connection information",
            parameters={"type": "object", "properties": {}, "required": []},
            func=get_server_info
        )
    ]
    
    # Agent credentials (auto-register with SPADE server)
    print("\n🤖 Agent Setup:")
    print("Note: Agents will auto-register with the SPADE built-in server")
    
    # Create unique JIDs for this session
    session_id = datetime.now().strftime("%H%M%S")
    llm_jid = f"assistant_{session_id}@{SPADE_SERVER}"
    chat_jid = f"human_{session_id}@{SPADE_SERVER}"
    
    # Simple passwords (SPADE server will handle registration)
    llm_password = "assistant_pass"
    chat_password = "human_pass"
    
    print(f"🤖 LLM Agent: {llm_jid}")
    print(f"👤 Chat Agent: {chat_jid}")
    
    # Create LLM agent with tools
    llm_agent = LLMAgent(
        jid=llm_jid,
        password=llm_password,
        provider=provider,
        system_prompt="""You are a helpful AI assistant running on SPADE's built-in server. 
        You have access to tools for time, math calculations, and server info.
        Be friendly and demonstrate your capabilities!""",
        tools=tools
    )
    
    # Display callback for chat
    def display_response(message: str, sender: str):
        print(f"\n🤖 Assistant: {message}")
        print("-" * 50)
    
    def on_message_sent(message: str, recipient: str):
        print(f"👤 You: {message}")
    
    # Create chat agent
    chat_agent = ChatAgent(
        jid=chat_jid,
        password=chat_password,
        target_agent_jid=llm_jid,
        display_callback=display_response,
        on_message_sent=on_message_sent
    )
    
    try:
        # Start agents
        print("\n🚀 Starting agents...")
        await llm_agent.start()
        print(f"✅ LLM Agent started: {llm_jid}")
        
        await chat_agent.start()
        print(f"✅ Chat Agent started: {chat_jid}")
        
        # Wait for connections to establish
        await asyncio.sleep(2)
        
        print("\n🎉 SUCCESS: Multi-agent system running on SPADE built-in server!")
        print("\n💬 Chat Interface:")
        print("=" * 50)
        print("Try these commands:")
        print("• 'What time is it?' - Uses time tool")
        print("• 'Calculate 25 * 4' - Uses math tool") 
        print("• 'What server am I connected to?' - Uses server info tool")
        print("• 'Tell me a joke' - Regular conversation")
        print("• 'exit' - Quit the demo")
        print()
        
        # Run interactive chat
        await chat_agent.run_interactive(
            input_prompt="SPADE> ",
            exit_command="exit"
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure SPADE server is running:")
        print("   spade run")
        print("2. Check if another process is using port 5222")
        print("3. Verify LLM provider (OpenAI API key or Ollama running)")
        
    finally:
        # Cleanup
        print("\n🔄 Stopping agents...")
        try:
            await chat_agent.stop()
            print("✅ Chat agent stopped")
        except:
            pass
        
        try:
            await llm_agent.stop()
            print("✅ LLM agent stopped")
        except:
            pass
        
        print("\n👋 SPADE built-in server demo completed!")
        print("🛑 Don't forget to stop the SPADE server (Ctrl+C in the other terminal)")


if __name__ == "__main__":
    print("🔍 SPADE Built-in Server Demo")
    print("🔧 Prerequisites:")
    print("• SPADE 4.0+ installed: pip install spade_llm")
    print("• SPADE server running in another terminal: spade run")
    print("• LLM provider: OpenAI API key OR Ollama running")
    print("• Advanced server configuration available but not needed")
    print()
    
    spade.run(main())
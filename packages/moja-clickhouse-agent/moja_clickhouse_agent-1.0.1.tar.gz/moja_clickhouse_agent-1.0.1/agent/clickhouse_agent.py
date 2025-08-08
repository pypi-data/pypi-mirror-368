"""
ClickHouse AI Agent - Main agent implementation
Based on the architecture from fren and erpai-agent
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner

from ui.minimal_interface import ui

from config.settings import ClickHouseConfig
from providers.openrouter import OpenRouterProvider
from providers.local_llm import LocalLLMProvider
from tools.clickhouse_tools import ClickHouseConnection, ClickHouseToolExecutor, OPENAI_TOOLS
from tools.data_tools import DataLoader, DataVisualizer, DataExporter
from utils.logging import get_logger

logger = get_logger(__name__)
console = Console()

class ClickHouseAgent:
    """Main ClickHouse AI Agent class"""
    
    def __init__(self, config: ClickHouseConfig):
        self.config = config
        self.connection = ClickHouseConnection(config)
        self.tool_executor = None
        self.data_loader = None
        self.data_visualizer = None
        self.data_exporter = None
        self.llm_provider = None
        self.conversation_history = []
        self.max_tool_calls = config.max_tool_calls
        self.current_tool_calls = 0
        
    async def initialize(self):
        """Initialize all components"""
        
        # Initialize ClickHouse connection
        await self.connection.connect()
        
        # Initialize tool executor
        self.tool_executor = ClickHouseToolExecutor(self.connection)
        await self.tool_executor.initialize()
        
        # Initialize data utilities
        self.data_loader = DataLoader(self.tool_executor.client)
        self.data_visualizer = DataVisualizer(self.tool_executor.client)
        self.data_exporter = DataExporter(self.tool_executor.client)
        
        # Initialize LLM provider (default to local)
        if self.config.provider == "openrouter":
            if not self.config.openrouter_api_key:
                raise ValueError("OpenRouter API key is required for OpenRouter provider")
            self.llm_provider = OpenRouterProvider(
                api_key=self.config.openrouter_api_key,
                model=self.config.openrouter_model,
                provider_only=self.config.openrouter_provider_only,
                data_collection=self.config.openrouter_data_collection
            )
        else:
            self.llm_provider = LocalLLMProvider(
                base_url=self.config.local_llm_base_url,
                model=self.config.local_llm_model
            )
        
        logger.info("ClickHouse AI Agent initialized successfully")
    
    async def start_interactive_session(self):
        """Start interactive chat session"""
        
        await self.initialize()
        
        console.print("[dim bright_cyan]●[/dim bright_cyan] [bright_white]Ready to help with your data![/bright_white]")
        console.print("[dim]Type your questions or commands. Type 'exit' to quit.[/dim]\n")
        
        # Force reset conversation history completely
        self.conversation_history = []
        self.current_tool_calls = 0
        
        # Initialize conversation history cleanly
        system_message = self._build_system_prompt()
        self.conversation_history = [
            {"role": "system", "content": system_message}
        ]
        
        try:
            while True:
                # Get user input with beautiful prompt
                ui.show_user_input_prompt()
                user_input = input().strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    ui.show_goodbye()
                    break
                
                if user_input.lower() in ['clear', 'reset']:
                    self.conversation_history = [
                        {"role": "system", "content": system_message}
                    ]
                    self.current_tool_calls = 0
                    ui.show_success("Conversation reset")
                    continue
                
                # Add user message to conversation
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Process the conversation
                await self._process_conversation()
                
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
        finally:
            await self._cleanup()
    
    async def _process_conversation(self):
        """Process the conversation with the AI agent"""
        
        # Simple validation - ensure clean conversation history
        if not self.conversation_history:
            logger.warning("Empty conversation history detected, initializing")
            system_message = self._build_system_prompt()
            self.conversation_history = [
                {"role": "system", "content": system_message}
            ]
        elif self.conversation_history[0].get("role") != "system":
            logger.warning("Invalid conversation history, reinitializing")
            system_message = self._build_system_prompt()
            self.conversation_history = [
                {"role": "system", "content": system_message}
            ]
        
        stop_requested = False
        last_tool_calls = []  # Track recent tool calls to prevent loops
        
        # Create the live animation outside the context manager so we can control it manually
        live = ui.show_thinking_animation()
        live.start()
        
        try:
            while self.current_tool_calls < self.max_tool_calls and not stop_requested:
                print(f"\n")
                try:
                    # from rich.console import Console
                    # from rich.panel import Panel
                    # import json

                    # console = Console()
                    # formatted_history = json.dumps(self.conversation_history, indent=2, ensure_ascii=False)
                    # console.print(Panel.fit(formatted_history, title="Conversation History", border_style="cyan"))
                    # Make LLM call with OpenAI format tools
                    response = await self.llm_provider.chat_completion(
                        messages=self.conversation_history,
                        tools=OPENAI_TOOLS,
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens,
                        live_animation=live
                    )
                    # Extract message from OpenAI response
                    message = response["choices"][0]["message"]
                    # import json
                    # from rich.console import Console
                    # from rich.syntax import Syntax

                    # console = Console()
                    # formatted_json = json.dumps(response, indent=2, ensure_ascii=False)
                    # syntax = Syntax(formatted_json, "json", theme="monokai", line_numbers=False)
                    # console.print("[bold magenta]LLM Response:[/bold magenta]")
                    # console.print(syntax)

                    assistant_msg = {
                        **message,
                        "role": "assistant"
                    }
                    self.conversation_history.append(assistant_msg)

                    # Process the response
                    text_content = message.get("content", "")
                    tool_calls = message.get("tool_calls", [])
                    if tool_calls is None:
                        tool_calls = []

                    # Display text content (streaming already handled this, now persist and stop the live animation)
                    if text_content:
                        live.stop()
                        # Extract reasoning if available
                        reasoning = message.get("reasoning")
                        # Show the final streamed content with markdown rendering and reasoning
                        ui.show_agent_response_markdown(text_content, reasoning)
                        ui.console.print()

                    # Execute tools if present; otherwise, finish this turn
                    if tool_calls and len(tool_calls) > 0:
                        # Check for repeated tool calls (infinite loop prevention)
                        current_tool_names = [tool_call["function"]["name"] for tool_call in tool_calls]
                        # last_tool_calls.append(current_tool_names)
                        # if last_tool_calls and len(last_tool_calls) > 3:  # Keep only last 3 calls
                        #     last_tool_calls.pop(0)
                        tool_results = []
                        for tool_call in tool_calls:
                            tool_name = tool_call["function"]["name"]
                            tool_input = json.loads(tool_call["function"]["arguments"])
                            tool_id = tool_call["id"]
                            # Switch to tool execution animation
                            live.stop()
                            tool_live = ui.show_tool_execution(tool_name, f"Running {tool_name.replace('_', ' ')}")
                            tool_live.start()
                            try:
                                # Check for stop agent
                                if tool_name == "stop_agent":
                                    summary = tool_input.get("summary", "Task completed")
                                    result = f"Agent stopped: {summary}"
                                    # Add tool result BEFORE breaking (required for OpenAI format)
                                    tool_results.append({
                                        "tool_call_id": tool_id,
                                        "name": tool_name,
                                        "content": result
                                    })
                                    ui.show_success(summary)
                                    stop_requested = True
                                    break
                                # Execute the tool
                                result = await self._execute_tool(tool_name, tool_input)
                                # Store tool result for conversation history
                                tool_results.append({
                                    "tool_call_id": tool_id,
                                    "name": tool_name,
                                    "content": result
                                })
                                self.current_tool_calls += 1
                            finally:
                                tool_live.stop()
                        # Add tool results to conversation (OpenAI format)
                        for tool_result in tool_results:
                            self.conversation_history.append({
                                "role": "tool",
                                "tool_call_id": tool_result["tool_call_id"],
                                "name": tool_result["name"],
                                "content": tool_result["content"]
                            })
                        # If stop was requested, we're done - don't continue the loop
                        if stop_requested:
                            print(f"Stop requested: {stop_requested}")
                            break
                    else:
                        # No tools requested by the model; finish processing this user turn
                        break
                except Exception as e:
                    live.stop()
                    ui.show_error(f"Error in conversation processing: {e}")
                    logger.error(f"Error in conversation processing: {e}")
                    # Simple reset on any error
                    system_message = self._build_system_prompt()
                    self.conversation_history = [
                        {"role": "system", "content": system_message}
                    ]
                    self.current_tool_calls = 0
                    break
        finally:
            print("Stopping live animation")
            live.stop()  # Ensure the animation is always stopped
            print()  # Print a blank line to clear any spinner from the terminal
        # Check if we hit the tool call limit
        if self.current_tool_calls >= self.max_tool_calls:
            ui.show_warning(f"Reached maximum tool calls limit ({self.max_tool_calls})")
    
    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result"""
        
        try:
            if tool_name == "execute_clickhouse_query":
                return await self.tool_executor.execute_clickhouse_query(
                    query=tool_input["query"]
                )
            
            elif tool_name == "list_tables":
                return await self.tool_executor.list_tables()
            
            elif tool_name == "get_table_schema":
                return await self.tool_executor.get_table_schema(
                    table_name=tool_input["table_name"]
                )
            
            elif tool_name == "search_table":
                return await self.tool_executor.search_table(
                    table_name=tool_input["table_name"],
                    limit=tool_input.get("limit", 100),
                    where_clause=tool_input.get("where_clause")
                )
            
            elif tool_name == "stop_agent":
                # This is handled in the main conversation loop
                return f"Agent stopped: {tool_input.get('summary', 'Task completed')}"
            
            else:
                return f"Unknown tool: {tool_name}"
                
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(f"Tool {tool_name} failed: {e}")
            return error_msg
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI agent"""
        
        return f"""You are Moja, an expert ClickHouse AI agent designed to help users analyze data, run queries, and manage their ClickHouse database.

CORE CAPABILITIES:
🔍 Query Execution: Execute any SQL query and display results
📊 Data Analysis: Analyze data patterns, find anomalies, generate insights
📈 Data Exploration: Search tables, examine schemas, investigate data quality
🔧 Database Management: Understand table structures and relationships

AVAILABLE TOOLS:
{self._format_tools_for_prompt()}

INSTRUCTIONS:
1. Use multiple tools as needed to thoroughly analyze and understand data
2. For anomaly detection, run multiple queries to examine different aspects of the data
3. Provide detailed insights and explanations of your findings
4. Always explain what you're doing and why
5. Use execute_clickhouse_query for any clickhouse query operations
6. Use stop_agent to end the conversation when you're done
7. CALLING stop_agent is very very crucial when you are done what user has precisely asked for.
CURRENT CONNECTION:
- Host: {self.config.host}:{self.config.port}
- Database: {self.config.database}
- User: {self.config.username}


Rule:
Know when to stop.
Your context window is limited so fetch as many insight that covers whole db in as less rows as possible. But cover the whole db. its fine up to 100 rows not more than that. but ideally the number would be very very less than 100.
Do not repeat yourself. Do not go into infinite loop. Call stop_agent when a response has been given which would be enough for what user said.
CALL stop_agent function/tool when a valid response has been given.

Remember: You are an expert data analyst. Be thorough and provide comprehensive analysis."""
    

    
    def _format_tools_for_prompt(self) -> str:
        """Format tools list for the system prompt"""
        
        tool_descriptions = []
        for tool in OPENAI_TOOLS:
            tool_descriptions.append(f"• {tool['function']['name']}: {tool['function']['description']}")
        
        return "\n".join(tool_descriptions)
    
    async def execute_single_query(self, query: str, output_format: str = "table", save_to: Optional[Path] = None):
        """Execute a single query (for CLI query command)"""
        
        await self.initialize()
        
        try:
            result = await self.tool_executor.execute_query(
                query=query,
                format=output_format
            )
            
            if save_to and output_format != "table":
                with open(save_to, 'w') as f:
                    f.write(result)
                console.print(f"[green]✓ Results saved to {save_to}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
        finally:
            await self._cleanup()
    
    async def analyze_table(self, table_name: str, deep: bool = False):
        """Analyze a specific table (for CLI analyze command)"""
        
        await self.initialize()
        
        try:
            result = await self.tool_executor.analyze_table(
                table_name=table_name,
                sample_size=50000 if deep else 10000
            )
            console.print(result)
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
        finally:
            await self._cleanup()
    
    async def load_data_from_file(
        self,
        file_path: Path,
        table_name: str,
        create_table: bool = True,
        batch_size: int = 10000
    ):
        """Load data from file (for CLI load-data command)"""
        
        await self.initialize()
        
        try:
            if file_path.suffix.lower() == '.csv':
                result = await self.data_loader.load_from_csv(
                    file_path=str(file_path),
                    table_name=table_name,
                    create_table=create_table,
                    batch_size=batch_size
                )
            elif file_path.suffix.lower() == '.json':
                result = await self.data_loader.load_from_json(
                    file_path=str(file_path),
                    table_name=table_name,
                    create_table=create_table,
                    batch_size=batch_size
                )
            else:
                console.print(f"[red]❌ Unsupported file format: {file_path.suffix}[/red]")
                return
            
            console.print(f"[green]✓ {result}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
        finally:
            await self._cleanup()
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            if self.llm_provider:
                await self.llm_provider.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Export the main class
__all__ = ['ClickHouseAgent']
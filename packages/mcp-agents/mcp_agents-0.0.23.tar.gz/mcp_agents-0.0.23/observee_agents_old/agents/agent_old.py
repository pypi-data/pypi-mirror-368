"""
Simple MCP agent with Anthropic and tool filtering enabled by default
"""

import os
from typing import List, Dict, Any, Optional, Union
from fastmcp import Client
from dotenv import load_dotenv
import logging
import json

from ..search import create_filter
from ..search.cloud_infrastructure import VectorStoreManager
from ..providers.base import LLMProvider

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI 
from langchain_google_genai import ChatGoogleGenerativeAI   
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from ..utils.langchain_converter import LangChainConverter
from ..utils.tool_converter import convert_tools_to_anthropic, convert_custom_tools, clear_tool_cache

logger = logging.getLogger(__name__)


class MCPAgent:
    """Modular MCP agent that supports multiple LLM providers with tool filtering"""
    
    def __init__(
        self, 
        provider: Union[str, LLMProvider] = "anthropic",
        server_name: str = "observee", 
        model: Optional[str] = None,
        server_url: str = None,
        sync_tools: bool = True,
        filter_type: Optional[str] = None,
        enable_filtering: bool = True,
        auth_token: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **provider_kwargs
    ):
        load_dotenv()
        
        # Server configuration
        self.server_name = server_name
        self.auth_token = auth_token  # Store auth token for native MCP
        
        # server_url is required
        if not server_url:
            raise ValueError("server_url is required. Please provide the MCP server URL.")
        
        self.server_url = server_url
        
        # Create MCP client config
        config = {
            "mcpServers": {
                server_name: {"url": self.server_url}
            }
        }
        
        # Add headers if auth token is provided
        if auth_token:
            config["mcpServers"][server_name]["headers"] = {
                "Authorization": f"Bearer {auth_token}"
            }
        
        # Initialize MCP client
        self.mcp = Client(config)
        
        # Store filtering configuration
        self.enable_filtering = enable_filtering
        
        # Initialize tool filter only if filtering is enabled
        if enable_filtering:
            # Determine filter type - default is always bm25
            if filter_type is None:
                filter_type = "bm25"
            
            # Initialize vector store manager for cloud filters
            self.vector_store_manager = None
            if filter_type == "cloud":
                try:
                    self.vector_store_manager = VectorStoreManager(
                        use_cloud=True,
                        sync_tools=sync_tools
                    )
                    logger.debug("Vector store manager initialized for cloud search")
                except Exception as e:
                    logger.warning(f"Failed to initialize vector store: {e}. Falling back to BM25.")
                    filter_type = "bm25"
            
            # Create tool filter
            self.tool_filter = create_filter(
                filter_type=filter_type,
                vector_store_manager=self.vector_store_manager,
                sync_tools=sync_tools
            )
            self.tool_filter.set_server_info(server_name, server_url)
            
            logger.info(f"Using {filter_type} filter for tool search")
        else:
            self.tool_filter = None
            self.vector_store_manager = None
            logger.info("Tool filtering disabled - using native MCP")
        
        # Initialize LLM provider
        self._initialize_provider(provider, model, **provider_kwargs)
        
        # Model to use
        self.model = model or self._get_default_model()
        
        # Store all tools
        self.all_tools = []
        
        # Tool converter cache - clear on init to ensure fresh start
        clear_tool_cache()
        
        # Conversation history
        self.messages = []
        
        # System prompt configuration
        self.system_prompt = system_prompt or "You are a helpful AI assistant with access to various tools. Always use the appropriate tools to answer questions when they are available."
        
        # Context manager state
        self._client_context = None
    
    def _initialize_provider(self, provider: Union[str, LLMProvider], model: Optional[str], **kwargs):
        """Initialize the LLM provider"""
        if isinstance(provider, LLMProvider):
            self.provider = provider
            self.provider_name = provider.__class__.__name__
        else:
            # String provider name - load from registry
            from ..providers import PROVIDERS
            
            provider_lower = provider.lower()
            if provider_lower not in PROVIDERS:
                raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")
            
            provider_class = PROVIDERS[provider_lower]
            provider_args = kwargs.copy()
            if model:
                provider_args['model'] = model
            
            self.provider = provider_class(**provider_args)
            self.provider_name = provider_lower
        
        # Set MCP client for LangChain provider
        if hasattr(self.provider, 'set_mcp_client'):
            self.provider.set_mcp_client(self.mcp)
    
    def _get_default_model(self) -> str:
        """Get default model based on provider"""
        defaults = {
            "anthropic": "claude-sonnet-4-20250514",
            "openai": "gpt-4o",
            "gemini": "gemini-2.5-pro",
            "groq": "moonshotai/kimi-k2-instruct"
        }
        return defaults.get(self.provider_name, "default")
    
    async def __aenter__(self):
        """Enter async context"""
        self._client_context = await self.mcp.__aenter__()
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if self._client_context:
            await self.mcp.__aexit__(exc_type, exc_val, exc_tb)
    
    async def initialize(self):
        """Initialize the MCP connection and load tools"""
        # Get all available tools
        tools = await self.mcp.list_tools()
        self.all_tools = tools
        
        # Add tools to filter if filtering is enabled
        if self.enable_filtering and self.tool_filter:
            self.tool_filter.add_tools(tools)
        
        logger.debug(f"Loaded {len(tools)} tools from {self.server_name}")
        if self.enable_filtering and self.tool_filter:
            logger.debug(f"Categories discovered: {self.tool_filter.get_categories()}")
    
    async def chat(self, message: str, max_tools: int = 20, min_score: float = 8.0, context: Optional[Dict[str, Any]] = None, execute_tools: bool = True, custom_tools: Optional[List[Dict[str, Any]]] = None):
        """
        Chat with the agent using filtered tools
        
        Args:
            message: User message
            max_tools: Maximum number of tools to include (default 10)
            context: Optional context for tool filtering
            custom_tools: Optional list of custom tools in OpenAI format
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": message})
        
        # When filtering is enabled, use LangChain for ALL providers
        if self.enable_filtering and self.tool_filter:
            filtered_tools = await self.tool_filter.filter_tools(message, max_tools=max_tools, min_score=min_score, context=context)
            
            logger.debug(f"Filtered to {len(filtered_tools)} relevant tools for query: '{message}'")
            if filtered_tools:
                logger.debug(f"Top tools: {[t.name for t in filtered_tools[:5]]}")
            
            # Use LangChain for all providers when filtering is enabled
            try:
                # Import LangChain dependencies
                
                # Create LangChain LLM based on provider
                if self.provider_name == "anthropic":
                    llm = ChatAnthropic(
                        model=self.model,
                        temperature=0.7,
                        api_key=os.getenv("ANTHROPIC_API_KEY")
                    )
                elif self.provider_name == "openai":
                    llm = ChatOpenAI(
                        model=self.model,
                        temperature=0.7,
                        api_key=os.getenv("OPENAI_API_KEY")
                    )
                elif self.provider_name == "gemini":
                    llm = ChatGoogleGenerativeAI(
                        model=self.model,
                        temperature=0.7,
                        google_api_key=os.getenv("GOOGLE_API_KEY")
                    )
                else:
                    raise ValueError(f"Unsupported provider for LangChain: {self.provider_name}")
                
                # Create LangChain adapter
                adapter = LangChainConverter(self.mcp)
                
                # Convert filtered tools to LangChain format
                # We need to get the original tools with their schemas
                original_filtered_tools = []
                for filtered_tool in filtered_tools:
                    # Find the original tool with full schema
                    original_tool = next((t for t in self.all_tools if t.name == filtered_tool.name), None)
                    if original_tool:
                        original_filtered_tools.append(original_tool)
                
                langchain_tools = adapter.convert_tools_to_langchain(original_filtered_tools)
                
                if langchain_tools:
                    # Create agent prompt with configurable system prompt
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", self.system_prompt),
                        MessagesPlaceholder(variable_name="chat_history"),
                        ("human", "{input}"),
                        MessagesPlaceholder(variable_name="agent_scratchpad"),
                    ])
                    
                    # Create the agent
                    agent = create_tool_calling_agent(llm, langchain_tools, prompt)
                    agent_executor = AgentExecutor(
                        agent=agent,
                        tools=langchain_tools,
                        verbose=False,
                        max_iterations=10,
                        return_intermediate_steps=True,
                        handle_parsing_errors=True
                    )
                    
                    # Convert messages to LangChain format for chat history
                    langchain_history = []
                    # Skip the last message (current query) from history
                    for msg in self.messages[:-1]:
                        if msg["role"] == "user":
                            langchain_history.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            langchain_history.append(AIMessage(content=msg["content"]))
                    
                    # Run the agent
                    try:
                        # Extract just the message content (last user message)
                        current_query = self.messages[-1]["content"]
                        
                        result = await agent_executor.ainvoke({
                            "input": current_query,
                            "chat_history": langchain_history
                        })
                    except Exception as e:
                        logger.error(f"Agent execution error: {e}")
                        # Fallback to direct LLM call
                        result = {
                            "output": "I encountered an error while trying to use the tools. Please try again.",
                            "intermediate_steps": []
                        }
                    
                    # Extract tool calls from intermediate steps
                    tool_calls = []
                    if "intermediate_steps" in result:
                        for action in result["intermediate_steps"]:
                            if hasattr(action, "tool") and hasattr(action, "tool_input"):
                                tool_calls.append({
                                    "name": action.tool,
                                    "input": action.tool_input if isinstance(action.tool_input, dict) else {"input": action.tool_input}
                                })
                    
                    response = {
                        "content": result.get("output", ""),
                        "tool_calls": tool_calls
                    }
                else:
                    # No tools, just use LLM directly
                    langchain_history = []
                    for msg in self.messages[:-1]:
                        if msg["role"] == "user":
                            langchain_history.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            langchain_history.append(AIMessage(content=msg["content"]))
                    
                    # Add system message and current query
                    messages_to_send = [
                        SystemMessage(content=self.system_prompt),
                        *langchain_history,
                        HumanMessage(content=self.messages[-1]["content"])
                    ]
                    
                    response_msg = await llm.ainvoke(messages_to_send)
                    response = {
                        "content": response_msg.content,
                        "tool_calls": []
                    }
                
            except ImportError as e:
                logger.error(f"LangChain dependencies not installed: {e}")
                logger.info("Falling back to direct provider call")
                # Fallback to direct provider call
                # Get original tools that match filtered tools
                original_filtered_tools = []
                for tool in filtered_tools:
                    original_tool = next((t for t in self.all_tools if t.name == tool.name), None)
                    if original_tool:
                        original_filtered_tools.append(original_tool)
                
                # Convert to Anthropic format using our converter
                anthropic_tools = convert_tools_to_anthropic(original_filtered_tools)
                
                # Add custom tools if provided
                if custom_tools:
                    converted_custom_tools, _ = convert_custom_tools(custom_tools)
                    anthropic_tools.extend(converted_custom_tools)
                
                # Prepend system prompt to messages
                messages_with_system = [{"role": "system", "content": self.system_prompt}] + self.messages
                
                response = await self.provider.generate(
                    messages=messages_with_system,
                    tools=anthropic_tools if anthropic_tools else None,
                    max_tokens=1000
                )
            
            filtered_tools_count = len(filtered_tools)
            filtered_tools_list = [t.name for t in filtered_tools]
        else:
            # Use native MCP when filtering is disabled
            # Prepend system prompt to messages
            messages_with_system = [{"role": "system", "content": self.system_prompt}] + self.messages
            
            if self.provider_name == "anthropic":
                # Anthropic with native MCP support
                mcp_config = {
                    "type": "url",
                    "url": self.server_url,
                    "name": self.server_name
                }
                
                # Add authorization token if available
                if self.auth_token:
                    mcp_config["authorization_token"] = self.auth_token
                
                response = await self.provider.generate(
                    messages=messages_with_system,
                    mcp_config=mcp_config,
                    temperature=0.7
                )
            elif self.provider_name == "gemini":
                # Gemini with FastMCP session
                provider_config = {"mcp_config": {"session": self.mcp.session}}
                response = await self.provider.generate(
                    messages=messages_with_system,
                    mcp_config=provider_config["mcp_config"],
                    temperature=0.7
                )
            else:
                # Standard tool-based approach for other providers
                # Convert all tools to standard format using our converter
                openai_tools = convert_tools_to_anthropic(self.all_tools)
                
                # Add custom tools if provided
                if custom_tools:
                    converted_custom_tools, _ = convert_custom_tools(custom_tools)
                    openai_tools.extend(converted_custom_tools)
                
                response = await self.provider.generate(
                    messages=messages_with_system,
                    tools=openai_tools if openai_tools else None,
                    max_tokens=1000
                )
            
            filtered_tools_count = len(self.all_tools) + (len(custom_tools) if custom_tools else 0)
            filtered_tools_list = [t.name for t in self.all_tools]
            if custom_tools:
                filtered_tools_list.extend([ct["function"]["name"] for ct in custom_tools if ct.get("type") == "function" and "function" in ct and "name" in ct["function"]])
        
        # Call LLM provider with appropriate configuration
        try:
            # Extract response from provider format
            content = response.get("content", "")
            tool_calls = []
            
            # Handle tool calls from response
            for tc in response.get("tool_calls", []):
                if tc.get("type") == "function":
                    func = tc.get("function", {})
                    try:
                        args = json.loads(func.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        args = {}
                    
                    tool_calls.append({
                        "name": func.get("name"),
                        "input": args
                    })
            
            # Add assistant response to history
            self.messages.append({"role": "assistant", "content": content})
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "filtered_tools_count": filtered_tools_count,
                "filtered_tools": filtered_tools_list,
                "used_filtering": self.enable_filtering
            }
            
        except Exception as e:
            logger.error(f"Error calling {self.provider_name}: {e}")
            raise
    
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool call through MCP"""
        try:
            result = await self.mcp.call_tool(tool_name, tool_input)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.messages = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        return self.messages.copy()
    
    async def chat_with_tools(self, message: str, max_tools: int = 20, min_score: float = 8.0, custom_tools: Optional[List[Dict[str, Any]]] = None, custom_tool_handler: Optional[callable] = None):
        # Get initial response with tool calls
        initial_response = await self.chat(message, max_tools=max_tools, min_score=min_score, custom_tools=custom_tools)
        
        # If no tool calls, return the response as is
        if not initial_response['tool_calls']:
            return initial_response
        
        # Extract custom tool names for checking
        _, custom_tool_names = convert_custom_tools(custom_tools) if custom_tools else ([], [])
        
        # Execute tools and collect results
        tool_results = []
        for tool_call in initial_response['tool_calls']:
            try:
                # Check if it's a custom tool
                if tool_call['name'] in custom_tool_names and custom_tool_handler:
                    # Execute custom tool
                    result = await custom_tool_handler(tool_call['name'], tool_call['input'])
                    tool_results.append({
                        'tool': tool_call['name'],
                        'result': str(result)
                    })
                else:
                    # Execute MCP tool
                    result = await self.execute_tool(tool_call['name'], tool_call['input'])
                    tool_results.append({
                        'tool': tool_call['name'],
                        'result': str(result)
                    })
            except Exception as e:
                tool_results.append({
                    'tool': tool_call['name'],
                    'error': str(e)
                })
        
        # Format tool results for the assistant
        tool_results_text = "\n\n".join([
            f"Tool: {r['tool']}\nResult: {r.get('result', r.get('error', 'No result'))}"
            for r in tool_results
        ])
        
        # Add tool results to conversation
        self.messages.append({
            "role": "user",
            "content": f"{tool_results_text}"
        })
        
        # Get final response from the provider
        # Prepend system prompt to messages
        if self.system_prompt:
            messages_with_system = [{"role": "system", "content": self.system_prompt}] + self.messages
        else:
            messages_with_system = self.messages
        
        final_response = await self.provider.generate(
            messages=messages_with_system,
        )
        
        # Extract final content
        final_content = final_response.get("content", "")
        
        # Add to history
        self.messages.append({"role": "assistant", "content": final_content})
        
        return {
            "content": final_content,
            "initial_response": initial_response['content'],
            "tool_calls": initial_response['tool_calls'],
            "tool_results": tool_results,
            "filtered_tools_count": initial_response['filtered_tools_count'],
            "filtered_tools": initial_response['filtered_tools'],
            "used_filtering": initial_response['used_filtering']
        }
    
    async def chat_stream(self, message: str, max_tools: int = 20, min_score: float = 8.0, custom_tools: Optional[List[Dict[str, Any]]] = None):
        """
        Stream chat response with filtered tools
        
        Args:
            message: User message
            max_tools: Maximum number of tools to include
            min_score: Minimum relevance score for tools
            custom_tools: Optional list of custom tools in OpenAI format
            
        Yields:
            Dict with streaming data
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": message})
        
        # Get filtered tools if filtering is enabled
        if self.enable_filtering and self.tool_filter:
            filtered_tools = await self.tool_filter.filter_tools(message, max_tools=max_tools, min_score=min_score)
            
            logger.debug(f"Filtered to {len(filtered_tools)} relevant tools for query: '{message}'")
            
            # Get original tools that match filtered tools
            original_filtered_tools = []
            for tool in filtered_tools:
                original_tool = next((t for t in self.all_tools if t.name == tool.name), None)
                if original_tool:
                    original_filtered_tools.append(original_tool)
            
            # Convert tools to standard format using our converter
            openai_tools = convert_tools_to_anthropic(original_filtered_tools)
            
            # Add custom tools if provided
            if custom_tools:
                converted_custom_tools, _ = convert_custom_tools(custom_tools)
                openai_tools.extend(converted_custom_tools)
            
            filtered_tools_count = len(filtered_tools) + (len(custom_tools) if custom_tools else 0)
            filtered_tools_list = [t.name for t in filtered_tools]
            if custom_tools:
                filtered_tools_list.extend([ct["function"]["name"] for ct in custom_tools if ct.get("type") == "function" and "function" in ct and "name" in ct["function"]])
        else:
            # Use all tools when filtering is disabled
            openai_tools = convert_tools_to_anthropic(self.all_tools)
            
            # Add custom tools if provided
            if custom_tools:
                converted_custom_tools, _ = convert_custom_tools(custom_tools)
                openai_tools.extend(converted_custom_tools)
            
            filtered_tools_count = len(self.all_tools) + (len(custom_tools) if custom_tools else 0)
            filtered_tools_list = [t.name for t in self.all_tools]
            if custom_tools:
                filtered_tools_list.extend([ct["function"]["name"] for ct in custom_tools if ct.get("type") == "function" and "function" in ct and "name" in ct["function"]])
        
        # Stream response from provider
        accumulated_content = ""
        tool_calls = []
        
        # Determine MCP configuration based on provider and filtering settings
        mcp_config = None
        tools_to_use = None
        
        if self.enable_filtering:
            logger.info(f"Using converted tools: {openai_tools} from here")
            # When filtering is enabled, always use converted tools
            tools_to_use = openai_tools if openai_tools else None
        else:
            # When filtering is disabled, use native MCP support where available
            if self.provider_name == "anthropic":
                logger.info(f"Using native MCP with config: {mcp_config} from here")
                # Anthropic with native MCP support
                mcp_config = {
                    "type": "url",
                    "url": self.server_url,
                    "name": self.server_name
                }
                
                # Add authorization token if available
                if self.auth_token:
                    mcp_config["authorization_token"] = self.auth_token
                    
            elif self.provider_name == "gemini":
                # Gemini with FastMCP session
                mcp_config = {"session": self.mcp.session}
            else:
                # Standard tool-based approach for other providers
                tools_to_use = openai_tools if openai_tools else None
        
        # Prepend system prompt to messages
        messages_with_system = [{"role": "system", "content": self.system_prompt}] + self.messages
        
        async for chunk in self.provider.generate_stream(
            messages=messages_with_system,
            tools=tools_to_use,
            mcp_config=mcp_config,
            max_tokens=1000,
            temperature=0.7
        ):
            if chunk["type"] == "content":
                accumulated_content += chunk["content"]
                yield {
                    "type": "content",
                    "content": chunk["content"]
                }
            elif chunk["type"] == "tool_call":
                tool_calls.append(chunk["tool_call"])
                yield {
                    "type": "tool_call",
                    "tool_call": chunk["tool_call"]
                }
            elif chunk["type"] == "done":
                # Add assistant response to history
                self.messages.append({"role": "assistant", "content": accumulated_content})
                
                # Yield final metadata
                yield {
                    "type": "metadata",
                    "filtered_tools_count": filtered_tools_count,
                    "filtered_tools": filtered_tools_list,
                    "used_filtering": self.enable_filtering,
                    "tool_calls": tool_calls
                }
                break
    
    async def chat_with_tools_stream(self, message: str, max_tools: int = 20, min_score: float = 8.0, custom_tools: Optional[List[Dict[str, Any]]] = None, custom_tool_handler: Optional[callable] = None):
        """
        Complete streaming chat flow: initial response, tool execution, and final response
        
        Args:
            message: User message
            max_tools: Maximum number of tools to include
            min_score: Minimum relevance score for tools
            custom_tools: Optional list of custom tools in OpenAI format
            
        Yields:
            Dict with streaming data - content, tool_call, tool_result, tool_error, final_content, done
        """
        initial_tool_calls = []
        accumulated_content = ""
        
        async for chunk in self.chat_stream(message, max_tools=max_tools, min_score=min_score, custom_tools=custom_tools):
            if chunk["type"] == "content":
                accumulated_content += chunk["content"]
                yield chunk
            elif chunk["type"] == "tool_call":
                initial_tool_calls.append(chunk["tool_call"])
                # Include all context in tool_call
                chunk["initial_content"] = accumulated_content
                yield chunk
            elif chunk["type"] == "metadata":
                metadata = chunk
                break
        
        # If no tool calls, we're done
        if not initial_tool_calls:
            yield {"type": "done", "final_response": {
                "content": accumulated_content,
                "tool_calls": [],
                "tool_results": [],
                "filtered_tools_count": metadata["filtered_tools_count"],
                "filtered_tools": metadata["filtered_tools"],
                "used_filtering": metadata["used_filtering"]
            }}
            return
        
        # Extract custom tool names for checking
        _, custom_tool_names = convert_custom_tools(custom_tools) if custom_tools else ([], [])
        
        tool_results = []
        for tool_call in initial_tool_calls:
            try:
                # Parse tool call arguments
                function_info = tool_call.get("function", {})
                tool_name = function_info.get("name", "")
                
                # Skip empty tool names
                if not tool_name:
                    continue
                
                # Parse arguments
                arguments = function_info.get("arguments", "{}")
                if isinstance(arguments, str):
                    import json
                    try:
                        args = json.loads(arguments) if arguments.strip() else {}
                    except json.JSONDecodeError:
                        args = {}
                else:
                    args = arguments if arguments else {}
                
                # Check if it's a custom tool
                if tool_name in custom_tool_names and custom_tool_handler:
                    # Execute custom tool
                    result = await custom_tool_handler(tool_name, args)
                    tool_results.append({
                        'tool': tool_name,
                        'result': str(result)
                    })
                else:
                    # Execute MCP tool
                    result = await self.execute_tool(tool_name, args)
                    tool_results.append({
                        'tool': tool_name,
                        'result': str(result)
                    })
                
                yield {
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "result": str(result)
                }
            except Exception as e:
                tool_results.append({
                    'tool': tool_name,
                    'error': str(e)
                })
                
                yield {
                    "type": "tool_error",
                    "tool_name": tool_name,
                    "error": str(e)
                }
        
        # Format tool results for the assistant
        tool_results_text = "\n\n".join([
            f"Tool: {r['tool']}\nResult: {r.get('result', r.get('error', 'No result'))}"
            for r in tool_results
        ])
        
        # Add tool results to conversation
        self.messages.append({
            "role": "user",
            "content": f"{tool_results_text}"
        })
        
        # Stream final response
        final_content = ""
        
        # Determine MCP configuration for final response (no tools needed for final response)
        final_mcp_config = None
        if not self.enable_filtering:
            if self.provider_name == "anthropic":
                # Anthropic with native MCP support
                final_mcp_config = {
                    "type": "url",
                    "url": self.server_url,
                    "name": self.server_name
                }
                
                # Add authorization token if available
                if self.auth_token:
                    final_mcp_config["authorization_token"] = self.auth_token
                    
            elif self.provider_name == "gemini":
                # Gemini with FastMCP session
                final_mcp_config = {"session": self.mcp.session}
        
        # Prepend system prompt to messages
        messages_with_system = [{"role": "system", "content": self.system_prompt}] + self.messages
        
        async for chunk in self.provider.generate_stream(
            messages=messages_with_system,
            mcp_config=final_mcp_config,
            max_tokens=1000
        ):
            if chunk["type"] == "content":
                final_content += chunk["content"]
                yield {
                    "type": "final_content",
                    "content": chunk["content"]
                }
            elif chunk["type"] == "done":
                # Add to history
                self.messages.append({"role": "assistant", "content": final_content})
                
                # Yield completion
                yield {"type": "done", "final_response": {
                    "content": final_content,
                    "initial_response": accumulated_content,
                    "tool_calls": initial_tool_calls,
                    "tool_results": tool_results,
                    "filtered_tools_count": metadata["filtered_tools_count"],
                    "filtered_tools": metadata["filtered_tools"],
                    "used_filtering": metadata["used_filtering"]
                }}
                break
"""Main agent logic"""
import json
from typing import List, Dict, Any, Generator
from openai import OpenAI

from .config import Config
from .tools import ToolRegistry
from .memory import Memory


class Agent:
    """LocalClaw Agent"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.client = OpenAI(
            base_url=self.config.model_base_url,
            api_key="ollama"  # Ollama doesn't need a real API key
        )
        self.tools = ToolRegistry(
            workspace_path=self.config.workspace_path,
            restrict_to_workspace=self.config.restrict_to_workspace
        )
        self.memory = Memory(
            db_path=self.config.memory_db_path,
            collection_name="localclaw_memory"
        )
        self.conversation_history: List[Dict[str, Any]] = []
    
    def chat(self, message: str, stream: bool = True) -> Generator[str, None, None]:
        """Chat with the agent"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Get tool definitions
        tool_definitions = self.tools.get_tool_definitions()
        
        # Call LLM
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=self._build_messages(),
                tools=tool_definitions,
                tool_choice="auto",
                temperature=self.config.model_temperature,
                max_tokens=self.config.model_max_tokens,
                stream=stream
            )
            
            if stream:
                yield from self._handle_streaming_response(response)
            else:
                result = self._handle_response(response)
                yield result
                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def _build_messages(self) -> List[Dict[str, Any]]:
        """Build message list for LLM"""
        messages = [
            {"role": "system", "content": self.config.system_prompt}
        ]
        messages.extend(self.conversation_history)
        return messages
    
    def _handle_streaming_response(self, response) -> Generator[str, None, None]:
        """Handle streaming response from LLM"""
        content_buffer = ""
        tool_calls = []
        
        for chunk in response:
            delta = chunk.choices[0].delta
            
            # Handle content
            if delta.content:
                content_buffer += delta.content
                yield delta.content
            
            # Handle tool calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if len(tool_calls) <= tc.index:
                        tool_calls.append({"name": "", "arguments": ""})
                    if tc.function.name:
                        tool_calls[tc.index]["name"] = tc.function.name
                    if tc.function.arguments:
                        tool_calls[tc.index]["arguments"] += tc.function.arguments
        
        # Execute tools if any
        if tool_calls:
            yield "\n\n🔧 Executing tools...\n"
            for tc in tool_calls:
                tool_name = tc["name"]
                try:
                    tool_args = json.loads(tc["arguments"])
                except json.JSONDecodeError:
                    tool_args = {}
                
                result = self.tools.execute(tool_name, **tool_args)
                yield f"**{tool_name}**: {result[:500]}...\n" if len(result) > 500 else f"**{tool_name}**: {result}\n"
                
                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": tool_name, "arguments": tc["arguments"]}}]
                })
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": "call_1",
                    "content": result
                })
            
            # Get final response after tool execution
            yield "\n💭 Thinking...\n"
            final_response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=self._build_messages(),
                temperature=self.config.model_temperature,
                max_tokens=self.config.model_max_tokens,
                stream=True
            )
            
            final_content = ""
            for chunk in final_response:
                if chunk.choices[0].delta.content:
                    final_content += chunk.choices[0].delta.content
                    yield chunk.choices[0].delta.content
            
            if final_content:
                self.conversation_history.append({"role": "assistant", "content": final_content})
        else:
            # No tool calls, just save the content
            if content_buffer:
                self.conversation_history.append({"role": "assistant", "content": content_buffer})
    
    def _handle_response(self, response) -> str:
        """Handle non-streaming response"""
        message = response.choices[0].message
        
        if message.tool_calls:
            # Handle tool calls
            results = []
            for tc in message.tool_calls:
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments)
                result = self.tools.execute(tool_name, **tool_args)
                results.append(f"{tool_name}: {result}")
            return "\n".join(results)
        
        return message.content or "(no response)"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def save_memory(self, content: str, category: str = "general"):
        """Save to long-term memory"""
        memory_id = self.memory.save(content, category)
        return f"Saved to memory: {memory_id}"
    
    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """Search long-term memory"""
        return self.memory.search(query)

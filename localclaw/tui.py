"""TUI interface for LocalClaw using Textual"""
import asyncio
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Input, Static, Button, 
    DirectoryTree, TextArea, TabbedContent, TabPane
)
from textual.reactive import reactive
from rich.markdown import Markdown

from localclaw.config import Config
from localclaw.agent import Agent


class Message(Static):
    """A chat message widget"""
    
    def __init__(self, content: str, is_user: bool = False, **kwargs):
        self.message_content = content
        self.is_user = is_user
        super().__init__(**kwargs)
    
    def compose(self) -> ComposeResult:
        prefix = "👤 You" if self.is_user else "🦞 LocalClaw"
        classes = "user-message" if self.is_user else "agent-message"
        yield Static(f"[bold]{prefix}[/bold]\n{self.message_content}", classes=classes)


class LocalClawApp(App):
    """LocalClaw TUI Application"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
    }
    
    #sidebar {
        width: 25%;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }
    
    #chat-area {
        width: 75%;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }
    
    #messages {
        height: 85%;
        border: solid $primary-lighten-2;
        padding: 1;
        overflow-y: auto;
    }
    
    #input-area {
        height: 15%;
        border: solid $primary-lighten-1;
        padding: 1;
    }
    
    #message-input {
        width: 85%;
    }
    
    #send-button {
        width: 15%;
    }
    
    .user-message {
        background: $primary-darken-2;
        color: $text;
        padding: 1;
        margin: 1 0;
        border-left: solid $primary;
    }
    
    .agent-message {
        background: $surface-darken-1;
        color: $text;
        padding: 1;
        margin: 1 0;
        border-left: solid $success;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $primary-darken-2;
        color: $text;
        content-align: center middle;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+l", "clear", "Clear Chat"),
    ]
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.agent: Optional[Agent] = None
        self.is_processing = False
        super().__init__()
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal(id="main-container"):
            # Sidebar with file browser
            with Vertical(id="sidebar"):
                yield Static("[bold]Workspace[/bold]", classes="sidebar-header")
                yield DirectoryTree(self.config.workspace_path)
            
            # Main chat area
            with Vertical(id="chat-area"):
                with VerticalScroll(id="messages"):
                    yield Message(
                        "Welcome to LocalClaw! 🦞\n"
                        "Your local AI assistant. Type a message to start.",
                        is_user=False
                    )
                
                with Horizontal(id="input-area"):
                    yield Input(
                        placeholder="Type your message here...",
                        id="message-input"
                    )
                    yield Button("Send", id="send-button", variant="primary")
        
        yield Static(
            f"Model: {self.config.model_name} | Workspace: {self.config.workspace_path}",
            id="status-bar"
        )
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize agent on mount"""
        try:
            self.agent = Agent(self.config)
            self.query_one("#status-bar", Static).update(
                f"✅ Connected | Model: {self.config.model_name}"
            )
        except Exception as e:
            self.query_one("#status-bar", Static).update(
                f"❌ Error: {e}"
            )
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        if event.input.id == "message-input":
            await self.send_message()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        if event.button.id == "send-button":
            await self.send_message()
    
    async def send_message(self) -> None:
        """Send message to agent"""
        if self.is_processing or not self.agent:
            return
        
        input_widget = self.query_one("#message-input", Input)
        message = input_widget.value.strip()
        
        if not message:
            return
        
        # Clear input
        input_widget.value = ""
        
        # Add user message
        messages_container = self.query_one("#messages", VerticalScroll)
        messages_container.mount(Message(message, is_user=True))
        messages_container.scroll_end()
        
        # Show processing status
        self.is_processing = True
        self.query_one("#status-bar", Static).update("🤔 Thinking...")
        
        # Get agent response
        try:
            response_text = ""
            async for chunk in self.stream_response(message):
                response_text += chunk
                # Update last message
                messages_container.children[-1].message_content = response_text
                messages_container.children[-1].refresh()
            
            # Add final response as new message
            messages_container.mount(Message(response_text, is_user=False))
            messages_container.scroll_end()
            
        except Exception as e:
            messages_container.mount(Message(f"Error: {e}", is_user=False))
        
        finally:
            self.is_processing = False
            self.query_one("#status-bar", Static).update(
                f"✅ Ready | Model: {self.config.model_name}"
            )
    
    async def stream_response(self, message: str):
        """Stream response from agent"""
        loop = asyncio.get_event_loop()
        
        # Run sync generator in executor
        def run_chat():
            return list(self.agent.chat(message, stream=True))
        
        chunks = await loop.run_in_executor(None, run_chat)
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.01)  # Small delay for smooth streaming
    
    def action_clear(self) -> None:
        """Clear chat history"""
        messages_container = self.query_one("#messages", VerticalScroll)
        messages_container.remove_children()
        messages_container.mount(Message(
            "Chat cleared. Start a new conversation!",
            is_user=False
        ))
        if self.agent:
            self.agent.clear_history()


def run_tui():
    """Run the TUI application"""
    app = LocalClawApp()
    app.run()


if __name__ == "__main__":
    run_tui()

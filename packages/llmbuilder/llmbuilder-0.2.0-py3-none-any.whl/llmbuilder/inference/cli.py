"""
Interactive command-line interface for text generation.

This module provides an interactive CLI for chatting with trained models
and adjusting generation parameters in real-time.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union

from ..utils import get_logger, ModelError
from .generate import TextGenerator, GenerationConfig

logger = get_logger("inference.cli")


class InferenceCLI:
    """
    Interactive command-line interface for text generation.
    
    Provides a chat-like interface for interacting with trained models
    with real-time parameter adjustment and command support.
    """
    
    def __init__(self, 
                 model_path: Union[str, Path],
                 tokenizer_path: Union[str, Path],
                 device: Optional[str] = None,
                 config: Optional[GenerationConfig] = None):
        """
        Initialize the interactive CLI.
        
        Args:
            model_path: Path to trained model checkpoint
            tokenizer_path: Path to tokenizer directory
            device: Device to run inference on
            config: Generation configuration
        """
        self.generator = TextGenerator(
            model_path=model_path,
            tokenizer_path=tokenizer_path,
            device=device,
            config=config
        )
        
        # CLI state
        self.running = True
        self.commands = {
            'help': self._show_help,
            'settings': self._show_settings,
            'set': self._set_parameter,
            'reset': self._reset_settings,
            'quit': self._quit,
            'exit': self._quit,
            'clear': self._clear_screen,
        }
        
        logger.info("Interactive CLI initialized")
    
    def run(self):
        """Run the interactive CLI."""
        self._show_welcome()
        
        while self.running:
            try:
                user_input = input("\n💬 Prompt: ").strip()
                
                if not user_input:
                    continue
                
                # Check if it's a command
                if user_input.startswith('/'):
                    self._handle_command(user_input[1:])
                else:
                    # Generate text
                    self._generate_and_display(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"CLI error: {e}")
                print(f"❌ Error: {e}")
    
    def _show_welcome(self):
        """Display welcome message."""
        print("\n" + "="*60)
        print("🤖 LLMBuilder Interactive Text Generation")
        print("="*60)
        print("Welcome! Start chatting with your AI model.")
        print("\nCommands:")
        print("  /help      - Show available commands")
        print("  /settings  - Show current generation settings")
        print("  /set <param> <value> - Change a setting")
        print("  /reset     - Reset settings to defaults")
        print("  /clear     - Clear screen")
        print("  /quit      - Exit the program")
        print("\nTip: Just type your message to start generating!")
        print("="*60)
    
    def _handle_command(self, command_line: str):
        """Handle CLI commands."""
        parts = command_line.split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                print(f"❌ Command error: {e}")
        else:
            print(f"❌ Unknown command: {command}")
            print("Type /help for available commands")
    
    def _show_help(self, args):
        """Show help information."""
        print("\n📖 Available Commands:")
        print("  /help                    - Show this help message")
        print("  /settings                - Show current generation settings")
        print("  /set <param> <value>     - Change a generation parameter")
        print("  /reset                   - Reset all settings to defaults")
        print("  /clear                   - Clear the screen")
        print("  /quit, /exit             - Exit the program")
        print("\n⚙️  Available Parameters:")
        print("  max_new_tokens          - Maximum tokens to generate (default: 100)")
        print("  temperature             - Sampling temperature (default: 0.8)")
        print("  top_k                   - Top-k sampling (default: 50)")
        print("  top_p                   - Top-p/nucleus sampling (default: 0.9)")
        print("  repetition_penalty      - Repetition penalty (default: 1.0)")
        print("  do_sample               - Use sampling vs greedy (default: true)")
        print("\n💡 Examples:")
        print("  /set temperature 0.5    - Make generation more focused")
        print("  /set max_new_tokens 200 - Generate longer responses")
        print("  /set do_sample false    - Use greedy decoding")
    
    def _show_settings(self, args):
        """Show current generation settings."""
        config = self.generator.config
        print("\n⚙️  Current Generation Settings:")
        print(f"  max_new_tokens:     {config.max_new_tokens}")
        print(f"  temperature:        {config.temperature}")
        print(f"  top_k:              {config.top_k}")
        print(f"  top_p:              {config.top_p}")
        print(f"  do_sample:          {config.do_sample}")
        print(f"  repetition_penalty: {config.repetition_penalty}")
        print(f"  early_stopping:     {config.early_stopping}")
    
    def _set_parameter(self, args):
        """Set a generation parameter."""
        if len(args) < 2:
            print("❌ Usage: /set <parameter> <value>")
            print("Type /help for available parameters")
            return
        
        param_name = args[0].lower()
        param_value = args[1]
        
        try:
            # Convert value to appropriate type
            if param_name in ['max_new_tokens', 'top_k']:
                value = int(param_value)
            elif param_name in ['temperature', 'top_p', 'repetition_penalty', 'length_penalty']:
                value = float(param_value)
            elif param_name in ['do_sample', 'early_stopping']:
                value = param_value.lower() in ['true', '1', 'yes', 'on']
            else:
                print(f"❌ Unknown parameter: {param_name}")
                print("Type /help for available parameters")
                return
            
            # Update the configuration
            if hasattr(self.generator.config, param_name):
                setattr(self.generator.config, param_name, value)
                print(f"✅ Set {param_name} = {value}")
            else:
                print(f"❌ Invalid parameter: {param_name}")
                
        except ValueError as e:
            print(f"❌ Invalid value for {param_name}: {param_value}")
        except Exception as e:
            print(f"❌ Error setting parameter: {e}")
    
    def _reset_settings(self, args):
        """Reset settings to defaults."""
        self.generator.config = GenerationConfig()
        print("✅ Settings reset to defaults")
    
    def _clear_screen(self, args):
        """Clear the screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self._show_welcome()
    
    def _quit(self, args):
        """Quit the CLI."""
        self.running = False
        print("👋 Goodbye!")
    
    def _generate_and_display(self, prompt: str):
        """Generate text and display the result."""
        print("\n🤔 Thinking...")
        
        try:
            # Generate text
            generated_text = self.generator.generate(prompt)
            
            # Display result
            print(f"\n🤖 Response:")
            print("-" * 50)
            print(generated_text)
            print("-" * 50)
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            print(f"❌ Generation failed: {e}")


def interactive_cli(model_path: Union[str, Path],
                   tokenizer_path: Union[str, Path],
                   device: Optional[str] = None,
                   config: Optional[GenerationConfig] = None):
    """
    Start an interactive CLI session.
    
    Args:
        model_path: Path to trained model checkpoint
        tokenizer_path: Path to tokenizer directory
        device: Device to run inference on
        config: Generation configuration
    """
    try:
        cli = InferenceCLI(
            model_path=model_path,
            tokenizer_path=tokenizer_path,
            device=device,
            config=config
        )
        cli.run()
    except Exception as e:
        logger.error(f"CLI initialization failed: {e}")
        print(f"❌ Failed to start interactive CLI: {e}")
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive LLM Text Generation CLI")
    parser.add_argument("--model", type=str, required=True,
                       help="Path to trained model checkpoint")
    parser.add_argument("--tokenizer", type=str, required=True,
                       help="Path to tokenizer directory")
    parser.add_argument("--device", type=str, default=None,
                       help="Device to use (cpu/cuda)")
    parser.add_argument("--temperature", type=float, default=0.8,
                       help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=100,
                       help="Maximum tokens to generate")
    parser.add_argument("--top-k", type=int, default=50,
                       help="Top-k sampling")
    parser.add_argument("--top-p", type=float, default=0.9,
                       help="Top-p sampling")
    
    args = parser.parse_args()
    
    # Create generation config
    config = GenerationConfig(
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p
    )
    
    # Start interactive CLI
    interactive_cli(
        model_path=args.model,
        tokenizer_path=args.tokenizer,
        device=args.device,
        config=config
    )


if __name__ == "__main__":
    main()
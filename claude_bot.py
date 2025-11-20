"""
Claude AI-Powered Portfolio Bot
Integrates Anthropic's Claude 3.5 API with developer portfolio metadata
"""

import os
import json
from pathlib import Path
from typing import Optional, Iterator
import anthropic


class ClaudePortfolioBot:
    """AI chatbot powered by Claude 3.5 for portfolio inquiries."""
    
    def __init__(self, portfolio_data_path: str = "portfolio_data.json", api_key: Optional[str] = None):
        """Initialize Claude bot with portfolio data and API key."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set it as environment variable or pass as argument."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.portfolio_data = self._load_portfolio_data(portfolio_data_path)
        self.system_prompt = self._build_system_prompt()
        self.conversation_history = []
    
    def _load_portfolio_data(self, path: str) -> dict:
        """Load portfolio data from JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Portfolio data file not found: {path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {path}")
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt with portfolio data."""
        dev = self.portfolio_data.get("developer", {})
        skills = self.portfolio_data.get("skills", {})
        projects = self.portfolio_data.get("projects", [])
        experience = self.portfolio_data.get("experience", {})
        
        # Format projects
        projects_text = "\n".join([
            f"""
**{p.get('name', 'Unknown')}**
- Subtitle: {p.get('subtitle', '')}
- Type: {p.get('type', '')}
- Description: {p.get('description', '')}
- Tech Stack: {', '.join(p.get('tech_stack', []))}
- Features: {', '.join(p.get('features', []))}
- Impact: {p.get('impact', '')}
- Key Learning: {p.get('key_learning', '')}
- Status: {p.get('status', '')}
"""
            for p in projects
        ])
        
        # Format skills
        skills_text = "\n".join([
            f"- {category.replace('_', ' ').title()}: {', '.join(items)}"
            if isinstance(items, list)
            else f"- {category.replace('_', ' ').title()}: {items}"
            for category, items in skills.items()
        ])
        
        system_prompt = f"""You are an AI assistant representing {dev.get('name', 'a developer')}'s GitHub portfolio and professional profile.

DEVELOPER PROFILE:
- Name: {dev.get('name', 'Unknown')}
- Alias: {dev.get('alias', 'N/A')}
- Role: {dev.get('role', 'N/A')}
- GitHub: {dev.get('github', 'N/A')}
- Summary: {dev.get('summary', 'N/A')}

TECHNICAL SKILLS:
{skills_text}

PORTFOLIO PROJECTS:
{projects_text}

CAREER INTERESTS:
{', '.join(experience.get('career_interests', []))}

CURRENT FOCUS:
{experience.get('current_focus', 'N/A')}

YOUR RESPONSIBILITIES:
1. Answer questions about projects with accurate technical details
2. Explain code examples and architectural decisions
3. Provide recruiter-friendly professional summaries
4. Suggest improvements and new project ideas
5. Explain learning concepts in simple, clear language
6. Generate code examples when requested
7. Provide learning roadmaps for skill development
8. Be personable, professional, and helpful

GUIDELINES:
- Speak in first person as the developer
- Use the provided portfolio data as your source of truth
- When asked about code, provide working, well-documented examples
- For improvements, give specific, actionable suggestions
- Maintain a friendly, mentor-like tone
- If you don't know specific details, say so and provide general expertise
- Always cite relevant projects or technologies from the portfolio
- Help recruiters understand the developer's capabilities
- Be enthusiastic about discussing projects and learning

TONE: Professional but friendly, mentor-style, encouraging, knowledgeable."""
        
        return system_prompt
    
    def chat(self, user_message: str, stream: bool = False) -> str | Iterator[str]:
        """
        Send a message and get a response from Claude.
        
        Args:
            user_message: User's question or message
            stream: Whether to stream the response
            
        Returns:
            Response text or iterator of response chunks if streaming
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        if stream:
            return self._stream_response()
        else:
            return self._get_response()
    
    def _get_response(self) -> str:
        """Get non-streaming response from Claude."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def _stream_response(self) -> Iterator[str]:
        """Get streaming response from Claude."""
        full_response = ""
        
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=self.conversation_history
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                yield text
        
        # Add complete response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
    
    def reset_conversation(self):
        """Clear conversation history to start fresh."""
        self.conversation_history = []
    
    def get_conversation_history(self) -> list:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def generate_code_example(self, topic: str, language: str = "python") -> str:
        """
        Generate a code example for a specific topic.
        
        Args:
            topic: What the code should demonstrate
            language: Programming language
            
        Returns:
            Code example as string
        """
        prompt = f"Generate a {language} code example for: {topic}. Make it production-ready and well-documented."
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def get_project_summary(self, project_name: str) -> str:
        """Get a detailed summary of a specific project."""
        prompt = f"Provide a detailed summary of the {project_name} project including its purpose, tech stack, key features, and what was learned."
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def get_recruiter_pitch(self) -> str:
        """Generate a professional recruiter pitch."""
        prompt = "Generate a compelling 2-3 paragraph pitch for a recruiter explaining my background, skills, and what makes me a great fit for a team."
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def explain_concept(self, concept: str, level: str = "intermediate") -> str:
        """
        Explain an ML/AI concept at different difficulty levels.
        
        Args:
            concept: The concept to explain
            level: 'beginner', 'intermediate', or 'advanced'
            
        Returns:
            Explanation of the concept
        """
        prompt = f"Explain the concept '{concept}' at a {level} level, with examples if relevant."
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


def main():
    """Interactive CLI for Claude Portfolio Bot."""
    print("=" * 60)
    print("Welcome to Claude-Powered GitHub Portfolio Bot!")
    print("=" * 60)
    print("\nI'm an AI assistant for Nishan Bhurtel's portfolio.")
    print("Ask me anything about projects, skills, code, or career!")
    print("Commands: 'reset' to clear history, 'exit' to quit.\n")
    
    try:
        bot = ClaudePortfolioBot()
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. ANTHROPIC_API_KEY is set as environment variable")
        print("2. portfolio_data.json exists in current directory")
        return
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'exit':
            print("\nBot: Thanks for chatting! Check out my projects on GitHub. Goodbye! 👋")
            break
        
        if user_input.lower() == 'reset':
            bot.reset_conversation()
            print("Bot: Conversation history cleared. Let's start fresh!\n")
            continue
        
        try:
            print("\nBot: ", end="", flush=True)
            # Stream response for interactive CLI
            for chunk in bot.chat(user_input, stream=True):
                print(chunk, end="", flush=True)
            print("\n")
        except anthropic.APIError as e:
            print(f"\nError: API request failed - {e}\n")


if __name__ == "__main__":
    main()

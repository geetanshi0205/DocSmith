import os
from typing import Dict, List, Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

class ClaudeDocGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    def generate_overview(self, codebase_info: Dict) -> str:
        prompt = f"""
        Analyze this codebase and generate a comprehensive architecture overview:

        Project Structure:
        {codebase_info.get('structure', '')}

        Key Files Content:
        {codebase_info.get('key_files', '')}

        Technologies Detected:
        {codebase_info.get('technologies', '')}

        Please provide:
        1. High-level architecture overview
        2. Main components and their relationships
        3. Key design patterns used
        4. Data flow and system boundaries
        5. Technology stack explanation

        Format the response as a professional technical document.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def generate_developer_guide(self, codebase_info: Dict) -> str:
        prompt = f"""
        Create a developer onboarding guide for this codebase:

        Project Structure:
        {codebase_info.get('structure', '')}

        Setup Instructions:
        {codebase_info.get('setup_files', '')}

        Key Components:
        {codebase_info.get('key_files', '')}

        Please provide:
        1. Getting started guide
        2. Development environment setup
        3. Code organization explanation
        4. Common development workflows
        5. Testing and deployment procedures
        6. Contributing guidelines

        Make it beginner-friendly but comprehensive.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def generate_api_docs(self, api_info: Dict) -> str:
        prompt = f"""
        Generate API documentation for this codebase:

        API Endpoints/Functions:
        {api_info.get('endpoints', '')}

        Models/Schemas:
        {api_info.get('models', '')}

        Configuration:
        {api_info.get('config', '')}

        Please provide:
        1. API reference with endpoints/functions
        2. Request/response examples
        3. Authentication requirements
        4. Error handling
        5. Rate limiting and usage guidelines

        Use clear, standardized API documentation format.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def explain_code_section(self, code: str, context: str = "") -> str:
        prompt = f"""
        Explain this code section in detail:

        Context: {context}

        Code:
        ```
        {code}
        ```

        Please provide:
        1. What this code does (high-level purpose)
        2. How it works (step-by-step breakdown)
        3. Key algorithms or patterns used
        4. Dependencies and relationships
        5. Potential improvements or considerations

        Make the explanation clear for developers at different skill levels.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
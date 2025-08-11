import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import json

from code_analyzer import CodebaseAnalyzer
from claude_integration import ClaudeDocGenerator

class DocumentationGenerator:
    def __init__(self):
        self.analyzer = CodebaseAnalyzer()
        self.claude = ClaudeDocGenerator()
    
    def generate_full_documentation(self, codebase_path: str, doc_types: List[str]) -> Dict[str, str]:
        analysis = self.analyzer.analyze_codebase(codebase_path)
        documentation = {}
        
        if 'architecture_overview' in doc_types:
            documentation['architecture_overview'] = self.claude.generate_overview(analysis)
        
        if 'developer_guide' in doc_types:
            documentation['developer_guide'] = self.claude.generate_developer_guide(analysis)
        
        if 'api_documentation' in doc_types:
            api_info = self._extract_api_info(analysis)
            documentation['api_documentation'] = self.claude.generate_api_docs(api_info)
        
        return documentation
    
    def generate_code_explanation(self, code: str, file_path: str = "", language: str = "") -> str:
        context = f"File: {file_path}, Language: {language}" if file_path else f"Language: {language}"
        return self.claude.explain_code_section(code, context)
    
    def generate_markdown_docs(self, documentation: Dict[str, str], output_dir: str) -> Dict[str, str]:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        generated_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for doc_type, content in documentation.items():
            filename = f"{doc_type}_{timestamp}.md"
            file_path = output_path / filename
            
            markdown_content = self._format_as_markdown(content, doc_type)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            generated_files[doc_type] = str(file_path)
        
        return generated_files
    
    def _extract_api_info(self, analysis: Dict) -> Dict:
        api_info = {
            'endpoints': [],
            'models': [],
            'config': []
        }
        
        key_files = analysis.get('key_files', {})
        
        for file_path, content in key_files.items():
            if self._looks_like_api_file(file_path, content):
                api_info['endpoints'].append(f"File: {file_path}\n{content}")
            elif self._looks_like_model_file(file_path, content):
                api_info['models'].append(f"File: {file_path}\n{content}")
            elif self._looks_like_config_file(file_path):
                api_info['config'].append(f"File: {file_path}\n{content}")
        
        return api_info
    
    def _looks_like_api_file(self, file_path: str, content: str) -> bool:
        api_indicators = [
            'router', 'route', 'endpoint', 'api', '@app.route',
            'def get(', 'def post(', 'def put(', 'def delete(',
            'app.get(', 'app.post(', 'app.put(', 'app.delete(',
            'router.get(', 'router.post(', 'FastAPI', 'Flask'
        ]
        return any(indicator in content for indicator in api_indicators)
    
    def _looks_like_model_file(self, file_path: str, content: str) -> bool:
        model_indicators = [
            'class.*Model', 'Schema', 'interface', 'type.*=', 'model',
            'from pydantic', 'from sqlalchemy', 'mongoose.Schema'
        ]
        return any(indicator in content for indicator in model_indicators)
    
    def _looks_like_config_file(self, file_path: str) -> bool:
        config_files = ['config', 'settings', '.env', 'constants']
        return any(config in file_path.lower() for config in config_files)
    
    def _format_as_markdown(self, content: str, doc_type: str) -> str:
        title = self._get_title_for_doc_type(doc_type)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown = f"""# {title}

*Generated on {timestamp} by DocSmith*

---

{content}

---

*This documentation was automatically generated using Claude AI. Please review and update as necessary.*
"""
        return markdown
    
    def _get_title_for_doc_type(self, doc_type: str) -> str:
        titles = {
            'architecture_overview': 'Architecture Overview',
            'developer_guide': 'Developer Guide',
            'api_documentation': 'API Documentation'
        }
        return titles.get(doc_type, doc_type.replace('_', ' ').title())
    
    def get_project_summary(self, codebase_path: str) -> Dict:
        analysis = self.analyzer.analyze_codebase(codebase_path)
        
        return {
            'project_name': Path(codebase_path).name,
            'total_files': analysis['structure']['total_files'],
            'total_lines': analysis['statistics']['total_lines'],
            'technologies': analysis['technologies'],
            'main_languages': list(analysis['statistics']['lines_by_language'].keys())[:5],
            'estimated_complexity': self._estimate_complexity(analysis)
        }
    
    def _estimate_complexity(self, analysis: Dict) -> str:
        total_lines = analysis['statistics']['total_lines']
        num_languages = len(analysis['statistics']['lines_by_language'])
        num_technologies = len(analysis['technologies'])
        
        if total_lines < 1000 and num_languages <= 2:
            return "Simple"
        elif total_lines < 10000 and num_languages <= 4:
            return "Medium"
        else:
            return "Complex"
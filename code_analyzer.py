import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import chardet
from langdetect import detect
import tiktoken

class CodebaseAnalyzer:
    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'shell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text'
        }
        
        self.config_files = {
            'package.json', 'requirements.txt', 'Gemfile', 'Cargo.toml',
            'pom.xml', 'build.gradle', 'composer.json', 'go.mod',
            'Dockerfile', 'docker-compose.yml', '.env', 'config.json',
            'settings.py', 'webpack.config.js', 'tsconfig.json'
        }
        
        self.ignore_patterns = {
            'node_modules', '__pycache__', '.git', 'venv', 'env',
            'dist', 'build', '.next', 'target', 'bin', 'obj',
            '.DS_Store', '*.pyc', '*.class', '*.o'
        }
    
    def analyze_codebase(self, path: str) -> Dict:
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        analysis = {
            'structure': self._analyze_structure(path_obj),
            'technologies': self._detect_technologies(path_obj),
            'key_files': self._extract_key_files(path_obj),
            'setup_files': self._find_setup_files(path_obj),
            'statistics': self._calculate_statistics(path_obj),
            'dependencies': self._analyze_dependencies(path_obj)
        }
        
        return analysis
    
    def _analyze_structure(self, path: Path) -> Dict:
        structure = {
            'directories': [],
            'files_by_type': {},
            'total_files': 0,
            'total_directories': 0
        }
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            relative_root = os.path.relpath(root, path)
            if relative_root != '.':
                structure['directories'].append(relative_root)
                structure['total_directories'] += 1
            
            for file in files:
                if self._should_ignore(file):
                    continue
                
                file_path = Path(root) / file
                extension = file_path.suffix.lower()
                
                if extension in self.supported_extensions:
                    file_type = self.supported_extensions[extension]
                    if file_type not in structure['files_by_type']:
                        structure['files_by_type'][file_type] = []
                    
                    relative_path = os.path.relpath(file_path, path)
                    structure['files_by_type'][file_type].append(relative_path)
                
                structure['total_files'] += 1
        
        return structure
    
    def _detect_technologies(self, path: Path) -> List[str]:
        technologies = set()
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for file in files:
                if self._should_ignore(file):
                    continue
                
                file_path = Path(root) / file
                
                if file == 'package.json':
                    technologies.update(self._analyze_package_json(file_path))
                elif file == 'requirements.txt':
                    technologies.add('Python')
                elif file == 'Cargo.toml':
                    technologies.add('Rust')
                elif file == 'go.mod':
                    technologies.add('Go')
                elif file == 'pom.xml':
                    technologies.add('Java/Maven')
                elif file.endswith('.py'):
                    technologies.add('Python')
                elif file.endswith(('.js', '.jsx')):
                    technologies.add('JavaScript')
                elif file.endswith(('.ts', '.tsx')):
                    technologies.add('TypeScript')
                elif file.endswith('.java'):
                    technologies.add('Java')
                elif file.endswith('.cpp'):
                    technologies.add('C++')
                elif file.endswith('.cs'):
                    technologies.add('C#')
                elif file.endswith('.php'):
                    technologies.add('PHP')
                elif file.endswith('.rb'):
                    technologies.add('Ruby')
                elif file.endswith('.go'):
                    technologies.add('Go')
                elif file.endswith('.rs'):
                    technologies.add('Rust')
        
        return list(technologies)
    
    def _analyze_package_json(self, file_path: Path) -> List[str]:
        technologies = ['JavaScript']
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = {
                **package_data.get('dependencies', {}),
                **package_data.get('devDependencies', {})
            }
            
            if 'react' in dependencies:
                technologies.append('React')
            if 'vue' in dependencies:
                technologies.append('Vue.js')
            if 'angular' in dependencies or '@angular/core' in dependencies:
                technologies.append('Angular')
            if 'express' in dependencies:
                technologies.append('Express.js')
            if 'next' in dependencies:
                technologies.append('Next.js')
            if 'typescript' in dependencies:
                technologies.append('TypeScript')
            
        except (json.JSONDecodeError, IOError):
            pass
        
        return technologies
    
    def _extract_key_files(self, path: Path, max_files: int = 10) -> Dict[str, str]:
        key_files = {}
        
        priority_files = [
            'main.py', 'app.py', 'index.js', 'index.ts',
            'main.js', 'server.js', 'app.js', 'Main.java',
            'main.cpp', 'main.c', 'main.go', 'lib.rs'
        ]
        
        for priority_file in priority_files:
            file_path = path / priority_file
            if file_path.exists():
                content = self._read_file_safely(file_path)
                if content:
                    key_files[priority_file] = content[:2000]
        
        if len(key_files) < max_files:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not self._should_ignore(d)]
                
                for file in files:
                    if len(key_files) >= max_files:
                        break
                    
                    if self._should_ignore(file) or file in key_files:
                        continue
                    
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in self.supported_extensions:
                        content = self._read_file_safely(file_path)
                        if content:
                            relative_path = os.path.relpath(file_path, path)
                            key_files[relative_path] = content[:2000]
        
        return key_files
    
    def _find_setup_files(self, path: Path) -> Dict[str, str]:
        setup_files = {}
        
        for file_name in self.config_files:
            file_path = path / file_name
            if file_path.exists():
                content = self._read_file_safely(file_path)
                if content:
                    setup_files[file_name] = content
        
        readme_files = ['README.md', 'README.txt', 'readme.md']
        for readme in readme_files:
            file_path = path / readme
            if file_path.exists():
                content = self._read_file_safely(file_path)
                if content:
                    setup_files[readme] = content[:3000]
                break
        
        return setup_files
    
    def _calculate_statistics(self, path: Path) -> Dict:
        stats = {
            'total_lines': 0,
            'lines_by_language': {},
            'file_count_by_language': {},
            'estimated_tokens': 0
        }
        
        encoding = tiktoken.get_encoding("cl100k_base")
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for file in files:
                if self._should_ignore(file):
                    continue
                
                file_path = Path(root) / file
                extension = file_path.suffix.lower()
                
                if extension in self.supported_extensions:
                    language = self.supported_extensions[extension]
                    content = self._read_file_safely(file_path)
                    
                    if content:
                        lines = content.count('\n') + 1
                        stats['total_lines'] += lines
                        
                        if language not in stats['lines_by_language']:
                            stats['lines_by_language'][language] = 0
                            stats['file_count_by_language'][language] = 0
                        
                        stats['lines_by_language'][language] += lines
                        stats['file_count_by_language'][language] += 1
                        
                        try:
                            tokens = len(encoding.encode(content[:4000]))
                            stats['estimated_tokens'] += tokens
                        except:
                            pass
        
        return stats
    
    def _analyze_dependencies(self, path: Path) -> Dict:
        dependencies = {
            'package_managers': [],
            'frameworks': [],
            'databases': []
        }
        
        package_json = path / 'package.json'
        if package_json.exists():
            dependencies['package_managers'].append('npm/yarn')
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'mongoose' in deps or 'mongodb' in deps:
                        dependencies['databases'].append('MongoDB')
                    if 'pg' in deps or 'postgresql' in deps:
                        dependencies['databases'].append('PostgreSQL')
                    if 'mysql2' in deps or 'mysql' in deps:
                        dependencies['databases'].append('MySQL')
            except:
                pass
        
        requirements_txt = path / 'requirements.txt'
        if requirements_txt.exists():
            dependencies['package_managers'].append('pip')
            content = self._read_file_safely(requirements_txt)
            if content:
                if 'django' in content.lower():
                    dependencies['frameworks'].append('Django')
                if 'flask' in content.lower():
                    dependencies['frameworks'].append('Flask')
                if 'fastapi' in content.lower():
                    dependencies['frameworks'].append('FastAPI')
        
        return dependencies
    
    def _read_file_safely(self, file_path: Path, max_size: int = 1024*1024) -> Optional[str]:
        try:
            if file_path.stat().st_size > max_size:
                return None
            
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')
            
            return raw_data.decode(encoding, errors='ignore')
        except Exception:
            return None
    
    def _should_ignore(self, name: str) -> bool:
        return any(pattern in name for pattern in self.ignore_patterns)
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
import os
import tempfile
import shutil
import zipfile
from pathlib import Path
import json
from typing import List, Dict
from werkzeug.utils import secure_filename
import io

from doc_generator import DocumentationGenerator
from code_analyzer import CodebaseAnalyzer
from github_handler import GitHubHandler

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Check if API key is configured
def check_api_key():
    return os.getenv("ANTHROPIC_API_KEY") is not None

@app.route('/')
def index():
    """Main page with mode selection"""
    api_configured = check_api_key()
    return render_template('index.html', api_configured=api_configured)

@app.route('/documentation-generator')
def documentation_generator():
    """Documentation generator page"""
    if not check_api_key():
        flash('API key not configured. Please set ANTHROPIC_API_KEY environment variable.', 'error')
        return redirect(url_for('index'))
    
    return render_template('doc_generator.html')

@app.route('/code-explanation')
def code_explanation():
    """Code explanation page"""
    if not check_api_key():
        flash('API key not configured. Please set ANTHROPIC_API_KEY environment variable.', 'error')
        return redirect(url_for('index'))
    
    return render_template('code_explanation.html')

@app.route('/upload-github', methods=['POST'])
def upload_github():
    """Handle GitHub repository upload"""
    github_url = request.form.get('github_url')
    branch = request.form.get('branch', 'main')
    
    if not github_url:
        return jsonify({'error': 'GitHub URL is required'}), 400
    
    try:
        github_handler = GitHubHandler()
        
        if not github_handler.is_valid_github_url(github_url):
            return jsonify({'error': 'Invalid GitHub repository URL'}), 400
        
        temp_dir = github_handler.clone_repository(github_url, branch)
        repo_info = github_handler.get_repository_info(temp_dir)
        
        # Store in session with additional metadata
        session['codebase_path'] = temp_dir
        session['repo_info'] = repo_info
        session['upload_type'] = 'github'
        session['github_url'] = github_url
        session['github_branch'] = branch
        
        return jsonify({
            'success': True,
            'repo_info': repo_info,
            'message': f'Repository {repo_info["owner"]}/{repo_info["repo_name"]} cloned successfully',
            'upload_type': 'github'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to clone repository: {str(e)}'}), 500

@app.route('/upload-zip', methods=['POST'])
def upload_zip():
    """Handle ZIP file upload"""
    if 'zip_file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['zip_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.zip'):
        return jsonify({'error': 'Please upload a ZIP file'}), 400
    
    try:
        temp_dir = tempfile.mkdtemp()
        filename = secure_filename(file.filename)
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        os.unlink(zip_path)  # Clean up the zip file
        
        # Store in session
        session['codebase_path'] = temp_dir
        session['repo_info'] = None
        session['upload_type'] = 'zip'
        session['uploaded_filename'] = filename
        
        return jsonify({
            'success': True,
            'message': f'ZIP file {filename} uploaded and extracted successfully',
            'upload_type': 'zip',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to process ZIP file: {str(e)}'}), 500

@app.route('/upload-files', methods=['POST'])
def upload_files():
    """Handle individual file uploads"""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    try:
        temp_dir = tempfile.mkdtemp()
        
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(temp_dir, filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
        
        # Store in session
        session['codebase_path'] = temp_dir
        session['repo_info'] = None
        session['upload_type'] = 'files'
        session['uploaded_files_count'] = len(files)
        
        return jsonify({
            'success': True,
            'message': f'{len(files)} files uploaded successfully',
            'upload_type': 'files',
            'files_count': len(files)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload files: {str(e)}'}), 500

@app.route('/set-local-path', methods=['POST'])
def set_local_path():
    """Handle local directory path"""
    local_path = request.form.get('local_path')
    
    if not local_path:
        return jsonify({'error': 'Local path is required'}), 400
    
    if not os.path.exists(local_path):
        return jsonify({'error': 'Directory does not exist'}), 400
    
    if not os.path.isdir(local_path):
        return jsonify({'error': 'Path is not a directory'}), 400
    
    # Store in session
    session['codebase_path'] = local_path
    session['repo_info'] = None
    
    return jsonify({
        'success': True,
        'message': f'Local directory set: {local_path}'
    })

@app.route('/generate-docs', methods=['POST'])
def generate_docs():
    """Generate documentation"""
    if 'codebase_path' not in session:
        return jsonify({'error': 'No codebase uploaded'}), 400
    
    doc_types = request.form.getlist('doc_types')
    if not doc_types:
        return jsonify({'error': 'Please select at least one documentation type'}), 400
    
    # Check if API key is configured - if not, return demo content
    if not check_api_key():
        # Return demo documentation for testing
        demo_documentation = {}
        if 'architecture_overview' in doc_types:
            demo_documentation['architecture_overview'] = """# Architecture Overview (Demo)

## System Architecture
This is a demonstration of the documentation generator. In a real scenario, this would contain:
- High-level system architecture
- Component relationships
- Design patterns
- Technology stack analysis

**Note**: This is demo content. Set ANTHROPIC_API_KEY environment variable to generate real documentation using Claude AI.
"""
        
        if 'developer_guide' in doc_types:
            demo_documentation['developer_guide'] = """# Developer Guide (Demo)

## Getting Started
This is a demonstration guide. A real developer guide would include:
- Setup instructions
- Development environment configuration
- Code structure explanation
- Common workflows

**Note**: This is demo content. Set ANTHROPIC_API_KEY environment variable to generate real documentation using Claude AI.
"""
        
        demo_project_summary = {
            'project_name': 'Demo Project',
            'total_files': 10,
            'total_lines': 500,
            'technologies': ['Python', 'Flask'],
            'main_languages': ['python'],
            'estimated_complexity': 'Demo'
        }
        
        session['documentation'] = demo_documentation
        session['project_summary'] = demo_project_summary
        
        return jsonify({
            'success': True,
            'project_summary': demo_project_summary,
            'documentation': demo_documentation,
            'demo_mode': True
        })
    
    try:
        print(f"Starting documentation generation for: {doc_types}")
        
        # Import and initialize components
        doc_generator = DocumentationGenerator()
        codebase_path = session['codebase_path']
        print(f"Codebase path: {codebase_path}")
        
        # Check if path exists, if not try to re-clone for GitHub repos
        if not os.path.exists(codebase_path):
            if session.get('upload_type') == 'github' and session.get('github_url'):
                print("GitHub repo path missing, attempting to re-clone...")
                try:
                    github_handler = GitHubHandler()
                    github_url = session.get('github_url')
                    branch = session.get('github_branch', 'main')
                    temp_dir = github_handler.clone_repository(github_url, branch)
                    session['codebase_path'] = temp_dir
                    codebase_path = temp_dir
                    print(f"Successfully re-cloned to: {temp_dir}")
                except Exception as e:
                    print(f"Failed to re-clone: {str(e)}")
                    return jsonify({'error': 'Codebase path no longer exists and failed to re-clone. Please re-upload your codebase.'}), 400
            else:
                return jsonify({'error': 'Codebase path no longer exists. Please re-upload your codebase.'}), 400
        
        # Get project summary
        print("Getting project summary...")
        project_summary = doc_generator.get_project_summary(codebase_path)
        print(f"Project summary: {project_summary}")
        
        # Generate documentation
        documentation = {}
        
        for doc_type in doc_types:
            print(f"Generating {doc_type}...")
            if doc_type == "architecture_overview":
                analyzer = CodebaseAnalyzer()
                analysis = analyzer.analyze_codebase(codebase_path)
                documentation[doc_type] = doc_generator.claude.generate_overview(analysis)
            elif doc_type == "developer_guide":
                analyzer = CodebaseAnalyzer()
                analysis = analyzer.analyze_codebase(codebase_path)
                documentation[doc_type] = doc_generator.claude.generate_developer_guide(analysis)
            elif doc_type == "api_documentation":
                analyzer = CodebaseAnalyzer()
                analysis = analyzer.analyze_codebase(codebase_path)
                api_info = doc_generator._extract_api_info(analysis)
                documentation[doc_type] = doc_generator.claude.generate_api_docs(api_info)
            print(f"Generated {doc_type} successfully")
        
        # Store results in session
        session['documentation'] = documentation
        session['project_summary'] = project_summary
        
        return jsonify({
            'success': True,
            'project_summary': project_summary,
            'documentation': documentation
        })
        
    except ImportError as e:
        error_msg = f"Missing dependency: {str(e)}. Please install required packages."
        print(f"Import error: {error_msg}")
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        import traceback
        print(f"Error generating documentation: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Check for specific API errors
        if "API key" in str(e) or "authentication" in str(e).lower():
            return jsonify({'error': 'API authentication failed. Please check your ANTHROPIC_API_KEY.'}), 500
        
        return jsonify({'error': f'Error generating documentation: {str(e)}'}), 500

@app.route('/explain-code', methods=['POST'])
def explain_code():
    """Explain code snippet"""
    code = request.form.get('code')
    language = request.form.get('language', 'Python')
    
    if not code:
        return jsonify({'error': 'Code is required'}), 400
    
    # Check if API key is configured - if not, return demo explanation
    if not check_api_key():
        demo_explanation = f"""# Code Explanation (Demo Mode)

## Code Analysis
**Language**: {language}

## What This Code Does
This is a demonstration of the code explanation feature. In a real scenario with an API key configured, Claude AI would provide:

- Detailed explanation of the code's purpose
- Step-by-step breakdown of how it works
- Key algorithms and patterns identified
- Dependencies and relationships
- Potential improvements and best practices

## Demo Code
```{language.lower()}
{code[:200]}{'...' if len(code) > 200 else ''}
```

**Note**: This is demo content. Set ANTHROPIC_API_KEY environment variable to get real AI-powered code explanations.
"""
        
        return jsonify({
            'success': True,
            'explanation': demo_explanation,
            'demo_mode': True
        })
    
    try:
        from claude_integration import ClaudeDocGenerator
        claude = ClaudeDocGenerator()
        
        explanation = claude.explain_code_section(code, language)
        
        return jsonify({
            'success': True,
            'explanation': explanation
        })
        
    except Exception as e:
        return jsonify({'error': f'Error explaining code: {str(e)}'}), 500

@app.route('/download/<doc_type>')
def download_doc(doc_type):
    """Download individual documentation file"""
    if 'documentation' not in session:
        flash('No documentation available', 'error')
        return redirect(url_for('documentation_generator'))
    
    documentation = session['documentation']
    if doc_type not in documentation:
        flash('Documentation type not found', 'error')
        return redirect(url_for('documentation_generator'))
    
    content = documentation[doc_type]
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name=f'{doc_type}.md',
        mimetype='text/markdown'
    )

@app.route('/download-all')
def download_all():
    """Download all documentation as ZIP"""
    if 'documentation' not in session:
        flash('No documentation available', 'error')
        return redirect(url_for('documentation_generator'))
    
    documentation = session['documentation']
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for doc_type, content in documentation.items():
            zip_file.writestr(f'{doc_type}.md', content)
    
    zip_buffer.seek(0)
    
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='documentation.zip',
        mimetype='application/zip'
    )

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
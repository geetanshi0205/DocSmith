# DocSmith

A powerful tool that generates human-readable documentation from complex codebases using Claude AI. Built with Python and Flask.

## ✨ Features

- **🏗️ Architecture Overview Generation**: Automatically analyzes your codebase and generates comprehensive architecture documentation
- **👨‍💻 Developer Onboarding Guides**: Creates beginner-friendly guides for new developers joining your project  
- **🔌 API Documentation**: Extracts and documents APIs, endpoints, and data models
- **🔍 Code Explanation**: Provides detailed explanations for specific code sections
- **💻 Multi-language Support**: Supports Python, JavaScript/TypeScript, Java, C++, Go, Rust, and more
- **🐙 GitHub Integration**: Clone and analyze public GitHub repositories directly
- **📦 Multiple Upload Options**: GitHub repos, ZIP files, individual files, or local directory paths
- **📥 Export Options**: Download documentation as Markdown files or ZIP archives
- **🎨 Beautiful Dark UI**: Modern, sleek dark mode interface with professional styling
- **⚡ Fast Performance**: Optimized for quick analysis and documentation generation
- **🆓 Demo Mode**: Test the interface without an API key

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd codedocs
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key (optional for demo mode):
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key to the `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and replace 'your_anthropic_api_key_here' with your actual API key
   ```

## Usage

1. Start the Flask application:
```bash
python3 server.py
```

2. Open your browser and navigate to `http://localhost:5001`

3. Choose between two main features:
   - **Documentation Generator**: Upload entire codebases for comprehensive docs
   - **Code Explanation**: Get explanations for specific code snippets

4. Upload your codebase using one of these methods:
   - **GitHub Repository**: Enter a public GitHub repo URL
   - Upload a ZIP file containing your project
   - Upload individual code files

5. Select documentation types:
   - Architecture Overview
   - Developer Guide  
   - API Documentation

6. Click "Generate Documentation" and wait for processing

7. Review and download the generated documentation

## Demo Mode

DocSmith includes a demo mode that works without an API key:
- Shows example documentation and explanations
- Demonstrates the interface and features
- Perfect for testing and evaluation
- Set `ANTHROPIC_API_KEY` for full AI-powered functionality

## Supported Technologies

The tool automatically detects and handles:

- **Languages**: Python, JavaScript, TypeScript, Java, C++, C, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, Scala
- **Frameworks**: React, Vue.js, Angular, Express.js, Django, Flask, FastAPI, Next.js
- **Databases**: MongoDB, PostgreSQL, MySQL
- **Package Managers**: npm/yarn, pip, Maven, Gradle, Cargo

## Project Structure

```
codedocs/
├── flask_app.py           # Main Flask application
├── server.py          # Application runner
├── claude_integration.py  # Claude AI integration
├── code_analyzer.py      # Codebase analysis functionality
├── doc_generator.py      # Documentation generation logic
├── github_handler.py     # GitHub repository handling
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── doc_generator.html
│   └── code_explanation.html
├── static/              # CSS and JS files
│   ├── css/main.css
│   └── js/main.js
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude AI access (optional for demo mode)

### Customization

You can customize the analysis by modifying:

- `supported_extensions` in `code_analyzer.py` - Add support for more file types
- `ignore_patterns` in `code_analyzer.py` - Customize which files/directories to ignore
- Prompt templates in `claude_integration.py` - Modify how documentation is generated
- UI styling in `static/css/main.css` - Customize the dark theme

## API Integration

The tool uses the Anthropic Claude API to generate documentation. You'll need:

1. An Anthropic account
2. API access and credits
3. Your API key configured in the application

**Note**: The app works in demo mode without an API key for testing purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Limitations

- Large codebases may take longer to process
- API usage is subject to Anthropic's rate limits and pricing
- Generated documentation should be reviewed for accuracy
- Some complex architectural patterns may require manual refinement

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
1. Check the existing issues in the repository
2. Create a new issue with detailed information about your problem
3. Include sample code and error messages when applicable

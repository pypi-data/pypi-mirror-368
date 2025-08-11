import click
import requests
import json
import os
import sys
from typing import Optional
from pathlib import Path
from cli.auth import get_authenticated_user

# Backend API configuration
BACKEND_API_URL = "http://localhost:8000"

# Global configuration cache
_config_cache = None

def get_cli_config() -> Optional[dict]:
    """Fetch CLI configuration from backend"""
    global _config_cache
    
    # Return cached config if available
    if _config_cache:
        return _config_cache
    
    # Fetch from backend
    config = make_authenticated_request("/api/cli/config")
    if config:
        _config_cache = config
        click.echo("✅ Using backend configuration")
        return config
    
    click.echo("⚠️  Using fallback configuration")
    return None

def get_mistral_api_key() -> str:
    """Get Mistral API key from backend or environment"""
    config = get_cli_config()
    if config and config.get('mistral_api_key'):
        return config['mistral_api_key']
    return ""

def get_python_agent_id() -> Optional[str]:
    res = make_authenticated_request("/api/cli/agent/python")
    if res and res.get("agent_id"):
        return res["agent_id"]
    return None

def get_cpp_agent_id() -> Optional[str]:
    res = make_authenticated_request("/api/cli/agent/cpp")
    if res and res.get("agent_id"):
        return res["agent_id"]
    return None

def get_ollama_url() -> str:
    """Get Ollama URL from backend or environment"""
    config = get_cli_config()
    if config and config.get('ollama_url'):
        return config['ollama_url']
    
    # Fallback to environment variable
    return os.getenv("OLLAMA_URL", "http://localhost:11434")

def get_prompt(language: str, framework: str, code: str, positive_cases: int, negative_cases: int) -> str:
    """Get prompt template from backend"""
    config = get_cli_config()
    if config and config.get('prompts'):
        prompts = config['prompts']
        if language in prompts and framework in prompts[language]:
            template = prompts[language][framework]
            prompt = template.format(
                code=code,
                positive_cases=positive_cases,
                negative_cases=negative_cases
            )
            click.echo(f"📝 Using backend prompt for {language}/{framework}")
            return prompt
    return None
    # Fallback to default prompts
    # click.echo(f"📝 Using fallback prompt for {language}/{framework}")
    # return get_default_prompt(language, framework, code, positive_cases, negative_cases)

def get_suffix(language: str, framework: str) -> str:
    """Get suffix template from backend"""
    config = get_cli_config()
    if config and config.get('suffixes'):
        suffixes = config['suffixes']
        if language in suffixes and framework in suffixes[language]:
            click.echo(f"📝 Using backend suffix for {language}/{framework}")
            return suffixes[language][framework]
    
    # Fallback to default suffixes
    return None
    # return get_default_suffix(language, framework)

def get_auth_token() -> Optional[str]:
    """Get authentication token from CLI config"""
    config_path = Path.home() / ".testgenie" / "config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('token')
        except:
            return None
    return None

def make_authenticated_request(endpoint: str, method: str = "GET", data: dict = None) -> Optional[dict]:
    """Make authenticated request to backend API"""
    token = get_auth_token()
    if not token:
        click.echo("❌ Not logged in. Please run 'test_genie login' first.")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BACKEND_API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            click.echo(f"Unsupported method: {method}")
            return None
        
        if response.status_code == 401:
            click.echo("❌ Token expired. Please login again with 'test_genie login'")
            return None
        elif response.status_code != 200:
            click.echo(f"❌ API Error: {response.status_code} - {response.text}")
            return None
        
        return response.json()
    
    except requests.RequestException as e:
        click.echo(f"❌ Connection error: {e}")
        return None

def log_usage_to_backend(language: str, tokens_used: int = 0):
    """Log usage to backend for analytics"""
    data = {
        "language": language,
        "tokens_used": tokens_used,
    }
    make_authenticated_request("/cli/usage", method="POST", data=data)

def read_file_content(file_path: str) -> str:
    """Read and return the content of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        click.echo(f"Error reading file {file_path}: {e}")
        sys.exit(1)

def detect_language(file_path: str) -> str:
    """Detect programming language from file extension"""
    ext = Path(file_path).suffix.lower()
    language_map = {
        '.py': 'python',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c++': 'cpp',
        '.c': 'c',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust'
    }
    return language_map.get(ext, 'python')


def generate_test_cases(file_path: str, language: str, framework: str, positive_cases: int = 2, negative_cases: int = 2) -> Optional[str]:
    """Generate test cases for the given file"""
    code_content = read_file_content(file_path)
    
    # Get prompt and suffix from backend configuration
    # prompt = get_prompt(language, framework, code_content, positive_cases, negative_cases)
    # suffix = get_suffix(language, framework)
    
    if language == 'python':
        if framework == 'gtest':
            return "PYTHON DOES NOT SUPPORT GTEST FRAMEWORK"
        # Use backend completion for Python
        # full_prompt = prompt + "\n" + suffix
        response = make_authenticated_request("/api/cli/generate", method="POST", data={
            # "prompt": prompt,
            "code_content": code_content,
            "framework": framework,
            "positive_cases": positive_cases,
            "negative_cases": negative_cases,
            "language": language
        })
        # prompt = get_prompt(language, framework, code_content, positive_cases, negative_cases)
        # suffix = get_suffix(language, framework)
        # print("RESP: ", response)
        if response and "content" in response:
            return response["content"]
        return None
            # return get_response_from_backend(full_prompt, "python")
    elif language == 'cpp':
        if framework == 'pytest':
            return "CPP DOES NOT SUPPORT PYTEST FRAMEWORK"
        response = make_authenticated_request("/api/cli/generate", method="POST", data={
            # "prompt": prompt,
            "code_content": code_content,
            "framework": framework,
            "positive_cases": positive_cases,
            "negative_cases": negative_cases,
            "language": language
        })
        # prompt = get_prompt(language, framework, code_content, positive_cases, negative_cases)
        # suffix = get_suffix(language, framework)
        # print("RESP: ", response)
        if response and "content" in response:
            return response["content"]
        return None
        # Use backend completion for C++
        # full_prompt = prompt + "\n" + suffix
        # return get_response_from_backend(full_prompt, "cpp")
    else:
        click.echo(f"❌ Unsupported language: {language}")
        return None

def save_test_file(file_path: str, test_content: str, language: str, framework: str, positive_cases: int, negative_cases: int, output_path: Optional[str] = None) -> str:
    """Save the generated test content to a file"""
    if not output_path:
        # Generate output filename based on input file
        input_path = Path(file_path)
        # stem = input_path.stem
        # suffix = input_path.suffix

        # Add imports and main execution based on language and framework
    if language == 'python':
        if framework == 'pytest':
            # For pytest, just add the test content
            import_statement = f"from {Path(file_path).stem} import *\n\n"
            full_content = import_statement + test_content
            test_execution = "\n# Run all test cases\n"
            for i in range(1, positive_cases + 1):
                test_execution += f"positive_test_case_{i}()\n"
            for i in range(1, negative_cases + 1):
                test_execution += f"negative_test_case_{i}()\n"
            test_execution += f"print('ALL TEST CASES PASSED!')"
            full_content = full_content + test_execution
        
        elif framework == 'unittest':
            print('in here')
            # For unittest, add proper class structure
            import_statement = f"import unittest\nfrom {Path(file_path).stem} import *\n\n"
            class_start = "class TestSuite(unittest.TestCase):\n"
            class_end = "\n\nif __name__ == '__main__':\n    unittest.main()\n"
            
            # Indent the test content for unittest class
            indented_content = "\n".join("    " + line if line.strip() else line for line in test_content.split('\n'))
            full_content = import_statement + class_start + indented_content + class_end

    
    elif language == 'cpp':
        # FIXED: Include the original C++ file header
        original_file_name = Path(file_path).name
        includes = f"#include <iostream>\n#include <exception>\n#include \"{original_file_name}\"\n\n"
        
        if framework == 'gtest':
            # For gtest, add proper includes
            gtest_includes = f"#include <gtest/gtest.h>\n\n#include \"{original_file_name}\"\n\n"
            full_content = gtest_includes + test_content
        
        else:
            # Default format (your original)
            main_function = "\nint main() {\n    std::cout << \"Running all test cases...\\n\";\n"
            # FIXED: Call all test cases based on user input
            for i in range(1, positive_cases + 1):
                main_function += f"    positive_test_case_{i}();\n"
            for i in range(1, negative_cases + 1):
                main_function += f"    negative_test_case_{i}();\n"
            main_function += "    return 0;\n}\n"
            
            full_content = includes + test_content + main_function
    
    # else:
    #     full_content = test_content
        
    # if language.lower() == 'python':
    #     output_filename = f"test_{stem}.py"
    # elif language.lower() in ['cpp', 'c++']:
    #     output_filename = f"test_{stem}.cpp"
    # else:
    #     output_filename = f"test_{stem}.txt"
        
    # output_path = str(input_path.parent / output_filename)
    if output_path is None:
        # Generate output path based on input file - FIXED: Remove double dots
        input_path = Path(file_path)
        # Fix the double dot issue by properly handling the extension
        if input_path.suffix:
            output_path = input_path.parent / f"test_{input_path.stem}{input_path.suffix}"
        else:
            output_path = input_path.parent / f"test_{input_path.name}"
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    try:
         # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        click.echo(f"✅ Test file generated successfully: {output_path}")
        return str(output_path)
    except Exception as e:
        click.echo(f"❌ Error saving test file: {e}")
        return ""

def user_login():
    os.system("python cli/main.py login")
    user = get_authenticated_user()
    if not user:
        return None
    return user


@click.command()
@click.option('--path', '-pt', 'file_path', required=True, type=click.Path(exists=True), help='Path to the source file')
@click.option('--positive', '-p', 'positive_cases', default=2, help='Number of positive test cases (default: 2)')
@click.option('--negative', '-n', 'negative_cases', default=2, help='Number of negative test cases (default: 2)')
@click.option('--framework', '-f', default="unittest", help='Testing framework (pytest, unittest, gtest) (default: unittest)')
@click.option('--language', '-l', default=None, help='Programming language (auto-detected if not specified)')
@click.option('--output', '-o', type=click.Path(), help='Output file path (optional)')
def generate(file_path, positive_cases, negative_cases, framework, language, output):
    """Generate test cases for your code files"""

    user = get_authenticated_user()
    if user:
        click.echo(f"Welcome back {user.get('username', 'Unknown')}")
        # click.echo(f"🆔 User ID: {user.get('plabn', 'Unknown')}")
        # click.echo("🔑 Token: [HIDDEN]")
    else:
        click.echo("❌ Not logged in or token is invalid!") 
        click.echo("Please login first!")
        user = user_login()
        if user is None:
            click.echo("❌ Login failed. Aborting...")
            return
    
    
    # Validate input
    if positive_cases < 0 or positive_cases > 8:
        click.echo("❌ Positive test cases must be between 0 and 8")
        return
    
    if negative_cases < 0 or negative_cases > 8:
        click.echo("❌ Negative test cases must be between 0 and 8")
        return
    
    # Auto-detect language if not specified
    if not language:
        language = detect_language(file_path)
        click.echo(f"🔍 Auto-detected language: {language}")
    
    if language != "python" and language != "cpp":
        click.echo(f"Error: {language} is not supported yet.\nSupport for {language} is coming soon! Stay tuned\n")
        return
    
    click.echo(f"🚀 Generating test cases for: {file_path}")
    
    # Generate test cases
    test_content = generate_test_cases(file_path, language, framework, positive_cases, negative_cases)
    
    if test_content:
        click.echo(f"Summary-\n -> Language: {language}")
        click.echo(f" -> Framework: {framework}")
        click.echo(f" -> Positive cases: {positive_cases}; Negative cases: {negative_cases}")
        # click.echo(f"")
        # Save test file
        output_path = save_test_file(file_path, test_content, language, framework, positive_cases, negative_cases, output)
        
        if output_path:
            # Log usage to backend
            log_usage_to_backend(language, len(test_content.split()))
            # click.echo("📊 Usage logged to backend")
    else:
        click.echo("❌ Failed to generate test cases") 


# New backend response function
def get_response_from_backend(framework: str, code_content: str, language: str, positive_cases: int, negative_cases: int) -> Optional[str]:
    response = make_authenticated_request("/api/cli/generate", method="POST", data={
        # "prompt": prompt,
        "code_content": code_content,
        "framework": framework,
        "positive_cases": positive_cases,
        "negative_cases": negative_cases,
        "language": language
    })
    # prompt = get_prompt(language, framework, code_content, positive_cases, negative_cases)
    # suffix = get_suffix(language, framework)
    if response and "content" in response:
        return response["content"]
    return None
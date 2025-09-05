#!/usr/bin/env python3
"""
Test Setup Script for YouTube Extractor Tool
============================================

This script helps set up the testing environment and validates
that everything is configured correctly for testing.
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def check_virtual_environment():
    """Check if running in virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return True
    print("⚠️  Not running in virtual environment (recommended)")
    return True


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'litellm', 'youtube_transcript_api', 'yt-dlp', 'pydantic',
        'rich', 'click', 'pytest', 'diskcache'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_configuration():
    """Check API key configuration."""
    env_file = Path('.env')
    env_test_file = Path('.env.test')
    
    print("\n🔧 Configuration Check:")
    
    if env_file.exists():
        print("✅ .env file found")
        
        # Check for API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY') 
        ollama_model = os.getenv('LLM_MODEL', '').startswith('ollama/')
        
        if openai_key:
            print("✅ OpenAI API key configured")
        elif anthropic_key:
            print("✅ Anthropic API key configured")
        elif ollama_model:
            print("✅ Ollama model configured (local)")
        else:
            print("⚠️  No API keys found - copy from .env.test and configure")
            
    else:
        print("⚠️  .env file not found")
        if env_test_file.exists():
            print("   → Copy .env.test to .env and configure API keys")
        else:
            print("   → Run: python main.py config init")


def check_test_videos():
    """Check test video configuration."""
    test_videos_file = Path('tests/test_videos.json')
    
    if not test_videos_file.exists():
        print("⚠️  tests/test_videos.json not found")
        return False
        
    try:
        import json
        with open(test_videos_file) as f:
            data = json.load(f)
        
        videos = data.get('test_videos', {})
        real_videos = [v for v in videos.values() if 'example' not in v.get('url', '')]
        
        print(f"✅ Test videos config found ({len(real_videos)}/{len(videos)} real URLs)")
        
        if len(real_videos) == 0:
            print("⚠️  No real YouTube URLs configured - replace example URLs")
            return False
            
    except Exception as e:
        print(f"❌ Error reading test videos: {e}")
        return False
        
    return True


def setup_test_directories():
    """Create test directories."""
    dirs = ['test_output', '.test_cache', '.processing_state']
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        
    print("✅ Test directories created")


def run_basic_tests():
    """Run basic unit tests to ensure setup works."""
    print("\n🧪 Running Basic Tests:")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/test_models.py', 
            'tests/test_utils.py',
            '-v', '--tb=short'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Basic unit tests passed")
            return True
        else:
            print("❌ Basic unit tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Could not run tests: {e}")
        return False


def suggest_next_steps():
    """Suggest next steps based on setup status."""
    print("\n🎯 Next Steps:")
    print("1. Configure API keys in .env file")
    print("2. Update tests/test_videos.json with real YouTube URLs")
    print("3. Run unit tests: pytest tests/test_models.py tests/test_utils.py")
    print("4. Run integration tests: pytest tests/test_integration.py")
    print("5. Test CLI: python main.py info <youtube_url>")
    print("6. Test full processing: python main.py process <youtube_url>")


def main():
    """Main setup validation."""
    print("🔍 YouTube Extractor Tool - Test Setup Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment), 
        ("Dependencies", check_dependencies),
    ]
    
    passed = 0
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        if check_func():
            passed += 1
    
    # Configuration checks (informational)
    check_configuration()
    check_test_videos()
    setup_test_directories()
    
    print(f"\n📊 Setup Status: {passed}/{len(checks)} critical checks passed")
    
    if passed == len(checks):
        print("🎉 Basic setup is ready!")
        if run_basic_tests():
            print("🚀 All systems go!")
        suggest_next_steps()
    else:
        print("❌ Please fix the issues above before testing")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
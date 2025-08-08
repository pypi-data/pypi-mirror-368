import argparse
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Minimax TTS to OpenAI API Proxy")
    parser.add_argument(
        "--dir",
        default=os.path.expanduser("~/.config/minimax-tts-openai/"),
        help="Working directory to read config.yaml from (default: ~/.config/minimax-tts-openai/)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Ensure the working directory exists
    work_dir = Path(args.dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # Change to the working directory
    os.chdir(work_dir)
    
    # Check if config.yaml exists
    config_file = work_dir / "config.yaml"
    if not config_file.exists():
        # Check if config.yaml.example exists in the package
        example_file = Path(__file__).parent / "config.yaml.example"
        if example_file.exists():
            print(f"Error: config.yaml not found in {work_dir}")
            print(f"Please copy {example_file} to {config_file} and edit it with your Minimax API credentials.")
            sys.exit(1)
        else:
            print("Error: config.yaml.example not found in the package")
            sys.exit(1)
    
    # Import app after changing directory and confirming config file exists
    from minimax_tts_openai.app import app
    import uvicorn
    
    # Run the FastAPI app
    uvicorn.run(
        "minimax_tts_openai.app:app",
        host=args.host,
        port=args.port,
        reload=False
    )

if __name__ == "__main__":
    main()
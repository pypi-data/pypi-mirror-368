import argparse
from commity.config import get_llm_config
from commity.core import get_git_diff, generate_prompt
from commity.llm import llm_client_factory
from commity.utils.prompt_organizer import summary_and_tokens_checker
from commity.utils.spinner import Spinner

def main():
    parser = argparse.ArgumentParser(description="AI-powered git commit message generator")
    parser.add_argument("--provider", type=str, help="LLM provider")
    parser.add_argument("--base_url", type=str, help="LLM base URL")
    parser.add_argument("--model", type=str, help="LLM model name")
    parser.add_argument("--api_key", type=str, help="LLM API key")
    parser.add_argument("--language", type=str, default="en", help="Language for commit message")
    parser.add_argument("--temperature", type=float, help="Temperature for generation")
    parser.add_argument("--max_tokens", type=int, help="Max tokens for generation")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds")
    parser.add_argument("--proxy", type=str, help="Proxy URL")
    parser.add_argument("--emoji", action="store_true", help="Include emojis")
    parser.add_argument("--type", type=str, default="conventional", help="Commit style type")

    args = parser.parse_args()
    config = get_llm_config(args)
    client = llm_client_factory(config)

    diff = get_git_diff()
    if not diff:
        print("⚠️ No staged changes detected.")
        return
    else:
        diff = summary_and_tokens_checker(diff, config.max_tokens, config.model)


    prompt = generate_prompt(diff, language=args.language, emoji=args.emoji, type_=args.type)
    try:
        with Spinner("🚀 Generating commit message..."):
            commit_msg = client.generate(prompt)
        if commit_msg:
            print(f"✅ Suggested Commit Message:\n {commit_msg}")
        else:
            print("❌ Failed to generate commit message.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()

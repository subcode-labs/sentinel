import os
import sys


def main():
    print("🤖 Mock AutoGPT Starting...")
    print("-" * 30)

    # Check for critical API keys
    openai_key = os.environ.get("OPENAI_API_KEY")
    github_key = os.environ.get("GITHUB_TOKEN")

    if openai_key:
        print(f"✅ OPENAI_API_KEY found: {openai_key[:8]}...{openai_key[-4:]}")
    else:
        print("❌ OPENAI_API_KEY not found in environment!")

    if github_key:
        print(f"✅ GITHUB_TOKEN found: {github_key[:8]}...{github_key[-4:]}")
    else:
        print("⚠️  GITHUB_TOKEN not found (optional)")

    print("-" * 30)
    print("Ready to take over the world! (Just kidding)")


if __name__ == "__main__":
    main()

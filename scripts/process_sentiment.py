import json
import subprocess
import os
import sys

STAGING_FILE = '/workspaces/Real-Time-Market-Sentiment-Volatility-Orchestrator/data/staged_news.json'
PROCESSED_FILE = '/workspaces/Real-Time-Market-Sentiment-Volatility-Orchestrator/data/processed_news.json'

SYSTEM_PROMPT = """
You are a financial analyst. Analyze the following news item and provide:
1. Sentiment score: A float between -1.0 (very negative) and 1.0 (very positive).
2. Volatility drivers: A list of key factors identified in the text that could drive market volatility.

OUTPUT STRICTLY IN JSON FORMAT:
{
  "sentiment_score": float,
  "volatility_drivers": ["driver1", "driver2", ...]
}
"""

def process_item(item):
    text_to_analyze = f"{SYSTEM_PROMPT}\n\nHeadline: {item['headline']}\nContent: {item['content']}"
    
    # Construct the gemini cli command for version 0.40.1
    command = [
        "gemini",
        "--yolo",  # Auto-approve actions if model tries to run tools (unlikely here but safe)
        "-p", text_to_analyze
    ]
    
    try:
        # Run the command and capture output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON output from Gemini CLI
        # Note: In a real scenario, we might need to strip extra characters if the CLI adds them
        raw_output = result.stdout.strip()
        
        # Sometimes LLMs wrap JSON in code blocks
        if raw_output.startswith("```json"):
            raw_output = raw_output.split("```json")[1].split("```")[0].strip()
        elif raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1].split("```")[0].strip()

        sentiment_data = json.loads(raw_output)
        
        # Merge with original item data
        item.update(sentiment_data)
        return item
    
    except subprocess.CalledProcessError as e:
        print(f"Error calling Gemini CLI for ticker {item['ticker']}: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output for ticker {item['ticker']}: {e}", file=sys.stderr)
        print(f"Raw output: {raw_output}", file=sys.stderr)
        return None

def main():
    if not os.path.exists(STAGING_FILE):
        print(f"Staging file {STAGING_FILE} not found.")
        return

    with open(STAGING_FILE, 'r') as f:
        news_items = json.load(f)

    processed_items = []
    for item in news_items:
        print(f"Processing sentiment for {item['ticker']}...")
        processed_item = process_item(item)
        if processed_item:
            processed_items.append(processed_item)

    with open(PROCESSED_FILE, 'w') as f:
        json.dump(processed_items, f, indent=4)
    
    print(f"Processed {len(processed_items)} items. Saved to {PROCESSED_FILE}")

if __name__ == "__main__":
    main()

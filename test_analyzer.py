from dotenv import load_dotenv
from app.services.ai_analyzer import analyze_text_with_openai

# Load environment variables from .env
load_dotenv()

def main():
    sample_text = (
        """
        Artificial intelligence (AI) is transforming industries across the globe. Businesses are leveraging AI to automate processes, gain insights from data, and improve customer experiences. 
        As AI technologies continue to evolve, organizations must adapt to stay competitive in the digital age. Key trends include the rise of generative AI, increased focus on ethical AI, and the integration of AI with cloud computing platforms.
        """
    )
    try:
        result = analyze_text_with_openai(sample_text)
        print("\n=== OpenAI Text Analysis ===")
        print(f"Summary:\n{result.get('summary', '')}\n")
        print("Keywords:")
        for kw in result.get('keywords', []):
            print(f"- {kw}")
        if 'error' in result:
            print(f"\n[Error]: {result['error']}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main() 
import os
import sys
from datetime import datetime

# Add the src directory to Python path so we can import our modules
sys.path.append('src')

# Import our modules
from src.excel_reader  import ExcelReader
from src.blog_generator import BlogGenerator


def main():
    print("🚀 Blog Generation Pipeline - Simple Version")
    print("=" * 60)

    # Step 1: Initialize components
    excel_file = os.getenv('EXCEL_FILE_PATH', 'data/Key Insights.xlsx')
    reader = ExcelReader(excel_file)
    generator = BlogGenerator()

    # Step 2: Load Excel data
    print("📊 Loading Excel data...")
    data = reader.read_all_sheets()

    if not data:
        print("❌ Failed to load Excel data. Check your file path.")
        return

    # Step 3: Test OpenAI connection
    print("🔍 Testing OpenAI connection...")
    if not generator.test_connection():
        print("❌ OpenAI connection failed. Check your API key.")
        return

    # Step 4: Prepare data
    seo_keywords = data['SEO - Keywords']
    llm_keywords = data['LLM - Keywords']
    website_links = data['Website']
    key_topics = data['key topics']

    print(f"✅ Ready to generate blogs from {len(key_topics)} topics")

    # Step 5: Ask user how many blogs to generate
    print("\nHow many blogs would you like to generate?")
    print("1. Generate 1 test blog")
    print("2. Generate 3 blogs")
    print("3. Generate 5 blogs")
    print("4. Generate all blogs")

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        num_blogs = 1
    elif choice == "2":
        num_blogs = 3
    elif choice == "3":
        num_blogs = 5
    elif choice == "4":
        num_blogs = len(key_topics)
    else:
        num_blogs = 1
        print("Invalid choice, generating 1 test blog")

    # Step 6: Generate blogs
    print(f"\n🤖 Generating {num_blogs} blogs...")

    # Create output directory
    os.makedirs('generated_blogs', exist_ok=True)

    results = []
    successful = 0

    for i in range(min(num_blogs, len(key_topics))):
        topic_data = key_topics.iloc[i]
        topic_name = topic_data.get('Topic', f'Topic_{i + 1}')

        print(f"\n📝 Blog {i + 1}/{num_blogs}: {topic_name}")

        # Generate blog
        result = generator.generate_blog(
            topic_data,
            seo_keywords,
            llm_keywords,
            website_links
        )

        if result['status'] == 'success':
            successful += 1

            # Create safe filename
            safe_topic = topic_name.replace(' ', '_').replace('/', '_')[:30]
            filename = f"generated_blogs/blog_{i + 1:02d}_{safe_topic}.txt"

            # Save blog to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"BLOG GENERATION REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Topic: {result['topic']}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Word Count: {result['word_count']}\n")
                f.write(f"SEO Keywords: {', '.join(result['seo_keywords_used'])}\n")
                f.write(f"LLM Keywords: {', '.join(result['llm_keywords_used'])}\n")
                f.write(f"Links Used: {', '.join(result['links_used'])}\n")
                f.write("\n" + "=" * 50 + "\n\n")
                f.write(result['content'])

            print(f"✅ Blog generated! ({result['word_count']} words)")
            print(f"💾 Saved to: {filename}")

        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")

        results.append(result)

    # Step 7: Generate summary
    print(f"\n🎉 Generation Complete!")
    print(f"✅ Successfully generated: {successful}/{num_blogs} blogs")
    print(f"📁 All blogs saved in: generated_blogs/")

    # Create summary file
    summary_file = f"generated_blogs/SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("BLOG GENERATION SUMMARY\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Blogs Attempted: {num_blogs}\n")
        f.write(f"Successfully Generated: {successful}\n")
        f.write(f"Failed: {num_blogs - successful}\n\n")

        f.write("BLOG DETAILS:\n")
        f.write("-" * 30 + "\n")

        for i, result in enumerate(results, 1):
            f.write(f"\nBlog {i}: {result.get('topic', 'Unknown')}\n")
            f.write(f"Status: {result.get('status', 'unknown')}\n")
            if result['status'] == 'success':
                f.write(f"Word Count: {result.get('word_count', 0)}\n")
                f.write(f"SEO Keywords: {', '.join(result.get('seo_keywords_used', []))}\n")
                f.write(f"LLM Keywords: {', '.join(result.get('llm_keywords_used', []))}\n")
            else:
                f.write(f"Error: {result.get('error', 'Unknown')}\n")
            f.write("-" * 20 + "\n")

    print(f"📊 Summary saved to: {summary_file}")

    if successful > 0:
        print(f"\n🎯 Next steps:")
        print(f"1. Review the generated blogs in 'generated_blogs/' folder")
        print(f"2. Edit and customize as needed")
        print(f"3. Set up Google Sheets integration later for automation")
        print(f"4. Deploy to GCP for scheduled generation")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    main()
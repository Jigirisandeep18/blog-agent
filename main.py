import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the src directory to Python path so we can import our modules
sys.path.append('src')

# Import our modules
from src.excel_reader import ExcelReader
from src.blog_generator import BlogGenerator
from airtable_blog_writer import AirtableBlogWriter


class EnhancedBlogGenerationPipeline:
    def __init__(self):
        """Initialize the complete blog generation pipeline with token tracking and Airtable integration"""
        self.excel_file = os.getenv('EXCEL_FILE_PATH', 'data/Key Insights.xlsx')
        self.excel_reader = ExcelReader(self.excel_file)
        self.blog_generator = BlogGenerator()
        self.airtable_writer = AirtableBlogWriter()  # Add Airtable integration
        self.results = []

        # Token tracking totals
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def load_data(self):
        """Load data from Excel file"""
        print("📊 Loading data from Excel...")
        self.data = self.excel_reader.read_all_sheets()

        if not self.data:
            print("❌ Failed to load Excel data")
            return False

        self.seo_keywords = self.data['SEO - Keywords']
        self.llm_keywords = self.data['LLM - Keywords']
        self.website_links = self.data['Website']
        self.key_topics = self.data['key topics']

        print(f"✅ Loaded {len(self.key_topics)} topics for blog generation")
        return True

    def test_connections(self):
        """Test all API connections including Airtable"""
        print("🔍 Testing connections...")

        # Test OpenAI
        if not self.blog_generator.test_connection():
            return False

        # Test Airtable
        if not self.airtable_writer.test_connection():
            print("⚠️ Airtable connection failed - blogs will only be saved as files")

        print("✅ Connections tested!")
        return True

    def generate_blogs(self, num_blogs=None):
        """Generate blogs for topics with enhanced token tracking and Airtable integration"""
        if not hasattr(self, 'key_topics'):
            print("❌ No data loaded. Run load_data() first.")
            return []

        # Determine how many blogs to generate
        total_topics = len(self.key_topics)
        if num_blogs is None:
            num_blogs = min(5, total_topics)  # Default: generate 5 blogs
        else:
            num_blogs = min(num_blogs, total_topics)

        print(f"🤖 Generating {num_blogs} blogs with token tracking and Airtable integration...")

        for i in range(num_blogs):
            topic_data = self.key_topics.iloc[i]
            topic_name = topic_data.get('Topic', 'Unknown')
            print(f"\n📝 Blog {i + 1}/{num_blogs}: {topic_name}")

            # Generate blog with enhanced tracking
            result = self.blog_generator.generate_blog(
                topic_data,
                self.seo_keywords,
                self.llm_keywords,
                self.website_links
            )

            # Add timestamp and index
            result['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result['blog_index'] = i + 1

            # Update totals
            if result['status'] == 'success':
                self.total_input_tokens += result.get('input_tokens', 0)
                self.total_output_tokens += result.get('output_tokens', 0)
                self.total_cost += result.get('cost', 0.0)

            self.results.append(result)

            # Save individual blog with ENHANCED FORMAT including token data
            if result['status'] == 'success':
                safe_topic = topic_name.replace(' ', '_').replace('/', '_')[:30]
                filename = f"generated_blogs/blog_{i + 1:02d}_{safe_topic}.txt"
                os.makedirs('generated_blogs', exist_ok=True)

                # ENHANCED FILE FORMAT WITH TOKEN AND COST DATA
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"BLOG GENERATION REPORT\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Topic: {result['topic']}\n")
                    f.write(f"Model Used: {result.get('model_used', 'Unknown')}\n")
                    f.write(f"Input Tokens: {result.get('input_tokens', 0):,}\n")
                    f.write(f"Output Tokens: {result.get('output_tokens', 0):,}\n")
                    f.write(f"Total Tokens: {result.get('total_tokens', 0):,}\n")
                    f.write(f"Cost: ${result.get('cost', 0.0):.4f}\n")
                    f.write(f"Word Count: {result['word_count']}\n")
                    f.write(f"Generated: {result['generated_at']}\n")
                    f.write(f"SEO Keywords: {', '.join(result.get('seo_keywords_used', []))}\n")
                    f.write(f"LLM Keywords: {', '.join(result.get('llm_keywords_used', []))}\n")
                    f.write(f"Links Used: {', '.join(result.get('links_used', []))}\n")
                    f.write("\n" + "=" * 50 + "\n\n")
                    f.write(result['content'])

                print(f"💾 Saved to file: {filename}")
                print(f"📊 Tokens: {result.get('total_tokens', 0):,} | Cost: ${result.get('cost', 0.0):.4f}")

                # SAVE TO AIRTABLE as well
                print("📤 Saving to Airtable...")
                self.airtable_writer.write_blog_to_airtable(result)

            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")

        return self.results

    def save_enhanced_summary(self):
        """Save enhanced summary with token tracking and cost analysis"""
        if not self.results:
            print("❌ No results to save")
            return

        successful_blogs = [r for r in self.results if r['status'] == 'success']
        failed_blogs = [r for r in self.results if r['status'] == 'failed']

        # Enhanced summary with token data
        summary = {
            'generation_summary': {
                'total_blogs_attempted': len(self.results),
                'successful_blogs': len(successful_blogs),
                'failed_blogs': len(failed_blogs),
                'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_input_tokens': self.total_input_tokens,
                'total_output_tokens': self.total_output_tokens,
                'total_tokens': self.total_input_tokens + self.total_output_tokens,
                'total_cost': round(self.total_cost, 4),
                'average_cost_per_blog': round(self.total_cost / len(successful_blogs), 4) if successful_blogs else 0,
                'cost_per_1k_tokens': round(
                    (self.total_cost * 1000 / (self.total_input_tokens + self.total_output_tokens)), 4) if (
                                                                                                                       self.total_input_tokens + self.total_output_tokens) > 0 else 0
            },
            'blog_details': []
        }

        for result in self.results:
            blog_summary = {
                'topic': result.get('topic', 'Unknown'),
                'word_count': result.get('word_count', 0),
                'status': result.get('status', 'unknown'),
                'model_used': result.get('model_used', 'Unknown'),
                'input_tokens': result.get('input_tokens', 0),
                'output_tokens': result.get('output_tokens', 0),
                'total_tokens': result.get('total_tokens', 0),
                'cost': result.get('cost', 0.0),
                'seo_keywords_used': result.get('seo_keywords_used', []),
                'llm_keywords_used': result.get('llm_keywords_used', []),
                'links_used': result.get('links_used', []),
                'generated_at': result.get('generated_at', ''),
                'error': result.get('error', '')
            }
            summary['blog_details'].append(blog_summary)

        # Save detailed JSON summary
        summary_file = f"generated_blogs/ENHANCED_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Save readable text summary with token data
        text_summary_file = f"generated_blogs/SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_summary_file, 'w', encoding='utf-8') as f:
            f.write("ENHANCED BLOG GENERATION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generation Time: {summary['generation_summary']['generation_time']}\n")
            f.write(f"Total Blogs Attempted: {summary['generation_summary']['total_blogs_attempted']}\n")
            f.write(f"Successful: {summary['generation_summary']['successful_blogs']}\n")
            f.write(f"Failed: {summary['generation_summary']['failed_blogs']}\n\n")

            f.write("TOKEN USAGE AND COST ANALYSIS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Input Tokens: {summary['generation_summary']['total_input_tokens']:,}\n")
            f.write(f"Total Output Tokens: {summary['generation_summary']['total_output_tokens']:,}\n")
            f.write(f"Total Tokens Used: {summary['generation_summary']['total_tokens']:,}\n")
            f.write(f"Total Cost: ${summary['generation_summary']['total_cost']:.4f}\n")
            f.write(f"Average Cost per Blog: ${summary['generation_summary']['average_cost_per_blog']:.4f}\n")
            f.write(f"Cost per 1,000 tokens: ${summary['generation_summary']['cost_per_1k_tokens']:.4f}\n\n")

            f.write("AIRTABLE INTEGRATION: ✅ ENABLED\n")
            f.write("All successful blogs saved to both files and Airtable database.\n\n")

            f.write("INDIVIDUAL BLOG DETAILS:\n")
            f.write("-" * 50 + "\n")

            for i, blog in enumerate(summary['blog_details'], 1):
                f.write(f"\nBlog {i}: {blog['topic']}\n")
                f.write(f"Status: {blog['status']}\n")
                f.write(f"Model: {blog['model_used']}\n")
                f.write(f"Word Count: {blog['word_count']}\n")
                if blog['status'] == 'success':
                    f.write(f"Input Tokens: {blog['input_tokens']:,}\n")
                    f.write(f"Output Tokens: {blog['output_tokens']:,}\n")
                    f.write(f"Total Tokens: {blog['total_tokens']:,}\n")
                    f.write(f"Cost: ${blog['cost']:.4f}\n")
                    f.write(f"SEO Keywords: {', '.join(blog['seo_keywords_used'])}\n")
                    f.write(f"LLM Keywords: {', '.join(blog['llm_keywords_used'])}\n")
                if blog['error']:
                    f.write(f"Error: {blog['error']}\n")
                f.write("-" * 30 + "\n")

        print(f"📊 Enhanced summary saved to: {text_summary_file}")
        print(f"📄 JSON data saved to: {summary_file}")

    def run_complete_pipeline(self, num_blogs=5):
        """Run the complete blog generation pipeline with enhanced tracking and Airtable integration"""
        print("🚀 Enhanced Blog Generation Pipeline with Token Tracking & Airtable")
        print("=" * 70)

        # Step 1: Load data
        if not self.load_data():
            print("❌ Pipeline failed at data loading")
            return False

        # Step 2: Test connections
        if not self.test_connections():
            print("❌ Pipeline failed at connection testing")
            return False

        # Step 3: Generate blogs with token tracking and Airtable integration
        results = self.generate_blogs(num_blogs)

        # Step 4: Save enhanced summary
        self.save_enhanced_summary()

        # Step 5: Final report with token data and Airtable confirmation
        successful = len([r for r in results if r['status'] == 'success'])

        print(f"\n🎉 Pipeline Complete!")
        print(f"✅ Successfully generated {successful}/{len(results)} blogs")
        print(f"📊 Total Input Tokens: {self.total_input_tokens:,}")
        print(f"📊 Total Output Tokens: {self.total_output_tokens:,}")
        print(f"📊 Total Tokens Used: {self.total_input_tokens + self.total_output_tokens:,}")
        print(f"💰 Total Cost: ${self.total_cost:.4f}")
        if successful > 0:
            avg_cost = self.total_cost / successful
            print(f"💰 Average Cost per Blog: ${avg_cost:.4f}")
        print(f"📁 Blogs saved to files: generated_blogs/ folder")
        print(f"📤 Blogs saved to Airtable: Check your Airtable base")
        print(f"📊 Check summary files for detailed token and cost analysis")

        return True


# Main execution
if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Create and run enhanced pipeline with Airtable integration
    pipeline = EnhancedBlogGenerationPipeline()

    # Run with different options:
    print("Choose an option:")
    print("1. Generate 1 test blog")
    print("2. Generate 3 blogs")
    print("3. Generate 5 blogs (default)")
    print("4. Generate all blogs from your Excel file")
    print("5. Custom number")

    choice = input("\nEnter choice (1-5) or press Enter for default: ").strip()

    if choice == "1":
        num_blogs = 1
    elif choice == "2":
        num_blogs = 3
    elif choice == "4":
        num_blogs = None
    elif choice == "5":
        try:
            num_blogs = int(input("How many blogs to generate? "))
        except:
            num_blogs = 5
    else:
        num_blogs = 5

    print(f"\n🚀 Generating {num_blogs if num_blogs else 'all'} blogs with token tracking and Airtable integration...")
    pipeline.run_complete_pipeline(num_blogs)
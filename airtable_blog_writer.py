import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class AirtableBlogWriter:
    def __init__(self):
        """Initialize Airtable connection for blog storage"""
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        self.table_name = os.getenv('AIRTABLE_TABLE_NAME', 'Table 1')

        if not self.api_key or not self.base_id:
            print("Missing Airtable credentials in .env file")
            return

        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def extract_blog_sections(self, blog_content):
        """Extract different sections from blog content"""
        sections = {
            'meta_title': '',
            'meta_description': '',
            'main_content': blog_content
        }

        lines = blog_content.split('\n')

        for line in lines:
            if line.startswith('META_TITLE:'):
                sections['meta_title'] = line.replace('META_TITLE:', '').strip()
            elif line.startswith('META_DESCRIPTION:'):
                sections['meta_description'] = line.replace('META_DESCRIPTION:', '').strip()

        return sections

    def write_blog_to_airtable(self, blog_result):
        """Write blog result to Airtable"""
        try:
            # Extract blog sections
            sections = self.extract_blog_sections(blog_result.get('content', ''))

            # Prepare record data for Airtable
            record_data = {
                "records": [
                    {
                        "fields": {
                            "Name": blog_result.get('topic', 'Unknown'),  # Maps to existing Name field
                            "Notes": f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                                     f"Model: {blog_result.get('model_used', 'Unknown')} | "
                                     f"Tokens: {blog_result.get('total_tokens', 0):,} | "
                                     f"Cost: ${blog_result.get('cost', 0.0):.4f}",  # Maps to existing Notes field
                            # Add more fields if you created them in Airtable
                            # "Meta Title": sections['meta_title'],
                            # "Meta Description": sections['meta_description'],
                            # "Blog Content": sections['main_content'][:50000],  # Airtable has field limits
                            # "Word Count": blog_result.get('word_count', 0),
                            # "Model Used": blog_result.get('model_used', 'Unknown'),
                            # "Input Tokens": blog_result.get('input_tokens', 0),
                            # "Output Tokens": blog_result.get('output_tokens', 0),
                            # "Cost": blog_result.get('cost', 0.0),
                            # "Generation Status": "Success" if blog_result.get('status') == 'success' else "Failed",
                            # "SEO Keywords": ', '.join(blog_result.get('seo_keywords_used', [])),
                            # "LLM Keywords": ', '.join(blog_result.get('llm_keywords_used', [])),
                            # "Links Used": ', '.join(blog_result.get('links_used', []))
                        }
                    }
                ]
            }

            # Make API call to Airtable
            response = requests.post(self.base_url, headers=self.headers, json=record_data)

            if response.status_code == 200:
                created_record = response.json()
                record_id = created_record['records'][0]['id']
                print(f"✅ Blog '{blog_result.get('topic', 'Unknown')}' saved to Airtable! (ID: {record_id})")
                return True
            else:
                print(f"❌ Airtable API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error writing to Airtable: {str(e)}")
            return False

    def write_multiple_blogs(self, blog_results):
        """Write multiple blog results to Airtable"""
        success_count = 0

        for blog_result in blog_results:
            if blog_result.get('status') == 'success':
                if self.write_blog_to_airtable(blog_result):
                    success_count += 1
            else:
                print(f"⚠️ Skipping failed blog: {blog_result.get('topic', 'Unknown')}")

        print(
            f"📊 Airtable Summary: {success_count}/{len([r for r in blog_results if r.get('status') == 'success'])} successful blogs saved to Airtable")
        return success_count

    def test_connection(self):
        """Test Airtable connection"""
        try:
            response = requests.get(self.base_url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Airtable connection successful! Found {len(data.get('records', []))} existing records")
                return True
            else:
                print(f"❌ Airtable connection failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Airtable connection error: {str(e)}")
            return False


# Test the integration
if __name__ == "__main__":
    print("🚀 Testing Airtable Blog Writer Integration...")

    writer = AirtableBlogWriter()

    if writer.test_connection():
        # Test with sample blog data
        sample_blog = {
            'topic': 'Test AI Blog Integration',
            'content': '''META_TITLE: Test Blog Title
META_DESCRIPTION: Test blog description for Airtable integration

# Test Blog for Airtable Integration

This is test content for Airtable integration.

## Conclusion
Successfully integrated with Airtable.''',
            'word_count': 50,
            'model_used': 'gpt-4o',
            'input_tokens': 100,
            'output_tokens': 200,
            'total_tokens': 300,
            'cost': 0.05,
            'status': 'success',
            'seo_keywords_used': ['AI Technology', 'Integration'],
            'llm_keywords_used': ['GPT', 'Airtable'],
            'links_used': ['OpenAI Blog']
        }

        print("\n📝 Testing blog write to Airtable...")
        if writer.write_blog_to_airtable(sample_blog):
            print("🎉 Airtable integration working perfectly!")
        else:
            print("❌ Failed to write test blog")
    else:
        print("❌ Airtable connection failed")
import os
import openai
import pandas as pd
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()


class BlogGenerator:
    def __init__(self):
        """Initialize the blog generator with OpenAI API"""
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def create_blog_prompt(self, topic_data, seo_keywords, llm_keywords, website_links):
        """
        Create a comprehensive prompt for blog generation
        """
        # Get topic details
        topic = topic_data.get('Topic', 'AI Technology')
        description = topic_data.get('Description', '')
        source = topic_data.get('Source & URL', '')

        # Select random keywords from each category
        seo_kw_list = seo_keywords.iloc[:, 0].tolist()[:5]  # First 5 SEO keywords
        llm_kw_list = llm_keywords.iloc[:, 0].tolist()[:5]  # First 5 LLM keywords

        # Select random website links for internal linking
        random_links = website_links.sample(min(3, len(website_links)))
        links_text = ""
        for _, link in random_links.iterrows():
            links_text += f"- {link.get('Name', 'Link')}: {link.get('URL', '')}\n"

        prompt = f"""
Write a comprehensive, SEO-optimized blog post about "{topic}".

TOPIC DETAILS:
- Main Topic: {topic}
- Context: {description}
- Reference: {source}

SEO REQUIREMENTS:
- Target these SEO keywords naturally: {', '.join(seo_kw_list)}
- Include these LLM-optimized phrases: {', '.join(llm_kw_list)}
- Target 90+ SEMrush SEO score
- 1500-2000 words
- Keyword density: 1-2%

CONTENT STRUCTURE:
1. Compelling meta title (max 60 characters)
2. Meta description (max 160 characters)
3. H1 title
4. Introduction with hook
5. 4-5 H2 sections with H3 subsections
6. Include these internal links naturally:
{links_text}
7. Add [IMAGE PLACEHOLDER: descriptive alt text] in 3 relevant places
8. FAQ section with 5 questions
9. Strong conclusion with CTA

WRITING STYLE:
- Professional but engaging
- Clear, actionable insights
- Include statistics and examples
- Optimize for both human readers and AI search
- Use transition words for flow
- Include bullet points and numbered lists where appropriate

OUTPUT FORMAT:
```
META_TITLE: [60 char title]
META_DESCRIPTION: [160 char description]

# [H1 Title]

[Introduction paragraph with hook]

## [H2 Section 1]
[Content with H3 subsections if needed]
[IMAGE PLACEHOLDER: descriptive alt text]

## [H2 Section 2]
[Content]

## [H2 Section 3]
[Content]
[IMAGE PLACEHOLDER: descriptive alt text]

## [H2 Section 4]
[Content]

## [H2 Section 5]
[Content]
[IMAGE PLACEHOLDER: descriptive alt text]

## Frequently Asked Questions

**Q1: [Question]**
A: [Answer]

**Q2: [Question]**
A: [Answer]

**Q3: [Question]**
A: [Answer]

**Q4: [Question]**
A: [Answer]

**Q5: [Question]**
A: [Answer]

## Conclusion

[Strong conclusion with clear CTA]
```

Generate the complete blog post following this structure exactly.
"""
        return prompt

    def generate_blog(self, topic_data, seo_keywords, llm_keywords, website_links):
        """
        Generate a single blog post using OpenAI
        """
        try:
            print(f"🤖 Generating blog for topic: {topic_data.get('Topic', 'Unknown')}")

            # Create the prompt
            prompt = self.create_blog_prompt(topic_data, seo_keywords, llm_keywords, website_links)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 for better quality
                messages=[
                    {"role": "system",
                     "content": "You are an expert SEO blog writer specializing in AI and technology content. You create engaging, well-structured, and highly optimized blog posts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )

            blog_content = response.choices[0].message.content

            print("✅ Blog generated successfully!")
            return {
                'topic': topic_data.get('Topic', 'Unknown'),
                'content': blog_content,
                'seo_keywords_used': seo_keywords.iloc[:, 0].tolist()[:5],
                'llm_keywords_used': llm_keywords.iloc[:, 0].tolist()[:5],
                'links_used': website_links.sample(min(3, len(website_links)))['Name'].tolist(),
                'word_count': len(blog_content.split()),
                'status': 'success'
            }

        except Exception as e:
            print(f"❌ Error generating blog: {str(e)}")
            return {
                'topic': topic_data.get('Topic', 'Unknown'),
                'content': '',
                'error': str(e),
                'status': 'failed'
            }

    def test_connection(self):
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Say 'Connection successful!'"}],
                max_tokens=10
            )
            print("✅ OpenAI API connection successful!")
            return True
        except Exception as e:
            print(f"❌ OpenAI API connection failed: {str(e)}")
            return False


# Test the blog generator
if __name__ == "__main__":
    # Import the Excel reader
    from excel_reader import ExcelReader

    print("🚀 Testing Blog Generator...")

    # Initialize blog generator
    generator = BlogGenerator()

    # Test OpenAI connection
    if not generator.test_connection():
        print("Please check your OpenAI API key in .env file")
        exit()

    # Read Excel data
    excel_file = os.getenv('EXCEL_FILE_PATH', 'data/Key Insights.xlsx')
    reader = ExcelReader(excel_file)
    data = reader.read_all_sheets()

    if not data:
        print("Failed to read Excel data")
        exit()

    # Get data from sheets
    seo_keywords = data['SEO - Keywords']
    llm_keywords = data['LLM - Keywords']
    website_links = data['Website']
    key_topics = data['key topics']

    # Generate a test blog for the first topic
    first_topic = key_topics.iloc[0]
    print(f"\n📝 Generating test blog for: {first_topic.get('Topic', 'Unknown')}")

    result = generator.generate_blog(first_topic, seo_keywords, llm_keywords, website_links)

    if result['status'] == 'success':
        print(f"✅ Blog generated! Word count: {result['word_count']}")
        print("📄 Preview (first 500 characters):")
        print(result['content'][:500] + "...")

        # Save to file for review
        with open('test_blog.txt', 'w', encoding='utf-8') as f:
            f.write(result['content'])
        print("\n💾 Full blog saved to 'test_blog.txt'")
    else:
        print(f"❌ Blog generation failed: {result.get('error', 'Unknown error')}")
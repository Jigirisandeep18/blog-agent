import os
import openai
import pandas as pd
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Try to import tiktoken for token counting, fallback if not available
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    print("⚠️ tiktoken not installed. Install with: pip install tiktoken")


class BlogGenerator:
    def __init__(self):
        """Initialize the blog generator with OpenAI API"""
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Token tracking variables
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

        # GPT pricing (as of 2024)
        self.pricing = {
            'gpt-4o': {
                'input': 0.005 / 1000,
                'output': 0.015 / 1000
            },
            'gpt-3.5-turbo': {
                'input': 0.0005 / 1000,
                'output': 0.0015 / 1000
            }
        }

    def count_tokens(self, text, model="gpt-4o"):
        """Count tokens in text"""
        if HAS_TIKTOKEN:
            try:
                encoding = tiktoken.encoding_for_model(model)
                return len(encoding.encode(text))
            except:
                pass
        return len(text) // 4

    def calculate_cost(self, input_tokens, output_tokens, model="gpt-4o"):
        """Calculate cost"""
        if model not in self.pricing:
            model = "gpt-4o"
        input_cost = input_tokens * self.pricing[model]['input']
        output_cost = output_tokens * self.pricing[model]['output']
        return input_cost + output_cost

    def create_blog_prompt(self, topic_data, seo_keywords, llm_keywords, website_links):
        """Builds the structured blog prompt"""
        topic = topic_data.get('Topic', 'AI Technology')
        description = topic_data.get('Description', '')
        source = topic_data.get('Source & URL', '')

        seo_kw_list = seo_keywords.iloc[:, 0].tolist()[:5]
        llm_kw_list = llm_keywords.iloc[:, 0].tolist()[:5]

        random_links = website_links.sample(min(3, len(website_links)))
        links_text = "\n".join(
            [f"- {link.get('Name', 'Link')}: {link.get('URL', '')}" for _, link in random_links.iterrows()]
        )

        prompt = f"""
Write a comprehensive, SEO-optimized blog post about "{topic}".

TOPIC DETAILS:
- Main Topic: {topic}
- Context: {description}
- Reference: {source}

IMPORTANT: Never hallucinate statistics or numbers. Only use verified information.

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
- Include statistics and examples (only verified ones)
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
        """Generate a blog post with token tracking"""
        try:
            topic_name = topic_data.get('Topic', 'Unknown')
            print(f"🤖 Generating blog for topic: {topic_name}")

            prompt = self.create_blog_prompt(topic_data, seo_keywords, llm_keywords, website_links)
            system_message = "You are an expert SEO blog writer specializing in AI and technology content."

            estimated_input_tokens = self.count_tokens(system_message + prompt)
            print(f"📊 Estimated input tokens: {estimated_input_tokens:,}")

            models_to_try = ["gpt-4o", "gpt-3.5-turbo"]

            response = None
            model = None
            for m in models_to_try:
                try:
                    print(f"🔄 Trying model: {m}")
                    response = openai.ChatCompletion.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=3000 if m == "gpt-3.5-turbo" else 4000,
                        temperature=0.7
                    )
                    model = m
                    print(f"✅ Successfully used model: {m}")
                    break
                except Exception as model_error:
                    print(f"❌ Model {m} failed: {str(model_error)}")
                    continue

            if not response:
                raise RuntimeError("All models failed")

            blog_content = response["choices"][0]["message"]["content"]

            usage = response["usage"]
            actual_input_tokens = usage["prompt_tokens"]
            actual_output_tokens = usage["completion_tokens"]
            total_tokens = usage["total_tokens"]

            cost = self.calculate_cost(actual_input_tokens, actual_output_tokens, model)

            self.total_input_tokens += actual_input_tokens
            self.total_output_tokens += actual_output_tokens
            self.total_cost += cost

            print(f"✅ Blog generated successfully!")
            print(f"📊 Input tokens: {actual_input_tokens:,}")
            print(f"📊 Output tokens: {actual_output_tokens:,}")
            print(f"📊 Total tokens: {total_tokens:,}")
            print(f"💰 Cost for this blog: ${cost:.4f}")
            print(f"💰 Running total cost: ${self.total_cost:.4f}")

            return {
                'topic': topic_name,
                'content': blog_content,
                'seo_keywords_used': seo_keywords.iloc[:, 0].tolist()[:5],
                'llm_keywords_used': llm_keywords.iloc[:, 0].tolist()[:5],
                'links_used': website_links.sample(min(3, len(website_links)))['Name'].tolist(),
                'word_count': len(blog_content.split()),
                'model_used': model,
                'input_tokens': actual_input_tokens,
                'output_tokens': actual_output_tokens,
                'total_tokens': total_tokens,
                'cost': cost,
                'status': 'success'
            }

        except Exception as e:
            print(f"❌ Error generating blog: {str(e)}")
            return {
                'topic': topic_data.get('Topic', 'Unknown'),
                'content': '',
                'error': str(e),
                'model_used': 'unknown',
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cost': 0.0,
                'status': 'failed'
            }

    def test_connection(self):
        """Test OpenAI API connection"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'Connection successful!'"}],
                max_tokens=10
            )
            print("✅ OpenAI API connection successful!")
            return True
        except openai.error.RateLimitError:
            print("❌ OpenAI API quota exceeded.")
            return False
        except openai.error.AuthenticationError:
            print("❌ Invalid OpenAI API key. Please check your .env file")
            return False
        except Exception as e:
            print(f"❌ OpenAI API connection failed: {str(e)}")
            return False

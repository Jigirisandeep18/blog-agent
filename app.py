from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.append('src')

# Import our modules
from src.excel_reader import ExcelReader
from src.blog_generator import BlogGenerator
from airtable_blog_writer import AirtableBlogWriter

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Global variables for data
excel_reader = None
blog_generator = None
airtable_writer = None
seo_keywords = None
llm_keywords = None
website_links = None
key_topics = None


def initialize_components():
    """Initialize all components once at startup"""
    global excel_reader, blog_generator, airtable_writer
    global seo_keywords, llm_keywords, website_links, key_topics

    try:
        # Initialize components
        excel_file = os.getenv('EXCEL_FILE_PATH', 'data/Key Insights.xlsx')
        excel_reader = ExcelReader(excel_file)
        blog_generator = BlogGenerator()
        airtable_writer = AirtableBlogWriter()

        # Load data
        data = excel_reader.read_all_sheets()
        if data:
            seo_keywords = data['SEO - Keywords']
            llm_keywords = data['LLM - Keywords']
            website_links = data['Website']
            key_topics = data['key topics']
            return True
        return False
    except Exception as e:
        print(f"Initialization error: {str(e)}")
        return False


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Blog Generator API is running'
    })


@app.route('/api/topics', methods=['GET'])
def get_topics():
    """Get available topics for blog generation"""
    try:
        if key_topics is None:
            return jsonify({'error': 'Data not loaded'}), 500

        topics_list = []
        for _, row in key_topics.iterrows():
            topics_list.append({
                'id': len(topics_list),
                'topic': row.get('Topic', 'Unknown'),
                'description': row.get('Description', ''),
                'source': row.get('Source & URL', '')
            })

        return jsonify({
            'topics': topics_list,
            'count': len(topics_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    """Get available keywords by category"""
    try:
        if seo_keywords is None or llm_keywords is None:
            return jsonify({'error': 'Keywords not loaded'}), 500

        # Get column names (categories)
        seo_categories = {}
        llm_categories = {}

        # Process SEO keywords
        for col in seo_keywords.columns:
            seo_categories[col] = seo_keywords[col].dropna().tolist()

        # Process LLM keywords
        for col in llm_keywords.columns:
            llm_categories[col] = llm_keywords[col].dropna().tolist()

        return jsonify({
            'seo_keywords': seo_categories,
            'llm_keywords': llm_categories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-blog', methods=['POST'])
def generate_blog():
    """Generate a blog based on topic and selected keywords"""
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        topic_id = data.get('topic_id')
        custom_topic = data.get('custom_topic')
        selected_keywords = data.get('selected_keywords', [])

        # Determine topic data
        if custom_topic:
            topic_data = {
                'Topic': custom_topic,
                'Description': 'Custom topic provided by user',
                'Source & URL': 'User input'
            }
        elif topic_id is not None and topic_id < len(key_topics):
            topic_data = key_topics.iloc[topic_id]
        else:
            return jsonify({'error': 'Invalid topic selection'}), 400

        # Test connections
        if not blog_generator.test_connection():
            return jsonify({'error': 'OpenAI connection failed'}), 500

        # Generate blog
        result = blog_generator.generate_blog(
            topic_data,
            seo_keywords,
            llm_keywords,
            website_links
        )

        if result['status'] == 'success':
            # Save to Airtable
            airtable_writer.write_blog_to_airtable(result)

            # Return result
            return jsonify({
                'status': 'success',
                'blog': {
                    'topic': result['topic'],
                    'content': result['content'],
                    'word_count': result['word_count'],
                    'model_used': result.get('model_used', 'unknown'),
                    'input_tokens': result.get('input_tokens', 0),
                    'output_tokens': result.get('output_tokens', 0),
                    'total_tokens': result.get('total_tokens', 0),
                    'cost': result.get('cost', 0.0),
                    'seo_keywords_used': result.get('seo_keywords_used', []),
                    'llm_keywords_used': result.get('llm_keywords_used', []),
                    'links_used': result.get('links_used', []),
                    'generated_at': datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'error': result.get('error', 'Blog generation failed')
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-multiple', methods=['POST'])
def generate_multiple_blogs():
    """Generate multiple blogs"""
    try:
        data = request.get_json()
        count = data.get('count', 3)
        topic_ids = data.get('topic_ids', [])

        if count > 10:
            return jsonify({'error': 'Maximum 10 blogs per request'}), 400

        results = []
        total_cost = 0.0

        # Determine which topics to use
        if topic_ids:
            topics_to_use = [key_topics.iloc[tid] for tid in topic_ids[:count]]
        else:
            topics_to_use = [key_topics.iloc[i] for i in range(min(count, len(key_topics)))]

        for i, topic_data in enumerate(topics_to_use):
            result = blog_generator.generate_blog(
                topic_data,
                seo_keywords,
                llm_keywords,
                website_links
            )

            if result['status'] == 'success':
                # Save to Airtable
                airtable_writer.write_blog_to_airtable(result)
                total_cost += result.get('cost', 0.0)

            results.append({
                'index': i + 1,
                'topic': result['topic'],
                'status': result['status'],
                'word_count': result.get('word_count', 0),
                'cost': result.get('cost', 0.0),
                'tokens': result.get('total_tokens', 0),
                'error': result.get('error', '')
            })

        successful = len([r for r in results if r['status'] == 'success'])

        return jsonify({
            'status': 'completed',
            'summary': {
                'total_requested': count,
                'successful': successful,
                'failed': count - successful,
                'total_cost': round(total_cost, 4),
                'average_cost': round(total_cost / successful, 4) if successful > 0 else 0
            },
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get generation statistics"""
    try:
        return jsonify({
            'available_topics': len(key_topics) if key_topics is not None else 0,
            'seo_categories': len(seo_keywords.columns) if seo_keywords is not None else 0,
            'llm_categories': len(llm_keywords.columns) if llm_keywords is not None else 0,
            'website_links': len(website_links) if website_links is not None else 0,
            'openai_connected': blog_generator.test_connection() if blog_generator else False,
            'airtable_connected': airtable_writer.test_connection() if airtable_writer else False
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Blog Generator API...")

    if initialize_components():
        print("✅ Components initialized successfully")
        print("✅ API server starting on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Failed to initialize components")
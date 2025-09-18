import os
import json
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials as ServiceCredentials
except ImportError:
    print("❌ Google API libraries not installed. Install with:")
    print("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    exit()


class SheetsWriter:
    def __init__(self):
        """Initialize Google Sheets connection"""
        self.service = None
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', '../credentials.json')

        if not self.sheet_id:
            print("❌ GOOGLE_SHEET_ID not found in .env file")
            return

        self.setup_sheets_connection()

    def setup_sheets_connection(self):
        """Setup Google Sheets API connection"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_file):
                print(f"❌ Credentials file not found: {self.credentials_file}")
                print("Please make sure your Google credentials JSON file is in the project folder")
                return

            # Try service account first (recommended for automation)
            try:
                credentials = ServiceCredentials.from_service_account_file(
                    self.credentials_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                print("✅ Using Service Account authentication")
            except Exception:
                # Fall back to OAuth flow
                print("🔄 Using OAuth authentication (will open browser)")
                flow = Flow.from_client_secrets_file(
                    self.credentials_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets'],
                    redirect_uri='http://localhost:8080/callback'
                )

                # Check for existing token
                token_file = 'token.json'
                if os.path.exists(token_file):
                    credentials = Credentials.from_authorized_user_file(token_file)
                    if credentials.expired and credentials.refresh_token:
                        credentials.refresh(Request())
                else:
                    # Run OAuth flow
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print(f"Please visit: {auth_url}")
                    code = input("Enter authorization code: ")
                    flow.fetch_token(code=code)
                    credentials = flow.credentials

                    # Save token for future use
                    with open(token_file, 'w') as f:
                        f.write(credentials.to_json())

            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ Google Sheets API connection successful!")

        except Exception as e:
            print(f"❌ Failed to connect to Google Sheets: {str(e)}")
            self.service = None

    def create_blog_sheet_headers(self):
        """Create headers for the blog data sheet"""
        return [
            'Timestamp',
            'Topic',
            'Meta Title',
            'Meta Description',
            'Blog Content',
            'Word Count',
            'SEO Keywords Used',
            'LLM Keywords Used',
            'Website Links Used',
            'Generation Status',
            'Notes'
        ]

    def setup_sheet_headers(self):
        """Setup headers in the Google Sheet"""
        if not self.service:
            print("❌ Google Sheets not connected")
            return False

        try:
            headers = self.create_blog_sheet_headers()

            # Clear existing content and add headers
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.sheet_id,
                range='A1:Z1000'
            ).execute()

            # Add headers
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range='A1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()

            print("✅ Sheet headers created successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to setup headers: {str(e)}")
            return False

    def extract_meta_from_blog(self, blog_content):
        """Extract meta title and description from blog content"""
        lines = blog_content.split('\n')
        meta_title = ""
        meta_description = ""

        for line in lines:
            if line.startswith('META_TITLE:'):
                meta_title = line.replace('META_TITLE:', '').strip()
            elif line.startswith('META_DESCRIPTION:'):
                meta_description = line.replace('META_DESCRIPTION:', '').strip()

        return meta_title, meta_description

    def write_blog_to_sheets(self, blog_result):
        """Write a single blog result to Google Sheets"""
        if not self.service:
            print("❌ Google Sheets not connected")
            return False

        try:
            # Extract meta information
            meta_title, meta_description = self.extract_meta_from_blog(blog_result['content'])

            # Prepare row data
            row_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Timestamp
                blog_result.get('topic', ''),  # Topic
                meta_title,  # Meta Title
                meta_description,  # Meta Description
                blog_result.get('content', ''),  # Blog Content
                blog_result.get('word_count', 0),  # Word Count
                ', '.join(blog_result.get('seo_keywords_used', [])),  # SEO Keywords
                ', '.join(blog_result.get('llm_keywords_used', [])),  # LLM Keywords
                ', '.join(blog_result.get('links_used', [])),  # Links Used
                blog_result.get('status', 'unknown'),  # Status
                blog_result.get('error', '')  # Notes/Errors
            ]

            # Append to sheet
            self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range='A2',  # Start from row 2 (after headers)
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()

            print(f"✅ Blog '{blog_result.get('topic', 'Unknown')}' saved to Google Sheets!")
            return True

        except Exception as e:
            print(f"❌ Failed to write to Google Sheets: {str(e)}")
            return False

    def write_multiple_blogs(self, blog_results):
        """Write multiple blog results to Google Sheets"""
        if not self.service:
            print("❌ Google Sheets not connected")
            return False

        success_count = 0
        for blog_result in blog_results:
            if self.write_blog_to_sheets(blog_result):
                success_count += 1

        print(f"✅ Successfully saved {success_count}/{len(blog_results)} blogs to Google Sheets!")
        return success_count == len(blog_results)

    def test_connection(self):
        """Test Google Sheets connection"""
        if not self.service:
            return False

        try:
            # Try to read sheet metadata
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()

            sheet_title = sheet_metadata.get('properties', {}).get('title', 'Unknown')
            print(f"✅ Successfully connected to sheet: {sheet_title}")
            return True

        except Exception as e:
            print(f"❌ Sheet connection test failed: {str(e)}")
            return False


# Test the sheets writer
if __name__ == "__main__":
    print("🚀 Testing Google Sheets Writer...")

    # Initialize sheets writer
    writer = SheetsWriter()

    # Test connection
    if not writer.test_connection():
        print("\n📝 To fix Google Sheets connection:")
        print("1. Make sure GOOGLE_SHEET_ID is in your .env file")
        print("2. Make sure credentials.json file exists")
        print("3. Make sure the sheet is shared with your service account email (if using service account)")
        exit()

    # Setup headers
    print("\n📋 Setting up sheet headers...")
    if writer.setup_sheet_headers():
        print("✅ Sheet is ready for blog data!")

        # Test with sample data
        sample_blog = {
            'topic': 'Test Blog',
            'content': 'META_TITLE: Test Title\nMETA_DESCRIPTION: Test Description\n\n# Test Blog\n\nThis is test content.',
            'word_count': 10,
            'seo_keywords_used': ['test', 'sample'],
            'llm_keywords_used': ['demo', 'example'],
            'links_used': ['OpenAI Blog'],
            'status': 'success'
        }

        print("\n🧪 Testing with sample blog...")
        if writer.write_blog_to_sheets(sample_blog):
            print("🎉 Google Sheets integration working perfectly!")
        else:
            print("❌ Failed to write sample blog")
    else:
        print("❌ Failed to setup sheet headers")
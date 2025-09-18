import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ExcelReader:
    def __init__(self, excel_file_path):
        """
        Initialize the Excel reader with the path to your Excel file
        """
        self.excel_file_path = excel_file_path
        self.data = {}

    def read_all_sheets(self):
        """
        Read the first 4 sheets from Excel file as mentioned in your project
        """
        try:
            print(f"Reading Excel file: {self.excel_file_path}")

            # Define the expected sheet names
            expected_sheets = [
                'SEO - Keywords',
                'LLM - Keywords',
                'Website',
                'key topics'
            ]

            # Read all sheets
            excel_data = pd.read_excel(self.excel_file_path, sheet_name=None)

            # Display available sheets
            print(f"Available sheets: {list(excel_data.keys())}")

            # Try to read each expected sheet
            for sheet_name in expected_sheets:
                if sheet_name in excel_data:
                    self.data[sheet_name] = excel_data[sheet_name]
                    print(f"✅ Successfully read '{sheet_name}' - {len(excel_data[sheet_name])} rows")

                    # Display first few rows to see the structure
                    print(f"Preview of '{sheet_name}':")
                    print(excel_data[sheet_name].head())
                    print("-" * 50)
                else:
                    print(f"❌ Sheet '{sheet_name}' not found")

            return self.data

        except FileNotFoundError:
            print(f"❌ Error: Excel file not found at {self.excel_file_path}")
            return None
        except Exception as e:
            print(f"❌ Error reading Excel file: {str(e)}")
            return None

    def get_seo_keywords(self):
        """Get SEO keywords from the data"""
        if 'SEO - Keywords' in self.data:
            return self.data['SEO - Keywords']
        return None

    def get_llm_keywords(self):
        """Get LLM keywords from the data"""
        if 'LLM - Keywords' in self.data:
            return self.data['LLM - Keywords']
        return None

    def get_website_links(self):
        """Get website links from the data"""
        if 'Website' in self.data:
            return self.data['Website']
        return None

    def get_key_topics(self):
        """Get key topics from the data"""
        if 'key topics' in self.data:
            return self.data['key topics']
        return None


# Test the Excel reader
if __name__ == "__main__":
    # Get Excel file path from environment variable
    excel_file = os.getenv('EXCEL_FILE_PATH', 'data/Key Insights.xlsx')
    print(f"Looking for Excel file at: {excel_file}")

    # Check if file exists
    if not os.path.exists(excel_file):
        print(f"❌ File not found! Please make sure '{excel_file}' exists")
        print("Current directory contents:")
        if os.path.exists('data'):
            print("Files in data folder:", os.listdir('data'))
        else:
            print("'data' folder doesn't exist - please create it and put your Excel file there")
        exit()

    # Create reader instance
    reader = ExcelReader(excel_file)

    # Read all sheets
    data = reader.read_all_sheets()

    if data:
        print("\n🎉 Excel file reading successful!")
        print(f"Total sheets read: {len(data)}")

        # Test individual sheet access
        seo_keywords = reader.get_seo_keywords()
        if seo_keywords is not None:
            print(f"\nSEO Keywords sheet has {len(seo_keywords)} rows")
    else:
        print("\n❌ Failed to read Excel file")
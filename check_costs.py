import os


def check_blog_costs():
    """Simple script to check if our blogs have cost information"""

    blog_folder = "generated_blogs"

    # Check if folder exists
    if not os.path.exists(blog_folder):
        print("❌ No generated_blogs folder found")
        return

    # Find blog files
    blog_files = [f for f in os.listdir(blog_folder) if f.startswith('blog_') and f.endswith('.txt')]

    print(f"📁 Found {len(blog_files)} blog files")

    # Check first blog file to see structure
    if blog_files:
        first_blog = blog_files[0]
        filepath = os.path.join(blog_folder, first_blog)

        print(f"\n📄 Checking: {first_blog}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Show first 20 lines to see structure
        lines = content.split('\n')[:20]

        print("📊 First 20 lines of blog file:")
        print("-" * 40)
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line}")

        # Check if we have token/cost info
        has_tokens = "Input Tokens:" in content
        has_cost = "Cost:" in content

        print(f"\n🔍 Analysis:")
        print(f"Has token information: {'✅' if has_tokens else '❌'}")
        print(f"Has cost information: {'✅' if has_cost else '❌'}")

        if not has_tokens or not has_cost:
            print("\n💡 Your blogs don't have token/cost tracking yet.")
            print("We need to regenerate them with the enhanced version.")
        else:
            print("\n✅ Your blogs already have token/cost tracking!")


if __name__ == "__main__":
    print("🚀 Checking your blog files for token/cost data...")
    check_blog_costs()
import os
import re


def create_manager_report():
    """Create a summary report for your manager showing token usage and costs"""

    blog_folder = "generated_blogs"

    if not os.path.exists(blog_folder):
        print("❌ Please generate blogs first using: python main.py")
        return

    # Find all blog files
    blog_files = [f for f in os.listdir(blog_folder) if f.startswith('blog_') and f.endswith('.txt')]

    if not blog_files:
        print("❌ No blog files found")
        return

    # Analyze all blogs
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    blog_data = []

    print("📊 MANAGER REPORT - TOKEN USAGE AND COSTS")
    print("=" * 60)

    for filename in sorted(blog_files):
        filepath = os.path.join(blog_folder, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract data
        topic_match = re.search(r'Topic: (.+)', content)
        input_tokens_match = re.search(r'Input Tokens: ([\d,]+)', content)
        output_tokens_match = re.search(r'Output Tokens: ([\d,]+)', content)
        cost_match = re.search(r'Cost: \$([\d.]+)', content)
        word_count_match = re.search(r'Word Count: (\d+)', content)
        model_match = re.search(r'Model Used: (.+)', content)

        if all([topic_match, input_tokens_match, output_tokens_match, cost_match]):
            topic = topic_match.group(1)
            input_tokens = int(input_tokens_match.group(1).replace(',', ''))
            output_tokens = int(output_tokens_match.group(1).replace(',', ''))
            cost = float(cost_match.group(1))
            word_count = int(word_count_match.group(1)) if word_count_match else 0
            model = model_match.group(1) if model_match else "Unknown"

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_cost += cost

            blog_data.append({
                'topic': topic,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens,
                'cost': cost,
                'word_count': word_count,
                'model': model
            })

    # Show summary
    blog_count = len(blog_data)
    total_tokens = total_input_tokens + total_output_tokens
    avg_cost_per_blog = total_cost / blog_count if blog_count > 0 else 0

    print(f"📅 Report Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Model Used: {blog_data[0]['model'] if blog_data else 'Unknown'}")
    print(f"📝 Total Blogs Generated: {blog_count}")
    print(f"📊 Total Input Tokens: {total_input_tokens:,}")
    print(f"📊 Total Output Tokens: {total_output_tokens:,}")
    print(f"📊 Total Tokens Used: {total_tokens:,}")
    print(f"💰 Total Cost: ${total_cost:.4f}")
    print(f"💰 Average Cost per Blog: ${avg_cost_per_blog:.4f}")
    print(f"💰 Cost per 1,000 tokens: ${(total_cost * 1000 / total_tokens):.4f}")

    print(f"\n📋 INDIVIDUAL BLOG BREAKDOWN:")
    print("-" * 80)
    print(f"{'#':<3} {'Topic':<35} {'Tokens':<8} {'Words':<6} {'Cost':<8}")
    print("-" * 80)

    for i, blog in enumerate(blog_data, 1):
        topic_short = blog['topic'][:34] + "..." if len(blog['topic']) > 34 else blog['topic']
        print(f"{i:<3} {topic_short:<35} {blog['total_tokens']:<8,} {blog['word_count']:<6} ${blog['cost']:<7.4f}")

    # Save detailed report
    with open('MANAGER_REPORT.txt', 'w', encoding='utf-8') as f:
        f.write("BLOG GENERATION - TOKEN USAGE AND COST REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Report Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Project: Blog Generation Agent\n")
        f.write(f"Developer: Sandeep\n\n")

        f.write("SUMMARY:\n")
        f.write("-" * 30 + "\n")
        f.write(f"Model Used: {blog_data[0]['model'] if blog_data else 'Unknown'}\n")
        f.write(f"Total Blogs: {blog_count}\n")
        f.write(f"Total Input Tokens: {total_input_tokens:,}\n")
        f.write(f"Total Output Tokens: {total_output_tokens:,}\n")
        f.write(f"Total Tokens: {total_tokens:,}\n")
        f.write(f"Total Cost: ${total_cost:.4f}\n")
        f.write(f"Average Cost per Blog: ${avg_cost_per_blog:.4f}\n")
        f.write(f"Cost per 1,000 tokens: ${(total_cost * 1000 / total_tokens):.4f}\n\n")

        f.write("PRICING BREAKDOWN:\n")
        f.write("-" * 30 + "\n")
        f.write(f"Input Token Cost (${0.005}/1K): ${total_input_tokens * 0.005 / 1000:.4f}\n")
        f.write(f"Output Token Cost (${0.015}/1K): ${total_output_tokens * 0.015 / 1000:.4f}\n\n")

        f.write("INDIVIDUAL BLOG DETAILS:\n")
        f.write("-" * 30 + "\n")
        for i, blog in enumerate(blog_data, 1):
            f.write(f"\nBlog {i}: {blog['topic']}\n")
            f.write(f"  Input Tokens: {blog['input_tokens']:,}\n")
            f.write(f"  Output Tokens: {blog['output_tokens']:,}\n")
            f.write(f"  Total Tokens: {blog['total_tokens']:,}\n")
            f.write(f"  Word Count: {blog['word_count']}\n")
            f.write(f"  Cost: ${blog['cost']:.4f}\n")

    print(f"\n💾 Detailed report saved to: MANAGER_REPORT.txt")
    print(f"\n🎯 KEY INSIGHTS FOR MANAGER:")
    print(f"   • Each blog costs approximately ${avg_cost_per_blog:.4f}")
    print(f"   • Total project cost: ${total_cost:.4f}")
    print(f"   • Very cost-effective: ~{avg_cost_per_blog * 100:.1f} cents per professional blog")
    print(f"   • Token efficiency: {(total_tokens / blog_count):,.0f} tokens per blog on average")


if __name__ == "__main__":
    import pandas as pd

    print("🚀 Creating Manager Report...")
    create_manager_report()
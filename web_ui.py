#!/usr/bin/env python
"""Simple Streamlit web UI for YouTube Video Processor."""

import os
import glob
import subprocess
from pathlib import Path

import streamlit as st


def get_existing_categories():
    """Get list of existing categories from outputs directory."""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        return []

    categories = []
    for item in outputs_dir.iterdir():
        if item.is_dir():
            # Handle nested categories (e.g., AI/Agents)
            for subitem in item.rglob("*.md"):
                relative_path = subitem.parent.relative_to(outputs_dir)
                category = str(relative_path)
                if category not in categories:
                    categories.append(category)

    return sorted(categories)


def process_video(url: str, category: str = None):
    """Process a YouTube video using the CLI with real-time progress updates."""
    cmd = ["python", "-m", "yt_extractor.cli", "process", url, "--output-dir", "./outputs"]

    if category:
        cmd.extend(["--category", category])

    try:
        # Use Popen for real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        output_lines = []
        progress_placeholder = st.empty()

        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                output_lines.append(line.strip())

                # Update progress based on key indicators
                if "metadata" in line.lower():
                    progress_placeholder.info("📋 Extracting video metadata...")
                elif "transcript" in line.lower():
                    progress_placeholder.info("📝 Downloading transcript...")
                elif "llm_processing" in line.lower():
                    progress_placeholder.info("🤖 Analyzing with GPT-5 (this may take several minutes)...")
                elif "analyzing full transcript" in line.lower():
                    progress_placeholder.info("🧠 GPT-5 analyzing video content...")
                elif "generating markdown" in line.lower():
                    progress_placeholder.info("📄 Generating final report...")
                elif "saved to:" in line.lower():
                    progress_placeholder.success("✅ Processing completed!")
                elif "failed" in line.lower() or "error" in line.lower():
                    progress_placeholder.error(f"❌ {line.strip()}")

        # Wait for process to complete
        return_code = process.wait(timeout=600)

        full_output = '\n'.join(output_lines)

        if return_code == 0:
            return True, full_output
        else:
            return False, full_output

    except subprocess.TimeoutExpired:
        if 'process' in locals():
            process.kill()
        return False, "⏰ Processing timed out after 10 minutes. The video might be too long or GPT-5 might be busy. Please try again."
    except Exception as e:
        return False, f"❌ Unexpected error: {str(e)}"


def get_recent_videos(limit: int = 10):
    """Get recently processed videos."""
    md_files = glob.glob("outputs/**/*.md", recursive=True)

    # Sort by modification time (most recent first)
    md_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    recent = []
    for file_path in md_files[:limit]:
        path = Path(file_path)
        category = path.parent.relative_to(Path("outputs"))
        filename = path.name

        recent.append({
            "category": str(category) if str(category) != "." else "Uncategorized",
            "filename": filename,
            "path": file_path
        })

    return recent


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="YouTube Video Processor",
        page_icon="🎥",
        layout="wide"
    )

    st.title("🎥 YouTube Video Processor")
    st.markdown("Process YouTube videos and organize them by category")

    # Main processing form
    with st.form("process_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            url = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Paste the full YouTube URL here"
            )

        with col2:
            existing_categories = get_existing_categories()

            if existing_categories:
                category_option = st.selectbox(
                    "Select Category",
                    ["Custom..."] + existing_categories,
                    help="Choose an existing category or select 'Custom...' to create a new one"
                )

                if category_option == "Custom...":
                    category = st.text_input(
                        "Custom Category",
                        placeholder="e.g., AI/Agents, Business/Marketing",
                        help="Use forward slashes for nested categories"
                    )
                else:
                    category = category_option
            else:
                category = st.text_input(
                    "Category",
                    placeholder="e.g., AI/Agents, Business/Marketing",
                    help="Use forward slashes for nested categories"
                )

        submitted = st.form_submit_button("🚀 Process Video", use_container_width=True)

    if submitted:
        if not url:
            st.error("Please enter a YouTube URL")
        else:
            # Create a container for dynamic updates
            status_container = st.container()

            with status_container:
                st.info("🚀 Starting video processing...")

                # Process video with real-time updates
                success, output = process_video(url, category)

                if success:
                    st.success("🎉 Video processed successfully!")

                    # Extract file path from output
                    import re
                    saved_to_match = re.search(r'✅ Saved to: (.+)', output)
                    if saved_to_match:
                        file_path = saved_to_match.group(1)
                        st.info(f"📄 **File saved to:** `{file_path}`")

                        # Add a button to refresh the recent videos list
                        if st.button("🔄 Refresh Recent Videos"):
                            st.rerun()
                    elif category:
                        st.info(f"📁 **Saved to category:** `./outputs/{category}/`")
                    else:
                        st.info(f"📁 **Saved to:** `./outputs/`")

                    # Show enhanced success info
                    st.markdown("### ✨ What happened:")
                    st.markdown("""
                    1. 📋 **Metadata extracted** - Video title, duration, and channel info
                    2. 📝 **Transcript downloaded** - Full video transcript obtained
                    3. 🤖 **GPT-5 analysis** - AI analyzed the entire transcript for insights
                    4. 📄 **Report generated** - Comprehensive markdown report created
                    5. 💾 **File saved** - Report saved to your specified category folder
                    """)

                    # Show output in expandable section
                    with st.expander("📋 View Detailed Processing Log"):
                        st.text(output)
                else:
                    st.error("❌ Processing failed")

                    # Better error handling and troubleshooting
                    st.markdown("### 🔧 Troubleshooting:")
                    if "timeout" in output.lower():
                        st.markdown("- **Timeout occurred**: The video might be very long or GPT-5 is busy")
                        st.markdown("- **Try**: Wait a few minutes and try again with a shorter video")
                    elif "api" in output.lower() or "key" in output.lower():
                        st.markdown("- **API Issue**: Check your OpenAI API key configuration")
                        st.markdown("- **Try**: Verify your API key has sufficient credits")
                    elif "transcript" in output.lower():
                        st.markdown("- **Transcript Issue**: Video might not have captions available")
                        st.markdown("- **Try**: Use a video with auto-generated or manual captions")
                    else:
                        st.markdown("- **General Error**: See detailed log below for specific error")

                    with st.expander("📋 View Error Details"):
                        st.text(output)

    # Divider
    st.divider()

    # Recent videos section
    st.header("📚 Recent Videos")

    recent_videos = get_recent_videos()

    if not recent_videos:
        st.info("No videos processed yet. Process your first video above!")
    else:
        for video in recent_videos:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    # Remove file extension and format filename
                    display_name = video["filename"].replace(".md", "").replace("--", " - ")
                    st.markdown(f"**{display_name}**")

                with col2:
                    st.markdown(f"📁 {video['category']}")

                with col3:
                    if st.button("👁️ View", key=video["path"]):
                        # Read and display the markdown content
                        try:
                            content = Path(video["path"]).read_text(encoding="utf-8")
                            st.markdown("---")
                            st.markdown(content)
                            st.markdown("---")
                        except Exception as e:
                            st.error(f"Error reading file: {e}")

    # Footer
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("💡 **Tip**: Use categories like `AI/Agents`, `Business/Marketing`, or `Crypto/DeFi` to organize your videos")
    with col2:
        st.markdown("📁 **Files saved to**: `./outputs/$Category/` directory")

    # Processing info
    st.markdown("---")
    st.markdown("### ⏱️ Processing Times with GPT-5:")
    st.markdown("""
    - **Short videos** (< 5 min): ~30-60 seconds
    - **Medium videos** (5-20 min): ~2-3 minutes
    - **Long videos** (20+ min): ~3-5 minutes
    - **Very long videos** (45+ min): ~5-10 minutes

    💰 **Note**: GPT-5 provides significantly higher quality analysis than GPT-4o-mini but takes longer and costs more per request.
    """)


if __name__ == "__main__":
    main()
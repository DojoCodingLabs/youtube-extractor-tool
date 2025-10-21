#!/usr/bin/env python
"""Simple Streamlit web UI for YouTube Video Processor."""

import os
import glob
import subprocess
from pathlib import Path
from datetime import datetime

import streamlit as st
import threading
import time

from yt_extractor.utils.pdf_generator import PDFGenerator
from yt_extractor.utils.queue_manager import ProcessingQueue, QueueStatus
from yt_extractor.core.extractor import YouTubeExtractor


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
                    progress_placeholder.info("🔍 **Analyzing video details...** Fetching title, duration, and channel info")
                elif "transcript" in line.lower():
                    progress_placeholder.info("📝 **Extracting transcript...** Downloading full video captions")
                elif "llm_processing" in line.lower():
                    progress_placeholder.info("🧠 **AI is analyzing content...** GPT-5 is extracting insights (2-5 minutes)")
                elif "analyzing full transcript" in line.lower():
                    progress_placeholder.info("💡 **Deep analysis in progress...** Identifying key insights and frameworks")
                elif "generating markdown" in line.lower():
                    progress_placeholder.info("📄 **Creating your report...** Formatting insights into structured document")
                elif "saved to:" in line.lower():
                    progress_placeholder.success("🎉 **Insights extracted successfully!** Your report is ready")
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


def export_markdown_to_pdf(
    uploaded_file,
    include_metadata: bool = True,
    page_size: str = "letter",
    font_size: int = 11,
) -> tuple[bool, str, Path | None]:
    """
    Export a markdown file to PDF.

    Args:
        uploaded_file: Streamlit uploaded file object
        include_metadata: Whether to include metadata section
        page_size: Page size (letter, a4)
        font_size: Base font size

    Returns:
        Tuple of (success, message, pdf_path)
    """
    try:
        # Create temporary directory for PDF exports
        pdf_dir = Path("outputs/pdf_exports")
        pdf_dir.mkdir(parents=True, exist_ok=True)

        # Save uploaded file temporarily
        temp_md_path = pdf_dir / f"temp_{uploaded_file.name}"
        temp_md_path.write_bytes(uploaded_file.getvalue())

        # Generate PDF filename
        pdf_filename = temp_md_path.stem + ".pdf"
        pdf_path = pdf_dir / pdf_filename

        # Generate PDF
        generator = PDFGenerator()
        generator.generate_pdf(
            markdown_path=temp_md_path,
            output_path=pdf_path,
            include_metadata=include_metadata,
            page_size=page_size,
            font_size=font_size,
        )

        # Clean up temp markdown file
        temp_md_path.unlink()

        return True, f"✅ PDF generated successfully: {pdf_filename}", pdf_path

    except Exception as e:
        return False, f"❌ Error generating PDF: {str(e)}", None


def get_recent_pdf_exports(limit: int = 10):
    """Get recently generated PDFs."""
    pdf_dir = Path("outputs/pdf_exports")
    if not pdf_dir.exists():
        return []

    pdf_files = list(pdf_dir.glob("*.pdf"))
    # Sort by modification time (most recent first)
    pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    recent = []
    for pdf_path in pdf_files[:limit]:
        stat = pdf_path.stat()
        recent.append({
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
        })

    return recent


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="YouTube Value Extractor - AI-Powered Insights",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
            ⚡ YouTube Value Extractor
        </h1>
        <p style="font-size: 1.3rem; color: #666; margin-bottom: 1rem;">
            Turn YouTube Videos Into Actionable Insights
        </p>
        <p style="font-size: 1rem; color: #888; max-width: 700px; margin: 0 auto 1.5rem auto;">
            AI-powered analysis that extracts key insights, frameworks, and strategies from any video.
            Get publication-grade summaries in minutes, not hours.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Benefits badges
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**✨ Full-Context Analysis**<br/>Understands entire videos", unsafe_allow_html=True)
    with col2:
        st.markdown("**🎯 Actionable Frameworks**<br/>Step-by-step guides", unsafe_allow_html=True)
    with col3:
        st.markdown("**📊 Structured Insights**<br/>Organized format", unsafe_allow_html=True)
    with col4:
        st.markdown("**⚡ Fast Processing**<br/>Results in 2-5 min", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["⚡ Extract Insights", "📚 Batch Processing", "📄 Export to PDF"])

    with tab1:
        render_process_tab()

    with tab2:
        render_batch_queue_tab()

    with tab3:
        render_pdf_export_tab()

    # Professional footer
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem 0;">
        <p style="margin: 0.5rem 0;">
            <strong>⚡ YouTube Value Extractor</strong> — Powered by GPT-5
        </p>
        <p style="margin: 0.5rem 0; font-size: 0.9rem;">
            Transform hours of video into actionable insights in minutes
        </p>
        <p style="margin: 0.5rem 0; font-size: 0.85rem;">
            <a href="https://github.com/yourusername/youtube-extractor-tool" target="_blank" style="color: #1E88E5; text-decoration: none;">
                Documentation
            </a> •
            <a href="https://github.com/yourusername/youtube-extractor-tool/issues" target="_blank" style="color: #1E88E5; text-decoration: none;">
                Report Issue
            </a> •
            <a href="https://github.com/yourusername/youtube-extractor-tool" target="_blank" style="color: #1E88E5; text-decoration: none;">
                GitHub
            </a>
        </p>
        <p style="margin: 0.5rem 0; font-size: 0.8rem; color: #aaa;">
            Built with ❤️ using Streamlit & LiteLLM • Version 1.0
        </p>
    </div>
    """, unsafe_allow_html=True)


def process_video_with_cli(url: str, category: str, progress_placeholder, detail_placeholder, queue, item_id: str):
    """
    Process a single video using CLI to capture rich progress output.

    Args:
        url: YouTube URL
        category: Category for organization
        progress_placeholder: Streamlit placeholder for progress indicator
        detail_placeholder: Streamlit placeholder for detailed output
        queue: ProcessingQueue instance
        item_id: Queue item ID for status updates

    Returns:
        Tuple of (success: bool, output_path: str or None)
    """
    cmd = ["python", "-m", "yt_extractor.cli", "process", url, "--output-dir", "./outputs"]

    if category:
        cmd.extend(["--category", category])

    try:
        # Update status to processing
        queue.update_status(item_id, QueueStatus.PROCESSING)

        # Use Popen for real-time output capture
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        output_lines = []
        output_path = None

        # Read output line by line with rich progress updates
        for line in iter(process.stdout.readline, ''):
            if line:
                output_lines.append(line.strip())

                # Update progress based on key indicators
                if "metadata" in line.lower() or "extracting" in line.lower():
                    progress_placeholder.info("🔍 **Analyzing video details...** Fetching title, duration, and channel info")
                elif "transcript" in line.lower() or "downloading" in line.lower():
                    progress_placeholder.info("📝 **Extracting transcript...** Downloading full video captions")
                elif "llm" in line.lower() or "analyzing" in line.lower():
                    progress_placeholder.info("🧠 **AI is analyzing content...** GPT-5 is extracting insights (2-5 minutes)")
                elif "generating" in line.lower() or "markdown" in line.lower():
                    progress_placeholder.info("📄 **Creating your report...** Formatting insights into structured document")
                elif "saved to:" in line.lower():
                    progress_placeholder.success("🎉 **Insights extracted successfully!** Your report is ready")
                    # Extract output path
                    import re
                    match = re.search(r'Saved to: (.+)', line)
                    if match:
                        output_path = match.group(1)
                elif "failed" in line.lower() or "error" in line.lower():
                    progress_placeholder.error(f"❌ {line.strip()}")

                # Show last few lines in detail placeholder
                detail_placeholder.text("\n".join(output_lines[-10:]))

        # Wait for process to complete
        return_code = process.wait(timeout=600)

        if return_code == 0 and output_path:
            queue.update_status(item_id, QueueStatus.COMPLETED, output_path=output_path)
            return True, output_path
        else:
            error_msg = "\n".join(output_lines[-5:]) if output_lines else "Unknown error"
            queue.update_status(item_id, QueueStatus.FAILED, error=error_msg)
            return False, None

    except subprocess.TimeoutExpired:
        if 'process' in locals():
            process.kill()
        error_msg = "Processing timed out after 10 minutes"
        queue.update_status(item_id, QueueStatus.FAILED, error=error_msg)
        progress_placeholder.error(f"⏰ {error_msg}")
        return False, None
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        queue.update_status(item_id, QueueStatus.FAILED, error=error_msg)
        progress_placeholder.error(f"❌ {error_msg}")
        return False, None


def render_batch_queue_tab():
    """Render the batch queue tab with modern responsive UI."""
    st.header("📚 Batch Process Multiple Videos")
    st.markdown("Queue up videos and extract insights from entire playlists or series. Perfect for learning from multiple sources or processing content libraries.")

    # Add custom CSS for animations and modern styling
    st.markdown("""
    <style>
    /* Animations */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .processing-indicator {
        animation: spin 2s linear infinite;
        display: inline-block;
    }

    /* Modern card design */
    .queue-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        animation: fadeIn 0.3s ease-out;
    }

    .queue-card:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        transform: translateX(4px);
        border-left-color: #1565C0;
    }

    /* Enhanced status badges */
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 16px;
        font-size: 0.85em;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .status-pending {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        color: #E65100;
        border: 1px solid #FFB74D;
    }

    .status-processing {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        color: #0D47A1;
        animation: pulse 2s ease-in-out infinite;
        border: 1px solid #64B5F6;
    }

    .status-completed {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        color: #1B5E20;
        border: 1px solid #81C784;
    }

    .status-failed {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        color: #B71C1C;
        border: 1px solid #E57373;
    }

    /* Better spacing and typography */
    .stMarkdown h1 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .stMarkdown h2 {
        font-weight: 600;
        margin-top: 2rem;
        color: #1E88E5;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left-width: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize queue
    if "queue" not in st.session_state:
        st.session_state.queue = ProcessingQueue()

    queue = st.session_state.queue

    # Add URLs section
    st.subheader("➕ Add Videos to Queue")

    col1, col2 = st.columns([3, 1])

    with col1:
        # Text area for multiple URLs
        urls_input = st.text_area(
            "YouTube URLs (one per line)",
            height=150,
            placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...",
            help="Paste YouTube URLs, one per line. Lines starting with # are ignored."
        )

        # File uploader for .txt files
        uploaded_file = st.file_uploader(
            "Or upload a .txt file with URLs",
            type=["txt"],
            help="Upload a text file with one YouTube URL per line"
        )

    with col2:
        # Category selection - initialize to None
        category = None

        existing_categories = get_existing_categories()
        if existing_categories:
            category_option = st.selectbox(
                "Category",
                ["Custom..."] + existing_categories,
                help="Select category for all videos in this batch"
            )
            if category_option == "Custom...":
                custom_input = st.text_input(
                    "Custom Category",
                    placeholder="e.g., AI/Agents",
                    help="Use forward slashes for nested categories"
                )
                # Sanitize: convert empty string to None
                category = custom_input.strip() if custom_input and custom_input.strip() else None
            else:
                category = category_option
        else:
            user_input = st.text_input(
                "Category",
                placeholder="e.g., AI/Agents",
                help="Use forward slashes for nested categories"
            )
            # Sanitize: convert empty string to None
            category = user_input.strip() if user_input and user_input.strip() else None

    # Add to queue button
    if st.button("➕ Add to Queue", type="primary", use_container_width=True):
        urls = []

        # Get URLs from text area
        if urls_input:
            urls.extend([line.strip() for line in urls_input.split("\n")])

        # Get URLs from uploaded file
        if uploaded_file:
            content = uploaded_file.getvalue().decode("utf-8")
            urls.extend([line.strip() for line in content.split("\n")])

        # Filter and add URLs
        urls = [url for url in urls if url and not url.startswith("#")]

        if urls:
            added_count = 0
            duplicate_count = 0
            invalid_count = 0

            for url in urls:
                try:
                    queue.add(url, category=category)
                    added_count += 1
                except ValueError as e:
                    # Check if it's a duplicate or invalid URL
                    if "already in queue" in str(e):
                        duplicate_count += 1
                    else:
                        invalid_count += 1

            if added_count > 0:
                st.success(f"✅ Added {added_count} video(s) to queue")
            if duplicate_count > 0:
                st.warning(f"⚠️ Skipped {duplicate_count} duplicate URL(s)")
            if invalid_count > 0:
                st.error(f"❌ Skipped {invalid_count} invalid URL(s)")

            # Auto-start processing after adding URLs
            if added_count > 0:
                st.session_state.auto_start_queue = True
                st.rerun()
        else:
            st.error("❌ No valid URLs provided")

    # Queue statistics
    stats = queue.get_stats()
    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", stats["total"])
    col2.metric("Pending", stats["pending"], delta=None)
    col3.metric("Processing", stats["processing"])
    col4.metric("Completed", stats["completed"])
    col5.metric("Failed", stats["failed"])

    # Auto-start logic: automatically begin processing after adding URLs
    if st.session_state.get("auto_start_queue", False) and stats["pending"] > 0:
        st.session_state.auto_start_queue = False
        st.session_state.processing = True

    # Queue controls
    st.divider()
    st.subheader("🎬 Queue Controls")

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        if st.button("▶️ Process Queue", disabled=stats["pending"] == 0, use_container_width=True):
            st.session_state.processing = True
            st.rerun()

    with col2:
        if st.button("🗑️ Clear Completed", disabled=stats["completed"] == 0, use_container_width=True):
            queue.clear(status_filter=QueueStatus.COMPLETED)
            st.success("Cleared completed items")
            st.rerun()

    with col3:
        if st.button("🗑️ Clear Failed", disabled=stats["failed"] == 0, use_container_width=True):
            queue.clear(status_filter=QueueStatus.FAILED)
            st.success("Cleared failed items")
            st.rerun()

    # Process queue if requested (manual or auto-start)
    if st.session_state.get("processing", False):
        process_queue_with_live_updates(queue)
        st.session_state.processing = False

    # Display queue
    st.divider()
    st.subheader("📜 Queue Items")

    items = queue.get_all()

    if not items:
        st.info("📚 **Ready to batch process?** Add YouTube URLs above to queue multiple videos for extraction.")
    else:
        for item in items:
            render_queue_item(item, queue)


def render_queue_item(item, queue):
    """Render a single queue item with modern card-based UI."""
    # Status emoji
    status_emoji = {
        QueueStatus.PENDING: "⏳",
        QueueStatus.PROCESSING: "🔄",
        QueueStatus.COMPLETED: "✅",
        QueueStatus.FAILED: "❌",
    }

    # Status CSS class mapping
    status_class = {
        QueueStatus.PENDING: "status-pending",
        QueueStatus.PROCESSING: "status-processing",
        QueueStatus.COMPLETED: "status-completed",
        QueueStatus.FAILED: "status-failed",
    }

    # Processing indicator with animation
    if item.status == QueueStatus.PROCESSING:
        emoji_html = f'<span class="processing-indicator">{status_emoji[item.status]}</span>'
    else:
        emoji_html = status_emoji[item.status]

    # Build card HTML
    card_html = f"""
    <div class="queue-card">
        <div style="display: flex; align-items: flex-start; gap: 16px;">
            <div style="font-size: 2em; line-height: 1;">
                {emoji_html}
            </div>
            <div style="flex: 1;">
                <div style="margin-bottom: 8px;">
    """

    with st.container():
        # Render card header
        st.markdown(card_html, unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])

        with col1:
            if item.title:
                st.markdown(f"**{item.title}**")
                if item.channel:
                    st.caption(f"📺 {item.channel}")
            else:
                st.markdown(f"`{item.url}`")

            if item.category:
                st.caption(f"📁 Category: **{item.category}**")

            # Status badge
            status_badge = f'<span class="status-badge {status_class[item.status]}">{item.status.value.upper()}</span>'
            st.markdown(status_badge, unsafe_allow_html=True)

            # Show timestamps
            if item.added_at:
                from datetime import datetime
                try:
                    added_dt = datetime.fromisoformat(item.added_at)
                    st.caption(f"🕐 Added: {added_dt.strftime('%Y-%m-%d %H:%M')}")
                except:
                    pass

            if item.processed_at:
                from datetime import datetime
                try:
                    processed_dt = datetime.fromisoformat(item.processed_at)
                    st.caption(f"✓ Processed: {processed_dt.strftime('%Y-%m-%d %H:%M')}")
                except:
                    pass

            # Show error or output path
            if item.error:
                with st.expander("❌ Error Details", expanded=False):
                    st.error(item.error)
            elif item.output_path:
                st.caption(f"💾 Output: `{item.output_path}`")

        with col2:
            # Action buttons
            if item.status == QueueStatus.PENDING:
                if st.button("⬆️", key=f"up_{item.id}", help="Move up", use_container_width=True):
                    queue.move_up(item.id)
                    st.rerun()
                if st.button("⬇️", key=f"down_{item.id}", help="Move down", use_container_width=True):
                    queue.move_down(item.id)
                    st.rerun()
                if st.button("🗑️", key=f"del_{item.id}", help="Remove", use_container_width=True):
                    queue.remove(item.id)
                    st.rerun()
            elif item.status == QueueStatus.FAILED:
                if st.button("🔄 Retry", key=f"retry_{item.id}", use_container_width=True):
                    queue.update_status(item.id, QueueStatus.PENDING, error=None)
                    st.rerun()
            elif item.status == QueueStatus.COMPLETED:
                st.success("Done", icon="✅")

        # Close card HTML
        st.markdown("</div></div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)


def process_queue_with_live_updates(queue: ProcessingQueue) -> None:
    """
    Process the queue with rich real-time UI updates per video.

    Uses CLI subprocess approach (same as single video tab) to capture
    detailed progress output. Updates UI live during processing with
    expandable per-video sections.

    Args:
        queue: ProcessingQueue instance to process
    """
    # Get initial count for progress tracking
    stats = queue.get_stats()
    initial_pending = stats["pending"]

    if initial_pending == 0:
        st.warning("No pending items to process")
        return

    # Overall progress tracking
    st.markdown("### 🚀 Processing Queue")
    overall_progress = st.progress(0)
    overall_status = st.empty()

    processed_count = 0
    failed_count = 0
    completed_count = 0

    # Initialize extractor for metadata
    extractor = YouTubeExtractor()

    # Container for live queue display
    queue_display = st.container()

    # Process items dynamically (fixes race condition)
    while True:
        item = queue.get_next_pending()
        if not item:
            break  # No more pending items

        processed_count += 1

        # Update overall progress
        progress = processed_count / initial_pending
        overall_progress.progress(min(progress, 1.0))
        overall_status.info(f"📹 Processing video {processed_count} of {initial_pending}")

        # Fetch metadata if not already available
        if not item.title:
            try:
                meta = extractor.fetch_metadata(item.url)
                queue.update_metadata(item.id, title=meta.title, channel=meta.channel)
                # Refresh item
                item = queue.get_by_id(item.id)
            except Exception:
                pass  # Continue even if metadata fetch fails

        # Create expandable section for this video
        with queue_display:
            video_title = item.title or item.url
            with st.expander(f"🔄 Processing: {video_title}", expanded=True):
                st.markdown(f"**URL:** {item.url}")
                if item.category:
                    st.markdown(f"**Category:** {item.category}")

                # Progress and detail placeholders
                progress_placeholder = st.empty()
                detail_placeholder = st.empty()

                # Process using CLI for rich output
                success, output_path = process_video_with_cli(
                    url=item.url,
                    category=item.category,
                    progress_placeholder=progress_placeholder,
                    detail_placeholder=detail_placeholder,
                    queue=queue,
                    item_id=item.id
                )

                if success:
                    completed_count += 1
                    st.success(f"✅ Completed: {output_path}")
                else:
                    failed_count += 1
                    st.error(f"❌ Failed - check error details above")

        # Brief pause to show final status before next video
        time.sleep(1)

        # Update live queue display (refresh the queue list)
        with queue_display:
            st.divider()

    # Final status
    overall_progress.progress(1.0)

    if failed_count > 0:
        overall_status.warning(
            f"⚠️ Queue processing complete: {completed_count} succeeded, {failed_count} failed"
        )
    else:
        overall_status.success(f"🎉 All {processed_count} video(s) processed successfully!")

    # Force UI refresh to show updated queue
    time.sleep(2)
    st.rerun()


def render_pdf_export_tab():
    """Render the PDF export tab."""
    st.header("📄 Create Professional PDF Reports")
    st.markdown("Convert your insights into shareable, print-ready PDF documents. Perfect for sharing knowledge, creating study guides, or archiving research.")

    # File uploader with drag-and-drop
    uploaded_file = st.file_uploader(
        "Choose a markdown file",
        type=["md", "markdown"],
        help="Drag and drop a .md file here, or click to browse",
    )

    if uploaded_file is not None:
        # Show file info
        st.success(f"📁 File uploaded: **{uploaded_file.name}**")

        # Preview section
        with st.expander("👁️ Preview Markdown Content", expanded=False):
            content = uploaded_file.getvalue().decode("utf-8")
            st.markdown(content[:2000] + ("..." if len(content) > 2000 else ""))

        # Export options
        st.subheader("⚙️ Export Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            include_metadata = st.checkbox(
                "Include Metadata Section",
                value=True,
                help="Include video title, channel, date, etc. at the top of PDF"
            )

        with col2:
            page_size = st.selectbox(
                "Page Size",
                options=["Letter", "A4"],
                help="Select page size for PDF"
            ).lower()

        with col3:
            font_size = st.slider(
                "Font Size",
                min_value=9,
                max_value=14,
                value=11,
                help="Base font size in points"
            )

        # Generate button
        if st.button("🚀 Generate PDF", use_container_width=True, type="primary"):
            with st.spinner("Generating PDF..."):
                success, message, pdf_path = export_markdown_to_pdf(
                    uploaded_file=uploaded_file,
                    include_metadata=include_metadata,
                    page_size=page_size,
                    font_size=font_size,
                )

                if success:
                    st.success(message)

                    # Download button
                    if pdf_path and pdf_path.exists():
                        with open(pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=pdf_file,
                                file_name=pdf_path.name,
                                mime="application/pdf",
                                use_container_width=True,
                            )
                else:
                    st.error(message)

    else:
        # Show instructions when no file uploaded
        st.info("📄 **Ready to create a PDF?** Upload a markdown insight file above to transform it into a professional document.")

        with st.expander("📋 How It Works", expanded=False):
            st.markdown("""
            ### Simple 4-Step Process:
            1. **Upload** - Choose a markdown file from your `outputs/` folder
            2. **Preview** - Review the content before converting (optional)
            3. **Configure** - Adjust page size, font, and metadata options
            4. **Generate** - Create and download your professional PDF

            ### ✨ What You Get:
            - 📖 Professional typography and layout
            - 📑 Automatic table of contents
            - 🎨 Syntax highlighting for code
            - 📄 Page numbers and headers
            - 🖨️ Print-optimized formatting
            """)

    # Divider
    st.divider()

    # Recent exports section
    st.subheader("📚 Recent PDF Exports")

    recent_pdfs = get_recent_pdf_exports()

    if not recent_pdfs:
        st.info("📄 **No PDFs yet.** Upload a markdown file above to create your first professional report.")
    else:
        for pdf in recent_pdfs:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.markdown(f"**{pdf['filename']}**")

            with col2:
                size_mb = pdf['size'] / (1024 * 1024)
                st.markdown(f"📊 {size_mb:.2f} MB")

            with col3:
                time_str = pdf['modified'].strftime("%Y-%m-%d %H:%M")
                st.markdown(f"🕐 {time_str}")

            with col4:
                # Download button for existing PDFs
                pdf_path = Path(pdf['path'])
                if pdf_path.exists():
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="⬇️",
                            data=f,
                            file_name=pdf['filename'],
                            mime="application/pdf",
                            key=f"download_{pdf['filename']}",
                        )


def render_process_tab():
    """Render the video processing tab."""

    # Tab header
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #1E88E5; margin-bottom: 0.5rem;">⚡ Extract Insights from Any Video</h2>
        <p style="color: #666; font-size: 1.1rem;">
            Paste a YouTube URL below and get comprehensive insights in minutes. Perfect for:
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("📚 **Learning**<br/>Educational content", unsafe_allow_html=True)
    with col2:
        st.markdown("💼 **Business**<br/>Strategies & frameworks", unsafe_allow_html=True)
    with col3:
        st.markdown("🎯 **Research**<br/>Key methodologies", unsafe_allow_html=True)
    with col4:
        st.markdown("🧠 **Knowledge**<br/>Save hours of watching", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Main processing form
    with st.form("process_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            url = st.text_input(
                "YouTube Video URL",
                placeholder="Paste your YouTube video URL here...",
                help="Works with any YouTube video that has captions available"
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

        submitted = st.form_submit_button("⚡ Extract Insights", use_container_width=True, type="primary")

    if submitted:
        if not url:
            st.error("Please enter a YouTube URL")
        else:
            # Create a container for dynamic updates
            status_container = st.container()

            with status_container:
                st.info("🚀 **Starting extraction...** This will take 2-5 minutes depending on video length")

                # Process video with real-time updates
                success, output = process_video(url, category)

                if success:
                    st.success("🎉 **Insights Extracted Successfully!**")

                    # Extract file path from output
                    import re
                    saved_to_match = re.search(r'✅ Saved to: (.+)', output)
                    if saved_to_match:
                        file_path = saved_to_match.group(1)
                        st.info(f"📄 **Your report is ready:** `{file_path}`")

                        # Add a button to refresh the recent videos list
                        if st.button("🔄 Refresh Recent Videos"):
                            st.rerun()
                    elif category:
                        st.info(f"📁 **Saved to:** `./outputs/{category}/`")
                    else:
                        st.info(f"📁 **Saved to:** `./outputs/`")

                    # Show enhanced success info
                    with st.expander("✨ What We Extracted", expanded=True):
                        st.markdown("""
                        **Your comprehensive analysis includes:**

                        - 📋 **Executive Summary** - Key takeaways in 2-3 paragraphs
                        - 💡 **Detailed Insights** - Comprehensive analysis with context
                        - 🎯 **Actionable Frameworks** - Step-by-step implementation guides
                        - ⏱️ **Key Timestamps** - Quick navigation to important moments
                        - 📊 **Structured Format** - Clean, scannable markdown document

                        All ready to read, share, or export to PDF!
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
        st.info("👋 **Ready to extract your first insight?** Paste a YouTube URL above to get started.")
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

    # Tips section
    st.markdown("---")
    with st.expander("💡 Pro Tips & Processing Info", expanded=False):
        st.markdown("""
        ### 📁 Organization Tips
        - Use clear category names like `AI/Agents`, `Business/Marketing`, or `Learning/Productivity`
        - Forward slashes create nested folders (e.g., `AI/Agents` → `outputs/AI/Agents/`)
        - Files are automatically named based on video title and upload date

        ### ⏱️ Processing Times
        Processing time depends on video length and GPT-5 availability:
        - **Short videos** (< 5 min): ~30-60 seconds
        - **Medium videos** (5-20 min): ~2-3 minutes
        - **Long videos** (20-45 min): ~3-5 minutes
        - **Very long videos** (45+ min): ~5-10 minutes

        ### 🎯 Best Practices
        - Videos with accurate captions work best
        - Longer videos provide more comprehensive insights
        - Use batch processing for multiple videos from same topic
        - Export to PDF for easy sharing and archiving

        ### 💰 Model Info
        **GPT-5** provides publication-grade analysis with deep contextual understanding.
        Higher quality than GPT-4o-mini but takes longer and costs more per request.
        """)


if __name__ == "__main__":
    main()
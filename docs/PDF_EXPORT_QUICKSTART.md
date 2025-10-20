# PDF Export - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install PDF dependencies (if not already installed)
pip install weasyprint markdown2
```

### 2. Start Web UI
```bash
streamlit run web_ui.py
```

### 3. Navigate to PDF Export
- Click the **"📄 PDF Export"** tab in the web interface

## 📤 Export Your First PDF

### Step-by-Step

1. **Upload File**
   - Drag and drop any `.md` file from your `outputs/` folder
   - Or click "Browse files" to select

2. **Preview Content** (Optional)
   - Click "👁️ Preview Markdown Content" to review before export

3. **Configure Options**
   - **Include Metadata Section**: ✅ (recommended)
   - **Page Size**: Letter (or A4 for international)
   - **Font Size**: 11pt (default, range: 9-14)

4. **Generate**
   - Click **"🚀 Generate PDF"**
   - Wait 1-3 seconds for generation

5. **Download**
   - Click **"⬇️ Download PDF"** button
   - PDF saved to `outputs/pdf_exports/`

## 🎯 Example Workflow

```bash
# 1. Process a video
streamlit run web_ui.py
# → Process Videos tab → Enter YouTube URL → Process

# 2. Export to PDF
# → PDF Export tab → Upload generated .md file → Generate PDF

# 3. Find your PDF
ls outputs/pdf_exports/
```

## 💡 Tips

### Best Practices
- ✅ Keep metadata enabled for context
- ✅ Use Letter size for US audiences, A4 for international
- ✅ Default font size (11pt) works well for most cases
- ✅ Preview large files before exporting

### Common Use Cases
- **Share with clients**: Professional PDFs for presentations
- **Archive content**: Print-friendly format for storage
- **Offline reading**: PDFs work without internet
- **Email attachments**: Easier to share than markdown

### Keyboard Shortcuts
While no direct shortcuts exist, you can:
- Use **Tab** to navigate between fields
- **Enter** to submit forms (after typing)
- **Drag files** directly from Finder/Explorer

## 🔍 What Gets Exported?

Your PDF will include:

### Metadata Section (if enabled)
```
Video Title (Large heading)
Channel: Channel Name | Published: YYYY-MM-DD | URL: youtube.com/...
Category: Your/Category
Tags: tag1, tag2, tag3...
```

### Content
- Executive Summary
- Key Insights
- Frameworks & Methods
- Key Timestamps
- All other markdown sections

### Formatting
- ✅ Headings (styled hierarchy)
- ✅ Code blocks (with background)
- ✅ Lists and tables
- ✅ Links (clickable)
- ✅ Page numbers
- ✅ Professional typography

## 🎨 Customization

### Page Size Options
- **Letter**: 8.5" × 11" (standard US)
- **A4**: 210mm × 297mm (international)

### Font Size Range
- **9pt**: Compact, more content per page
- **11pt**: Default, balanced readability
- **14pt**: Large, accessibility-friendly

### Metadata Toggle
- **Enabled**: Includes video info header
- **Disabled**: Content only (cleaner for reports)

## 📊 Recent Exports

The UI shows your last 10 PDF exports with:
- **Filename**: Original markdown name + .pdf
- **File Size**: In MB
- **Generated**: Timestamp of creation
- **Download**: Re-download anytime

## ❓ Troubleshooting

### PDF Not Generating?
1. Check file is valid markdown
2. Ensure dependencies installed: `pip list | grep weasyprint`
3. Review error message in UI
4. Try test script: `python test_pdf_generation.py`

### Markdown Not Rendering Correctly?
- Verify YAML frontmatter is valid (check `---` delimiters)
- Ensure special characters are escaped
- Preview in UI before generating

### Large File Slow to Generate?
- Normal for 20+ page documents (5-10 seconds)
- Consider reducing font size to fit more content
- Split very long files if needed

### Can't Find Generated PDF?
- Check `outputs/pdf_exports/` directory
- Look in "Recent PDF Exports" section of UI
- Filename matches your markdown file (with .pdf extension)

## 🆘 Need Help?

1. **Documentation**: See `docs/PDF_EXPORT.md` for full guide
2. **Test Script**: Run `python test_pdf_generation.py`
3. **Examples**: Check existing PDFs in `outputs/pdf_exports/`
4. **GitHub Issues**: Report bugs or request features

## ⚡ Pro Tips

### Batch Processing
While UI is single-file, you can use Python:
```python
from pathlib import Path
from yt_extractor.utils.pdf_generator import PDFGenerator

generator = PDFGenerator()
for md_file in Path("outputs/category").glob("*.md"):
    pdf_file = Path("outputs/pdf_exports") / f"{md_file.stem}.pdf"
    generator.generate_pdf(md_file, pdf_file)
```

### Custom Styling
Edit `yt_extractor/utils/pdf_generator.py` → `_get_css()` method to customize:
- Colors
- Fonts
- Spacing
- Headers/footers

### Automation
Integrate into your workflow:
```bash
# Process video AND export to PDF
python -m yt_extractor.cli process "$VIDEO_URL" --category "AI/Agents"
python your_auto_export_script.py
```

## 🎓 Learn More

- Full documentation: `docs/PDF_EXPORT.md`
- Architecture notes: `CLAUDE.md` → PDF Export Feature section
- Implementation summary: `PDF_EXPORT_SUMMARY.md`

---

**Ready to export?** Start the web UI and try it out!

```bash
source venv/bin/activate && streamlit run web_ui.py
```

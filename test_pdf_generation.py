#!/usr/bin/env python
"""Test script for PDF generation functionality."""

from pathlib import Path
from yt_extractor.utils.pdf_generator import PDFGenerator


def test_pdf_generation():
    """Test PDF generation with a sample markdown file."""
    # Use an existing markdown file
    sample_md = Path("outputs/content-creation/20250912--nJhTQpiuNow--copy-this-content-strategy-itll-blow-up-your-business.md")

    if not sample_md.exists():
        print(f"❌ Sample file not found: {sample_md}")
        return False

    # Output directory
    output_dir = Path("outputs/pdf_exports")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate PDF
    output_pdf = output_dir / "test_export.pdf"

    print(f"📄 Generating PDF from: {sample_md}")
    print(f"📁 Output path: {output_pdf}")

    try:
        generator = PDFGenerator()
        result_path = generator.generate_pdf(
            markdown_path=sample_md,
            output_path=output_pdf,
            include_metadata=True,
            page_size="letter",
            font_size=11,
        )

        if result_path.exists():
            size_mb = result_path.stat().st_size / (1024 * 1024)
            print(f"✅ PDF generated successfully!")
            print(f"📊 File size: {size_mb:.2f} MB")
            print(f"📂 Location: {result_path}")
            return True
        else:
            print("❌ PDF file was not created")
            return False

    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_generation()
    exit(0 if success else 1)

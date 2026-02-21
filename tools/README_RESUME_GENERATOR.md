# Resume/Portfolio PDF Generator

This tool generates a professional PDF resume showcasing the RL Environment Framework project achievements.

## Overview

The `generate_resume_pdf.py` script creates a polished, multi-page PDF document that highlights:
- Project summary and description
- Key achievements and metrics
- Technical skills demonstrated
- Project deliverables
- Implementation highlights
- Repository information

## Installation

The PDF generator requires `reportlab` which is included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or install just reportlab:

```bash
pip install reportlab>=4.0.0
```

## Usage

### Basic Usage

Generate the resume PDF with default settings:

```bash
python tools/generate_resume_pdf.py
```

This will create `RL_Framework_Portfolio_Resume.pdf` in the repository root directory.

### Output

The script generates:
- **File**: `RL_Framework_Portfolio_Resume.pdf`
- **Size**: ~5-6 KB
- **Format**: US Letter (8.5" x 11")
- **Style**: Professional with consistent formatting

### What's Included in the PDF

The generated resume includes:

1. **Header Section**
   - Name/Title: "RL Engineer - Reinforcement Learning Framework Developer"
   - Professional formatting

2. **Featured Project**
   - Project title: RL Environment Framework - Gymnasium Migration
   - Comprehensive description of the migration work

3. **Key Achievements**
   - 100% Migration Success (13 Python files)
   - 40/40 tests passing (100% pass rate)
   - 0 security vulnerabilities
   - 4,500+ lines of production code
   - 2,100+ lines of documentation
   - Modern API implementation
   - Q-Learning agent implementation

4. **Technical Skills Demonstrated**
   - Languages & Frameworks (Python, Gymnasium, NumPy, PyTorch)
   - Testing & QA (Pytest, Coverage, API Compliance)
   - Development Tools (Git, YAML, Type Hints)
   - RL Concepts (Q-Learning, Reward Shaping, Environment Design)
   - Documentation expertise
   - Software Engineering best practices

5. **Project Deliverables**
   - Core implementation details
   - Example environments and agents
   - Testing infrastructure
   - Development tools
   - Configuration system
   - Documentation suite
   - Quality metrics

6. **Technical Implementation Highlights**
   - Action space validation
   - Dense reward shaping
   - Proper seeding for reproducibility
   - Optional dependencies
   - Gymnasium env_checker integration
   - Nested YAML configuration
   - Reward scaling and clipping

7. **Repository & Resources**
   - GitHub repository link
   - Branch information
   - File statistics
   - Code quality standards
   - License information

## Customization

To customize the resume, edit the `generate_resume_pdf.py` script:

### Change Header Information

```python
# In main() or when calling add_header()
generator.add_header(
    name="Your Name",
    title="Your Professional Title"
)
```

### Modify Output Path

```python
# In main()
output_path = "/custom/path/to/resume.pdf"
generator = ResumeGenerator(output_path)
```

### Adjust Styling

Modify the `_setup_custom_styles()` method to change:
- Font sizes
- Colors (using HexColor)
- Spacing
- Alignment
- Indentation

### Add/Remove Sections

Comment out or add method calls in the `generate()` method:

```python
def generate(self):
    self.add_header()
    self.add_project_summary()
    # self.add_key_achievements()  # Comment to remove
    # self.add_custom_section()     # Add your own
    self.add_footer()
    self.doc.build(self.story)
```

## Technical Details

### Dependencies

- **reportlab**: PDF generation library (>=4.0.0)
- **datetime**: For timestamp generation (standard library)
- **os**: For file path operations (standard library)

### PDF Structure

The generator uses ReportLab's Platypus (Page Layout and Typography Using Scripts):
- `SimpleDocTemplate`: Main document container
- `Paragraph`: Text blocks with styling
- `Table`: Tabular data (e.g., technical skills)
- `Spacer`: Vertical spacing
- `TableStyle`: Table formatting

### Styling

Custom paragraph styles:
- `CustomTitle`: Large, bold, centered title (24pt)
- `SectionHeading`: Section headers with color (14pt, blue)
- `ProjectTitle`: Project names (12pt, bold)
- `CustomBody`: Body text (10pt, justified)
- `CustomBullet`: Bullet points (10pt, indented)

### Page Layout

- **Page Size**: US Letter (8.5" × 11")
- **Margins**: 0.75 inches on all sides
- **Content Width**: 6.5 inches
- **Font**: Helvetica (standard PDF font)

## Example Output

The generated PDF includes approximately:
- **1-2 pages** of content
- **~50 bullet points** across all sections
- **Professional formatting** with consistent spacing
- **Color accents** for section headings (blue)
- **Table layout** for technical skills

## Troubleshooting

### "No module named 'reportlab'"

**Solution**: Install reportlab:
```bash
pip install reportlab>=4.0.0
```

### "Permission denied" when writing PDF

**Solution**: Ensure you have write permissions in the output directory:
```bash
chmod +w /path/to/output/directory
```

### PDF appears blank or corrupted

**Solution**: Check that all paragraph content is properly formatted and no None values are passed to Paragraph constructors.

### Style already exists error

**Solution**: Ensure custom style names don't conflict with built-in ReportLab styles. Use unique prefixes like `Custom*`.

## Integration with Project

This resume generator is designed to showcase the RL Environment Framework project. It automatically extracts information from:
- Project documentation
- Test results
- Code metrics
- Quality assurance data

The content is optimized for:
- Technical interviews
- Portfolio presentations
- Project demonstrations
- Academic submissions
- Professional networking

## Future Enhancements

Potential improvements:
1. **Command-line arguments** for customization
2. **Multiple templates** (academic, industry, minimalist)
3. **Dynamic content extraction** from codebase
4. **Charts and graphs** for metrics visualization
5. **Multi-page layouts** for longer resumes
6. **Export to other formats** (HTML, Markdown)

## License

This tool is part of the RL Environment Framework project and follows the same MIT License.

---

**Generated by**: RL Environment Framework Team
**Last Updated**: February 2026
**Version**: 1.0.0

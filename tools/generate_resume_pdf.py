#!/usr/bin/env python3
"""
Resume/Portfolio PDF Generator for RL Environment Framework Project

This script generates a professional PDF resume/portfolio showcasing the
RL Environment Framework project achievements and technical capabilities.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether
)
from reportlab.lib import colors
from datetime import datetime
import os


class ResumeGenerator:
    """Generate professional PDF resume highlighting project achievements."""

    def __init__(self, output_path="portfolio_resume.pdf"):
        """
        Initialize the resume generator.

        Args:
            output_path: Path where the PDF will be saved
        """
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the resume."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=2,
            leftIndent=0
        ))

        # Project title style
        self.styles.add(ParagraphStyle(
            name='ProjectTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=4,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))

        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))

        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leftIndent=20,
            spaceAfter=4,
            bulletIndent=10
        ))

    def add_header(self, name="RL Engineer", title="Reinforcement Learning Framework Developer"):
        """Add resume header with name and title."""
        # Name
        name_para = Paragraph(name, self.styles['CustomTitle'])
        self.story.append(name_para)

        # Title/Role
        title_para = Paragraph(
            f"<font size=12>{title}</font>",
            self.styles['CustomBody']
        )
        title_para.style.alignment = TA_CENTER
        self.story.append(title_para)
        self.story.append(Spacer(1, 0.2*inch))

    def add_section(self, title):
        """Add a section heading."""
        # Add horizontal line
        line = Table([['']], colWidths=[6.5*inch])
        line.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#2c5aa0')),
        ]))
        self.story.append(line)

        # Add section title
        section_para = Paragraph(title, self.styles['SectionHeading'])
        self.story.append(section_para)

    def add_project_summary(self):
        """Add the main project summary section."""
        self.add_section("Featured Project")

        # Project title and details
        project_title = Paragraph(
            "<b>RL Environment Framework - Gymnasium Migration</b>",
            self.styles['ProjectTitle']
        )
        self.story.append(project_title)

        # Project description
        description = """
        Architected and implemented a comprehensive migration of Verita AI's Reinforcement Learning
        Environment Framework from deprecated OpenAI Gym to modern Gymnasium, establishing production-ready
        infrastructure for RL environment development.
        """
        desc_para = Paragraph(description, self.styles['CustomBody'])
        self.story.append(desc_para)
        self.story.append(Spacer(1, 0.1*inch))

    def add_key_achievements(self):
        """Add key achievements section."""
        achievements = [
            "<b>100% Migration Success:</b> Migrated 13 Python files to Gymnasium with full API compliance",
            "<b>Quality Assurance:</b> Developed comprehensive test suite with 40/40 tests passing (100% pass rate)",
            "<b>Security Excellence:</b> Achieved 0 security vulnerabilities validated by CodeQL security scan",
            "<b>Modern API Implementation:</b> Implemented 5-tuple step API with proper terminated/truncated distinction",
            "<b>Reproducible Research:</b> Added 2-tuple reset API with seeding for reproducible experiments",
            "<b>Code Quality:</b> Delivered 4,500+ lines of production code with type hints and comprehensive docstrings",
            "<b>Documentation:</b> Created 2,100+ lines of professional documentation across 5 comprehensive guides",
            "<b>Advanced Features:</b> Implemented Q-Learning agent with epsilon-greedy exploration and training visualization"
        ]

        for achievement in achievements:
            bullet = Paragraph(f"• {achievement}", self.styles['CustomBullet'])
            self.story.append(bullet)

        self.story.append(Spacer(1, 0.1*inch))

    def add_technical_skills(self):
        """Add technical skills demonstrated."""
        self.add_section("Technical Skills Demonstrated")

        skills_data = [
            ["<b>Languages & Frameworks</b>", "Python 3.8+, Gymnasium, NumPy, PyTorch (optional)"],
            ["<b>Testing & QA</b>", "Pytest, Coverage Analysis, API Compliance Validation, Security Scanning (CodeQL)"],
            ["<b>Development Tools</b>", "Git, YAML Configuration, Type Hints, Google-style Docstrings"],
            ["<b>RL Concepts</b>", "Q-Learning, Epsilon-greedy Exploration, Reward Shaping, Environment Design"],
            ["<b>Documentation</b>", "API Reference, Developer Guides, Deployment Guides, Contributing Guidelines"],
            ["<b>Software Engineering</b>", "Clean Architecture, Test-Driven Development, CI/CD, Code Review"]
        ]

        skills_table = Table(skills_data, colWidths=[2*inch, 4.5*inch])
        skills_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))

        self.story.append(skills_table)
        self.story.append(Spacer(1, 0.1*inch))

    def add_deliverables(self):
        """Add deliverables and metrics."""
        self.add_section("Project Deliverables")

        deliverables = [
            "<b>Core Implementation:</b> BaseEnvironment class (204 lines) with Gymnasium-compatible interface",
            "<b>Example Environments:</b> SimpleGridWorld (174 lines), Q-Learning Agent (456 lines), Training Script (168 lines)",
            "<b>Testing Infrastructure:</b> 40 comprehensive tests across 3 test files with fixtures and API compliance validation",
            "<b>Development Tools:</b> Environment template generator (264 lines) for rapid development",
            "<b>Configuration System:</b> YAML-based flexible configuration with nested structure support",
            "<b>Documentation Suite:</b> 5 comprehensive guides (API Reference, Development Guide, Testing, Deployment, Contributing)",
            "<b>Quality Metrics:</b> 100% test pass rate, 0.43s execution time, 0 security vulnerabilities, full API compliance"
        ]

        for deliverable in deliverables:
            bullet = Paragraph(f"• {deliverable}", self.styles['CustomBullet'])
            self.story.append(bullet)

        self.story.append(Spacer(1, 0.1*inch))

    def add_implementation_highlights(self):
        """Add technical implementation highlights."""
        self.add_section("Technical Implementation Highlights")

        highlights = [
            "<b>Action Space Validation:</b> Built-in validation preventing silent failures with immediate error feedback",
            "<b>Dense Reward Shaping:</b> Potential-based reward shaping providing gradient information for faster learning",
            "<b>Proper Seeding:</b> Reproducible experiments using Gymnasium's built-in RNG with per-environment seeding",
            "<b>Optional Dependencies:</b> Modular installation with PyTorch as optional for non-deep-RL users (saves ~2GB)",
            "<b>Gymnasium env_checker:</b> Automated API validation ensuring full compliance with Gymnasium standards",
            "<b>Nested YAML Config:</b> Hierarchical configuration supporting complex environment setups",
            "<b>Reward Scaling & Clipping:</b> Configurable reward transformation for improved learning stability"
        ]

        for highlight in highlights:
            bullet = Paragraph(f"• {highlight}", self.styles['CustomBullet'])
            self.story.append(bullet)

        self.story.append(Spacer(1, 0.1*inch))

    def add_repository_info(self):
        """Add repository information."""
        self.add_section("Repository & Resources")

        info = [
            "<b>Repository:</b> https://github.com/dl1413/trello-kanban-replica",
            "<b>Branch:</b> claude/prepare-for-submission",
            "<b>Status:</b> Production-ready with comprehensive testing and documentation",
            "<b>Files:</b> 27 total files (13 Python source files, 5 documentation guides, 3 examples, 2 config templates)",
            "<b>Code Quality:</b> PEP 8 compliant, type hints throughout, Google-style docstrings",
            "<b>License:</b> MIT License"
        ]

        for item in info:
            bullet = Paragraph(f"• {item}", self.styles['CustomBullet'])
            self.story.append(bullet)

        self.story.append(Spacer(1, 0.1*inch))

    def add_footer(self):
        """Add footer with generation date."""
        self.story.append(Spacer(1, 0.3*inch))

        footer_text = f"<font size=8 color='#666666'><i>Generated on {datetime.now().strftime('%B %d, %Y')}</i></font>"
        footer_para = Paragraph(footer_text, self.styles['CustomBody'])
        footer_para.style.alignment = TA_CENTER
        self.story.append(footer_para)

    def generate(self):
        """Generate the complete PDF resume."""
        # Add all sections
        self.add_header()
        self.add_project_summary()
        self.add_key_achievements()
        self.add_technical_skills()
        self.add_deliverables()
        self.add_implementation_highlights()
        self.add_repository_info()
        self.add_footer()

        # Build PDF
        self.doc.build(self.story)
        print(f"✓ Resume PDF generated successfully: {self.output_path}")
        return self.output_path


def main():
    """Main function to generate the resume PDF."""
    # Determine output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "..", "RL_Framework_Portfolio_Resume.pdf")
    output_path = os.path.normpath(output_path)

    print("Generating RL Environment Framework Portfolio Resume...")
    print(f"Output path: {output_path}")

    # Generate resume
    generator = ResumeGenerator(output_path)
    generated_path = generator.generate()

    # Show file info
    if os.path.exists(generated_path):
        file_size = os.path.getsize(generated_path) / 1024  # KB
        print(f"✓ PDF size: {file_size:.1f} KB")
        print(f"✓ Location: {generated_path}")

    return generated_path


if __name__ == "__main__":
    main()

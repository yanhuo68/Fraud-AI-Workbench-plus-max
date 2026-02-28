import os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

def generate_docx():
    doc = Document()
    
    # 1. Cover Page
    title = doc.add_heading('Instruction to Fraud Detection AI Workbench', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph('\n' * 10)
    
    date_str = datetime.now().strftime('%B %d, %Y')
    date_para = doc.add_paragraph(date_str)
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()
    
    # 2. TOC (Placeholder - python-docx doesn't auto-generate, but we'll list chapters)
    doc.add_heading('Table of Contents', level=1)
    toc_para = doc.add_paragraph("Table of Contents is generated manually for this document.")
    doc.add_page_break()
    
    # helper to read md
    def read_md(path):
        if not path.exists():
            return "Documentation under development."
        return path.read_text(encoding='utf-8')

    # Chapter 1: Introduction
    doc.add_heading('Chapter 1: Introduction', level=1)
    doc.add_paragraph("Fraud Detection AI Workbench is a sophisticated Streamlit + LangGraph + RAG workspace designed for comprehensive fraud analytics and investigation.")
    doc.add_paragraph("This project integrates high-performance LLM agents with traditional machine learning and graph-based reasoning to provide forensic accountants and data scientists with a command-center for fraud detection.")

    # Chapter 2: Getting Started
    doc.add_heading('Chapter 2: Getting Started', level=1)
    doc.add_paragraph("To get started, users can deploy the environment using Docker Compose. Ensure your OpenAI API keys are configured in the sidebar or via environment variables.")
    doc.add_paragraph("The application operates through a tabbed interface, starting with 'Upload Data' to ingest datasets and set up the investigation context.")

    # Chapter 3: Sidebar & Global Config
    doc.add_heading('Chapter 3: Sidebar & Global Configuration', level=1)
    sidebar_design = read_md(Path("documentation/ui_design/sidebar.md"))
    doc.add_paragraph(sidebar_design)
    doc.add_page_break()

    # Tab Pages Mapping
    tabs = [
        ("Upload Data", "upload_data", "01"),
        ("ML Dashboard", "ml_dashboard", "02"),
        ("SQL RAG", "sql_rag", "03"),
        ("KB RAG", "kb_rag", "04"),
        ("Graph RAG", "graph_rag", "05"),
        ("RAG Comparison", "rag_comparison", "06"),
        ("Model Comparison", "model_comparison", "07"),
        ("Guideline Comparison", "guideline_comparison", "08"),
        ("ERD Diagram", "erd_diagram", "09"),
        ("Agent Workflow", "agent_workflow", "10"),
    ]

    for i, (name, folder, num) in enumerate(tabs):
        chapter_num = i + 4
        doc.add_heading(f'Chapter {chapter_num}: {name}', level=1)
        
        # x.1 Introduction
        doc.add_heading(f'{chapter_num}.1 Introduction', level=2)
        design_content = read_md(Path(f"documentation/ui_design/{num}_{folder}.md"))
        doc.add_paragraph(design_content.split('##')[0] if '##' in design_content else design_content)
        
        # x.2 UI Design
        doc.add_heading(f'{chapter_num}.2 UI Design', level=2)
        doc.add_paragraph(design_content)
        
        # x.3 User Manual
        doc.add_heading(f'{chapter_num}.3 User Manual', level=2)
        manual_content = read_md(Path(f"documentation/ui_user_manual/{num}_{folder}_manual.md"))
        doc.add_paragraph(manual_content)
        
        # x.4 Demo
        doc.add_heading(f'{chapter_num}.4 Demo', level=2)
        screen_dir = Path(f"documentation/screen/{folder}")
        if screen_dir.exists():
            images = sorted(list(screen_dir.glob("*.jpg")) + list(screen_dir.glob("*.png")))
            if images:
                for img_path in images:
                    doc.add_paragraph(f"Figure: {img_path.name}")
                    try:
                        doc.add_picture(str(img_path), width=Inches(6))
                    except Exception:
                        doc.add_paragraph("[Image could not be inserted]")
            else:
                doc.add_paragraph("No demo images available for this tab.")
        else:
            doc.add_paragraph("No demo screenshots directory found.")
            
        doc.add_page_break()

    # Last Chapter: Help and Guidelines
    last_chap_num = len(tabs) + 4
    doc.add_heading(f'Chapter {last_chap_num}: Feedback & Assistance', level=1)
    doc.add_paragraph("Help and forensic guidelines can be accessed directly from the Sidebar. The 'Help & Documentation' expander provides a library of user manuals and technical design documents, while the 'Fraud Guidelines' section allows searching and viewing specific risk policies and detection rulebooks.")
    
    # Save
    out_path = "Instruction_to_Fraud_Detection_AI_Workbench.docx"
    doc.save(out_path)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_docx()

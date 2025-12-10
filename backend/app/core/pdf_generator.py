"""
PDF generation for reports with Arabic support
"""
import tempfile
import os
from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display

# Default font path
FONT_PATH = os.path.join(os.path.dirname(__file__), '../assets/fonts/NotoSansArabic-Regular.ttf')

# Register Arabic font
try:
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont('NotoSansArabic', FONT_PATH))
        FONT_NAME = 'NotoSansArabic'
    else:
        # Fallback to standard if not found (will break arabic)
        FONT_NAME = 'Helvetica'
        print(f"Warning: Arabic font not found at {FONT_PATH}")
except Exception as e:
    FONT_NAME = 'Helvetica'
    print(f"Error registering font: {e}")

def reshape_arabic(text):
    """Reshape Arabic text for proper display"""
    if not text:
        return ""
    try:
        if not isinstance(text, str):
            text = str(text)
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    except Exception:
        return str(text)

def create_champions_pdf(class_name: str, section_name: str, champions_list: List[Dict]) -> str:
    """
    Create a PDF file for champions of a specific class and section
    """
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            temp_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#0d6efd',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=FONT_NAME
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor='#495057',
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName=FONT_NAME
        )
        
        # Champion name style
        champion_style = ParagraphStyle(
            'ChampionStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor='#212529',
            spaceAfter=15,
            alignment=TA_RIGHT,
            fontName=FONT_NAME
        )
        
        # Add title
        title = Paragraph(reshape_arabic("🏆 أبطال الأسبوع"), title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Add class and section
        class_str = reshape_arabic(f"الصف: {class_name}")
        section_str = reshape_arabic(f"الشعبة: {section_name}")
        subtitle = Paragraph(f"{class_str} - {section_str}", subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 1*cm))
        
        # Add champions list
        if champions_list:
            for i, champion in enumerate(champions_list, 1):
                raw_name = champion.get('name') or champion.get('full_name') or champion.get('username', 'Unknown')
                champion_name = reshape_arabic(raw_name)
                champion_text = f"{i}. {champion_name}"
                champion_para = Paragraph(champion_text, champion_style)
                elements.append(champion_para)
        else:
            no_champions = Paragraph(reshape_arabic("لا يوجد أبطال هذا الأسبوع"), champion_style)
            elements.append(no_champions)
        
        # Build PDF
        doc.build(elements)
        
        return temp_path
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None


def create_student_report_pdf(student_data: Dict) -> str:
    """
    Create a PDF report for a student
    """
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            temp_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor='#0d6efd',
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName=FONT_NAME
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor='#212529',
            spaceAfter=10,
            alignment=TA_RIGHT,
            fontName=FONT_NAME
        )
        
        # Add title
        raw_name = student_data.get('full_name', student_data.get('username', 'Unknown'))
        title_text = reshape_arabic(f"تقرير الطالب: {raw_name}")
        title = Paragraph(title_text, title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Add student info
        c_name = student_data.get('class_name', 'N/A')
        s_name = student_data.get('section_name', 'N/A')
        info_text = reshape_arabic(f"الصف: {c_name} - الشعبة: {s_name}")
        elements.append(Paragraph(info_text, normal_style))
        elements.append(Spacer(1, 0.3*cm))
        
        # Add videos count
        videos_manhaji = student_data.get('videos_manhaji', [])
        videos_ithrai = student_data.get('videos_ithrai', [])
        
        v_text_raw = f"عدد الفيديوهات المنهجية: {len(videos_manhaji)} | عدد الفيديوهات الإثرائية: {len(videos_ithrai)}"
        videos_text = reshape_arabic(v_text_raw)
        
        elements.append(Paragraph(videos_text, normal_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Build PDF
        doc.build(elements)
        
        return temp_path
    except Exception as e:
        print(f"Error creating student report PDF: {e}")
        return None


def create_champions_pdf(class_name: str, section_name: str, champions_list: List[Dict]) -> str:
    """
    Create a PDF file for champions of a specific class and section
    
    Args:
        class_name: Class name
        section_name: Section name
        champions_list: List of champion dictionaries with 'name' key
    
    Returns:
        Path to created PDF file, or None if error
    """
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            temp_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#0d6efd',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor='#495057',
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Champion name style
        champion_style = ParagraphStyle(
            'ChampionStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor='#212529',
            spaceAfter=15,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        )
        
        # Add title
        title = Paragraph("🏆 أبطال الأسبوع", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Add class and section
        class_section_text = f"الصف: {class_name} - الشعبة: {section_name}"
        subtitle = Paragraph(class_section_text, subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 1*cm))
        
        # Add champions list
        if champions_list:
            for i, champion in enumerate(champions_list, 1):
                champion_name = champion.get('name') or champion.get('full_name') or champion.get('username', 'Unknown')
                champion_text = f"{i}. {champion_name}"
                champion_para = Paragraph(champion_text, champion_style)
                elements.append(champion_para)
        else:
            no_champions = Paragraph("لا يوجد أبطال هذا الأسبوع", champion_style)
            elements.append(no_champions)
        
        # Build PDF
        doc.build(elements)
        
        return temp_path
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None


def create_student_report_pdf(student_data: Dict) -> str:
    """
    Create a PDF report for a student
    
    Args:
        student_data: Dictionary containing student information and video data
    
    Returns:
        Path to created PDF file, or None if error
    """
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            temp_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor='#0d6efd',
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Normal style
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor='#212529',
            spaceAfter=10,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        )
        
        # Add title
        title = Paragraph(f"تقرير الطالب: {student_data.get('full_name', student_data.get('username', 'Unknown'))}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Add student info
        info_text = f"الصف: {student_data.get('class_name', 'N/A')} - الشعبة: {student_data.get('section_name', 'N/A')}"
        elements.append(Paragraph(info_text, normal_style))
        elements.append(Spacer(1, 0.3*cm))
        
        # Add videos count
        videos_manhaji = student_data.get('videos_manhaji', [])
        videos_ithrai = student_data.get('videos_ithrai', [])
        videos_text = f"عدد الفيديوهات المنهجية: {len(videos_manhaji)} | عدد الفيديوهات الإثرائية: {len(videos_ithrai)}"
        elements.append(Paragraph(videos_text, normal_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Build PDF
        doc.build(elements)
        
        return temp_path
    except Exception as e:
        print(f"Error creating student report PDF: {e}")
        return None


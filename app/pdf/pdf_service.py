from logger_config import logger
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime


class PDFService:
    def __init__(self) -> None:
        pass

    def generate_pdf(self, data: dict) -> str:
        if not data:
            logger.error("No data provided for PDF generation")
            return ""
        pdf_path = f"pdf/output/{datetime.now().strftime('%d-%m-%Y_%H.%M.%S')}.pdf"
        try:
            c = canvas.Canvas(pdf_path, pagesize=letter)
            text = c.beginText(50, 750)
            for key, value in data.items():
                text.textLine(f"{key}: {value}")
            c.drawText(text)
            c.save()
            return pdf_path
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            return ""


if __name__ == "__main__":
    #  For testing purposes
    pdf_service = PDFService()
    data = {"title": "Sample PDF", "description": "This is a sample PDF document."}
    pdf_path = pdf_service.generate_pdf(data)
    print(f"PDF generated and saved to: {pdf_path}")

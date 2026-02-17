"""
Create a sample PDF file for testing question extraction
Uses reportlab to create a PDF with sample questions
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def create_sample_pdf(output_path: str = "sample_questions.pdf"):
    """Create a sample PDF with questions in standard format"""
    
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 0.5 * inch
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.5 * inch, y, "Azure Fundamentals - Sample Questions")
    y -= 0.3 * inch
    
    # Questions
    questions = [
        {
            "question": "Q1) Which Azure service is used for unstructured data storage?",
            "options": [
                "A) Azure SQL Database",
                "B) Azure Blob Storage",
                "C) Azure Queue Storage",
                "D) Azure Table Storage"
            ]
        },
        {
            "question": "Q2) Select all that apply: Which of the following are Azure compute services?",
            "options": [
                "A) Virtual Machines",
                "B) App Service",
                "C) Azure Storage",
                "D) Azure Functions",
                "E) Azure Cosmos DB"
            ]
        },
        {
            "question": "Q3) What is the first step when creating a virtual machine in Azure Portal?",
            "options": [
                "A) Create a resource group",
                "B) Choose the VM size",
                "C) Configure networking",
                "D) Add storage"
            ]
        },
        {
            "question": "Q4) Match the Azure service to its use case:",
            "options": [
                "A) Unstructured data storage",
                "B) Relational database",
                "C) NoSQL data",
                "D) Web hosting"
            ]
        },
        {
            "question": "Q5) Fill in the blank: Azure _____ provides serverless computing.",
            "options": [
                "A) Virtual Machines",
                "B) Functions",
                "C) App Service",
                "D) Container Instances"
            ]
        },
        {
            "question": "Scenario: Your company needs a cost-effective solution for occasional batch processing without managing infrastructure.\nStatement 1: Azure Functions is suitable for this scenario.",
            "options": [
                "Yes",
                "No"
            ]
        }
    ]
    
    c.setFont("Helvetica", 10)
    
    for q_data in questions:
        # Question text
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0.5 * inch, y, q_data["question"])
        y -= 0.2 * inch
        
        # Options
        c.setFont("Helvetica", 9)
        for option in q_data["options"]:
            c.drawString(0.75 * inch, y, option)
            y -= 0.15 * inch
        
        # Add spacing
        y -= 0.15 * inch
        
        # New page if needed
        if y < 1 * inch:
            c.showPage()
            y = height - 0.5 * inch
    
    c.save()
    print(f"✅ Sample PDF created: {output_path}")
    return output_path


if __name__ == "__main__":
    pdf_path = create_sample_pdf()
    print(f"📄 PDF path: {pdf_path}")
    print(f"📊 Contains 6 sample questions for testing")

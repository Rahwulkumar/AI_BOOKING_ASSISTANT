"""
Simple script to create sample PDFs using fpdf (lighter alternative)
If fpdf is not available, creates text files that can be converted to PDF
"""
import os

def create_text_file(filename, title, content_lines):
    """Create a text file with content (can be converted to PDF manually)"""
    os.makedirs("docs", exist_ok=True)
    filepath = f"docs/{filename}"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        for line in content_lines:
            f.write(line + "\n")
    
    print(f"Created: {filepath}")
    return filepath

# Doctors list content
doctors_content = [
    "DOCTORS LIST & SPECIALTIES",
    "",
    "Dr. Sarah Johnson - Cardiology",
    "Experience: 15 years",
    "Consultation Fee: $150",
    "Availability: Monday-Friday, 9:00 AM - 5:00 PM",
    "Languages: English, Spanish",
    "",
    "Dr. Michael Chen - Dermatology",
    "Experience: 12 years",
    "Consultation Fee: $120",
    "Availability: Tuesday-Saturday, 10:00 AM - 6:00 PM",
    "Languages: English, Mandarin",
    "",
    "Dr. Emily Rodriguez - Pediatrics",
    "Experience: 10 years",
    "Consultation Fee: $100",
    "Availability: Monday-Friday, 8:00 AM - 4:00 PM",
    "Languages: English, Spanish",
    "",
    "Dr. James Wilson - Orthopedics",
    "Experience: 18 years",
    "Consultation Fee: $180",
    "Availability: Monday-Thursday, 9:00 AM - 5:00 PM",
    "Languages: English",
    "",
    "Dr. Lisa Anderson - General Practice",
    "Experience: 8 years",
    "Consultation Fee: $90",
    "Availability: Monday-Friday, 8:00 AM - 6:00 PM",
    "Languages: English, French",
    "",
    "Dr. Robert Kim - Neurology",
    "Experience: 14 years",
    "Consultation Fee: $200",
    "Availability: Tuesday-Friday, 10:00 AM - 4:00 PM",
    "Languages: English, Korean",
    "",
    "Dr. Maria Garcia - Gynecology",
    "Experience: 11 years",
    "Consultation Fee: $130",
    "Availability: Monday-Wednesday, Friday, 9:00 AM - 5:00 PM",
    "Languages: English, Spanish"
]

# Clinic policies content
policies_content = [
    "CLINIC POLICIES & GUIDELINES",
    "",
    "OPERATING HOURS:",
    "Monday to Friday: 8:00 AM - 6:00 PM",
    "Saturday: 9:00 AM - 4:00 PM",
    "Sunday: Closed",
    "",
    "APPOINTMENT BOOKING POLICY:",
    "- Appointments can be booked up to 30 days in advance",
    "- Same-day appointments available based on doctor availability",
    "- Minimum 24 hours advance booking recommended",
    "- Walk-in patients accepted subject to availability",
    "",
    "CANCELLATION POLICY:",
    "- Free cancellation up to 24 hours before appointment",
    "- 50% charge for same-day cancellation",
    "- No-show: Full consultation fee applies",
    "- Rescheduling allowed up to 48 hours before appointment",
    "",
    "LATE ARRIVAL POLICY:",
    "- 15-minute grace period for late arrivals",
    "- After 15 minutes, appointment may be rescheduled",
    "- Please arrive 10 minutes early for check-in",
    "",
    "PAYMENT METHODS:",
    "- Cash",
    "- Credit/Debit Cards (Visa, Mastercard, Amex)",
    "- Online payment via portal",
    "- Insurance accepted (see below)",
    "",
    "INSURANCE PROVIDERS:",
    "- Blue Cross Blue Shield",
    "- Aetna",
    "- Cigna",
    "- UnitedHealthcare",
    "- Medicare/Medicaid",
    "",
    "PATIENT RIGHTS & RESPONSIBILITIES:",
    "- Right to receive quality medical care",
    "- Right to privacy and confidentiality",
    "- Responsibility to provide accurate medical history",
    "- Responsibility to arrive on time for appointments",
    "- Responsibility to inform about cancellations in advance",
    "",
    "CONTACT INFORMATION:",
    "Phone: (555) 123-4567",
    "Email: info@clinic.com",
    "Address: 123 Medical Center Drive, City, State 12345",
    "Emergency: Call 911 for medical emergencies"
]

# Services pricing content
services_content = [
    "SERVICES & PRICING",
    "",
    "CONSULTATION FEES BY SPECIALTY:",
    "Cardiology: $150",
    "Dermatology: $120",
    "Pediatrics: $100",
    "Orthopedics: $180",
    "General Practice: $90",
    "Neurology: $200",
    "Gynecology: $130",
    "",
    "DIAGNOSTIC TESTS:",
    "Blood Test (Complete): $50",
    "Blood Test (Basic): $30",
    "X-Ray (Chest): $80",
    "X-Ray (Limb): $60",
    "ECG (Electrocardiogram): $75",
    "Ultrasound (Abdominal): $150",
    "Ultrasound (Pelvic): $140",
    "MRI Scan: $500",
    "CT Scan: $400",
    "",
    "VACCINATION PRICES:",
    "Flu Vaccine: $40",
    "COVID-19 Vaccine: $0 (covered by insurance)",
    "Hepatitis A: $60",
    "Hepatitis B: $65",
    "MMR (Measles, Mumps, Rubella): $85",
    "Tetanus: $45",
    "HPV Vaccine: $200 (3-dose series)",
    "",
    "HEALTH CHECKUP PACKAGES:",
    "Basic Health Checkup: $200",
    "Includes: Physical exam, basic blood test, ECG",
    "",
    "Comprehensive Health Checkup: $400",
    "Includes: Physical exam, complete blood test, ECG, X-Ray, consultation",
    "",
    "Executive Health Checkup: $600",
    "Includes: All comprehensive tests plus MRI, specialist consultation",
    "",
    "MINOR PROCEDURES:",
    "Sutures/Wound Care: $100",
    "Minor Surgery: $300-$500",
    "Biopsy: $200",
    "Cryotherapy: $150",
    "",
    "PAYMENT & DISCOUNTS:",
    "- Senior citizens (65+): 10% discount",
    "- Students: 15% discount (with valid ID)",
    "- Group bookings (5+ people): 10% discount",
    "- Insurance copays apply as per plan",
    "- Payment plans available for major procedures",
    "",
    "NOTE:",
    "Prices are subject to change. Please confirm current pricing when booking.",
    "Insurance coverage varies by plan. Contact your insurance provider for details."
]

if __name__ == "__main__":
    # Try to use fpdf2 if available, otherwise create text files
    try:
        from fpdf import FPDF  # fpdf2 package uses 'from fpdf import FPDF'
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, '', 0, 1, 'C')
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        def create_pdf_fpdf(filename, title, content_lines):
            pdf = PDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, title, 0, 1, 'L')
            pdf.ln(5)
            pdf.set_font('Arial', '', 11)
            
            for line in content_lines:
                if line.strip():
                    pdf.cell(0, 8, line, 0, 1, 'L')
                else:
                    pdf.ln(4)
            
            os.makedirs("docs", exist_ok=True)
            filepath = f"docs/{filename}"
            pdf.output(filepath)
            print(f"Created PDF: {filepath}")
            return filepath
        
        # Create PDFs using fpdf
        create_pdf_fpdf("doctors_list.pdf", "Doctors List & Specialties", doctors_content)
        create_pdf_fpdf("clinic_policies.pdf", "Clinic Policies & Guidelines", policies_content)
        create_pdf_fpdf("services_pricing.pdf", "Services & Pricing", services_content)
        
    except ImportError:
        print("fpdf not available. Creating text files instead.")
        print("You can convert these to PDF using Word, Google Docs, or online converters.")
        print("Or install fpdf: pip install fpdf2\n")
        
        # Create text files
        create_text_file("doctors_list.txt", "Doctors List & Specialties", doctors_content)
        create_text_file("clinic_policies.txt", "Clinic Policies & Guidelines", policies_content)
        create_text_file("services_pricing.txt", "Services & Pricing", services_content)
        
        print("\nNOTE: Text files created. Please convert to PDF manually:")
        print("   1. Open each .txt file")
        print("   2. Copy content to Word/Google Docs")
        print("   3. Save as PDF")
        print("   4. Rename to .pdf and place in docs/ folder")


"""
Script to create sample PDFs for the booking assistant
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_pdf(filename, title, content_lines):
    """Create a PDF file with given title and content"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, title)
    
    # Content
    c.setFont("Helvetica", 11)
    y_position = height - 100
    line_height = 15
    
    for line in content_lines:
        if y_position < 50:  # New page if needed
            c.showPage()
            y_position = height - 50
        
        # Handle long lines
        if len(line) > 80:
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line + word) < 80:
                    current_line += word + " "
                else:
                    c.drawString(50, y_position, current_line.strip())
                    y_position -= line_height
                    current_line = word + " "
            if current_line:
                c.drawString(50, y_position, current_line.strip())
                y_position -= line_height
        else:
            c.drawString(50, y_position, line)
            y_position -= line_height
        
        y_position -= 5  # Spacing between lines
    
    c.save()
    print(f"Created: {filename}")

# Create doctors_list.pdf
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

# Create clinic_policies.pdf
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

# Create services_pricing.pdf
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
    import os
    os.makedirs("docs", exist_ok=True)
    
    create_pdf("docs/doctors_list.pdf", "Doctors List & Specialties", doctors_content)
    create_pdf("docs/clinic_policies.pdf", "Clinic Policies & Guidelines", policies_content)
    create_pdf("docs/services_pricing.pdf", "Services & Pricing", services_content)
    
    print("\n✅ All sample PDFs created successfully!")


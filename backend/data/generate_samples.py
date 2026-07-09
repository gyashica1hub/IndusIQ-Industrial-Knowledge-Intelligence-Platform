"""
Generates 3 realistic dummy industrial documents (maintenance log, inspection
report, SOP) so the prototype can be demoed without real plant data. Run once:
    python generate_samples.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path

OUT_DIR = Path(__file__).parent / "sample_docs"
OUT_DIR.mkdir(exist_ok=True)
styles = getSampleStyleSheet()


def make_pdf(filename, title, paragraphs):
    doc = SimpleDocTemplate(str(OUT_DIR / filename), pagesize=A4)
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for p in paragraphs:
        story.append(Paragraph(p, styles["BodyText"]))
        story.append(Spacer(1, 8))
    doc.build(story)
    print(f"Created {filename}")


maintenance_log = [
    "Work Order WO-4521. Date: 12-Mar-2026. Equipment: Pump-101 (Centrifugal Feed Pump, Unit 3).",
    "Reported issue: Elevated vibration levels detected during routine rounds by technician Ramesh Kumar. "
    "Vibration reading was 8.2 mm/s RMS, above the alarm threshold of 7.1 mm/s specified in the OEM manual.",
    "Root cause identified: bearing wear on the drive-end bearing, likely due to lubrication interval "
    "exceeding the recommended 90-day cycle. Last lubrication was performed 142 days prior.",
    "Corrective action: Drive-end bearing replaced. New bearing installed per OEM spec (SKF 6309). "
    "Lubrication schedule updated to 60-day cycle for this pump going forward, approved by supervisor Anita Sharma.",
    "Work Order WO-4522. Date: 15-Mar-2026. Equipment: Boiler-3 (Unit 2).",
    "Scheduled inspection under OISD-118 guidelines for pressure vessel safety. Pressure reading recorded "
    "at 12.4 bar, within the operating range of 10-14 bar. No anomalies found. Inspected by Vikram Singh.",
    "Work Order WO-4530. Date: 22-Mar-2026. Equipment: Compressor-7 (Unit 1).",
    "Unplanned downtime event. Compressor tripped due to high discharge temperature (98 C, threshold 90 C). "
    "Root cause: cooling water flow restriction from partially blocked strainer. Strainer cleaned, flow restored. "
    "Downtime duration: 3 hours 40 minutes. Estimated production loss: 45 units.",
]

inspection_report = [
    "Quality & Safety Inspection Report. Report ID: QSI-2026-0091. Date: 05-Apr-2026.",
    "Facility: Unit 2 Process Area. Inspector: Anita Sharma, Senior QA Engineer.",
    "Scope: Compliance check against Factory Act 1948 and internal Quality Management System (QMS) "
    "procedure QMS-SOP-014 for pressure vessel documentation.",
    "Finding 1: Boiler-3 pressure vessel certification renewal is due within 30 days (expires 04-May-2026). "
    "Renewal application not yet submitted. Flagged as a compliance gap requiring action before deadline.",
    "Finding 2: Pump-101 maintenance records now up to date following bearing replacement on 12-Mar-2026 "
    "(ref Work Order WO-4521). No further action required.",
    "Finding 3: Compressor-7 near-miss incident (22-Mar-2026, high discharge temperature trip) has been "
    "logged but the strainer inspection frequency has not yet been revised in the Preventive Maintenance "
    "schedule. Recommend reducing strainer inspection interval from 90 days to 45 days.",
    "Overall compliance status: 2 of 3 items compliant. 1 item requires corrective action before next audit cycle.",
]

sop_document = [
    "Standard Operating Procedure: SOP-MNT-009. Title: Centrifugal Pump Vibration Monitoring and Response.",
    "Applicable Equipment: All centrifugal pumps rated above 50 HP, including Pump-101, Pump-102, Pump-105.",
    "Regulatory Basis: OISD-118 (Pressure Vessel and Rotating Equipment Safety), internal QMS-SOP-014.",
    "Procedure: 1) Record vibration readings weekly using handheld vibration analyzer. "
    "2) Alarm threshold is 7.1 mm/s RMS per OEM specification. Trip threshold is 11.0 mm/s RMS.",
    "3) If reading exceeds alarm threshold, raise a Work Order within 24 hours and notify the shift supervisor. "
    "4) If reading exceeds trip threshold, equipment must be shut down immediately and isolated per LOTO procedure.",
    "5) Standard lubrication interval is 90 days unless equipment-specific history (as recorded in the CMMS) "
    "indicates a shorter interval is required, in which case the shorter interval takes precedence.",
    "Responsible roles: Maintenance Technician (readings), Shift Supervisor (Work Order approval), "
    "Senior QA Engineer (compliance sign-off during audits).",
]

make_pdf("maintenance_log_march2026.pdf", "Maintenance Work Order Log — March 2026", maintenance_log)
make_pdf("inspection_report_qsi2026.pdf", "Quality & Safety Inspection Report — QSI-2026-0091", inspection_report)
make_pdf("sop_pump_vibration.pdf", "SOP-MNT-009: Pump Vibration Monitoring", sop_document)

print("\nAll sample documents generated in sample_docs/")

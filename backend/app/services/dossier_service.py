"""
e-BIS Sahayak — Official Compliance Dossier Generator Service.
Generates comprehensive, audit-ready compliance dossiers for MSMEs, Startups, and Manufacturers
seeking BIS Conformity Assessment (Scheme-I ISI Mark, Scheme-II CRS, Scheme-IV FMCS, Scheme-X, etc.).
"""
import uuid
import datetime
import html
from typing import Dict, Any, Optional
from app.schemas.intelligence import DossierExportRequest, DossierExportResponse


class DossierService:
    """
    Service responsible for formatting, structuring, and generating official
    compliance dossiers for printing (PDF) and offline archive (.html).
    """

    @classmethod
    def generate_dossier(cls, request: DossierExportRequest) -> DossierExportResponse:
        roadmap = request.roadmap
        now = datetime.datetime.now(datetime.timezone.utc)
        date_str = now.strftime("%d %B %Y, %H:%M UTC")
        date_file_str = now.strftime("%Y%m%d")
        
        # Unique Dossier Identification Number
        random_suffix = uuid.uuid4().hex[:6].upper()
        dossier_id = f"BIS-DOS-{date_file_str}-{random_suffix}"
        
        product_clean = (roadmap.product or "Product").replace(" ", "_")
        file_name = f"BIS_Compliance_Dossier_{product_clean}_{dossier_id}.html"

        # Generate the complete self-contained HTML
        html_content = cls._build_dossier_html(
            dossier_id=dossier_id,
            generated_at=date_str,
            request=request
        )

        metadata: Dict[str, Any] = {
            "dossier_id": dossier_id,
            "generated_at": date_str,
            "product": roadmap.product,
            "standard_number": roadmap.standard_number,
            "applicable_scheme": roadmap.applicable_scheme,
            "is_mandatory_qco": roadmap.is_mandatory_qco,
            "applicant_name": request.applicant_name,
            "organization": request.organization or "Not Specified",
            "checklist_count": len(roadmap.document_checklist),
            "steps_count": len(roadmap.steps),
        }

        return DossierExportResponse(
            dossier_id=dossier_id,
            generated_at=date_str,
            file_name=file_name,
            html_content=html_content,
            metadata=metadata
        )

    @classmethod
    def _build_dossier_html(
        cls,
        dossier_id: str,
        generated_at: str,
        request: DossierExportRequest
    ) -> str:
        roadmap = request.roadmap
        lang = request.language or "en"
        
        # Clean inputs
        applicant = html.escape(request.applicant_name or "MSME Industrial Applicant")
        organization = html.escape(request.organization or "Proprietorship / Enterprise")
        address = html.escape(request.factory_address or "Manufacturing Works, India")
        license_type = html.escape(request.license_type or "Grant of New License (Initial Application)")
        
        product = html.escape(roadmap.product or "N/A")
        standard_num = html.escape(roadmap.standard_number or "Under Determination / Sector Standard")
        scheme_name = html.escape(roadmap.scheme_name or roadmap.applicable_scheme or "Scheme-I Normal Procedure")
        rationale = html.escape(roadmap.route_rationale or "Standard manufacturing evaluation applies.")
        disclaimer = html.escape(roadmap.disclaimer)

        # Build Steps HTML
        steps_rows = []
        for step in roadmap.steps:
            badges_html = ""
            if step.status_badge:
                badges_html = f'<span class="badge badge-timeline">{html.escape(step.status_badge)}</span>'
            
            docs_html = ""
            if step.checklist:
                docs_items = "".join([f"<li>{html.escape(d)}</li>" for d in step.checklist])
                docs_html = f'<div class="step-docs"><strong>Milestone Checkpoints:</strong><ul>{docs_items}</ul></div>'

            steps_rows.append(f"""
            <div class="step-card">
              <div class="step-num">Stage {step.step_number}</div>
              <div class="step-body">
                <div class="step-title-row">
                  <h4 class="step-title">{html.escape(step.title)}</h4>
                  <div class="step-badges">{badges_html}</div>
                </div>
                <p class="step-desc">{html.escape(step.description)}</p>
                {docs_html}
              </div>
            </div>
            """)
        steps_html = "\n".join(steps_rows) if steps_rows else "<p>Standard 4-stage procedural audit applies.</p>"

        # Build Document Checklist Rows
        checklist_rows = []
        for idx, doc in enumerate(roadmap.document_checklist, 1):
            category_label = doc.category.replace("_", " ").title()
            verified_badge = '<span class="status-verified">&#10003; Statutory Official</span>' if doc.is_verified_official else '<span class="status-general">Pre-requisite</span>'
            note_cell = f'<div class="doc-note">{html.escape(doc.note)}</div>' if doc.note else ""
            
            checklist_rows.append(f"""
            <tr>
              <td class="text-center font-mono">{idx}</td>
              <td>
                <div class="doc-name">{html.escape(doc.item)}</div>
                {note_cell}
              </td>
              <td><span class="category-pill">{category_label}</span></td>
              <td>{verified_badge}</td>
              <td class="sign-off-cell">
                <div class="sign-box">
                  <span class="box">&#9633; Ready</span>
                  <span class="initials">Sign: ________</span>
                </div>
              </td>
            </tr>
            """)
        checklist_table = "\n".join(checklist_rows) if checklist_rows else "<tr><td colspan='5'>Standard statutory documentation checklist applies.</td></tr>"

        # Build Sources Rows
        sources_rows = []
        for src in (roadmap.official_sources or []):
            sources_rows.append(f"""
            <div class="source-item">
              <div class="source-title">&#127760; {html.escape(src.title)}</div>
              <div class="source-desc">{html.escape(src.description)}</div>
              <a href="{html.escape(src.url)}" target="_blank" rel="noopener noreferrer" class="source-link">{html.escape(src.url)}</a>
            </div>
            """)
        sources_html = "\n".join(sources_rows)

        # Mandatory QCO Badge
        qco_banner = ""
        if roadmap.is_mandatory_qco:
            qco_order = f" ({html.escape(roadmap.qco_order_number)})" if roadmap.qco_order_number else ""
            qco_banner = f"""
            <div class="alert-box alert-danger">
              <strong>&#9888; MANDATORY QUALITY CONTROL ORDER (QCO) ENFORCED{qco_order}:</strong>
              Manufacturing, importing, storing, or selling this product without a valid BIS Standard Mark (ISI / CRS) constitutes a non-bailable offense under Section 16 & Section 17 of the BIS Act, 2016.
            </div>
            """

        air_banner = ""
        if roadmap.requires_air:
            air_banner = """
            <div class="alert-box alert-purple">
              <strong>&#128100; AUTHORIZED INDIAN REPRESENTATIVE (AIR) MANDATORY:</strong>
              As this product involves foreign manufacturing (Scheme-IV FMCS / Scheme-II CRS), an entity registered in India must be formally designated as the AIR to accept legal and regulatory accountability.
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BIS Compliance Dossier — {product} ({dossier_id})</title>
  <style>
    /* CSS Reset & Typography */
    *, *::before, *::after {{ box-sizing: border-box; }}
    @page {{
      size: A4;
      margin: 15mm 15mm 15mm 15mm;
      @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
      }}
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 11pt;
      line-height: 1.5;
      color: #0f172a;
      background-color: #f8fafc;
      margin: 0;
      padding: 24px;
    }}
    .dossier-wrapper {{
      max-width: 900px;
      margin: 0 auto;
      background: #ffffff;
      padding: 36px 44px;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
    }}
    
    /* Header & Branding */
    .national-ribbon {{
      height: 6px;
      background: linear-gradient(90deg, #ff9933 33.3%, #ffffff 33.3%, #ffffff 66.6%, #138808 66.6%);
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      margin-bottom: 20px;
    }}
    .header-table {{
      width: 100%;
      border-bottom: 2px solid #0a2540;
      padding-bottom: 16px;
      margin-bottom: 20px;
    }}
    .emblem-title {{
      font-size: 16pt;
      font-weight: 900;
      color: #0a2540;
      letter-spacing: -0.02em;
      margin: 0;
      text-transform: uppercase;
    }}
    .emblem-sub {{
      font-size: 9.5pt;
      font-weight: 700;
      color: #475569;
      margin-top: 3px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .dossier-tag {{
      text-align: right;
    }}
    .dossier-id {{
      display: inline-block;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 10pt;
      font-weight: 800;
      color: #0369a1;
      background: #e0f2fe;
      border: 1px solid #7dd3fc;
      padding: 4px 10px;
      border-radius: 6px;
    }}
    .dossier-date {{
      font-size: 8.5pt;
      color: #64748b;
      margin-top: 4px;
    }}

    /* Action Bar (Hidden in print) */
    .print-controls {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #0a2540;
      color: #ffffff;
      padding: 12px 20px;
      border-radius: 8px;
      margin-bottom: 24px;
    }}
    .print-btn {{
      background: #f59e0b;
      color: #0f172a;
      font-weight: 800;
      border: none;
      padding: 8px 18px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 10pt;
      transition: background 0.2s;
    }}
    .print-btn:hover {{ background: #fbbf24; }}

    /* Section Headers */
    .section-title {{
      font-size: 12.5pt;
      font-weight: 800;
      color: #0a2540;
      border-left: 4px solid #f59e0b;
      padding-left: 10px;
      margin-top: 26px;
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }}

    /* Metadata Grid Table */
    .meta-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
      font-size: 10pt;
    }}
    .meta-table th, .meta-table td {{
      padding: 8px 12px;
      border: 1px solid #e2e8f0;
      text-align: left;
    }}
    .meta-table th {{
      background-color: #f1f5f9;
      color: #334155;
      font-weight: 700;
      width: 25%;
    }}
    .meta-table td {{
      background-color: #ffffff;
      color: #0f172a;
      font-weight: 500;
    }}

    /* Alerts */
    .alert-box {{
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 9.5pt;
      line-height: 1.45;
      margin: 14px 0;
    }}
    .alert-danger {{
      background-color: #fef2f2;
      border: 1px solid #f87171;
      color: #991b1b;
    }}
    .alert-purple {{
      background-color: #faf5ff;
      border: 1px solid #c084fc;
      color: #6b21a8;
    }}

    /* Steps Cards */
    .step-card {{
      display: flex;
      gap: 16px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 12px;
      page-break-inside: avoid;
    }}
    .step-num {{
      font-size: 10pt;
      font-weight: 900;
      text-transform: uppercase;
      color: #0369a1;
      background: #e0f2fe;
      border: 1px solid #bae6fd;
      border-radius: 6px;
      padding: 4px 8px;
      height: fit-content;
      white-space: nowrap;
    }}
    .step-body {{ flex: 1; }}
    .step-title-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }}
    .step-title {{
      font-size: 11pt;
      font-weight: 800;
      color: #0f172a;
      margin: 0;
    }}
    .step-desc {{
      font-size: 9.5pt;
      color: #334155;
      margin: 4px 0;
    }}
    .step-docs {{
      font-size: 9pt;
      background: #ffffff;
      border: 1px dashed #cbd5e1;
      border-radius: 6px;
      padding: 8px 12px;
      margin-top: 8px;
    }}
    .step-docs ul {{ margin: 4px 0 0 16px; padding: 0; }}
    .step-docs li {{ margin-bottom: 2px; color: #475569; }}

    /* Badges */
    .badge {{
      display: inline-block;
      font-size: 8pt;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }}
    .badge-timeline {{ background: #e2e8f0; color: #1e293b; }}
    .badge-fee {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}

    /* Checklist Table */
    .checklist-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 9pt;
      margin-top: 10px;
    }}
    .checklist-table th, .checklist-table td {{
      padding: 8px 10px;
      border: 1px solid #cbd5e1;
      text-align: left;
    }}
    .checklist-table th {{
      background: #0a2540;
      color: #ffffff;
      font-weight: 800;
      font-size: 8.5pt;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .checklist-table tr:nth-child(even) {{ background: #f8fafc; }}
    .doc-name {{ font-weight: 700; color: #0f172a; }}
    .doc-note {{ font-size: 8pt; color: #64748b; margin-top: 2px; }}
    .category-pill {{
      font-size: 7.5pt;
      font-weight: 700;
      background: #e2e8f0;
      color: #334155;
      padding: 2px 6px;
      border-radius: 4px;
      white-space: nowrap;
    }}
    .status-verified {{
      font-size: 8pt;
      font-weight: 800;
      color: #047857;
      background: #d1fae5;
      padding: 2px 6px;
      border-radius: 4px;
      white-space: nowrap;
    }}
    .status-general {{
      font-size: 8pt;
      font-weight: 700;
      color: #0369a1;
      background: #e0f2fe;
      padding: 2px 6px;
      border-radius: 4px;
      white-space: nowrap;
    }}
    .sign-off-cell {{
      width: 130px;
    }}
    .sign-box {{
      font-size: 8pt;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .box {{ font-weight: 700; color: #475569; }}
    .initials {{ color: #94a3b8; font-family: monospace; }}

    /* Official Sources */
    .source-item {{
      background: #f1f5f9;
      border-left: 3px solid #0369a1;
      padding: 8px 12px;
      margin-bottom: 8px;
      border-radius: 0 6px 6px 0;
      font-size: 9pt;
      page-break-inside: avoid;
    }}
    .source-title {{ font-weight: 800; color: #0f172a; }}
    .source-desc {{ color: #475569; font-size: 8.5pt; }}
    .source-link {{ color: #0284c7; text-decoration: none; word-break: break-all; font-family: monospace; font-size: 8pt; }}

    /* Footer & Seal */
    .footer-section {{
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px solid #cbd5e1;
      font-size: 8.5pt;
      color: #64748b;
      line-height: 1.4;
    }}
    .seal-box {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 16px;
      padding: 12px 16px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
    }}
    .seal-text {{ font-weight: 700; color: #0a2540; }}
    .seal-badge {{
      font-family: monospace;
      font-size: 8pt;
      color: #475569;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      padding: 4px 8px;
      border-radius: 4px;
    }}

    /* Print Overrides */
    @media print {{
      body {{
        background: #ffffff;
        padding: 0;
        font-size: 9.5pt;
      }}
      .dossier-wrapper {{
        border: none;
        box-shadow: none;
        padding: 0;
        max-width: 100%;
      }}
      .print-controls {{ display: none !important; }}
      .section-title {{ page-break-after: avoid; }}
      .step-card, .meta-table, .checklist-table {{ page-break-inside: avoid; }}
      a {{ text-decoration: none; color: inherit; }}
    }}
  </style>
</head>
<body>
  <div class="dossier-wrapper">
    <!-- Action controls (hidden when printing) -->
    <div class="print-controls">
      <div>
        <strong>Official Compliance Dossier</strong> &bull; Ready for A4 Print / PDF Export
      </div>
      <button class="print-btn" onclick="window.print()">&#128424; Print / Save as PDF</button>
    </div>

    <div class="national-ribbon"></div>

    <!-- Header Section -->
    <table class="header-table">
      <tr>
        <td style="vertical-align: middle;">
          <h1 class="emblem-title">e-BIS Sahayak &bull; Compliance Dossier</h1>
          <div class="emblem-sub">Bureau of Indian Standards Technical Advisory &bull; MSME Readiness Pack</div>
        </td>
        <td class="dossier-tag" style="vertical-align: middle;">
          <div class="dossier-id">{dossier_id}</div>
          <div class="dossier-date">Generated: {generated_at}</div>
        </td>
      </tr>
    </table>

    {qco_banner}
    {air_banner}

    <!-- Executive Summary Table -->
    <h2 class="section-title">1. Enterprise & Product Classification Summary</h2>
    <table class="meta-table">
      <tr>
        <th>Applicant Name</th>
        <td>{applicant}</td>
        <th>Target Indian Standard</th>
        <td><strong style="color: #0369a1;">{standard_num}</strong></td>
      </tr>
      <tr>
        <th>Enterprise Legal Entity</th>
        <td>{organization}</td>
        <th>Conformity Assessment Scheme</th>
        <td><strong style="color: #92400e;">{scheme_name}</strong></td>
      </tr>
      <tr>
        <th>Product Description</th>
        <td>{product}</td>
        <th>Application Purpose</th>
        <td>{license_type}</td>
      </tr>
      <tr>
        <th>Manufacturing Facility</th>
        <td>{address}</td>
        <th>Mandatory QCO Enforced</th>
        <td>{"YES — Statutory Obligation" if roadmap.is_mandatory_qco else "Voluntary / Market Conformity"}</td>
      </tr>
    </table>

    <!-- Route Rationale -->
    <h2 class="section-title">2. Statutory Scheme Determination & Route Rationale</h2>
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px 18px; border-radius: 8px; font-size: 10pt; color: #1e293b; line-height: 1.5;">
      {rationale}
    </div>

    <!-- Procedural Steps -->
    <h2 class="section-title">3. Four-Stage Grant-of-License Procedural Timeline</h2>
    <div class="steps-container">
      {steps_html}
    </div>

    <!-- Document Checklist -->
    <h2 class="section-title">4. Statutory Document Audit Checklist & Sign-Off</h2>
    <p style="font-size: 9pt; color: #64748b; margin-top: -6px; margin-bottom: 10px;">
      Verify and check off each statutory document prior to submitting your formal application on the ManakOnline portal.
    </p>
    <table class="checklist-table">
      <thead>
        <tr>
          <th style="width: 35px; text-align: center;">#</th>
          <th>Statutory Document Description</th>
          <th style="width: 140px;">Category</th>
          <th style="width: 100px;">Verification</th>
          <th style="width: 120px;">Audit Sign-Off</th>
        </tr>
      </thead>
      <tbody>
        {checklist_table}
      </tbody>
    </table>

    <!-- Official Sources & Verification Links -->
    <h2 class="section-title">5. Official BIS Gazetted Source Portals</h2>
    <div class="sources-container">
      {sources_html}
    </div>

    <!-- Footer & Disclaimer -->
    <div class="footer-section">
      <div style="margin-bottom: 8px;">
        <strong>Statutory Notice & Legal Disclaimer:</strong> {disclaimer}
      </div>
      <div>
        This dossier was compiled by <em>e-BIS Sahayak</em> (Smart India Hackathon 2026 Problem Statement #107) from official Gazette notifications, BIS (Conformity Assessment) Regulations 2018, and published Quality Control Orders.
      </div>
      <div class="seal-box">
        <div class="seal-text">&#128737; e-BIS Sahayak Automated Compliance Audit System</div>
        <div class="seal-badge">Dossier Checksum: {dossier_id}</div>
      </div>
    </div>
  </div>
</body>
</html>"""

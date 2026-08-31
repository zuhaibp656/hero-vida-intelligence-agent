import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "docs_assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Brand Color Definitions
COLOR_HERO_RED = "#D32F2F"       # Hero Crimson Red
COLOR_VIDA_TEAL = "#00838F"      # VIDA Electric Teal
COLOR_GOOGLE_BLUE = "#1A73E8"    # Google Cloud Deep Blue
COLOR_GOOGLE_GREEN = "#0F9D58"   # Google Green
COLOR_GOOGLE_YELLOW = "#F4B400"  # Google Yellow
COLOR_DARK_SLATE = "#202124"     # Off-Black Body Text
COLOR_LIGHT_BG = "#F8F9FA"       # Subtle grey container
COLOR_BORDER_GREY = "#E0E0E0"    # Divider lines

def set_cell_background(cell, fill_hex):
    """Sets the background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    """Sets internal cell margins in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def generate_header_banner():
    """Generates an executive branded banner combining Google Cloud and Hero MotoCorp identities."""
    fig, ax = plt.subplots(figsize=(10, 2.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.5)
    ax.axis("off")

    # Background gradient container
    bg = patches.FancyBboxPatch(
        (0.1, 0.1), 9.8, 2.3,
        boxstyle="round,pad=0.08,rounding_size=0.15",
        facecolor="#1A202C",
        edgecolor="#2D3748",
        linewidth=1.5
    )
    ax.add_patch(bg)

    # Accent color bars
    bar_hero = patches.Rectangle((0.3, 2.2), 3.0, 0.08, facecolor=COLOR_HERO_RED)
    bar_vida = patches.Rectangle((3.3, 2.2), 3.0, 0.08, facecolor=COLOR_VIDA_TEAL)
    bar_google = patches.Rectangle((6.3, 2.2), 3.4, 0.08, facecolor=COLOR_GOOGLE_BLUE)
    ax.add_patch(bar_hero)
    ax.add_patch(bar_vida)
    ax.add_patch(bar_google)

    # Header Titles
    ax.text(0.5, 1.7, "GOOGLE CLOUD & HERO MOTOCORP | STRATEGIC AI INITIATIVE",
            fontsize=9.5, fontweight="bold", color="#A0AEC0", fontfamily="sans-serif")
    ax.text(0.5, 1.15, "Hero VIDA — Autonomous Competitor Intelligence Multi-Agent",
            fontsize=17, fontweight="heavy", color="#FFFFFF", fontfamily="sans-serif")
    ax.text(0.5, 0.65, "100% Real-Time Web Grounding • Zero Hardcoded Prices • 493 Cities • 1-Click CSV Export",
            fontsize=10.5, color="#63B3ED", fontfamily="sans-serif")

    # Status pill
    pill = patches.FancyBboxPatch(
        (7.9, 1.45), 1.7, 0.5,
        boxstyle="round,pad=0.04,rounding_size=0.1",
        facecolor="#2D3748",
        edgecolor="#48BB78",
        linewidth=1.2
    )
    ax.add_patch(pill)
    ax.text(8.75, 1.7, "ACTIVE • PRODUCTION", fontsize=7.5, fontweight="bold", color="#68D391",
            ha="center", va="center", fontfamily="sans-serif")

    output_path = os.path.join(ASSETS_DIR, "header_banner.png")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    return output_path

def generate_architecture_diagram():
    """Generates a crystal-clear, non-technical architecture graphic for business stakeholders."""
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Title of diagram
    ax.text(5.5, 7.15, "End-to-End Autonomous Intelligence Architecture",
            fontsize=15, fontweight="bold", color=COLOR_DARK_SLATE, ha="center", fontfamily="sans-serif")
    ax.text(5.5, 6.75, "From Natural Language Questions to Live Verified On-Road Pricing & Instant Downloads",
            fontsize=10, color="#5F6368", ha="center", fontfamily="sans-serif")

    # Layer 1: Stakeholder Inputs
    box_user = patches.FancyBboxPatch(
        (0.5, 4.3), 2.8, 1.9,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        facecolor="#E8F0FE", edgecolor="#1A73E8", linewidth=1.5
    )
    ax.add_patch(box_user)
    ax.text(1.9, 5.85, "1. Business Stakeholder", fontsize=11, fontweight="bold", color="#174EA6", ha="center")
    ax.text(1.9, 5.4, "• Executive Questions\n• Slangs (dilli, blr, poona)\n• Multi-City / Multi-Model\n• Conversational Follow-ups",
            fontsize=8.5, color="#3C4043", ha="center")

    # Layer 2: Main Orchestrator
    box_agent = patches.FancyBboxPatch(
        (4.1, 4.1), 2.8, 2.3,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        facecolor="#FCE8E6", edgecolor="#D32F2F", linewidth=2.0
    )
    ax.add_patch(box_agent)
    ax.text(5.5, 6.05, "2. Main AI Orchestrator", fontsize=11, fontweight="bold", color="#C5221F", ha="center")
    ax.text(5.5, 5.75, "(Gemini 2.5 on Vertex AI)", fontsize=8.5, color="#7F1D1D", ha="center")
    ax.text(5.5, 4.9, "• Natural Slang Normalizer\n• Context Continuity Memory\n• Coordinates 3 Sub-Agents\n• Verifies Data Integrity",
            fontsize=8.5, color="#3C4043", ha="center")

    # Layer 3: Live Grounding Engines
    box_crawl = patches.FancyBboxPatch(
        (7.7, 4.3), 2.8, 1.9,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        facecolor="#E6FFFA", edgecolor="#00838F", linewidth=1.5
    )
    ax.add_patch(box_crawl)
    ax.text(9.1, 5.85, "3. 100% Real-Time Ingestion", fontsize=10.5, fontweight="bold", color="#00695C", ha="center")
    ax.text(9.1, 5.05, "• Hero VIDA Master Feed (493 cities)\n• Ather Energy live JSON state\n• Bajaj Chetak live series\n• TVS iQube city cards\n• Ola Electric & River Indie",
            fontsize=8, color="#3C4043", ha="center")

    # Layer 4: Subsidy & Tax Calculation Engine
    box_pricing = patches.FancyBboxPatch(
        (1.5, 1.2), 3.6, 2.2,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        facecolor="#FEF7E0", edgecolor="#F2994A", linewidth=1.5
    )
    ax.add_patch(box_pricing)
    ax.text(3.3, 3.05, "4. Dynamic Subsidy & Price Engine", fontsize=11, fontweight="bold", color="#B05E00", ha="center")
    ax.text(3.3, 2.15, "• Central PM E-Drive Scheme (₹2,500/kWh)\n• 15+ State EV Policy Waivers\n• Real-Time Road Tax (RTO) Exemption Math\n• Exact Customer On-Road Pricing",
            fontsize=8.5, color="#3C4043", ha="center")

    # Layer 5: Output & Storage
    box_output = patches.FancyBboxPatch(
        (5.9, 1.2), 3.6, 2.2,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        facecolor="#E6F4EA", edgecolor="#137333", linewidth=1.5
    )
    ax.add_patch(box_output)
    ax.text(7.7, 3.05, "5. Executive Output & 1-Click CSV", fontsize=11, fontweight="bold", color="#137333", ha="center")
    ax.text(7.7, 2.15, "• Standardized Executive Table\n• Bold Green VIDA Final Price (Verified INR)\n• Uploaded to Google Cloud Storage\n• 1-Click Console Download Link\n• Instant Copyable Raw CSV Block",
            fontsize=8.5, color="#3C4043", ha="center")

    # Connecting Arrows
    def draw_arrow(x1, y1, x2, y2, color="#5F6368", label=""):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                            color=color, lw=2.0)
        )
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 0.15, label, fontsize=8, fontweight="bold", color=color, ha="center")

    draw_arrow(3.3, 5.25, 4.1, 5.25, color="#1A73E8", label="Query")
    draw_arrow(6.9, 5.25, 7.7, 5.25, color="#C5221F", label="Crawl")
    draw_arrow(7.7, 4.3, 6.9, 3.4, color="#00838F", label="")
    draw_arrow(5.5, 4.1, 3.3, 3.4, color="#C5221F", label="Specs & Prices")
    draw_arrow(5.1, 2.3, 5.9, 2.3, color="#137333", label="Calculate")

    output_path = os.path.join(ASSETS_DIR, "architecture_infographic.png")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    return output_path

def generate_value_matrix_chart():
    """Generates an executive comparison graphic: Traditional BI vs Autonomous Agent."""
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")

    # Header Card
    ax.text(5.0, 3.85, "Traditional Market Dashboards vs. Autonomous AI Agent",
            fontsize=13, fontweight="bold", color=COLOR_DARK_SLATE, ha="center")

    headers = ["Evaluation Metric", "Traditional Static Dashboards", "Hero VIDA Autonomous AI Agent"]
    col_x = [0.5, 3.6, 6.8]
    col_w = [3.0, 3.1, 2.8]

    # Header row box
    ax.add_patch(patches.Rectangle((0.3, 3.1), 9.4, 0.45, facecolor="#1F2937"))
    for i, h in enumerate(headers):
        ax.text(col_x[i] + 0.1, 3.32, h, fontsize=9.5, fontweight="bold", color="#FFFFFF")

    rows = [
        ("Data Freshness", "Stale weekly or monthly manual data dumps", "100% Live crawl on every query (zero cache)"),
        ("Price Accuracy", "Hardcoded national averages; misses local deals", "Exact city on-road prices + active state subsidies"),
        ("City Granularity", "Limited to top 4-5 major metro hubs", "493 Indian cities in live master feed"),
        ("Query Experience", "Complex SQL, BI slice-and-dice, fixed charts", "Natural conversation, slangs (dilli, blr, poona)"),
        ("Data Export", "Manual CSV export button or scheduled email", "Instant 1-Click Cloud Storage link & raw CSV"),
        ("Integration", "Standalone dashboard silo", "A2A Protocol (embeds in WhatsApp, CRM, web)")
    ]

    y_pos = 2.6
    for idx, (m, old, new) in enumerate(rows):
        bg_col = "#F9FAFB" if idx % 2 == 0 else "#FFFFFF"
        ax.add_patch(patches.Rectangle((0.3, y_pos - 0.05), 9.4, 0.45, facecolor=bg_col, edgecolor="#E5E7EB", linewidth=0.6))
        ax.text(col_x[0] + 0.1, y_pos + 0.12, m, fontsize=8.5, fontweight="bold", color="#111827")
        ax.text(col_x[1] + 0.1, y_pos + 0.12, f"[NO]  {old}", fontsize=8, color="#DC2626")
        ax.text(col_x[2] + 0.1, y_pos + 0.12, f"[YES] {new}", fontsize=8, fontweight="bold", color="#059669")
        y_pos -= 0.48

    output_path = os.path.join(ASSETS_DIR, "value_matrix.png")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    return output_path

def build_executive_brief_document():
    """Builds a comprehensive, executive-ready Word document for Hero MotoCorp."""
    # 1. Generate diagrams
    header_img = generate_header_banner()
    arch_img = generate_architecture_diagram()
    matrix_img = generate_value_matrix_chart()

    # 2. Initialize Document
    doc = Document()

    # Configure Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(32, 33, 36)

    # --- COVER / HEADER BANNER ---
    doc.add_picture(header_img, width=Inches(6.8))
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(4)
    p_spacer.paragraph_format.space_after = Pt(8)

    # Metadata Strip Box (Table)
    meta_table = doc.add_table(rows=1, cols=4)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    
    meta_data = [
        ("PROJECT", "Hero VIDA AI Consultant"),
        ("TARGET AUDIENCE", "Hero Leadership & Commercial Teams"),
        ("TECH STACK", "Google ADK & Gemini 2.5"),
        ("STATUS", "Active Production Deployment")
    ]
    for i, (label, val) in enumerate(meta_data):
        cell = meta_table.cell(0, i)
        cell.width = Inches(1.7)
        set_cell_background(cell, "F1F3F4")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_lbl = p.add_run(f"{label}\n")
        r_lbl.font.size = Pt(7.5)
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = RGBColor(100, 110, 120)
        r_val = p.add_run(val)
        r_val.font.size = Pt(8.5)
        r_val.font.bold = True
        r_val.font.color.rgb = RGBColor(26, 115, 232)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECTION 1: EXECUTIVE SUMMARY ---
    h1 = doc.add_heading(level=1)
    r_h1 = h1.add_run("1. Executive Summary: The Business Challenge & Solution")
    r_h1.font.color.rgb = RGBColor(211, 47, 47)
    r_h1.font.size = Pt(15)

    p1 = doc.add_paragraph()
    p1.add_run("In India's hyper-competitive electric two-wheeler (EV 2W) market, product pricing and promotional offers change weekly. Key rivals like ")
    p1.add_run("Ather Energy, Bajaj Chetak, TVS iQube, and Ola Electric ").bold = True
    p1.add_run("frequently update introductory pricing, festive cash discounts, exchange bonuses, and charger bundle costs. Simultaneously, state governments implement differing EV subsidies, road tax exemptions, and registration fees across cities like ")
    p1.add_run("Delhi, Bengaluru, Mumbai, Pune, Ahmedabad, and Chennai.").bold = True

    p2 = doc.add_paragraph()
    p2.add_run("Historically, Hero MotoCorp sales representatives, regional territory managers, and dealership consultants relied on fragmented spreadsheets, stale internal emails, or third-party blogs that frequently contained obsolete prices or discontinued models (such as old V1 units).")

    # Highlight Callout Box
    callout = doc.add_table(rows=1, cols=1)
    callout.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cell = callout.cell(0, 0)
    c_cell.width = Inches(6.8)
    set_cell_background(c_cell, "E8F0FE")
    set_cell_margins(c_cell, top=140, bottom=140, left=180, right=180)
    cp = c_cell.paragraphs[0]
    cp_run1 = cp.add_run("The Autonomous Solution: ")
    cp_run1.bold = True
    cp_run1.font.color.rgb = RGBColor(26, 115, 232)
    cp.add_run(
        "Hero MotoCorp and Google Cloud have deployed the Hero VIDA Competitor Intelligence Multi-Agent. "
        "Built on Google ADK and powered by Gemini 2.5 on Vertex AI, the agent executes 100% real-time web crawls against official manufacturer portals, "
        "computes exact state and central subsidies, and delivers standardized executive comparison reports with 1-click Cloud Storage CSV downloads in under 30 seconds."
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Value Matrix Graphic
    doc.add_picture(matrix_img, width=Inches(6.8))
    p_spacer2 = doc.add_paragraph()
    p_spacer2.paragraph_format.space_after = Pt(12)

    # --- SECTION 2: WHAT THE AGENT DOES ---
    h2 = doc.add_heading(level=1)
    r_h2 = h2.add_run("2. What This Agent Does (Plain-English Capabilities)")
    r_h2.font.color.rgb = RGBColor(0, 131, 143)
    r_h2.font.size = Pt(15)

    capabilities = [
        ("100% Real-Time Live Grounding (Zero Hardcoded Data)",
         "The agent does not guess, hallucinate, or use pre-stored static tables. On every query, it reaches out directly to https://www.vidaworld.com (ingesting live product-master and price-master feeds covering 493 Indian cities) and rival portals (Ather, Chetak, TVS, Ola, River Indie) to pull exact Ex-Showroom prices, battery kWh, certified ranges, and active discounts."),
        
        ("Understands Real Indian Slangs & Regional City Names",
         "Non-technical users do not need to format SQL queries or click through dropdowns. They can type or ask in everyday business language using regional slangs: 'dilli' or 'ncr' (Delhi), 'blr' (Bengaluru), 'bombay' or 'mmr' (Mumbai), 'poona' (Pune), 'madras' (Chennai), 'calcutta' (Kolkata), 'hyd' (Hyderabad), 'amdavad' (Ahmedabad), 'pink city' (Jaipur), 'chd' (Chandigarh), and 'lko' (Lucknow)."),

        ("Complex Matrix Comparisons & Multi-Turn Memory",
         "The agent natively understands complex multi-dimensional requests:\n"
         "• Same company, different models, different cities (e.g. 'Compare VIDA V2 Pro vs VX2 Plus in Delhi and Bangalore')\n"
         "• Multiple competitors across multiple cities (e.g. 'Ather Rizta vs Chetak C3501 vs TVS iQube in Pune and Ahmedabad')\n"
         "• Seamless follow-up conversations without resetting context (e.g. 'Now add Chennai too' or 'What about Chetak?')."),

        ("Exact Central & State EV Subsidy Math",
         "It calculates the Government of India's PM E-Drive central subsidy (₹2,500/kWh up to ₹10,000) and city-specific state EV policies (e.g. Delhi EV incentives, Maharashtra EV policies, Gujarat incentives, and state-level RTO tax exemptions), giving exact customer on-road figures."),

        ("1-Click CSV Export & Google Cloud Storage Download",
         "Every single comparison generates a structured CSV spreadsheet that is automatically uploaded to Google Cloud Storage. The user receives a direct 1-click Google Cloud Console link where they can download the file with one click, a direct storage URL, and a copyable CSV block directly inside the chat window.")
    ]

    for title, desc in capabilities:
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(4)
        r_title = p_cap.add_run(f"{title}\n")
        r_title.bold = True
        r_title.font.size = Pt(11)
        r_title.font.color.rgb = RGBColor(32, 33, 36)
        r_desc = p_cap.add_run(desc)
        r_desc.font.size = Pt(9.5)
        r_desc.font.color.rgb = RGBColor(60, 64, 67)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECTION 3: SYSTEM ARCHITECTURE ---
    h3 = doc.add_heading(level=1)
    r_h3 = h3.add_run("3. System Architecture: How It Works")
    r_h3.font.color.rgb = RGBColor(26, 115, 232)
    r_h3.font.size = Pt(15)

    doc.add_picture(arch_img, width=Inches(6.8))
    p_cap_arch = doc.add_paragraph()
    p_cap_arch.paragraph_format.space_after = Pt(8)
    r_arch_note = p_cap_arch.add_run("Figure 1: Architectural Flow from natural language stakeholder inquiry to real-time ingestion, calculation, and CSV generation.")
    r_arch_note.font.size = Pt(8.5)
    r_arch_note.font.italic = True
    r_arch_note.font.color.rgb = RGBColor(100, 110, 120)

    # Sub-agents table
    doc.add_paragraph().paragraph_format.space_before = Pt(6)
    p_tbl_lbl = doc.add_paragraph()
    p_tbl_lbl.add_run("The Google ADK Multi-Agent Team:").bold = True

    subagent_table = doc.add_table(rows=5, cols=3)
    subagent_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    subagent_table.autofit = False

    s_headers = ["Specialized Agent", "Model Tier", "Core Responsibilities"]
    col_widths = [Inches(1.8), Inches(1.4), Inches(3.6)]

    for j, h in enumerate(s_headers):
        cell = subagent_table.cell(0, j)
        cell.width = col_widths[j]
        set_cell_background(cell, "1F2937")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    agent_rows = [
        ("🌟 hero_vida_main_agent\n(Main Orchestrator)", "Gemini 2.5 Pro", "Handles conversational dialogue, normalizes Indian slangs, coordinates the specialist sub-agents, and produces the verified executive report."),
        ("🕷️ crawler_subagent\n(Live Scraper)", "Gemini 2.5 Flash", "Executes headless real-time web crawlers across official OEM websites; extracts live JSON state, specs, and prices; stores audit data."),
        ("💰 pricing_subagent\n(Subsidy Specialist)", "Gemini 2.5 Pro", "Computes PM E-Drive central subsidies, state EV policy incentives, road tax waivers, and on-road customer prices across 15+ Indian states."),
        ("📊 report_subagent\n(Executive Synthesis)", "Gemini 2.5 Pro", "Formats side-by-side comparison tables, highlights Hero VIDA competitive advantages, and links to Cloud Storage CSV exports.")
    ]

    for i, (name, tier, resp) in enumerate(agent_rows, start=1):
        r_cells = [subagent_table.cell(i, 0), subagent_table.cell(i, 1), subagent_table.cell(i, 2)]
        for j, cell in enumerate(r_cells):
            cell.width = col_widths[j]
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)

        r_cells[0].paragraphs[0].add_run(name).font.size = Pt(8.5)
        r_cells[0].paragraphs[0].runs[0].bold = True
        r_cells[1].paragraphs[0].add_run(tier).font.size = Pt(8.5)
        r_cells[2].paragraphs[0].add_run(resp).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECTION 4: HOW CUSTOMERS CAN DEPLOY THIS ---
    h4 = doc.add_heading(level=1)
    r_h4 = h4.add_run("4. How Hero MotoCorp Can Deploy This Agent")
    r_h4.font.color.rgb = RGBColor(211, 47, 47)
    r_h4.font.size = Pt(15)

    p_dep_intro = doc.add_paragraph()
    p_dep_intro.add_run("Depending on Hero MotoCorp's infrastructure preference, security posture, and target audience, the agent can be deployed in three distinct enterprise topologies:")

    deploy_options = [
        ("Option A: Vertex AI Agent Engine (Recommended — Fully Managed Serverless)",
         "• What it is: The agent runs entirely on Google Cloud's managed Vertex AI Agent Engine.\n"
         "• Business Benefit: Zero servers to manage, automated autoscaling, enterprise security, built-in session state memory, and an interactive Cloud Console Playground for leadership testing.\n"
         "• How it deploys: 1-click deployment using deploy.sh or adk deploy agent_engine.\n"
         "• Target Environment: Deployed directly into Hero MotoCorp's Google Cloud project (e.g. us-central1 or asia-south1)."),

        ("Option B: Google Cloud Run (Containerized Microservice for Private VPCs)",
         "• What it is: Packaged as a standard Docker container hosted on Google Cloud Run.\n"
         "• Business Benefit: Perfect if Hero wishes to place the agent behind an existing enterprise API Gateway, intranet portal, or secure internal dealership VPN.\n"
         "• How it deploys: Automated Docker container built via Cloud Build (gcloud run deploy)."),

        ("Option C: Dealership & Field Rep Local CLI (Direct Desktop Access)",
         "• What it is: A standalone lightweight Python application that runs on dealer computers or executive laptops.\n"
         "• Business Benefit: Allows territory managers or sales personnel to run fast benchmarks without requiring cloud console access.\n"
         "• How it deploys: 1-click launch via run.sh.")
    ]

    for title, details in deploy_options:
        p_opt = doc.add_paragraph()
        p_opt.paragraph_format.space_before = Pt(4)
        p_opt.paragraph_format.space_after = Pt(4)
        r_ot = p_opt.add_run(f"{title}\n")
        r_ot.bold = True
        r_ot.font.size = Pt(10.5)
        r_ot.font.color.rgb = RGBColor(26, 115, 232)
        r_od = p_opt.add_run(details)
        r_od.font.size = Pt(9)
        r_od.font.color.rgb = RGBColor(60, 64, 67)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECTION 5: A2A SHARING ---
    h5 = doc.add_heading(level=1)
    r_h5 = h5.add_run("5. Agent-to-Agent (A2A) Integration: Sharing with Other Hero Systems")
    r_h5.font.color.rgb = RGBColor(15, 157, 88)
    r_h5.font.size = Pt(15)

    p_a2a_1 = doc.add_paragraph()
    p_a2a_1.add_run("A critical requirement for enterprise AI is that agents should not live in silos. The Hero VIDA Competitor Intelligence Agent natively supports Google's ")
    p_a2a_1.add_run("Agent-to-Agent (A2A) protocol").bold = True
    p_a2a_1.add_run(". This means other digital systems at Hero MotoCorp can consume this agent automatically as an autonomous intelligence specialist.")

    p_a2a_examples = doc.add_paragraph()
    p_a2a_examples.add_run("Real-World Hero MotoCorp A2A Use Cases:\n").bold = True
    p_a2a_examples.add_run("1. Hero Virtual Showroom Chatbot: When an online customer asks 'Why should I buy VIDA V2 Pro instead of Ather Rizta?', the customer chatbot calls the Competitor Intelligence Agent via A2A to retrieve the latest live prices and subsidies in the customer's city.\n")
    p_a2a_examples.add_run("2. Dealership WhatsApp Assistant: Dealer sales agents can send a WhatsApp message like 'Need comparison sheet for VIDA VX2 vs Chetak in Jaipur', and the WhatsApp bot delegates the query to this agent, returning a PDF/CSV directly into the chat.\n")
    p_a2a_examples.add_run("3. Enterprise Fleet & Commercial Sales Bot: High-volume B2B fleet buyers evaluating commercial EV scooters can run multi-city TCO benchmarks automatically.\n")

    # A2A Code Sample Callout Box
    a2a_box = doc.add_table(rows=1, cols=1)
    a2a_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    a_cell = a2a_box.cell(0, 0)
    a_cell.width = Inches(6.8)
    set_cell_background(a_cell, "F8F9FA")
    set_cell_margins(a_cell, top=120, bottom=120, left=160, right=160)
    ap = a_cell.paragraphs[0]
    ap.add_run("How a Hero IT Developer Imports This Agent (Only 4 Lines of Python):\n").bold = True
    ap_code = (
        "from google.adk.agents.remote_agent import RemoteAgent\n\n"
        "# Connect to the live Hero VIDA Agent via A2A URI:\n"
        "hero_intelligence = RemoteAgent(\n"
        "    name='hero_vida_intelligence',\n"
        "    address='agentengine://projects/<YOUR_HERO_GCP_PROJECT>/locations/<REGION>/reasoningEngines/<AGENT_ENGINE_ID>'\n"
        ")\n"
        "# Now your existing customer bots can delegate any competitor query to this specialist!"
    )
    ap_run = ap.add_run(ap_code)
    ap_run.font.name = "Courier New"
    ap_run.font.size = Pt(8.5)
    ap_run.font.color.rgb = RGBColor(33, 33, 33)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECTION 6: TECHNICAL HAND-OFF & RESOURCES ---
    h6 = doc.add_heading(level=1)
    r_h6 = h6.add_run("6. Technical Hand-Off & Developer Resources")
    r_h6.font.color.rgb = RGBColor(26, 115, 232)
    r_h6.font.size = Pt(15)

    p_tech_intro = doc.add_paragraph()
    p_tech_intro.add_run("When handing this solution to Hero MotoCorp's engineering or cloud infrastructure team, please provide them with the following assets and pointers:")

    resources = [
        ("Complete Technical Documentation (README.md)",
         "Contains full architectural flowcharts, sequence diagrams, detailed API contracts, parameter descriptions, and environment configuration instructions.\nFile: README.md in repository root."),

        ("1-Click Deployment Script (deploy.sh)",
         "Automated deployment script that prompts for Hero's GCP Project ID, region, and automatically provisions or updates the Agent Engine instance.\nFile: deploy.sh in repository root."),

        ("Comprehensive Automated Test Suite (tests/)",
         "Includes 14 automated unit and integration tests verifying real-time web crawlers, subsidy calculations, slang resolvers, and CSV Cloud Storage generation.\nCommand: PYTHONPATH=. ./venv/bin/pytest tests/ -v (All 14 tests passing)."),

        ("Code Repository",
         "Complete high-code Python repository built with Google ADK:\nRepository Package: Hero_competitor_analysis_agent (Customer Distribution Branch)"),

        ("Google Cloud Console Vertex AI Playground",
         "Once deployed into Hero's project, the interactive playground is immediately accessible to business users at:\nhttps://console.cloud.google.com/vertex-ai/agents/agent-engines?project=<YOUR_HERO_GCP_PROJECT>"),

        ("Google Cloud Storage Reports Bucket",
         "Generated comparison spreadsheets will automatically reside in Hero's private storage bucket:\ngs://<YOUR_HERO_GCP_PROJECT>-hero-vida-reports/reports/")
    ]

    for title, details in resources:
        p_res = doc.add_paragraph()
        p_res.paragraph_format.space_before = Pt(3)
        p_res.paragraph_format.space_after = Pt(3)
        r_rt = p_res.add_run(f"{title}\n")
        r_rt.bold = True
        r_rt.font.size = Pt(10)
        r_rt.font.color.rgb = RGBColor(211, 47, 47)
        r_rd = p_res.add_run(details)
        r_rd.font.size = Pt(9)
        r_rd.font.color.rgb = RGBColor(60, 64, 67)

    # Closing sign-off box
    doc.add_paragraph().paragraph_format.space_before = Pt(8)
    sign_off = doc.add_table(rows=1, cols=1)
    sign_off.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_cell = sign_off.cell(0, 0)
    s_cell.width = Inches(6.8)
    set_cell_background(s_cell, "1F2937")
    set_cell_margins(s_cell, top=120, bottom=120, left=160, right=160)
    sp = s_cell.paragraphs[0]
    sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s_run1 = sp.add_run("Hero MotoCorp & Google Cloud | Advanced Agentic AI\n")
    s_run1.bold = True
    s_run1.font.size = Pt(10)
    s_run1.font.color.rgb = RGBColor(255, 255, 255)
    s_run2 = sp.add_run("Delivering Autonomous Real-Time Market Intelligence for the Next Generation of EV Mobility")
    s_run2.font.size = Pt(8.5)
    s_run2.font.color.rgb = RGBColor(160, 174, 192)

    # Save document
    doc_path = os.path.join(BASE_DIR, "Hero_VIDA_Competitor_Intelligence_Executive_Brief.docx")
    doc.save(doc_path)
    print(f"Document successfully created at: {doc_path}")
    return doc_path

if __name__ == "__main__":
    build_executive_brief_document()

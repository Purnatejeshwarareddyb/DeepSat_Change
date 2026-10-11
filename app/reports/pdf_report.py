import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_report(path, before_img_path, after_img_path, mask_img_path, overlay_img_path,
                     change_stats, metrics, regions, model_info, dataset_info=None):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=20)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], spaceBefore=12)

    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    story = []

    story.append(Paragraph("DeepSat-Change Satellite Change Detection Report", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Project Information", heading_style))
    story.append(Paragraph("DeepSat-Change: Deep Learning-Based Satellite Image Change Detection and Analysis System", styles["Normal"]))
    story.append(Paragraph("Course: INT422 - Deep Learning", styles["Normal"]))

    story.append(Paragraph("Input Images", heading_style))
    img_row = []
    for label, p in [("Before", before_img_path), ("After", after_img_path),
                      ("Change Mask", mask_img_path), ("Overlay", overlay_img_path)]:
        if p and os.path.exists(p):
            img_row.append([Paragraph(label, styles["Normal"]), RLImage(p, width=60 * mm, height=60 * mm)])
    for label, img in img_row:
        story.append(label)
        story.append(img)
        story.append(Spacer(1, 6))

    story.append(Paragraph("Change Statistics", heading_style))
    change_table = Table([
        ["Change Percentage", f"{change_stats.get('change_percent', 0)}%"],
        ["Severity", change_stats.get("severity", "-")],
        ["Total Pixels", str(change_stats.get("total_pixels", 0))],
        ["Changed Pixels", str(change_stats.get("changed_pixels", 0))],
        ["Confidence", f"{change_stats.get('confidence', 0):.4f}"],
    ], colWidths=[70 * mm, 70 * mm])
    change_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
    ]))
    story.append(change_table)

    story.append(Paragraph("Model Performance Metrics", heading_style))
    metric_rows = [[k.upper(), f"{v:.4f}" if isinstance(v, float) else str(v)] for k, v in metrics.items()]
    if metric_rows:
        metrics_table = Table([["Metric", "Value"]] + metric_rows, colWidths=[70 * mm, 70 * mm])
        metrics_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(metrics_table)

    story.append(Paragraph("Detected Regions", heading_style))
    if regions:
        region_rows = [["ID", "Area", "Width", "Height", "Centroid", "Relative %"]]
        for r in regions[:20]:
            region_rows.append([
                r["region_id"], r["area"], r["width"], r["height"],
                f"{r['centroid'][0]}, {r['centroid'][1]}", f"{r['relative_area']}%"
            ])
        region_table = Table(region_rows, colWidths=[15 * mm, 25 * mm, 25 * mm, 25 * mm, 35 * mm, 25 * mm])
        region_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(region_table)
    else:
        story.append(Paragraph("No regions detected.", styles["Normal"]))

    story.append(Paragraph("Model Information", heading_style))
    for k, v in (model_info or {}).items():
        story.append(Paragraph(f"{k}: {v}", styles["Normal"]))

    if dataset_info:
        story.append(Paragraph("Training Configuration", heading_style))
        for k, v in dataset_info.items():
            story.append(Paragraph(f"{k}: {v}", styles["Normal"]))

    doc.build(story)
    return path

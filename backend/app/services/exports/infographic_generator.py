import os
import datetime
from typing import Dict, Any, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from app.config import settings

def generate_infographic_image(
    form_id: str,
    form_title: str,
    stats: Dict[str, Any],
    ai_insights: Dict[str, Any],
    file_format: str = "png"
) -> str:
    """
    Generates a presentation-ready visual infographic card image (PNG/JPG) in Peach & White theme
    with KPI cards, primary distribution charts, and key insight bullets.
    """
    ext = "jpg" if file_format.lower() in ["jpg", "jpeg"] else "png"
    filename = f"FormMind_Infographic_{form_id[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    file_path = os.path.join(settings.EXPORTS_DIR, filename)

    basic = stats.get("basic", {})
    overview = stats.get("overview_cards", {})
    numerical = stats.get("numerical", {})
    categorical = stats.get("categorical", {})

    # Create figure with high DPI (1200 x 1600 px) in Peach & White Theme
    fig = plt.figure(figsize=(12, 16), dpi=150, facecolor='#FFF9F5')
    
    # Grid layout: Title (top), KPIs (row 1), Chart 1 & Chart 2 (row 2), Key Findings (bottom)
    gs = fig.add_gridspec(6, 2, hspace=0.6, wspace=0.3, left=0.08, right=0.92, top=0.92, bottom=0.06)

    # 1. Title Banner
    fig.text(0.5, 0.95, "FORMMIND AI — SURVEY INTELLIGENCE", color='#EA580C', fontsize=14, weight='bold', ha='center')
    fig.text(0.5, 0.92, form_title[:45] + ("..." if len(form_title) > 45 else ""), color='#24110A', fontsize=22, weight='bold', ha='center')
    fig.text(0.5, 0.895, f"Verified Analytical Breakdown • {datetime.datetime.now().strftime('%B %d, %Y')}", color='#6B3B2B', fontsize=11, ha='center')

    # 2. KPI Cards (4 Cards)
    kpis = [
        ("Total Submissions", str(basic.get("total_responses", 0)), "#EA580C"),
        ("Completion Rate", str(basic.get("completion_rate", "100%")), "#047857"),
        ("Average Rating", str(overview.get("average_rating", "N/A")), "#D97706"),
        ("Questions Analyzed", str(basic.get("total_questions", 0)), "#7C3AED")
    ]

    for idx, (label, val, col) in enumerate(kpis):
        ax_kpi = fig.add_subplot(gs[0 if idx < 2 else 1, idx % 2])
        ax_kpi.set_facecolor('#FFFFFF')
        for spine in ax_kpi.spines.values():
            spine.set_color('#FAD5C0')
            spine.set_linewidth(1.5)
        ax_kpi.set_xticks([])
        ax_kpi.set_yticks([])
        ax_kpi.text(0.5, 0.65, val, color=col, fontsize=26, weight='bold', ha='center', va='center')
        ax_kpi.text(0.5, 0.25, label, color='#522A1A', fontsize=11, weight='bold', ha='center', va='center')

    # 3. Chart 1: First Numerical / Rating Distribution
    ax_chart1 = fig.add_subplot(gs[2:4, 0])
    ax_chart1.set_facecolor('#FFFFFF')
    for spine in ax_chart1.spines.values():
        spine.set_color('#FAD5C0')

    first_num = list(numerical.values())[0] if numerical else None
    num_dist = first_num.get("distribution", []) if first_num else []

    if first_num and num_dist:
        labels = [d["label"] for d in num_dist]
        counts = [d["count"] for d in num_dist]
        bars = ax_chart1.bar(labels, counts, color='#F97342', edgecolor='#EA580C', linewidth=1.2, width=0.6)
        ax_chart1.set_title(first_num.get("question_text", "Rating Distribution")[:28] + "...", color='#24110A', fontsize=11, weight='bold', pad=10)
        ax_chart1.tick_params(colors='#3B1F14', labelsize=9)
        ax_chart1.grid(axis='y', linestyle='--', alpha=0.4, color='#FAD5C0')
        for bar in bars:
            yval = bar.get_height()
            ax_chart1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.3, int(yval), ha='center', va='bottom', color='#24110A', fontsize=8, weight='bold')
    else:
        ax_chart1.text(0.5, 0.5, "No rating metrics available", color='#6B3B2B', ha='center', va='center')

    # 4. Chart 2: First Categorical Distribution (Donut Chart)
    ax_chart2 = fig.add_subplot(gs[2:4, 1])
    ax_chart2.set_facecolor('#FFFFFF')
    for spine in ax_chart2.spines.values():
        spine.set_color('#FAD5C0')
    
    first_cat = list(categorical.values())[0] if categorical else None
    cat_dist = first_cat.get("distribution", [])[:5] if first_cat else []

    if first_cat and cat_dist:
        cat_labels = [d["label"][:15] + ("..." if len(d["label"]) > 15 else "") for d in cat_dist]
        cat_counts = [d["count"] for d in cat_dist]
        colors_donut = ['#F97342', '#34D399', '#FBBF24', '#F472B6', '#A78BFA']
        wedges, texts, autotexts = ax_chart2.pie(
            cat_counts,
            labels=cat_labels,
            autopct='%1.0f%%',
            pctdistance=0.75,
            colors=colors_donut[:len(cat_counts)],
            wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2.5),
            textprops=dict(color='#24110A', fontsize=8, weight='bold')
        )
        for autotext in autotexts:
            autotext.set_color('#FFFFFF')
            autotext.set_weight('bold')
        ax_chart2.set_title(first_cat.get("question_text", "Category Distribution")[:28] + "...", color='#24110A', fontsize=11, weight='bold', pad=10)
    else:
        ax_chart2.text(0.5, 0.5, "No categorical data available", color='#6B3B2B', ha='center', va='center')

    # 5. Bottom Insights Box
    ax_bottom = fig.add_subplot(gs[4:6, :])
    ax_bottom.set_facecolor('#FFFFFF')
    for spine in ax_bottom.spines.values():
        spine.set_color('#FAD5C0')
        spine.set_linewidth(1.5)
    ax_bottom.set_xticks([])
    ax_bottom.set_yticks([])

    ax_bottom.text(0.04, 0.88, "KEY STRATEGIC INSIGHTS & TAKEAWAYS", color='#EA580C', fontsize=12, weight='bold')

    insights_list = ai_insights.get("facts", [])[:3] + ai_insights.get("interpretations", [])[:2]
    y_pos = 0.72
    for item in insights_list:
        clean_item = item[:95] + ("..." if len(item) > 95 else "")
        ax_bottom.text(0.04, y_pos, f"• {clean_item}", color='#24110A', fontsize=9.5, weight='medium')
        y_pos -= 0.15

    plt.savefig(file_path, format=ext, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

    return file_path

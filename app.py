import json

import streamlit as st

from classifier import classify_po


st.set_page_config(page_title="PO Category Classifier", layout="wide")


def _hex_to_rgb(hex_color, fallback):
    if not isinstance(hex_color, str):
        return fallback
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        return fallback
    try:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return fallback


with st.sidebar:
    st.markdown("## PO Classifier")
    st.caption("Professional L1-L2-L3 categorization for procurement teams.")

    st.markdown("### Appearance")
    primary_color = st.color_picker("Primary (blue)", "#60a5fa")
    secondary_color = st.color_picker("Secondary (purple)", "#a78bfa")
    glow_intensity = st.slider("Glow intensity", 0.0, 0.4, 0.18, 0.02)
    card_style = st.selectbox("Card style", ["Glass", "Solid"])
    compact_mode = st.toggle("Compact mode", value=False)
    enable_motion = st.toggle("Enable motion", value=True)
    enable_shadows = st.toggle("Card shadows", value=True)

    st.markdown("### Layout")
    layout_mode = st.selectbox("Layout", ["Split", "Stacked"])
    results_layout = st.selectbox("Results view", ["Tabs", "Stacked"])

    st.markdown("### Display")
    show_hero = st.toggle("Show hero header", value=True)
    show_guidance = st.toggle("Show guidance", value=True)
    show_tips = st.toggle("Show tips", value=True)
    show_metrics = st.toggle("Show L1/L2/L3 metrics", value=True)
    show_json_payload = st.toggle("Show full JSON payload", value=True)
    show_raw_tab = st.toggle("Show raw response", value=True)

    if show_tips:
        st.markdown("### Workflow")
        st.markdown("1. Paste a PO description.")
        st.markdown("2. Add a supplier (optional).")
        st.markdown("3. Run classification.")
        st.markdown("### Tips")
        st.markdown("- Include quantity, brand, and model number.")
        st.markdown("- Add units and size details.")
        st.markdown("- Supplier helps disambiguate similar items.")


primary_rgb = _hex_to_rgb(primary_color, fallback=(96, 165, 250))
secondary_rgb = _hex_to_rgb(secondary_color, fallback=(167, 139, 250))

surface = "rgba(255,255,255,0.92)" if card_style == "Glass" else "#ffffff"
border = "rgba(148,163,184,0.35)" if card_style == "Glass" else "#e2e8f0"

card_shadow = "0 25px 50px rgba(15, 23, 42, 0.08)" if enable_shadows else "none"
form_shadow = "0 18px 35px rgba(15, 23, 42, 0.07)" if enable_shadows else "none"
tabs_shadow = "0 18px 35px rgba(15, 23, 42, 0.07)" if enable_shadows else "none"

hero_animation = "fadeInUp 0.7s ease both" if enable_motion else "none"
form_animation = "fadeInUp 0.8s ease both" if enable_motion else "none"
tabs_animation = "fadeInUp 0.9s ease both" if enable_motion else "none"

container_pad_top = "2rem" if compact_mode else "2.5rem"
hero_pad = "1.6rem 2rem" if compact_mode else "2rem 2.4rem"
hero_title = "2.1rem" if compact_mode else "2.4rem"
card_pad = "1.2rem" if compact_mode else "1.6rem"
text_area_height = 130 if compact_mode else 150

PRO_STYLE = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {{
  --ink: #0f172a;
  --muted: #475569;
  --surface: {surface};
  --border: {border};
  --primary: {primary_color};
  --secondary: {secondary_color};
  --accent: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
  --card-pad: {card_pad};
  --hero-pad: {hero_pad};
  --hero-title: {hero_title};
}}

html, body, [class*="css"] {{
  font-family: "Manrope", sans-serif;
}}

div[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(circle at 15% 20%, rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, {glow_intensity}), transparent 45%),
    radial-gradient(circle at 85% 10%, rgba({secondary_rgb[0]}, {secondary_rgb[1]}, {secondary_rgb[2]}, {glow_intensity}), transparent 40%),
    linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f8fafc 100%);
}}

div[data-testid="stHeader"] {{
  background: transparent;
}}

div.block-container {{
  padding-top: {container_pad_top};
  max-width: 1200px;
}}

.hero {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: var(--hero-pad);
  box-shadow: {card_shadow};
  margin-bottom: 1.6rem;
  animation: {hero_animation};
}}

.hero h1 {{
  font-family: "Space Grotesk", sans-serif;
  font-size: var(--hero-title);
  color: var(--ink);
  margin: 0;
}}

.hero p {{
  margin: 0.5rem 0 0;
  color: var(--muted);
  font-size: 1.02rem;
}}

.section-title {{
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #64748b;
  margin: 0 0 0.8rem 0;
}}

div[data-testid="stForm"] {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: var(--card-pad);
  box-shadow: {form_shadow};
  animation: {form_animation};
}}

div[data-testid="stForm"] > div {{
  gap: 1rem;
}}

div[data-testid="stTabs"] {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 0.8rem 1.2rem 1.4rem;
  box-shadow: {tabs_shadow};
  animation: {tabs_animation};
}}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {{
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.35);
  padding: 0.75rem 0.85rem;
}}

div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input:focus {{
  border-color: rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.7);
  box-shadow: 0 0 0 2px rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.12);
}}

div.stButton > button {{
  background: var(--accent);
  color: #f8fafc;
  border-radius: 12px;
  padding: 0.65rem 1.5rem;
  font-weight: 600;
  border: none;
  width: 100%;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.18);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}}

div.stButton > button:hover {{
  transform: translateY(-1px);
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.22);
}}

div[data-testid="stMetric"] {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.8rem;
  border-radius: 12px;
}}

section[data-testid="stSidebar"] {{
  background: linear-gradient(
    180deg,
    rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.18),
    rgba({secondary_rgb[0]}, {secondary_rgb[1]}, {secondary_rgb[2]}, 0.22)
  );
  color: var(--ink);
  border-right: 1px solid var(--border);
}}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] li {{
  color: var(--ink);
}}

section[data-testid="stSidebar"] a {{
  color: #1d4ed8 !important;
}}

@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
</style>
"""

st.markdown(PRO_STYLE, unsafe_allow_html=True)

if show_hero:
    st.markdown(
        """
        <div class="hero">
          <h1>PO Category Classifier</h1>
          <p>Fast, consistent L1-L2-L3 categorization for procurement line items.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _find_ci_key(data, target):
    for key in data.keys():
        if key.lower() == target.lower():
            return key
    return None


def _format_metric(value):
    if value is None:
        return "N/A"
    if isinstance(value, (int, float, str)):
        return value
    return json.dumps(value, ensure_ascii=True)


def _display_levels(data):
    l1_key = _find_ci_key(data, "l1")
    l2_key = _find_ci_key(data, "l2")
    l3_key = _find_ci_key(data, "l3")

    if not any([l1_key, l2_key, l3_key]):
        return

    cols = st.columns(3)
    cols[0].metric("L1", _format_metric(data.get(l1_key)) if l1_key else "N/A")
    cols[1].metric("L2", _format_metric(data.get(l2_key)) if l2_key else "N/A")
    cols[2].metric("L3", _format_metric(data.get(l3_key)) if l3_key else "N/A")


def _render_structured(parsed):
    if isinstance(parsed, dict):
        if show_metrics:
            _display_levels(parsed)
        if show_json_payload:
            st.markdown("**Full payload**")
            st.json(parsed)
        else:
            st.caption("Full JSON payload hidden by settings.")
    elif parsed is not None:
        st.json(parsed)
    else:
        st.warning("Model response was not valid JSON.")


if "result" not in st.session_state:
    st.session_state.result = None


if layout_mode == "Split":
    left_col, right_col = st.columns((1.05, 0.95), gap="large")
else:
    left_col = st.container()
    right_col = st.container()

with left_col:
    st.markdown('<div class="section-title">Input</div>', unsafe_allow_html=True)
    with st.form("classification_form", clear_on_submit=False):
        po_description = st.text_area("PO description", height=text_area_height)
        st.caption("Example: 12x Dell UltraSharp U2723QE monitors, 27-inch, USB-C")
        supplier = st.text_input("Supplier", help="Optional, used to improve precision.")
        submitted = st.form_submit_button("Classify PO")

    if submitted:
        if not po_description.strip():
            st.warning("Please enter a PO description.")
        else:
            with st.spinner("Classifying..."):
                raw_result = classify_po(po_description, supplier)

            parsed_result = None
            try:
                parsed_result = json.loads(raw_result)
            except Exception:
                parsed_result = None

            st.session_state.result = {
                "raw": raw_result,
                "parsed": parsed_result,
            }

    if show_guidance:
        st.markdown('<div class="section-title">Guidance</div>', unsafe_allow_html=True)
        st.markdown("- Keep descriptions concise and specific.")
        st.markdown("- Add brand or model when possible.")
        st.markdown("- Use supplier for better category matching.")


with right_col:
    st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)
    if st.button("Clear results"):
        st.session_state.result = None

    result = st.session_state.result
    if not result:
        st.info("Run a classification to see results here.")
    else:
        if results_layout == "Tabs" and show_raw_tab:
            tabs = st.tabs(["Structured", "Raw"])
            with tabs[0]:
                _render_structured(result.get("parsed"))
            with tabs[1]:
                st.code(result.get("raw", ""), language="json")
        elif results_layout == "Tabs":
            _render_structured(result.get("parsed"))
        else:
            st.markdown("**Structured**")
            _render_structured(result.get("parsed"))
            if show_raw_tab:
                with st.expander("Raw response", expanded=False):
                    st.code(result.get("raw", ""), language="json")

import json

import streamlit as st

from classifier import classify_po


st.set_page_config(page_title="PO Category Classifier", layout="wide")

PRO_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --ink: #0f172a;
  --muted: #475569;
  --surface: rgba(255,255,255,0.92);
  --border: rgba(148,163,184,0.35);
  --accent: #0f172a;
}

html, body, [class*="css"] {
  font-family: "Manrope", sans-serif;
}

div[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 15% 20%, rgba(14,165,233,0.14), transparent 45%),
    radial-gradient(circle at 85% 10%, rgba(99,102,241,0.12), transparent 40%),
    linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f8fafc 100%);
}

div[data-testid="stHeader"] {
  background: transparent;
}

div.block-container {
  padding-top: 2.5rem;
  max-width: 1200px;
}

.hero {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 2rem 2.4rem;
  box-shadow: 0 25px 50px rgba(15, 23, 42, 0.08);
  margin-bottom: 1.6rem;
  animation: fadeInUp 0.7s ease both;
}

.hero h1 {
  font-family: "Space Grotesk", sans-serif;
  font-size: 2.4rem;
  color: var(--ink);
  margin: 0;
}

.hero p {
  margin: 0.5rem 0 0;
  color: var(--muted);
  font-size: 1.05rem;
}

.section-title {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #64748b;
  margin: 0 0 0.8rem 0;
}

div[data-testid="stForm"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.6rem;
  box-shadow: 0 18px 35px rgba(15, 23, 42, 0.07);
  animation: fadeInUp 0.8s ease both;
}

div[data-testid="stForm"] > div {
  gap: 1rem;
}

div[data-testid="stTabs"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 0.8rem 1.2rem 1.4rem;
  box-shadow: 0 18px 35px rgba(15, 23, 42, 0.07);
  animation: fadeInUp 0.9s ease both;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #cbd5f5;
  padding: 0.75rem 0.85rem;
}

div.stButton > button {
  background: var(--accent);
  color: #f8fafc;
  border-radius: 12px;
  padding: 0.65rem 1.5rem;
  font-weight: 600;
  border: none;
  width: 100%;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.18);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

div.stButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.22);
}

div[data-testid="stMetric"] {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.8rem;
  border-radius: 12px;
}

section[data-testid="stSidebar"] {
  background: rgba(15, 23, 42, 0.93);
  color: #e2e8f0;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] li {
  color: #e2e8f0;
}

section[data-testid="stSidebar"] a {
  color: #bae6fd !important;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
"""

st.markdown(PRO_STYLE, unsafe_allow_html=True)

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


with st.sidebar:
    st.markdown("### Workflow")
    st.markdown("1. Paste a PO description.")
    st.markdown("2. Add a supplier (optional).")
    st.markdown("3. Run classification.")
    st.markdown("### Tips")
    st.markdown("- Include quantity, brand, and model number.")
    st.markdown("- Add units and size details.")
    st.markdown("- Supplier helps disambiguate similar items.")


if "result" not in st.session_state:
    st.session_state.result = None


left_col, right_col = st.columns((1.05, 0.95), gap="large")

with left_col:
    st.markdown('<div class="section-title">Input</div>', unsafe_allow_html=True)
    with st.form("classification_form", clear_on_submit=False):
        po_description = st.text_area("PO description", height=150)
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
        tabs = st.tabs(["Structured", "Raw"])
        with tabs[0]:
            parsed = result.get("parsed")
            if isinstance(parsed, dict):
                _display_levels(parsed)
                st.markdown("**Full payload**")
                st.json(parsed)
            elif parsed is not None:
                st.json(parsed)
            else:
                st.warning("Model response was not valid JSON.")

        with tabs[1]:
            st.code(result.get("raw", ""), language="json")

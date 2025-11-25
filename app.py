import streamlit as st
import re
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="MFIPPA Compliance Checker",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .compliant {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .violation {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# MFIPPA Compliance Rules
COMPLIANCE_RULES = {
    "personal_information": {
        "name": "Personal Information Detection",
        "section": "Section 2(1)",
        "keywords": [
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
            r'\b\d{3}-\d{2}-\d{4}\b',  # SIN-like patterns
            r'\b\d{9}\b',  # 9-digit numbers (potential IDs)
            r'\bdate of birth\b',
            r'\bDOB\b',
            r'\bmedical\b',
            r'\bhealth\b',
            r'\bcriminal\b',
            r'\bemployment history\b',
            r'\bfinancial\b',
            r'\bincome\b',
            r'\brace\b',
            r'\bethnic origin\b',
            r'\bsexual orientation\b',
            r'\breligion\b'
        ],
        "description": "Personal information includes recorded information about an identifiable individual"
    },
    "collection_authority": {
        "name": "Collection Authority & Notice",
        "section": "Section 28, 29",
        "keywords": [
            r'\bcollected\b',
            r'\bcollecting\b',
            r'\bauthorized by\b',
            r'\blegal authority\b',
            r'\bstatute\b',
            r'\blaw enforcement\b',
            r'\bnotice\b',
            r'\binformed\b'
        ],
        "description": "Collection must be authorized and individuals must be notified"
    },
    "use_limitation": {
        "name": "Use Limitation",
        "section": "Section 31",
        "keywords": [
            r'\buse\b',
            r'\bused for\b',
            r'\bpurpose\b',
            r'\bconsent\b',
            r'\bagreed\b',
            r'\bauthorization\b'
        ],
        "description": "Personal information must be used only for the purpose collected or with consent"
    },
    "disclosure": {
        "name": "Disclosure Rules",
        "section": "Section 32",
        "keywords": [
            r'\bdisclose\b',
            r'\bdisclosed\b',
            r'\bshare\b',
            r'\bshared\b',
            r'\btransfer\b',
            r'\bprovide to\b',
            r'\bsent to\b',
            r'\bthird party\b'
        ],
        "description": "Disclosure of personal information is restricted under Section 32"
    },
    "retention": {
        "name": "Retention Requirements",
        "section": "Section 30",
        "keywords": [
            r'\bretain\b',
            r'\bretention\b',
            r'\bdelete\b',
            r'\bdestroy\b',
            r'\bdispose\b',
            r'\bremove\b'
        ],
        "description": "Personal information must be retained for at least one year after use"
    },
    "access_request": {
        "name": "Access Request Procedures",
        "section": "Section 17, 19",
        "keywords": [
            r'\baccess request\b',
            r'\bFOI request\b',
            r'\brequest for information\b',
            r'\b30 days\b',
            r'\bthirty days\b'
        ],
        "description": "Access requests must be processed within 30 days"
    },
    "exemptions": {
        "name": "Exemptions",
        "section": "Sections 6-15",
        "keywords": [
            r'\blaw enforcement\b',
            r'\bsolicitor-client\b',
            r'\bprivilege\b',
            r'\bconfidential\b',
            r'\btrade secret\b',
            r'\bcommercial\b'
        ],
        "description": "Certain exemptions apply to disclosure"
    }
}

def analyze_text(text):
    """Analyze text for MFIPPA compliance issues"""
    results = []
    
    for rule_id, rule in COMPLIANCE_RULES.items():
        matches = []
        for pattern in rule["keywords"]:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                matches.extend(found)
        
        if matches:
            results.append({
                "rule": rule["name"],
                "section": rule["section"],
                "description": rule["description"],
                "matches": list(set(matches[:5])),  # Unique matches, max 5
                "status": "warning" if rule_id in ["personal_information", "disclosure"] else "info"
            })
    
    return results

def generate_report(results, text):
    """Generate compliance report"""
    st.markdown("---")
    st.markdown("## 📊 Compliance Analysis Report")
    st.markdown(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"**Document Length:** {len(text)} characters")
    
    if not results:
        st.success("✅ **No immediate compliance concerns detected**")
        st.info("Note: This is an automated check. Manual review by FOI/Privacy Coordinator is recommended.")
        return
    
    # Summary
    st.markdown("### Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Issues Found", len(results))
    
    with col2:
        warnings = sum(1 for r in results if r["status"] == "warning")
        st.metric("Warnings", warnings)
    
    with col3:
        info = sum(1 for r in results if r["status"] == "info")
        st.metric("Informational", info)
    
    # Detailed findings
    st.markdown("### Detailed Findings")
    
    for i, result in enumerate(results, 1):
        if result["status"] == "warning":
            st.markdown(f'<div class="warning">', unsafe_allow_html=True)
            st.markdown(f"**⚠️ {i}. {result['rule']}**")
        else:
            st.markdown(f'<div class="violation">', unsafe_allow_html=True)
            st.markdown(f"**ℹ️ {i}. {result['rule']}**")
        
        st.markdown(f"**MFIPPA Reference:** {result['section']}")
        st.markdown(f"**Description:** {result['description']}")
        
        if result["matches"]:
            st.markdown("**Detected in document:**")
            for match in result["matches"]:
                st.markdown(f"- `{match}`")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("---")
    st.markdown("### 📋 Recommendations")
    
    has_pi = any(r["rule"] == "Personal Information Detection" for r in results)
    has_disclosure = any(r["rule"] == "Disclosure Rules" for r in results)
    
    if has_pi:
        st.warning("""
        **Personal Information Detected:**
        - Verify collection authority (Section 28)
        - Ensure proper notice was provided (Section 29)
        - Confirm retention requirements are met (Section 30)
        - Review use is limited to authorized purposes (Section 31)
        """)
    
    if has_disclosure:
        st.error("""
        **Disclosure Language Detected:**
        - Verify disclosure is permitted under Section 32
        - Confirm consent was obtained if required
        - Check if exemptions apply
        - Document the legal basis for disclosure
        """)
    
    st.info("""
    **General Recommendations:**
    - Have your FOI/Privacy Coordinator review this document
    - Document the legal authority for any personal information collection
    - Ensure all disclosures comply with Section 32 requirements
    - Maintain records for the required retention period
    """)

# Main App
st.markdown('<div class="main-header">🔒 MFIPPA Compliance Checker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Municipal Freedom of Information and Protection of Privacy Act</div>', unsafe_allow_html=True)

st.markdown("""
This tool helps identify potential compliance issues with MFIPPA (R.S.O. 1990, c. M.56).
Upload a document or paste text to check for:
- Personal information
- Collection and use requirements
- Disclosure restrictions
- Retention obligations
- Access request procedures

**⚠️ Disclaimer:** This is an automated screening tool. All findings should be reviewed by your FOI/Privacy Coordinator or legal counsel.
""")

# Input options
tab1, tab2 = st.tabs(["📝 Paste Text", "📄 Upload File"])

with tab1:
    text_input = st.text_area(
        "Paste your document text here:",
        height=300,
        placeholder="Enter email content, form text, policy draft, etc..."
    )
    
    if st.button("🔍 Analyze Text", type="primary"):
        if text_input:
            with st.spinner("Analyzing for MFIPPA compliance..."):
                results = analyze_text(text_input)
                generate_report(results, text_input)
        else:
            st.warning("Please enter some text to analyze.")

with tab2:
    uploaded_file = st.file_uploader(
        "Upload a document (TXT, PDF, DOCX)",
        type=["txt", "pdf", "docx"]
    )
    
    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        try:
            if file_type == "txt":
                text = uploaded_file.read().decode('utf-8')
            elif file_type == "pdf":
                st.info("PDF support: Install PyPDF2 library")
                text = "PDF parsing not yet implemented. Please use text input."
            elif file_type == "docx":
                st.info("DOCX support: Install python-docx library")
                text = "DOCX parsing not yet implemented. Please use text input."
            else:
                text = ""
            
            if text and st.button("🔍 Analyze File", type="primary"):
                with st.spinner("Analyzing for MFIPPA compliance..."):
                    results = analyze_text(text)
                    generate_report(results, text)
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
Built with Streamlit | Based on MFIPPA R.S.O. 1990, c. M.56 (Current to November 20, 2025)<br>
For official guidance, consult the Information and Privacy Commissioner of Ontario
</div>
""", unsafe_allow_html=True)
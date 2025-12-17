import streamlit as st
import pandas as pd
import random
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Provider Validation Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Enterprise Look ---
st.markdown("""
<style>
    /* General Body and Font */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
    }

    /* Main Headers */
    h1, h2, h3 {
        color: #0E2A47; /* Dark Blue */
    }

    /* KPI Metrics */
    .stMetric {
        background-color: #F8F9FA;
        border: 1px solid #E3E6E8;
        border-radius: 0.5rem;
        padding: 10px;
    }

    /* Table Header */
    .table-header {
        display: grid;
        grid-template-columns: 2fr 1.5fr 1fr 2fr;
        font-weight: bold;
        padding: 10px;
        background-color: #F8F9FA;
        border-bottom: 2px solid #E3E6E8;
        align-items: center;
        color: #0E2A47; /* Dark Blue for header text */
    }

    /* Table Row */
    .table-row {
        display: grid;
        grid-template-columns: 2fr 1.5fr 1fr 1.5fr 1.5fr 0.5fr;
        padding: 12px 10px;
        border-bottom: 1px solid #E3E6E8;
        align-items: center;
        transition: background-color 0.2s;
    }
    .table-row:hover {
        background-color: #F0F4F8;
    }
    
    /* Status Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.8em;
        text-align: center;
        display: inline-block;
    }
    .badge-High { background-color: #F8D7DA; color: #721C24; }
    .badge-Medium { background-color: #FFF3CD; color: #856404; }
    .badge-Low { background-color: #D4EDDA; color: #155724; }

    /* Confidence Bar */
    .confidence-bar-container {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #F44336, #FFC107, #4CAF50);
    }
    
    /* Expander Details */
    .stExpander {
        border: none;
    }
    .stExpander > div[data-testid="stExpanderDetails"] {
        background-color: #FAFAFA;
        padding: 1rem;
        border-top: 1px solid #E3E6E8;
    }
</style>
""", unsafe_allow_html=True)


# --- Backend Logic (from main.py) ---

source_icons = {
    "NPI Registry": "🏛️",
    "Google Maps": "🗺️",
    "Provider Website": "🌐",
    "Scanned PDF": "📄",
    "Payer Records": "📄",
}

def convert_to_csv(provider_data):
    # Extract the 'after' data from each provider
    after_data = [p['details']['after'] for p in provider_data]
    df = pd.DataFrame(after_data)
    return df.to_csv(index=False).encode('utf-8')

def simulate_ai_validation(df):
    validated_providers = []
    sources = list(source_icons.keys())
    
    yield "high_level", "🤖 Agent Initializing..."
    time.sleep(1)
    
    yield "high_level", "🔍 Validating provider data across sources..."
    time.sleep(1)

    detailed_logs = []

    for i, row in df.iterrows():
        provider_name = row.get("provider_name", f"Provider {i+1}")
        detailed_logs.append(f"🕵️‍♀️ **Validator Agent:** Analyzing {provider_name}...")
        yield "detailed", "\n\n".join(detailed_logs)
        
        original_data = row.to_dict()
        validated_data = {}
        score_explanation = []
        confidence_score = 100
        invalid_count = 0
        updated_count = 0
        
        # Simulate Specialty and Primary Issue for UI
        specialties = ["Cardiology", "Pediatrics", "Orthopedics", "Neurology", "Oncology"]
        issues = ["Address Mismatch", "NPI Invalid", "License Expired", "Phone Disconnected", "Website Down"]
        
        for col, value in original_data.items():
            rand = random.random()
            source = random.choice(sources)
            
            if rand < 0.7:
                status = "verified"
                score_explanation.append(f"✓ '{col}' successfully verified via {source}.")
            elif rand < 0.9:
                status = "updated"
                value = f"{value} (updated)"
                score_explanation.append(f"~ '{col}' was updated based on {source}.")
                confidence_score -= 5
                updated_count += 1
            else:
                status = "invalid"
                value = "N/A"
                error_reason = f"✗ '{col}' is invalid or missing"
                score_explanation.append(f"{error_reason} (last checked: {source}).")
                confidence_score -= 10
                invalid_count += 1
            validated_data[col] = {"value": value, "status": status, "source": source}
        
        detailed_logs.append(f"✨ **Enrichment Agent:** Finding additional data for {provider_name}...")
        yield "detailed", "\n\n".join(detailed_logs)
        time.sleep(0.05)

        risk_level = "Low"
        primary_issue = "None"
        if invalid_count > 1 or confidence_score < 80:
            risk_level = "High"
            primary_issue = random.choice(issues)
        elif invalid_count > 0 or updated_count > 2:
            risk_level = "Medium"
            primary_issue = random.choice(issues)

        provider_data = {
            "id": f"prov_{i+1}",
            "provider_name": provider_name,
            "specialty": random.choice(specialties),
            "validation_status": risk_level,
            "confidence_score": max(0, confidence_score) / 100,
            "primary_issue": primary_issue,
            "details": {
                "before": original_data,
                "after": {k: v['value'] for k, v in validated_data.items()},
                "sources_used": random.sample(sources, k=random.randint(2,4)),
                "validation_reasoning": "\n".join(score_explanation)
            }
        }
        validated_providers.append(provider_data)
        detailed_logs.append(f"✅ **QA Agent:** Quality check passed for {provider_name} with score {provider_data['confidence_score']:.0%}.")
        yield "detailed", "\n\n".join(detailed_logs)
        time.sleep(0.05)

    phone_corrected_count = 0
    address_updated_count = 0
    missing_filled_count = 0
    other_updates = 0

    for provider in validated_providers:
        before = provider['details']['before']
        after = provider['details']['after']
        for col in before:
            if str(before[col]) != str(after[col]):
                if pd.isna(before[col]) or str(before[col]).strip() == "N/A" or str(before[col]).strip() == "":
                    missing_filled_count += 1
                elif "phone" in col.lower():
                    phone_corrected_count += 1
                elif "address" in col.lower():
                    address_updated_count += 1
                else:
                    other_updates += 1
    
    st.session_state.quality_metrics = {
        "phone_corrected": phone_corrected_count,
        "address_updated": address_updated_count,
        "missing_filled": missing_filled_count,
        "other_updates": other_updates
    }

    yield "high_level", "📈 Aggregating results and generating dashboard..."
    time.sleep(1)
    
    st.session_state.validated_data = validated_providers
    
    yield "high_level", "🎉 Process Complete!"


# --- UI Rendering ---

st.title("🏥 Agentic AI Provider Data Validation")
st.markdown("An operations console for healthcare payers to instantly review AI-driven provider data validation outcomes.")

uploaded_file = st.file_uploader("Upload your provider directory (CSV)", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("Provider data uploaded successfully! Click Start to begin.")
    
    if st.button("Start Validation", type="primary"):
        # --- Live Agent Activity Log ---
        st.header("🤖 Live Agent Activity Log")
        high_level_log_placeholder = st.empty()
        high_level_messages = []
        
        with st.expander("View Detailed Logs"):
            detailed_log_placeholder = st.empty()

        for level, message in simulate_ai_validation(data):
            if level == "high_level":
                high_level_messages.append(message)
                high_level_log_placeholder.markdown("\n\n".join(f"- {m}" for m in high_level_messages))
            else: # detailed
                detailed_log_placeholder.markdown(message)
        
        st.success("Validation process complete!")
        st.markdown("---")

        provider_data = st.session_state.get('validated_data', [])

        # --- 1. Executive Summary KPI Panel ---
        st.header("Executive Summary")
        total_processed = len(provider_data)
        flagged_for_review = len([p for p in provider_data if p["validation_status"] == "High"])
        avg_confidence = sum(p['confidence_score'] for p in provider_data) / total_processed if total_processed else 0
        effort_saved = total_processed * 5 # Assuming 5 mins saved per provider

        cols = st.columns(4)
        cols[0].metric("Total Providers Processed", f"{total_processed}")
        cols[1].metric("Providers Flagged for Review", f"{flagged_for_review}")
        cols[2].metric("Average Confidence Score", f"{avg_confidence:.1%}")
        cols[3].metric("Estimated Manual Effort Saved", f"~{effort_saved} mins")

        st.markdown("---")

        # --- Download Buttons ---
        st.header("⬇️ Download Results")
        download_cols = st.columns(2)

        with download_cols[0]:
            csv_data = convert_to_csv(provider_data)
            st.download_button(
                label="Download Updated Directory (CSV)",
                data=csv_data,
                file_name="updated_provider_directory.csv",
                mime="text/csv",
                use_container_width=True
            )

        with download_cols[1]:
            pdf_mock_data = b"This is a mock PDF report."
            st.download_button(
                label="Download Validation Report (PDF)",
                data=pdf_mock_data,
                file_name="validation_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.markdown("---")

        # --- Data Quality Improvement Summary ---
        st.header("📊 Data Quality Improvement Summary")
        quality_metrics = st.session_state.get("quality_metrics", {})
        
        q_cols = st.columns(3)
        q_cols[0].metric("Phone Numbers Corrected", quality_metrics.get("phone_corrected", 0))
        q_cols[1].metric("Addresses Updated", quality_metrics.get("address_updated", 0))
        q_cols[2].metric("Missing Fields Filled", quality_metrics.get("missing_filled", 0))


        st.markdown("---")

        # --- New Section: Providers Requiring Immediate Attention ---
        st.header("🔥 Providers Requiring Immediate Attention")

        attention_providers = [p for p in provider_data if p['validation_status'] in ['High', 'Medium']]
        risk_sort_order_attention = {"High": 0, "Medium": 1}
        sorted_attention_providers = sorted(
            attention_providers,
            key=lambda p: (risk_sort_order_attention[p['validation_status']], p['confidence_score'])
        )

        if not sorted_attention_providers:
            st.info("No providers require immediate attention at this time.")
        else:
            for provider in sorted_attention_providers:
                st.write(f"- **{provider['provider_name']}** (Risk: {provider['validation_status']}, Confidence: {provider['confidence_score']:.1%})")

        st.markdown("---")

        # --- 2. Smart, Compact Table ---
        st.header("Provider Validation Results")
        st.markdown(
            """
            <div class="table-header">
                <div>Provider Name</div>
                <div>Specialty</div>
                <div>Risk Level</div>
                <div>Confidence Score</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        risk_order = {"High": 0, "Medium": 1, "Low": 2}
        sorted_data = sorted(provider_data, key=lambda p: risk_order[p['validation_status']])

        def get_status_badge(status):
            return f'<span class="badge badge-{status}">{status}</span>'

        for provider in sorted_data:
            # Use st.columns to create the row
            cols = st.columns((2, 1.5, 1, 2))
            cols[0].markdown(f"**{provider['provider_name']}**")
            cols[1].markdown(provider['specialty'])
            cols[2].markdown(get_status_badge(provider['validation_status']), unsafe_allow_html=True)
            
            with cols[3]:
                st.progress(provider['confidence_score'])
                st.write(f"{provider['confidence_score']:.1%}")
                if provider['validation_status'] in ["High", "Medium"]:
                    st.caption(f"Reason: {provider['primary_issue']}")

            # The expander is now for details only, placed below the row
            with st.expander("View Details"):
                st.markdown("#### Deep Dive: Validation Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("##### Data Comparison (Before vs. After)")
                    
                    before_df = pd.DataFrame.from_dict(provider['details']['before'], orient='index', columns=['Before'])
                    after_df = pd.DataFrame.from_dict(provider['details']['after'], orient='index', columns=['AI Validated (After)'])
                    comparison_df = before_df.join(after_df, how='outer').fillna('N/A')
                    
                    st.table(comparison_df)
                    
                with col2:
                    st.markdown("##### Validation Reasoning")
                    st.info(provider['details']['validation_reasoning'])
                    
                    st.markdown("##### Data Sources Used")
                    source_tags = " ".join([f"`{s}`" for s in provider['details']['sources_used']])
                    st.markdown(source_tags)

                if provider['validation_status'] in ["High", "Medium"]:
                    st.markdown("##### Manual Review Actions")
                    action_cols = st.columns(3)
                    with action_cols[0]:
                        st.button("🟢 Mark as Verified", key=f"verify_{provider['id']}", use_container_width=True)
                    with action_cols[1]:
                        st.button("🔴 Send for Manual Review", key=f"review_{provider['id']}", use_container_width=True)
                    with action_cols[2]:
                        st.button("📧 Send Verification Email", key=f"email_{provider['id']}", use_container_width=True)
            st.markdown("---") # Add a separator between providers

st.sidebar.header("✅ Redesign Benefits")
st.sidebar.markdown(
    """
    **1. Simplified Agent Log:**
    The main view now shows only high-level status updates (Initializing, Validating, etc.), making the process easy to follow. Detailed, per-provider logs are available in an optional expander for power users.
    
    **2. Clean, Professional UI:**
    Provider results are displayed in a clean, table-like format. Raw HTML is gone, replaced by styled badges and progress bars for at-a-glance insights.

    **3. Improved Scalability:**
    The UI remains clean and responsive, even with thousands of providers, as only high-level logs are shown by default and the results table is clear and concise. 
    
    **4. Enhanced User Trust:**
    The polished interface and clear separation of summary and detail inspire confidence in the AI's validation process, presenting it as a reliable enterprise tool.
    """
)
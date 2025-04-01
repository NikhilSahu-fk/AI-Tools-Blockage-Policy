import streamlit as st
import pandas as pd
import json
from one import load_ai_tools_from_csv, fetch_ai_tool_info, generate_report

st.title("🔍 AI Tool Security Analyzer")

# File Upload
uploaded_file = st.file_uploader("📂 Upload CSV/Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Show file preview
    st.write("📋 **Preview of Uploaded Data:**")
    st.dataframe(df.head())

    # Load tools from the file
    tools = load_ai_tools_from_csv(df)

    if st.button("🔎 Generate Security Reports"):
        all_reports = {}

        for tool_name, domains in tools:
            st.write(f"🔄 Processing: {tool_name}...")

            # Placeholder for real-time updates
            tool_placeholder = st.empty()

            tool_data = fetch_ai_tool_info(domains)
            if tool_data:
                report = generate_report(tool_name, tool_data)
                all_reports[tool_name] = report  # Store report in dictionary

                # Display JSON report in readable format
                tool_placeholder.write(f"✅ **Report for {tool_name}:**")
                tool_placeholder.json(report)

        if all_reports:
            # Convert reports to JSON format
            json_report = json.dumps(all_reports, indent=4)

            # Provide final JSON download button
            st.download_button(
                "⬇️ Download Full Report",
                json_report,
                "ai_tools_security_report.json",
                "application/json",
            )

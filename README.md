# Generative AI Tool Security Analysis

This tool helps determine whether a Generative AI tool should be blocked based on its features, security risks, and compliance issues. Users can upload a CSV or Excel file containing AI tool names and their associated domains, and the tool generates a structured report assessing potential risks.

## Features

**File Upload Support**: Accepts CSV/Excel files containing AI tool details.

**Automated Analysis**: Extracts and evaluates security risks and compliance issues.

**BeautifulSoup Scraping**: Gathers additional data from online sources.

**AI-Powered Assessment**: Uses LLM models (Gemini/OpenAI) for deeper analysis.

**Interactive UI**: Built with Streamlit for ease of use.

**Exportable Reports**: Generates structured JSON reports for further evaluation.

## Installation

Prerequisites

Ensure you have the following installed:

Python (>=3.11)

Pip (Python package manager)

## Install Dependencies
pip install -r requirements.txt

## Uploading Files

Open the Streamlit app in your browser.

Upload a CSV/Excel file with columns:

Name: AI tool name

Domains list: Domains associated with the tool

Click Analyze to generate a security report.

## Understanding the Report

The output will highlight:

Potential Data Risks (PII exposure, IP leakage, etc.)

Security Compliance Issues

AI Processing Details (Data storage, external API calls)

Recommendation: Whether the tool should be blocked or not

## Technologies Used

Python: Core language for processing and analysis.

Pandas: For handling CSV/Excel data.

BeautifulSoup: Web scraping for additional data extraction.

Urllib3 / Requests: Fetching online data and API responses.

OpenAI / Gemini API: AI-driven risk evaluation.

Streamlit: Web-based UI for user interaction.

JSON: Report storage format.

Mermaid.js: Architecture diagram visualization.


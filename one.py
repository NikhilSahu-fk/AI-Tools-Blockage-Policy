import requests
from bs4 import BeautifulSoup
import re
import json
import google.generativeai as genai
import os
import pandas as pd
import time
import google.api_core.exceptions


# === 🔹 Configure Gemini API Key ===
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Google Chrome User-Agent for better website compatibility
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.google.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}
def fetch_internal_links(homepage_url):
    """Extracts all internal links from a given homepage."""
    try:
        response = requests.get(homepage_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch homepage {homepage_url}: {response.status_code}")
            return None  # Indicate failure to load

        soup = BeautifulSoup(response.text, "html.parser")
        base_url = homepage_url.rstrip("/")
        internal_links = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("/") or homepage_url in href:
                full_url = base_url + href if href.startswith("/") else href
                internal_links.add(full_url)

        return list(internal_links) if internal_links else []  # Return an empty list instead of None

    except requests.exceptions.Timeout:
        print(f"⏳ Timeout while fetching {homepage_url}")
        return None  # Indicate failure to load

    except Exception as e:
        print(f"❌ Error fetching internal links from {homepage_url}: {e}")
        return None  # Indicate failure to load


def fetch_text_from_url(url, retries=3):
    """Fetches and extracts readable text from a given URL, with retries."""
    if not url:
        return "Not Available"

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = "\n".join([p.get_text(strip=True) for p in soup.find_all(["p", "li"])])
                return text  

        except requests.exceptions.ConnectTimeout:
            print(f"Timeout: {url} (Attempt {attempt + 1}/{retries})")
            continue
        except:
            return "Not Available"

    return "Not Available"


def fetch_ai_tool_info(domains):
    """Tries multiple domains until one responds, then extracts relevant information."""
    if isinstance(domains, str):
        domains = [domains]
    
    for homepage_url in domains:
        print(f"🔹 Trying {homepage_url}")
        try:
            internal_links = fetch_internal_links(homepage_url)

            # ✅ If fetching homepage completely failed, move to next domain
            if internal_links is None:
                print(f"⚠️ Website {homepage_url} is not loading. Trying next domain...")
                continue  

            # ✅ If no internal links are found, **do NOT move to next domain**; instead, manually check standard URLs.
            if not internal_links:
                print(f"⚠️ No internal links found for {homepage_url}. Manually checking standard URLs...")

            # ✅ Fetch homepage content
            homepage_content = fetch_text_from_url(homepage_url)

            # Standard URL paths to check
            standard_paths = {
                "Privacy Policy": ["privacy", "privacy-policy", "privacypolicy", "legal/privacy"],
                "Terms of Service": ["terms", "terms-of-service"],
                "Features": ["features"],
                "API Docs": ["api", "api-docs"],
                "Documentation": ["docs", "documentation"],
                "FAQ": ["faq"],
                "Support": ["support", "help"],
                "About": ["about"],
                "Blog": ["blog"],
                "Pricing": ["pricing"],
                "Cookie Policy": ["cookie-policy", "cookie-notice", "cookies", "cookie"]
            }

            # ✅ **Always initialize `important_pages` with None for all keys**
            important_pages = {key: None for key in standard_paths.keys()}

            # ✅ Use found internal links if available
            if internal_links:
                for key, patterns in standard_paths.items():
                    match = next((url for url in internal_links if any(pattern in url.lower() for pattern in patterns)), None)
                    important_pages[key] = match if match else None

            # ✅ **Manually check standard URLs if no internal links found**
            for key, url in important_pages.items():
                if url is None:  # Only check if no match was found
                    for path in standard_paths[key]:
                        test_url = f"{homepage_url.rstrip('/')}/{path}"
                        print(f"🔍 Manually checking: {test_url}")
                        try:
                            response = requests.get(test_url, headers=HEADERS, timeout=5)
                            if response.status_code == 200:
                                important_pages[key] = test_url
                                break
                        except requests.exceptions.Timeout:
                            print(f"⏳ Timeout: {test_url}")
                        except Exception as e:
                            print(f"❌ Failed for {test_url}, Error: {e}")

            # ✅ Fetch text from available pages
            extracted_info = {key: fetch_text_from_url(url) if url else "Not Available" for key, url in important_pages.items()}

            # ✅ Ensure all keys are present
            for key in standard_paths.keys():
                if key not in extracted_info:
                    extracted_info[key] = "Not Available"

            # ✅ Construct full report
            full_context = f"""
            AI Tool Homepage: {homepage_url}

            === Important Pages ===
            Privacy Policy: {important_pages.get('Privacy Policy', 'Not Available')}
            Terms of Service: {important_pages.get('Terms of Service', 'Not Available')}
            API Docs: {important_pages.get('API Docs', 'Not Available')}
            Documentation: {important_pages.get('Documentation', 'Not Available')}
            Pricing: {important_pages.get('Pricing', 'Not Available')}

            === Homepage Content ===
            {homepage_content}

            === Privacy Policy ===
            {extracted_info['Privacy Policy']}

            === Terms of Service ===
            {extracted_info['Terms of Service']}

            === Features ===
            {extracted_info['Features']}

            === API Documentation ===
            {extracted_info['API Docs']}

            === Documentation ===
            {extracted_info['Documentation']}

            === FAQ ===
            {extracted_info['FAQ']}

            === Support Page ===
            {extracted_info['Support']}

            === About Us ===
            {extracted_info['About']}

            === Blog ===
            {extracted_info['Blog']}

            === Pricing Information ===
            {extracted_info['Pricing']}
            """

            print(f"✅ Successfully extracted data from {homepage_url}")
            return full_context.strip()

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout for {homepage_url}, trying next domain...")
            continue  # Move to next domain

        except Exception as e:
            print(f"❌ Error processing {homepage_url}: {e}")
            continue  # Move to next domain

    print("❌ No working domains found for this tool.")
    return "No data available."





# === 🔹 Ensure URLs start with 'https://' ===

def clean_url(domain):
    """Ensures the domain has a valid scheme (http/https)."""
    domain = domain.strip().lower()  # Remove spaces & convert to lowercase
    if not domain.startswith("http"):
        domain = "https://" + domain  # Default to HTTPS
    return domain

def load_ai_tools_from_csv(df, limit=100):
    """Reads a DataFrame and returns a list of (tool_name, homepage_urls) tuples."""
    try:
        # Ensure required columns exist
        if "Name" not in df.columns or "Domains list" not in df.columns:
            raise ValueError("CSV file must contain 'Name' and 'Domains list' columns.")

        tools = []
        for _, row in df.head(limit).iterrows():  # Process first 'limit' AI tools
            tool_name = row["Name"]
            domains_raw = str(row["Domains list"]).strip()  # Ensure it's a string
            
            # ✅ FIX: Split and filter domains correctly
            domains = [domain.strip() for domain in domains_raw.split(",") if domain]

            # ✅ FIX: Ensure valid URLs
            cleaned_domains = [clean_url(domain) for domain in domains]

            tools.append((tool_name, cleaned_domains))  # Store as tuple (tool_name, [list_of_domains])

        return tools
    except Exception as e:
        print(f"❌ Error processing CSV data: {e}")
        return []


    

def analyze_with_gemini(question, tool_data, max_retries=5):
    """Sends a query to Gemini API and handles rate limits (429 errors)."""
    prompt = (
        "You are a cybersecurity expert evaluating an AI tool for security and compliance risks. "
        # "Your response must be a **single, concise sentence** that determines whether the tool is safe or should be blocked in our organization."
        # "\n\n"
        "### Instructions:\n"
        "- Analyze the AI tool based on its privacy policy, terms of service, features, and API documentation.\n"
        "- Identify risks such as **PII/PHI exposure, external API calls, data logging, storage locations, and compliance violations**.\n"
        "- Provide a **one-line answer**.\n"
        # "- If there is insufficient information, state: 'Not enough data to determine risk.'"
        "\n\n"
        f"### AI Tool Data:\n{tool_data}\n\n"
        f"### Question:\n{question}\n"
        "### One-Line Answer:\n"
    )
    
    attempt = 0
    while attempt < max_retries:
        try:
            response = model.generate_content(prompt)
            return response.text.strip()  # Ensure it's a single line
        except google.api_core.exceptions.ResourceExhausted as e:
            retry_delay = 3 * (2 ** attempt)  # Exponential backoff (3, 6, 12, 24, 48 sec)
            print(f"⚠️ Rate limit hit! Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)  # Wait before retrying
            attempt += 1
        except Exception as e:
            print(f"❌ Error querying Gemini API: {e}")
            return None  # Fail gracefully

    print("🚨 Max retries reached. Skipping this request.")
    return None


def generate_report(tool_name, tool_data):
    """Generates a concise AI tool report in a single Gemini API call."""
    report = {
        "Tool Name": tool_name,
        "Features Included": analyze_with_gemini("What features are included? Chat, file uploads/downloads, API integrations, data analytics?", tool_data),
        "Potential Violations": analyze_with_gemini("What data security violations could occur? PII, PHI, PCI exposure, compliance risks?", tool_data),
        "Scrapable Data": analyze_with_gemini("What kind of sensitive data could be scraped? PII, financial records, source code?", tool_data),
        "Uploads/Downloads Support": analyze_with_gemini("Does the tool support file uploads and downloads?", tool_data),
        "Data Copying Options": analyze_with_gemini("Can users copy data from responses or export outputs?", tool_data),
        "Backend Data Handling": analyze_with_gemini("What happens with user data? AI processing, storage, external API calls?", tool_data),
        "Supported File Formats": analyze_with_gemini("What data formats are supported? PDF, DOCX, XLSX, CSV, JSON, TXT?", tool_data),
        "Unvalidated API Calls": analyze_with_gemini("Does the tool make any unvalidated external API calls?", tool_data),
    }
    return report

# === 🔹 Process multiple AI tools and save in a single JSON file ===
def process_ai_tools(file_path, output_file="ai_tools_report1_new.json", limit=2):
    """Fetches information and generates reports for multiple AI tools."""
    # ✅ Debugging Output
    df = pd.read_csv("GENAI-24thmar - Sheet3.csv")
    tools = load_ai_tools_from_csv(df, limit)
    for tool_name, domains in tools:
        print(f"✅ {tool_name}: {domains}")

    if not tools:
        print("No AI tools found in the Excel file.")
        return

    all_reports = {}

    for tool_name, homepage_urls in tools:
        if isinstance(homepage_urls, str):  # Convert single string to list
            homepage_urls = [homepage_urls]

        print(f"🔹 Processing: {tool_name} ({', '.join(homepage_urls)})")
        
        tool_data = None

        # Try fetching info from the first available domain
        for homepage_url in homepage_urls:
            tool_data = fetch_ai_tool_info(homepage_url)
            if tool_data:
                break  # Stop after fetching successful data

        if tool_data:
            report = generate_report(tool_name, tool_data)
            all_reports[tool_name] = report  # Store report in dictionary
            print(f"✅ Report generated for {tool_name}")
        else:
            print(f"❌ Failed to fetch info for {tool_name}")

        # === 🔹 Prevent hitting API limits with a delay ===
        print("⏳ Waiting 5 seconds before processing the next tool...")
        time.sleep(5)  # Pause to prevent too many API calls in a short time

    # Save all reports to a single JSON file
    with open(output_file, "w") as f:
        json.dump(all_reports, f, indent=4)

    print(f"\n📄 All reports saved in {output_file}")

# === 🔹 Run the script for first 10 AI tools from Excel ===
# excel_file = "GENAI-24thmar - Sheet3.csv"  # Ensure this file contains columns: 'Name' and 'Domains list'
# process_ai_tools(excel_file, limit=2)

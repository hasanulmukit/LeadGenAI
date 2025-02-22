# LeadGenAI - LinkedIn Lead Generation and Business Optimization App

LeadGenAI is a Streamlit-based application that empowers users to generate leads from LinkedIn and optimize their business strategies using the power of IBM Watsonx AI.  This application offers two core functionalities: lead generation based on specific criteria and AI-powered business plan generation.

## Features

**Lead Generation:**

* **Targeted Search:** Filter LinkedIn profiles based on criteria like country, industry, and company.
* **Data Extraction:** Extract key information such as name, location, company, position, and about section.
* **Data Export:** Download leads as CSV and PDF files for easy access and sharing.
* **Session History:** Access and download previous lead generation sessions.

**Business Optimization:**

* **AI-Powered Business Plans:** Generate comprehensive business plans based on user-provided requirements.
* **Detailed Insights:** Receive detailed business plans including concept, target audience, revenue model, key differentiators, and potential challenges.
* **Lead Targeting:** Get specific lead suggestions with links to Twitter, LinkedIn, and company websites.
* **Session History:** Review and download past business plan generation sessions.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/LeadGenAI.git
   ```

2. **Create a Virtual Environment (Recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   `requirements.txt` should contain the following:
   ```
   streamlit
   pandas
   fpdf
   ibm-watsonx-ai
   sqlite3
   json
   ```

4. **IBM Watsonx Credentials:**
   You will need an IBM Watsonx account and API key.  Store these credentials securely.  The app currently stores credentials directly in the `get_credentials()` function, but this should be updated to a more secure method such as environment variables or a secrets management tool.  Update the placeholder values in the `get_credentials()` function with your actual credentials:
   ```python
   def get_credentials():
       return {
           "url": "YOUR_WATSONX_URL",
           "apikey": "YOUR_WATSONX_API_KEY"
       }
   ```

5. **Data Files:**
   Ensure the `LinkedIn_profiles_info_modified.json` and `LinkedIn_company_info_modified.json` files are present in the same directory as the application.  These files contain the LinkedIn data. The format is expected to be JSON.  If the files do not start with `[`, the app will attempt to convert them to a valid JSON array.

## Usage

1. **Run the App:**
   ```bash
   streamlit run app.py
   ```

2. **Lead Generation:**
   - Enter your lead search criteria in the text area.
   - Select the desired number of leads.
   - Click "Generate Leads".

3. **Business Optimization:**
   - Enter your business idea requirements in the text area.
   - Click "Generate Idea & Leads".
   - Download the generated business plan as a PDF.

4. **Accessing Past Sessions:**
   Use the tabs to navigate to "Lead Sessions" or "Plan Sessions" to view and download data from previous runs.


## Technologies Used

* **Streamlit:** For building the interactive web application.
* **Pandas:** For data manipulation and analysis.
* **FPDF:** For generating PDF reports.
* **IBM Watsonx AI:** For generating business plans and ideas.
* **SQLite:** For storing session data.
* **JSON:** For data storage and exchange.

## License

Apache License Version 2.0

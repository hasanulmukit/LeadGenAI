import os
import sqlite3
import streamlit as st
import pandas as pd
import json
from fpdf import FPDF
from ibm_watsonx_ai.foundation_models import ModelInference

# Function to get IBM Watsonx credentials
def get_credentials():
    return {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": "e8jfiewbLaLuUoz_4ZAybPHwwrBOosuNGXipuP9Mwmu2"
    }

# Initialize the IBM Watsonx model
def initialize_model():
    model_id = "ibm/granite-3-8b-instruct"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 900,
        "min_new_tokens": 0,
        "repetition_penalty": 1
    }
    project_id = "e6b523ca-d2f8-412d-9f70-8bc99c542b68"
    model = ModelInference(
        model_id=model_id,
        params=parameters,
        credentials=get_credentials(),
        project_id=project_id
    )
    return model

# Function to load JSON data
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        if not content.strip().startswith('['):
            content = '[' + content.replace('}\n{', '},{') + ']'
        return json.loads(content)

# Function to initialize SQLite database for leads
def init_leads_db():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_leads
                 (id INTEGER PRIMARY KEY, name TEXT, city TEXT, country_code TEXT, region TEXT, 
                 current_company_company_id TEXT, current_company_name TEXT, position TEXT, 
                 following INTEGER, about TEXT, posts INTEGER, groups INTEGER, 
                 current_company TEXT, experience TEXT, url TEXT, 
                 people_also_viewed TEXT, educations_details TEXT, education TEXT, 
                 avatar TEXT, languages TEXT, certifications TEXT, 
                 recommendations TEXT, recommendations_count INTEGER, 
                 volunteer_experience TEXT, courses TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS company_leads
                 (id INTEGER PRIMARY KEY, name TEXT, country_code TEXT, locations TEXT, 
                 formatted_locations TEXT, followers INTEGER, employees_in_linkedin INTEGER, 
                 about TEXT, specialties TEXT, company_size TEXT, organization_type TEXT, 
                 industries TEXT, website TEXT, crunchbase_url TEXT, founded TEXT, 
                 company_id TEXT, employees TEXT, headquarters TEXT, image TEXT, 
                 logo TEXT, similar TEXT, sphere TEXT, url TEXT, type TEXT, 
                 updates TEXT, slogan TEXT, affiliated TEXT, funding TEXT, 
                 stock_info TEXT, investors TEXT)''')
    conn.commit()
    return conn

# Function to save leads to SQLite database
def save_leads_to_db(conn, leads, table_name):
    c = conn.cursor()
    for lead in leads:
        if table_name == 'user_leads':
            c.execute('''INSERT INTO user_leads 
                         (name, city, country_code, region, current_company_company_id, 
                         current_company_name, position, following, about, posts, groups, 
                         current_company, experience, url, people_also_viewed, 
                         educations_details, education, avatar, languages, certifications, 
                         recommendations, recommendations_count, volunteer_experience, courses) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (lead['name'], lead['city'], lead['country_code'], lead['region'], 
                       lead['current_company:company_id'], lead['current_company:name'], 
                       lead['position'], lead['following'], lead['about'], lead['posts'], 
                       lead['groups'], lead['current_company'], lead['experience'], 
                       lead['url'], str(lead['people_also_viewed']), lead['educations_details'], 
                       lead['education'], lead['avatar'], str(lead['languages']), 
                       str(lead['certifications']), str(lead['recommendations']), 
                       lead['recommendations_count'], lead['volunteer_experience'], 
                       str(lead['сourses'])))
        elif table_name == 'company_leads':
            c.execute('''INSERT INTO company_leads 
                         (name, country_code, locations, formatted_locations, followers, 
                         employees_in_linkedin, about, specialties, company_size, 
                         organization_type, industries, website, crunchbase_url, founded, 
                         company_id, employees, headquarters, image, logo, similar, 
                         sphere, url, type, updates, slogan, affiliated, funding, 
                         stock_info, investors) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (lead['name'], lead['country_code'], str(lead['locations']), 
                       str(lead['formatted_locations']), lead['followers'], 
                       lead['employees_in_linkedin'], lead['about'], lead['specialties'], 
                       lead['company_size'], lead['organization_type'], str(lead['industries']), 
                       lead['website'], lead['crunchbase_url'], lead['founded'], 
                       lead['company_id'], lead['employees'], lead['headquarters'], 
                       lead['image'], lead['logo'], str(lead['similar']), lead['sphere'], 
                       lead['url'], lead['type'], lead['updates'], lead['slogan'], 
                       lead['affiliated'], lead['funding'], lead['stock_info'], 
                       str(lead['investors'])))
    conn.commit()

# Function to filter leads based on user input
def filter_leads(leads, filter_key, filter_value):
    filtered_leads = []
    for lead in leads:
        if filter_key in lead and lead[filter_key] == filter_value:
            filtered_leads.append(lead)
    return filtered_leads

# Function to extract filtering criteria from user input
def extract_filter_criteria(user_input):
    country_mapping = {
        "afghanistan": "AF", "albania": "AL", "algeria": "DZ", "andorra": "AD", "angola": "AO",
        "antigua and barbuda": "AG", "argentina": "AR", "armenia": "AM", "australia": "AU", "austria": "AT",
        "azerbaijan": "AZ", "bahamas": "BS", "bahrain": "BH", "bangladesh": "BD", "barbados": "BB",
        "belarus": "BY", "belgium": "BE", "belize": "BZ", "benin": "BJ", "bhutan": "BT",
        "bolivia": "BO", "bosnia and herzegovina": "BA", "botswana": "BW", "brazil": "BR", "brunei": "BN",
        "bulgaria": "BG", "burkina faso": "BF", "burundi": "BI", "cabo verde": "CV", "cambodia": "KH",
        "cameroon": "CM", "canada": "CA", "central african republic": "CF", "chad": "TD", "chile": "CL",
        "china": "CN", "colombia": "CO", "comoros": "KM", "congo": "CG", "costa rica": "CR",
        "croatia": "HR", "cuba": "CU", "cyprus": "CY", "czech republic": "CZ", "denmark": "DK",
        "djibouti": "DJ", "dominica": "DM", "dominican republic": "DO", "ecuador": "EC", "egypt": "EG",
        "el salvador": "SV", "equatorial guinea": "GQ", "eritrea": "ER", "estonia": "EE", "eswatini": "SZ",
        "ethiopia": "ET", "fiji": "FJ", "finland": "FI", "france": "FR", "gabon": "GA",
        "gambia": "GM", "georgia": "GE", "germany": "DE", "ghana": "GH", "greece": "GR",
        "grenada": "GD", "guatemala": "GT", "guinea": "GN", "guinea-bissau": "GW", "guyana": "GY",
        "haiti": "HT", "honduras": "HN", "hungary": "HU", "iceland": "IS", "india": "IN",
        "indonesia": "ID", "iran": "IR", "iraq": "IQ", "ireland": "IE", "israel": "IL",
        "italy": "IT", "jamaica": "JM", "japan": "JP", "jordan": "JO", "kazakhstan": "KZ",
        "kenya": "KE", "kiribati": "KI", "korea, north": "KP", "korea, south": "KR", "kosovo": "XK",
        "kuwait": "KW", "kyrgyzstan": "KG", "laos": "LA", "latvia": "LV", "lebanon": "LB",
        "lesotho": "LS", "liberia": "LR", "libya": "LY", "liechtenstein": "LI", "lithuania": "LT",
        "luxembourg": "LU", "madagascar": "MG", "malawi": "MW", "malaysia": "MY", "maldives": "MV",
        "mali": "ML", "malta": "MT", "marshall islands": "MH", "mauritania": "MR", "mauritius": "MU",
        "mexico": "MX", "micronesia": "FM", "moldova": "MD", "monaco": "MC", "mongolia": "MN",
        "montenegro": "ME", "morocco": "MA", "mozambique": "MZ", "myanmar": "MM", "namibia": "NA",
        "nauru": "NR", "nepal": "NP", "netherlands": "NL", "new zealand": "NZ", "nicaragua": "NI",
        "niger": "NE", "nigeria": "NG", "north macedonia": "MK", "norway": "NO", "oman": "OM",
        "pakistan": "PK", "palau": "PW", "panama": "PA", "papua new guinea": "PG", "paraguay": "PY",
        "peru": "PE", "philippines": "PH", "poland": "PL", "portugal": "PT", "qatar": "QA",
        "romania": "RO", "russia": "RU", "rwanda": "RW", "saint kitts and nevis": "KN", "saint lucia": "LC",
        "saint vincent and the grenadines": "VC", "samoa": "WS", "san marino": "SM", "sao tome and principe": "ST",
        "saudi arabia": "SA", "senegal": "SN", "serbia": "RS", "seychelles": "SC", "sierra leone": "SL",
        "singapore": "SG", "slovakia": "SK", "slovenia": "SI", "solomon islands": "SB", "somalia": "SO",
        "south africa": "ZA", "south sudan": "SS", "spain": "ES", "sri lanka": "LK", "sudan": "SD",
        "suriname": "SR", "sweden": "SE", "switzerland": "CH", "syria": "SY", "taiwan": "TW",
        "tajikistan": "TJ", "tanzania": "TZ", "thailand": "TH", "timor-leste": "TL", "togo": "TG",
        "tonga": "TO", "trinidad and tobago": "TT", "tunisia": "TN", "turkey": "TR", "turkmenistan": "TM",
        "tuvalu": "TV", "uganda": "UG", "ukraine": "UA", "united arab emirates": "AE", "united kingdom": "GB",
        "united states": "US", "uruguay": "UY", "uzbekistan": "UZ", "vanuatu": "VU", "vatican city": "VA",
        "venezuela": "VE", "vietnam": "VN", "yemen": "YE", "zambia": "ZM", "zimbabwe": "ZW"
    }
    
    user_input_lower = user_input.lower()
    
    for country, code in country_mapping.items():
        if country in user_input_lower:
            return {"filter_key": "country_code", "filter_value": code}
    
    if "business" in user_input_lower or "industry" in user_input_lower:
        business_types = ["tech", "finance", "healthcare", "education", "manufacturing"]
        for business_type in business_types:
            if business_type in user_input_lower:
                return {"filter_key": "industries", "filter_value": business_type.capitalize()}
    
    if "company" in user_input_lower:
        company_names = ["google", "microsoft", "apple", "amazon", "facebook"]
        for company_name in company_names:
            if company_name in user_input_lower:
                return {"filter_key": "name", "filter_value": company_name.capitalize()}
    
    return None

# Function to create PDF from DataFrame
def create_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    
    for index, row in df.iterrows():
        for col in df.columns:
            text = f"{col}: {row[col]}"
            try:
                text.encode('latin1')
            except UnicodeEncodeError:
                text = text.encode('latin1', errors='replace').decode('latin1')
            pdf.cell(200, 10, txt=text, ln=True)
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin1')

# Function to generate business ideas
def generate_business_idea(model, prompt_input, user_input):
    formatted_question = f"""<|start_of_role|>user<|end_of_role|>{user_input}<|end_of_text|>
    <|start_of_role|>assistant<|end_of_role|>"""
    prompt = f"""{prompt_input}{formatted_question}"""
    generated_response = model.generate_text(prompt=prompt, guardrails=False)
    return generated_response

# Function to save text as a modern PDF
def save_as_pdf(text, filename="business_plan.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style="B")
    pdf.cell(0, 10, txt="Business Plan Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=text)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=f"Page {pdf.page_no()}", align="C")
    pdf.output(filename)
    return filename

# Function to initialize SQLite database for chat history
def initialize_chat_db():
    if not os.path.exists("chat_history.db"):
        conn = sqlite3.connect("chat_history.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                ai_response TEXT
            )
        """)
        conn.commit()
        conn.close()

# Function to save chat session to database
def save_chat_session(user_input, ai_response):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_sessions (user_input, ai_response)
        VALUES (?, ?)
    """, (user_input, ai_response))
    conn.commit()
    conn.close()

# Function to fetch all chat sessions from database
def fetch_chat_sessions():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_sessions")
    sessions = cursor.fetchall()
    conn.close()
    return sessions

# Streamlit App
def main():
    # App Name
    st.sidebar.title("LeadGenAI")
    # Sidebar navigation
    st.sidebar.header("Main Navigation")
    
    # Use buttons for navigation
    if st.sidebar.button("Lead Generation"):
        st.session_state.app_mode = "Lead Generation"
    
    if st.sidebar.button("Business Optimization"):
        st.session_state.app_mode = "Business Optimization"
    
    # Initialize session state for app mode if not already set
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "Lead Generation"

    if st.session_state.app_mode == "Lead Generation":
        st.title("LinkedIn Lead Generation")

        # Create tabs
        tab1, tab2 = st.tabs(["Lead Generation", "Lead Sessions"])

        with tab1:
            st.header("Lead Generation")
            user_input = st.text_area("Enter your lead requirements (e.g. Healthcare professionals in Canada):", height=150)
            num_leads = st.slider("Number of leads to generate (1-1000):", 1, 1000, 10)

            if st.button("Generate Leads"):
                # Load JSON data
                user_profiles = load_json_data("LinkedIn_profiles_info_modified.json")
                company_profiles = load_json_data("LinkedIn_company_info_modified.json")

                # Extract filtering criteria from user input
                filter_criteria = extract_filter_criteria(user_input)
                
                # Filter leads based on extracted criteria
                if filter_criteria:
                    selected_user_leads = filter_leads(user_profiles, filter_criteria["filter_key"], filter_criteria["filter_value"])[:num_leads]
                    selected_company_leads = filter_leads(company_profiles, filter_criteria["filter_key"], filter_criteria["filter_value"])[:num_leads]
                else:
                    selected_user_leads = user_profiles[:num_leads]
                    selected_company_leads = company_profiles[:num_leads]

                # Display leads in cards format
                st.header("LinkedIn User Profile Leads")
                for lead in selected_user_leads:
                    st.write(f"**Name:** {lead['name']}")
                    st.write(f"**City:** {lead['city']}")
                    st.write(f"**Country Code:** {lead['country_code']}")
                    st.write(f"**Region:** {lead['region']}")
                    st.write(f"**Current Company:** {lead['current_company:name']}")
                    st.write(f"**Position:** {lead['position']}")
                    st.write(f"**About:** {lead['about']}")
                    st.write(f"**URL:** {lead['url']}")
                    st.write("---")

                st.header("LinkedIn Company Profile Leads")
                for lead in selected_company_leads:
                    st.write(f"**Name:** {lead['name']}")
                    st.write(f"**Country Code:** {lead['country_code']}")
                    st.write(f"**Locations:** {lead['locations']}")
                    st.write(f"**Website:** {lead['website']}")
                    st.write(f"**About:** {lead['about']}")
                    st.write(f"**URL:** {lead['url']}")
                    st.write("---")

                # Save leads to SQLite database
                conn = init_leads_db()
                save_leads_to_db(conn, selected_user_leads, 'user_leads')
                save_leads_to_db(conn, selected_company_leads, 'company_leads')
                conn.close()

                # Download leads as CSV and PDF
                user_leads_df = pd.DataFrame(selected_user_leads)
                company_leads_df = pd.DataFrame(selected_company_leads)

                st.download_button(
                    label="Download User Leads as CSV",
                    data=user_leads_df.to_csv(index=False),
                    file_name='user_leads.csv',
                    mime='text/csv',
                    key="user_leads_csv"
                )

                st.download_button(
                    label="Download Company Leads as CSV",
                    data=company_leads_df.to_csv(index=False),
                    file_name='company_leads.csv',
                    mime='text/csv',
                    key="company_leads_csv"
                )

                user_pdf = create_pdf(user_leads_df, "LinkedIn User Profile Leads")
                company_pdf = create_pdf(company_leads_df, "LinkedIn Company Profile Leads")

                st.download_button(
                    label="Download User Leads as PDF",
                    data=user_pdf,
                    file_name='user_leads.pdf',
                    mime='application/pdf',
                    key="user_leads_pdf"
                )

                st.download_button(
                    label="Download Company Leads as PDF",
                    data=company_pdf,
                    file_name='company_leads.pdf',
                    mime='application/pdf',
                    key="company_leads_pdf"
                )

        with tab2:
            st.header("Lead Sessions")
            try:
                conn = init_leads_db()
                user_leads_df = pd.read_sql_query("SELECT * FROM user_leads", conn)
                company_leads_df = pd.read_sql_query("SELECT * FROM company_leads", conn)
                conn.close()

                st.header("User Leads from Previous Sessions")
                with st.expander("View User Leads"):
                    st.dataframe(user_leads_df)
                    user_pdf = create_pdf(user_leads_df, "LinkedIn User Profile Leads")
                    st.download_button(
                        label="Download User Leads as PDF",
                        data=user_pdf,
                        file_name='user_leads.pdf',
                        mime='application/pdf',
                        key="user_leads_pdf_session"
                    )
                    st.download_button(
                        label="Download User Leads as CSV",
                        data=user_leads_df.to_csv(index=False),
                        file_name='user_leads.csv',
                        mime='text/csv',
                        key="user_leads_csv_session"
                    )

                st.header("Company Leads from Previous Sessions")
                with st.expander("View Company Leads"):
                    st.dataframe(company_leads_df)
                    company_pdf = create_pdf(company_leads_df, "LinkedIn Company Profile Leads")
                    st.download_button(
                        label="Download Company Leads as PDF",
                        data=company_pdf,
                        file_name='company_leads.pdf',
                        mime='application/pdf',
                        key="company_leads_pdf_session"
                    )
                    st.download_button(
                        label="Download Company Leads as CSV",
                        data=company_leads_df.to_csv(index=False),
                        file_name='company_leads.csv',
                        mime='text/csv',
                        key="company_leads_csv_session"
                    )
            except sqlite3.OperationalError as e:
                st.error(f"Database error: {e}. Please ensure the database is initialized.")

    elif st.session_state.app_mode == "Business Optimization":
        st.title("Business Optimization")

        # Initialize SQLite database for chat history
        initialize_chat_db()

        # Initialize session state for chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Initialize the IBM Watsonx model
        model = initialize_model()

        # Enhanced system prompt for business optimization
        prompt_input = """<|start_of_role|>system<|end_of_role|>
        You are Granite, an AI language model developed by IBM in 2024. You are an expert in generating innovative and practical business ideas and plans. 
        Your task is to provide detailed, actionable, and creative business ideas and plans based on user input. 
        Each idea and plan should include:
        1. A clear business concept.
        2. Target audience.
        3. Revenue model.
        4. Key differentiators.
        5. Potential challenges and solutions.
        6. Target specific leads with at least 20 authentic Twitter links, LinkedIn profile links and 20 website URLs.
        Be concise, professional, and creative in your responses.
        <|end_of_text|>"""

        # Create tabs
        tab1, tab2 = st.tabs(["Plan", "Plan Sessions"])

        with tab1:
            st.write("Welcome to the Business Planner! Enter your requirements below and get innovative business plans or ideas.")

            # User input with resizable text area
            user_input = st.text_area(
                "Enter your business plan or idea requirements:",
                height=150,
                placeholder="Example: I want to start a sustainable fashion brand targeting millennials."
            )

            # Generate business idea on button click
            if st.button("Generate Idea & Leads"):
                if user_input:
                    with st.spinner("Generating your business plan..."):
                        business_idea = generate_business_idea(model, prompt_input, user_input)
                        st.session_state.chat_history.append(("You", user_input))
                        st.session_state.chat_history.append(("AI", business_idea))
                        save_chat_session(user_input, business_idea)
                else:
                    st.warning("Please enter your business idea requirements.")

            # Display the final plan/idea and allow downloading as PDF
            if st.session_state.chat_history:
                latest_idea = st.session_state.chat_history[-1][1]
                st.write("### Business Plan")
                st.write(latest_idea)
                if st.button("Download Business Plan as PDF"):
                    pdf_filename = save_as_pdf(latest_idea)
                    st.success(f"Business plan saved as {pdf_filename}!")
                    with open(pdf_filename, "rb") as file:
                        st.download_button(
                            label="Download PDF",
                            data=file,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )

        with tab2:
            st.write("### Plan Sessions")
            sessions = fetch_chat_sessions()
            if sessions:
                for idx, session in enumerate(sessions):
                    session_id, user_input, ai_response = session
                    with st.expander(f"Session {session_id}"):
                        st.write(f"**Input:** {user_input}")
                        st.write(f"**Plan:** {ai_response}")
                        if st.button(f"Download Session {session_id} as PDF", key=f"download_{session_id}"):
                            pdf_filename = save_as_pdf(f"Input: {user_input}\n\nPlan: {ai_response}", filename=f"business_plan_session_{session_id}.pdf")
                            st.success(f"Business plan saved as {pdf_filename}!")
                            with open(pdf_filename, "rb") as file:
                                st.download_button(
                                    label="Download PDF",
                                    data=file,
                                    file_name=pdf_filename,
                                    mime="application/pdf",
                                    key=f"download_button_{session_id}"
                                )
            else:
                st.write("No plan sessions available yet.")

if __name__ == "__main__":
    main()

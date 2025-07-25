import streamlit as st
import pandas as pd
import ast
from collections import Counter
import matplotlib.pyplot as plt # Import for custom plots
import seaborn as sns # Import for enhanced plots

# --- Page Config and Styling ---
st.set_page_config(page_title="Job Posting Analyzer", layout="wide")

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #333333; /* Slightly darker body text for better readability */
        }

        .main {
            background-color: #f8f9fa; /* Light background */
            padding: 2rem 3rem; /* Increased padding for more breathing room */
        }

        h1 {
            font-size: 2.5em; /* Slightly larger heading */
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 20px; /* More space below main title */
            border-bottom: 2px solid #eef2f7; /* Subtle underline */
            padding-bottom: 10px;
        }

        h2 {
            font-size: 1.8em;
            color: #34495e;
            font-weight: 600;
            margin-top: 2.5rem; /* More space above H2 sections */
            margin-bottom: 1rem;
        }

        h3 {
            font-size: 1.3em;
            color: #34495e;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 0.8rem;
        }

        section[data-testid="stSidebar"] {
            background-color: #eef2f7; /* Light sidebar background */
            padding: 1.5rem; /* Padding inside sidebar */
            border-right: 1px solid #e0e0e0; /* Subtle sidebar divider */
        }

        /* Labels for input widgets */
        .stSlider > label, .stTextInput > label, .stMultiSelect > label, .stSelectbox > label {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem; /* Space between label and input */
            display: block; /* Ensures label takes full width for margin to apply */
        }

        /* General input styling for a cleaner look */
        .stTextInput > div > div > input,
        .stMultiSelect > div > div,
        .stSelectbox > div > div {
            border: 1px solid #d0d0d0; /* Subtle border */
            border-radius: 5px; /* Slightly rounded corners */
            padding: 0.5rem 0.75rem; /* Internal padding */
            box-shadow: none; /* Remove default shadow if any */
            transition: border-color 0.2s ease-in-out; /* Smooth transition on focus */
        }

        .stTextInput > div > div > input:focus,
        .stMultiSelect > div > div:focus-within,
        .stSelectbox > div > div:focus-within {
            border-color: #007bff; /* Accent color on focus */
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25); /* Subtle glow on focus */
            outline: none; /* Remove default outline */
        }

        .stDataFrameContainer {
            background-color: white;
            border-radius: 8px;
            padding: 15px; /* Slightly more padding */
            box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* More pronounced shadow */
            border: 1px solid #e0e0e0; /* Subtle border */
        }

        .stAlert {
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem; /* Space below alerts */
        }

        /* Styling for chart containers */
        .st-emotion-cache-nahz7x + div > .element-container:has(svg), /* Specific target for charts */
        .element-container:has(.st-bar-chart),
        .element-container:has(.st-pyplot) { /* Also target pyplot containers */
            padding-bottom: 2rem;
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
            margin-top: 1rem; /* Added margin-top for charts */
        }


        /* Custom horizontal rule for separation */
        .st-emotion-cache-nahz7x { /* Targeting the default hr generated by st.markdown("---") */
            border-top: 1px solid #e0e0e0;
            margin-top: 2rem;
            margin-bottom: 2rem;
        }

        /* Adjust Streamlit default markdown for better spacing */
        p {
            margin-bottom: 1rem;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load CSV ---
try:
    df = pd.read_csv("data/naukri_skill_tagged_data.csv")
except FileNotFoundError:
    st.error("Error: The file 'data/naukri_skill_tagged_data.csv' was not found.")
    st.info("Please ensure the 'data' folder exists and contains the correct CSV file.")
    st.stop()

# Convert Skill_List and Skill_Type_List from strings to actual lists
for col in ['Skill_List', 'Skill_Type_List']:
    df[col] = df[col].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

# Create an 'Experience_Band' column for better visualization
def get_experience_band(min_exp, max_exp):
    if pd.isna(min_exp) or pd.isna(max_exp):
        return "Not Specified"
    avg_exp = (min_exp + max_exp) / 2
    if avg_exp <= 2:
        return "0-2 Years (Entry)"
    elif avg_exp <= 5:
        return "3-5 Years (Junior/Mid)"
    elif avg_exp <= 8:
        return "6-8 Years (Mid/Senior)"
    elif avg_exp <= 12:
        return "9-12 Years (Senior)"
    else:
        return "12+ Years (Lead/Architect)"

df['Experience_Band'] = df.apply(lambda row: get_experience_band(row['Min_Experience'], row['Max_Experience']), axis=1)


# --- App Header ---
st.title("AI vs Human Skill Demand in India's Job Market")

st.markdown("""
Explore and filter job postings to find relevant roles based on various criteria.
Use the sidebar filters to narrow down your search and gain insights into job market trends.
""")

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

selected_companies = st.sidebar.multiselect(
    "Select Companies",
    options=sorted(df['Company'].dropna().unique().tolist())
)

selected_locations = st.sidebar.multiselect(
    "Select Locations",
    options=sorted(df['Location'].dropna().unique().tolist())
)

# Experience Filter (Min/Max)
min_exp_overall = int(df['Min_Experience'].min())
max_exp_overall = int(df['Max_Experience'].max())
experience_range = st.sidebar.slider(
    "Experience Range (Years)",
    min_value=min_exp_overall,
    max_value=max_exp_overall,
    value=(min_exp_overall, max_exp_overall)
)

# Skills and Skill Type Filters
all_skills = sorted(list(set(skill for sublist in df['Skill_List'] for skill in sublist)))
selected_skills = st.sidebar.multiselect("Select Required Skills", options=all_skills)

all_skill_types = sorted(list(set(stype for sublist in df['Skill_Type_List'] for stype in sublist)))
selected_skill_types = st.sidebar.multiselect("Select Skill Types", options=all_skill_types)

job_title_search = st.sidebar.text_input("Search Job Title (keywords)", help="Enter keywords to search within job titles.")

posted_options = ["Any", "1 day ago", "1 week ago", "2 weeks ago", "3+ weeks ago"]
selected_posted = st.sidebar.selectbox("When Posted", options=posted_options)

# --- Apply Filters ---
filtered_df = df.copy()

if selected_companies:
    filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]

if selected_locations:
    filtered_df = filtered_df[filtered_df['Location'].isin(selected_locations)]

filtered_df = filtered_df[
    (filtered_df['Min_Experience'] >= experience_range[0]) &
    (filtered_df['Max_Experience'] <= experience_range[1])
]

if selected_skills:
    filtered_df = filtered_df[filtered_df['Skill_List'].apply(lambda x: any(skill in x for skill in selected_skills))]

if selected_skill_types:
    filtered_df = filtered_df[filtered_df['Skill_Type_List'].apply(lambda x: any(stype in x for stype in selected_skill_types))]

if job_title_search:
    filtered_df = filtered_df[filtered_df['Job Title'].str.contains(job_title_search, case=False, na=False)]

if selected_posted != "Any":
    if selected_posted == "1 day ago":
        filtered_df = filtered_df[filtered_df['Posted'].str.contains("1 day ago", case=False, na=False)]
    elif selected_posted == "1 week ago":
        filtered_df = filtered_df[filtered_df['Posted'].str.contains("1 week ago", case=False, na=False)]
    elif selected_posted == "2 weeks ago":
        filtered_df = filtered_df[filtered_df['Posted'].str.contains("2 weeks ago", case=False, na=False)]
    elif selected_posted == "3+ weeks ago":
        # This logic for "3+ weeks ago" is an approximation.
        # It tries to catch anything older than 2 weeks by looking for "days ago" or "weeks ago"
        # but explicitly excluding the "1 day", "1 week", "2 weeks" exact matches.
        filtered_df = filtered_df[
            filtered_df['Posted'].str.contains(r'(\d+\s(days?|weeks?)\sago)', case=False, na=False) &
            ~filtered_df['Posted'].str.contains("1 day ago|1 week ago|2 weeks ago", case=False, na=False)
        ]


# --- Display Filtered Jobs ---
st.subheader("Filtered Job Postings")

if not filtered_df.empty:
    st.write(f"Showing **{len(filtered_df)}** relevant job postings.")
    st.dataframe(filtered_df[['Job Title', 'Company', 'Location', 'Experience', 'Posted', 'Description', 'Skills']], use_container_width=True)
else:
    st.info("No job postings match your selected criteria. Try adjusting the filters.")

st.markdown("---")

# --- Insights Section ---
st.subheader("Job Market Insights")

if not filtered_df.empty:
    # Row 1: Top Job Titles, Top Locations
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Top 10 Job Titles:") # Increased to top 10 for more detail
        top_titles = filtered_df['Job Title'].value_counts().head(10)
        if not top_titles.empty:
            st.bar_chart(top_titles)
        else:
            st.info("No data for job titles.")

    with col2:
        st.write("### Top 10 Locations:") # Increased to top 10 for more detail
        top_locations = filtered_df['Location'].value_counts().head(10)
        if not top_locations.empty:
            st.bar_chart(top_locations)
        else:
            st.info("No data for locations.")

    st.markdown("---")

    # Row 2: Top Companies, Experience Level Distribution
    col3, col4 = st.columns(2)

    with col3:
        st.write("### Top 10 Companies by Job Postings:")
        top_companies = filtered_df['Company'].value_counts().head(10)
        if not top_companies.empty:
            st.bar_chart(top_companies)
        else:
            st.info("No data for companies.")

    with col4:
        st.write("### Job Postings by Experience Level:")
        # Order the experience bands for better visualization
        experience_band_order = ["0-2 Years (Entry)", "3-5 Years (Junior/Mid)", "6-8 Years (Mid/Senior)",
                                 "9-12 Years (Senior)", "12+ Years (Lead/Architect)", "Not Specified"]
        experience_counts = filtered_df['Experience_Band'].value_counts().reindex(experience_band_order, fill_value=0)

        if not experience_counts.empty and experience_counts.sum() > 0:
            st.bar_chart(experience_counts)
        else:
            st.info("No experience level data available for current filters.")

    st.markdown("---")

    # Row 3: Top Skills, Skill Type Distribution (Pie Chart)
    col5, col6 = st.columns(2)

    with col5:
        all_skills_filtered = [skill for sublist in filtered_df['Skill_List'] for skill in sublist]
        if all_skills_filtered:
            skill_counts = Counter(all_skills_filtered)
            top_skills_df = pd.DataFrame(skill_counts.most_common(10), columns=['Skill', 'Count'])
            st.write("### Top 10 Most Demanded Skills:")
            st.bar_chart(top_skills_df.set_index('Skill'))
        else:
            st.info("No skill data available for current filters.")

    with col6:
        all_skill_types_filtered = [stype for sublist in filtered_df['Skill_Type_List'] for stype in sublist]
        if all_skill_types_filtered:
            skill_type_counts = Counter(all_skill_types_filtered)
            skill_type_df = pd.DataFrame(skill_type_counts.items(), columns=['Skill Type', 'Count'])

            st.write("### Distribution of Skill Types (Proportion):")
            # Using matplotlib/seaborn for a pie chart as Streamlit's native doesn't support it directly
            fig, ax = plt.subplots(figsize=(8, 8))
            # Sort for consistent slice order, plot only if count > 0
            skill_type_df_filtered = skill_type_df[skill_type_df['Count'] > 0].sort_values(by='Count', ascending=False)
            if not skill_type_df_filtered.empty:
                ax.pie(skill_type_df_filtered['Count'], labels=skill_type_df_filtered['Skill Type'], autopct='%1.1f%%', startangle=90,
                       pctdistance=0.85, wedgeprops={'edgecolor': 'white'})
                ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
                # Add a circle at the center to make it a donut chart
                centre_circle = plt.Circle((0,0),0.70,fc='white')
                fig.gca().add_artist(centre_circle)
                st.pyplot(fig)
            else:
                st.info("No skill type data available to plot.")
        else:
            st.info("No skill type data available.")

else:
    st.info("Apply filters above to see visual analytics.")
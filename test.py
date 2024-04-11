import streamlit as st
import requests
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
import pdfplumber
from bs4 import BeautifulSoup
import hashlib

# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(groq_api_key=groq_api_key, model_name='mixtral-8x7b-32768', temperature=0)

# Function to extract text from PDF
def extract_text_from_pdf(filename):
    text = ""
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to extract job location from HTML
def extract_job_location(soup):
    job_location = soup.find('span', class_='aside-job-card__location')
    if job_location:
        return job_location.text.strip()
    else:
        return "Location Not Available"
    
def extract_job_title(soup):
    job_title = soup.title
    if job_title:
        return job_title.text.strip()
    else:
        return "Job Title Not Available"

# Function to extract job description from HTML
def extract_job_description(soup):
    job_description = soup.find('div', class_='show-more-less-html__markup')
    if job_description:
        return job_description.text.strip()
    else:
        return "Description Not Available"

# Function to extract salary information from HTML
def extract_salary(soup):
    salary_element = soup.find('div', class_='salary compensation__salary')
    if salary_element:
        return salary_element.text.strip()
    else:
        return "Salary Not Available"

# Function to extract job criteria from HTML
def extract_job_criteria(soup):
    job_criteria = {}
    criteria_items = soup.find_all('li', class_='description__job-criteria-item')
    for item in criteria_items:
        subheader = item.find('h3', class_='description__job-criteria-subheader').text.strip()
        text = item.find('span', class_='description__job-criteria-text').text.strip()
        job_criteria[subheader] = text
    return job_criteria

class SessionState:
    def __init__(self, **kwargs):
        self.hash_funcs = {"md5": hashlib.md5, "sha1": hashlib.sha1}
        self.cache = {}
        self.update(kwargs)

    def update(self, new_state):
        self.cache.update(new_state)

    def clear(self):
        self.cache.clear()

    def _get_cache_key(self, prefix=""):
        key = st.session_state.session_id
        if prefix:
            key = f"{prefix}_{key}"
        return key

    def __getitem__(self, item):
        return self.cache.get(self._get_cache_key(item), None)

    def __setitem__(self, item, value):
        self.cache[self._get_cache_key(item)] = value

def main():
    st.set_page_config(page_title="LinkedIn Job Details Extractor", page_icon=":briefcase:", layout="wide", initial_sidebar_state="expanded")

    st.title("LinkedIn Job Details Extractor")
    st.subheader("Upload PDF file and enter LinkedIn job URL")

    session_state = SessionState()

    extract_button = False
    compare_button = False

    # File uploader
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file is not None:
        # Read and extract text from the uploaded PDF file
        session_state.resume_text = extract_text_from_pdf(uploaded_file)
        # Display the extracted text
        st.success("Resume Details Extracted")

    # URL input field
    url = st.text_input("Enter LinkedIn job URL:")
    # Button for triggering extraction
    extract_button = st.button("Extract Details")
    if extract_button:
        if url:
            # Fetch webpage content
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract job title
            job_title = extract_job_title(soup)

            # Extract job location
            job_location = extract_job_location(soup)

            # Extract job description
            job_description = extract_job_description(soup)

            # Extract job criteria
            job_criteria = extract_job_criteria(soup)

            # Extract salary information
            salary = extract_salary(soup)

            # Display output in columns with wider job description area
            col1, col2 = st.columns([1, 3])  # Adjusted the ratio to 1:3

            with col1:
                
                st.markdown("## Job Title:")
                st.write(job_title)

                st.markdown("## Job Location:")
                st.write(job_location)

                st.markdown("## Salary:")
                st.write(salary)

                # Display job criteria
                st.markdown("## Job Criteria:")
                for key, value in job_criteria.items():
                    st.write(f"**{key}:** {value}")

            with col2:
                st.markdown("## Job Description:")
                st.write(job_description)
                if(job_description=="Description Not Available"):
                    st.write("Cannot Compare as Job Description is not available")
                   
                else:
                    with st.spinner(text="Comparison In progress..."):
                # Agent and Task execution
                        Problem_Definition_Agent = Agent(
                        role='talent assessment analyst',
                        goal="""Provide a comprehensive score for matching the job description summary with the candidate's resume summary. Identify the matching scores for each required hard skill (technical skills) and soft skill, and list the skills that don't match. Offer recommendations to the candidate to enhance their hard skills and soft skills, and align better with the job requirements.""",
                        backstory="""As an expert in talent assessment, your task is to evaluate the candidate's resume summary with respect to both hard skills (technical skills) and soft skills in relation to the provided job description. You aim to provide actionable insights to the candidate to ensure the best fit for the role.""",
                        verbose=False,
                        allow_delegation=False,
                        llm=llm,
                        )

                        task_define_problem = Task(
                        description="""Compare the hard skills (technical skills) and soft skills mentioned in the job description with those present in the candidate's resume.
                                        Assess the level of match between the candidate's skills and the required skills for the job.
                                        For each required hard skill and soft skill, provide a matching score on a scale of 0 to 5 based on how well the skill is covered in the candidate's resume.
                                        Identify any skills (both hard and soft) that don't match and list them.
                                        Offer constructive recommendations for the candidate to improve their hard skills and soft skills, and better align with the job requirements.

                                        Here is the resume:

                                        {resume_sum}

                                        Here is the job description:

                                        {job_sum}
                                        """.format(resume_sum=session_state.resume_text, job_sum=job_description),
                                            agent=Problem_Definition_Agent,
                                            expected_output="""Give the matching scores for hard skills and soft skills using the following format:
                                                                Hard Skills Matching:
                                                                - Skill 1 (Matching Score: x/5)
                                                                - Skill 2 (Matching Score: y/5)
                                                                ...
                                                                Overall Hard Skills Matching Score: z/5

                                                                Soft Skills Matching:
                                                                - Skill 1 (Matching Score: a/5)
                                                                - Skill 2 (Matching Score: b/5)
                                                                ...
                                                                Overall Soft Skills Matching Score:
                                                            """
                                            )

                        verification_task = Task(
                        description="""Verify the correctness of the output provided by the task_define_problem task and provide a comprehensive score for matching the job description summary with the candidate's resume summary. Identify the matching scores for each required hard skill (technical skill) and soft skill, and list the skills that don't match. Offer recommendations to the candidate to enhance their hard skills and soft skills, and align better with the job requirements.""",
                        agent=Problem_Definition_Agent,
                        expected_output="""Provide a summary of the verification results, similar to the output of task_define_problem:
                        - Overall Matching: Overall matching score between the job description summary and the candidate's resume summary.
                        - Matching Hard Skills: List of hard skills (technical skills) and their matching scores.
                        - Non-matching Hard Skills: List of hard skills that don't match.
                        - Matching Soft Skills: List of soft skills and their matching scores.
                        - Non-matching Soft Skills: List of soft skills that don't match.
                        - Recommendations: Recommendations for the candidate to enhance their hard skills and soft skills, and align better with the job requirements."""
                        )

                        table_task = Task(
                        description="""Using the output from the previous tasks, understand the information and create the following tables:
                                        1. Table of matching hard skills (technical skills) and their matching scores with remarks.
                                        2. Table of non-matching hard skills with remarks.
                                        3. Table of matching soft skills and their matching scores with remarks.
                                        4. Table of non-matching soft skills with remarks.
                                        Additionally, include the recommendations for the candidate to improve their hard skills and soft skills.""",
                        agent=Problem_Definition_Agent,
                        expected_output="""Provide four tables:
                                            1. Table containing matching hard skills and their matching scores with remarks.
                                            2. Table containing non-matching hard skills with remarks.
                                            3. Table containing matching soft skills and their matching scores with remarks.
                                            4. Table containing non-matching soft skills with remarks.
                                            Additionally, include recommendations for the candidate."""
                                    )

                        crew = Crew(agents=[Problem_Definition_Agent], tasks=[task_define_problem, verification_task,table_task], verbose=2)
                        result = crew.kickoff()
                        st.write(result)
                        st.button("Extract Another Job")
    

if __name__ == "__main__":
    main()

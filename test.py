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
import json

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

def main():
    st.set_page_config(page_title="LinkedIn Job Details Extractor", page_icon=":briefcase:", layout="wide", initial_sidebar_state="expanded")

    st.title("LinkedIn Job Details Extractor")
    st.subheader("Upload PDF file and enter LinkedIn job URL")

    extract_button = False
    compare_button = False

    # File uploader
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file is not None:
        # Read and extract text from the uploaded PDF file
        pdf_text = extract_text_from_pdf(uploaded_file)
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
                                    goal="""Provide a comprehensive score for matching the candidate's resume summary with the job description summary. Identify the percentage of matching for each required skill and list the skills that don't match. Offer recommendations to the candidate to enhance their skills and align better with the job requirements.""",
                                    backstory="""As an expert in talent assessment, your task is to evaluate the candidate's resume summary in relation to the provided job description. You aim to provide actionable insights to the candidate to ensure the best fit for the role.""",
                                    verbose=False,
                                    allow_delegation=False,
                                    llm=llm,
                                 )

                            task_define_problem = Task(
                                    description="""Review the candidate's resume summary and the job description summary.
                                    Assess the level of match between the candidate's skills and the required skills for the job.
                                    Provide a percentage score indicating the overall match between the two summaries.
                                    Club together similar skills to provide a more holistic view of the candidate's capabilities (e.g., Ansible and Chef, C++ and Java).
                                    For each required skill Calculate the matching percentage.
                                    Identify any skills that don't match and list them.
                                    Offer constructive recommendations for the candidate to improve their skills and better align with the job requirement. Summary not required.
                            
            
                                    Here is the resume:

                                    {resume_sum}

                                    Here is the job description:

                                    {job_sum}
                                    """.format(resume_sum=pdf_text, job_sum=job_description),
                                    agent=Problem_Definition_Agent,
                                    expected_output={
                                        "Matching Skills": {},
                                        "Non Matching Skills": {}
                                    }
                                    )

                            crew = Crew(agents=[Problem_Definition_Agent], tasks=[task_define_problem])
                            result = crew.kickoff()
                            st.write(result)

if __name__ == "__main__":
    main()

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
import pdfplumber
import requests
from bs4 import BeautifulSoup


url="https://www.linkedin.com/jobs/view/3853160557/?eBP=CwEAAAGOr_iaro8JqOgaVnUO2JGJTkniFtaUJn5sTloUPV2d2G8g8O_0pXZDSXGJ36VjsSs7wFl3yT8eUsc6OIEXeNGuUhEJXPZayeoJQdM2nTD3QPKiqEO__M84FaaFYs0kRyb1uJgn0eCBamF2wTkubCy0oCYzfzH8wSWyuI5v27OmGUpXVuKKDX1esVxF4R7BiDEZWYr94-satk-WaqHu4l10QMgt0AwFmWKTJbKEVHu00QOW3YyFjFoWXWvgXQWWZ_sYO-SKxbyPMoDaRmYILgtvlHYLzSjTqZKoCXIbLi8RC3fPyjon5vgiRVEJwQ92m3LPoERaTDwmVhrh2SXQEjkMImBf8PAgsUbp5LGk2aQVuBdAoe4kZOugJK2A&refId=c38V53%2Fpm1teU14RpoRnXg%3D%3D&trackingId=KyXjIUX0fxAE4L22bTNH2Q%3D%3D&trk=flagship3_jobs_discovery_jymbii"
response = requests.get(url)
def extract_job_location(soup):
    job_location = soup.find('span', class_='aside-job-card__location')
    if job_location:
        return job_location.text.strip()
    else:
        return "Location Not Available"

def extract_job_description(soup):
    job_description = soup.find('div', class_='show-more-less-html__markup')
    if job_description:
        return job_description.text.strip()
    else:
        return "Description Not Available"

def extract_salary(soup):
    salary_element = soup.find('div', class_='salary compensation__salary')
    if salary_element:
        return salary_element.text.strip()
    else:
        return "Salary Not Available"

def extract_job_criteria(soup):
    job_criteria = {}
    criteria_items = soup.find_all('li', class_='description__job-criteria-item')
    for item in criteria_items:
        subheader = item.find('h3', class_='description__job-criteria-subheader').text.strip()
        text = item.find('span', class_='description__job-criteria-text').text.strip()
        job_criteria[subheader] = text
    return job_criteria

def extract_text_from_pdf(filename):
    text = ""
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

soup = BeautifulSoup(response.text, 'html.parser')

job_location = extract_job_location(soup)

job_description = extract_job_description(soup)

job_criteria = extract_job_criteria(soup)

salary = extract_salary(soup)

print(job_description)

# Example usage
pdf_text = extract_text_from_pdf("DevOps_Resume.pdf")
print(pdf_text)

# Load environment variables


load_dotenv()

groq_api_key = os.environ['GROQ_API_KEY']



llm = ChatGroq(groq_api_key=groq_api_key,
               model_name='mixtral-8x7b-32768',temperature=0,max_tokens=32768,max_retries=4)



Problem_Definition_Agent = Agent(
        role='Resume and Job Description Analyser',
        goal="""Provide a comprehensive score for matching the candidate's resume summary with the job description summary. Identify the percentage of matching for each required skill and list the skills that don't match. Offer recommendations to the candidate to enhance their skills and align better with the job requirements.""",
        backstory="""As an expert in talent assessment, your task is to evaluate the candidate's resume summary in relation to the provided job description. You aim to provide actionable insights to both the candidate and the hiring team to ensure the best fit for the role.""",
        
        
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
task_define_problem = Task(
        description="""Review the candidate's resume summary and the job description summary.
                        Assess the level of match between the candidate's skills and the required skills for the job.
                        Provide a percentage score indicating the overall match between the two summaries.
                        For each required skill:
                        Calculate the matching percentage.
                        Identify any skills that don't match and list them. 
                        Offer constructive recommendations for the candidate to improve their skills and better align with the job requirements.
            
            Here is the resume:

            {resume_sum}

            Here is the job description:

            {job_sum}
            """.format(resume_sum=pdf_text,job_sum=job_description),
        agent=Problem_Definition_Agent,
        expected_output="""Overall matching score between the resume summary and the job description summary.
Matching percentage for each required skill.
List of skills that don't match the job requirements.
Recommendations for the candidate to enhance their skills and increase alignment with the job description."""
        )
table_task= Task(description="""Using the output of task_define_problem task understand the information and put it in two tables one table of maching skills another of non-matching skills with the percentages and remarks in both the tables"""")
crew = Crew(
            agents=[Problem_Definition_Agent], #, Summarization_Agent],
            tasks=[task_define_problem], #, task_summarize],
            verbose=2
        )
result = crew.kickoff()
print(result)



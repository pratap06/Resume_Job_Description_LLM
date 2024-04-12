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
import datetime
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
import base64

# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(groq_api_key=groq_api_key, model_name='mixtral-8x7b-32768', temperature=0)


# Define the JSON format as a string
output_format = '''{
    "Overall_Matching": {
        "Score": "Overall matching score",
        "Remark": "Overall matching remarks"
    },
    "Matching_Hard_Skills": [
        {
            "Skill": "Skill1",
            "Matching_Score": "Matching score",
            "Remark": "Matching remarks"
        },
        {
            "Skill": "Skill2",
            "Matching_Score": "Matching score",
            "Remark": "Matching remarks"
        },
        ...
    ],
    "Non_matching_Hard_Skills": [
        {
            "Skill": "Skill1",
            "Matching_Score": "Matching score",
            "Remark": "Matching remarks"
        },
        {
            "Skill": "Skill2",
            "Matching_Score": "Matching score",
            "Remark": "Matching remarks"
        },
        ...
    ],
    "Matching_Soft_Skills": [
        {
            "Skill": "Skill1",
            "Matching_Score": "Matching score",
            "Remark": "Matching remarks"
        },
        {
            "Skill": "Skill2",
            "Matching_Score": "Matching score",
            "Remark": "Matching remarks"
        },
        ...
    ],
    "Non_matching_Soft_Skills": [
        {
            "Skill": "Skill1",
            "Matching_Score": "Matching score",
            "Remark": "Matching remarks"
        },
        {
            "Skill": "Skill2",
            "Matching_Score": "Matching score",
            "Remark": "Matching remarks"
        },
        ...
    ],
    "Recommendations": "Provide recommendations for improvement."
}'''

# Combine all DataFrames into a single DataFrame
def combine_dataframes(df_overall, df_matching_hard_skills, df_matching_soft_skills, df_non_matching_hard_skills, df_non_matching_soft_skills):
    # Merge DataFrames on Skill column
    df = pd.concat([df_overall, df_matching_hard_skills, df_matching_soft_skills, df_non_matching_hard_skills, df_non_matching_soft_skills])
    return df

def plot_horizontal_bar(df, title):
    # Set Seaborn style
    sns.set_theme(style="whitegrid")

    # Initialize the matplotlib figure
    f, ax = plt.subplots(figsize=(10, 6))

    # Convert Matching_Score to integer
    df['Matching_Score'] = df['Matching_Score'].astype(int)
     # Sort the DataFrame by "Matching_Score" column in descending order
    df = df.sort_values(by="Matching_Score", ascending=False)

    # Plot horizontal bar chart
    sns.barplot(x="Matching_Score", y="Skill", data=df, palette="viridis", orient='h')

    # Set x-axis limits
    plt.xlim(0, 5)

    # Add labels and title
    plt.xlabel('Matching Score')
    plt.ylabel('Skill')
    plt.title(title)

    # Show the plot
    st.pyplot(f)


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


def main():
    st.set_page_config(page_title="LinkedIn Job Details Extractor", page_icon=":briefcase:", layout="wide", initial_sidebar_state="expanded")

    st.title("LinkedIn Job Details Extractor")
    st.subheader("Upload PDF file and enter LinkedIn job URL")

    

    extract_button = False

    # File uploader
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file is not None:
        # Read and extract text from the uploaded PDF file
        resume_text = extract_text_from_pdf(uploaded_file)
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
                    st.write("Cannot Compare as Job Description is not available due to javascript block from LinkedIn, Retry Again By Clicking Extract Details Button")
                   
                else:
                    with st.spinner(text="Comparison In progress..."):
                        # Agent and Task execution
                        Problem_Agent = Agent(
                            role='talent assessment analyst',
                            goal="""Provide a comprehensive score for matching the job description summary with the candidate's resume summary. Identify the matching scores for each required hard skill (technical skills) and soft skill, and list the skills that don't match. Offer recommendations to the candidate to enhance their hard skills and soft skills, and align better with the job requirements.""",
                            backstory="""As an expert in talent assessment, your task is to evaluate the candidate's resume summary with respect to both hard skills (technical skills) and soft skills in relation to the provided job description with the remarks for each. You aim to provide actionable insights to the candidate to ensure the best fit for the role.""",
                            verbose=False,
                            allow_delegation=False,
                            llm=llm,
                        )

                        task_define_problem = Task(
                        description='''Find hard skills (technical skills) and soft skills then Compare the hard skills (technical skills) and soft skills mentioned in the job description with those present in the candidate's resume.
                                        Assess the level of match between the candidate's skills and the required skills for the job.
                                        For each required hard skill and soft skill, provide a matching score on a scale of 0 to 10 based on how well the skill is covered in the candidate's resume with remark for each which tells where exactly it matched with job description.
                                        Identify any skills (both hard and soft) that don't match and list them with remark for each which tells why it didn't match with job description.
                                        Find Overall match on the scale of 0 to 10
                                        Offer constructive recommendations for the candidate to improve their hard skills and soft skills, and better align with the job requirements.

                                        Here is the resume:

                                        {resume_sum}

                                        Here is the job description:

                                        {job_sum}
                                         
                                        and summary of your work is not required

                                        The output should be provided in JSON format, structured as follows:
                                        
                                        {output}
                                    
                                        '''.format(resume_sum=resume_text, job_sum=job_description, output=output_format),
                                            agent=Problem_Agent,
                                            expected_output={output_format}
                                        
                                        
                                        )


                        crew = Crew(agents=[Problem_Agent], tasks=[task_define_problem], verbose=2)
                        result = crew.kickoff()

                        
                        

                        print(result)
                        # Check if the string starts and ends with double quotes
                        
                        #parsed_data = json.loads(result)
                        #print(parsed_data)
                        # Split the text into individual JSON objects
                        # Find the position of the first curly brace
                        
                        start_index = result.find('{')

                        # Find the position of the last curly brace
                        end_index = result.rfind('}')

                        # Extract the JSON string
                        json_data = result[start_index:end_index+1].strip()
                        data = json.loads(json_data)
                        #print(parsed_data)

                        # Extract Overall Matching
                        overall_matching_df = pd.DataFrame({
                            "Score": [data["Overall_Matching"]["Score"]],
                            "Remark": [data["Overall_Matching"]["Remark"]]
                        })

                        recommendations = data["Recommendations"]

                        # Extract Matching Hard Skills
                        matching_hard_skills_df = pd.DataFrame(data["Matching_Hard_Skills"])

                        # Extract Matching Soft Skills
                        matching_soft_skills_df = pd.DataFrame(data["Matching_Soft_Skills"])

                        # Extract Non-matching Hard Skills
                        non_matching_hard_skills_df = pd.DataFrame(data.get("Non_matching_Hard_Skills", []))

                        # Extract Non-matching Soft Skills
                        non_matching_soft_skills_df = pd.DataFrame(data.get("Non_matching_Soft_Skills", []))

                        # Combine all DataFrames
                        combined_df = combine_dataframes(overall_matching_df, matching_hard_skills_df, matching_soft_skills_df, non_matching_hard_skills_df, non_matching_soft_skills_df)

                        combined_df = combined_df.reindex(columns=["Skill", "Matching_Score", "Remark", "Overall_Score"])

                        # Print DataFrames
                        
                        st.write("Overall Score:")
                        st.dataframe(overall_matching_df)
                        
                        st.write("Matching Hard Skills:")
                        st.dataframe(matching_hard_skills_df)

                        st.write("Matching Soft Skills:")
                        st.dataframe(matching_soft_skills_df)
                        
                        st.write("Non Matching Hard Skills:")
                        st.dataframe(non_matching_hard_skills_df)

                        st.write("Non Matching Soft Skills:")
                        st.dataframe(non_matching_soft_skills_df)

                        st.write("Recommendations:")
                        st.write(recommendations)

                        # Convert DataFrame to CSV string
                        csv = combined_df.to_csv(index=False)

                        # Convert CSV string to bytes
                        csv_bytes = csv.encode()
    
                        # Get current date and time
                        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                        
                        # Construct dynamic file name with prefix and current date and time
                        file_name = f"Resume_Job_Report_{current_datetime}_sample.csv"

                        # Button to download CSV
                        st.write("To Download the Report")
                        st.download_button(
                            label="Download CSV",
                            data=csv_bytes,
                            file_name=file_name,
                            mime='text/csv'
                            )

                       
                        
                        

if __name__ == "__main__":
    main()

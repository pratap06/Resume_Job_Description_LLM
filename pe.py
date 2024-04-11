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
import json
import re
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(groq_api_key=groq_api_key, model_name='mixtral-8x7b-32768', temperature=0)

Problem_Agent = Agent(
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
                                         
                                        and summary of your work is not required

                                        The output should be provided in JSON format, structured as follows:
                                            "Overall_Matching": "Provide the overall matching score between the job description summary and the candidate's resume summary.",
                                            "Matching_Hard_Skills": "Provide matching hard skills with their respective matching scores.",
                                            "Non_matching_Hard_Skills": "Provide non-matching hard skills.",
                                            "Matching_Soft_Skills": "Provide matching soft skills with their respective matching scores.",
                                            "Non_matching_Soft_Skills": "Provide non-matching soft skills.",
                                            "Recommendations": "Provide recommendations for the candidate to enhance their hard skills and soft skills, and align better with the job requirements."

                                        make sure to keep consistent json format throughout
                                        
                                        
                                        """.format(resume_sum=session_state.resume_text, job_sum=job_description),
                                            agent=Problem_Agent,
                                            expected_output="""Provide the output in JSON format, structured as follows:
                                        {
                                            "Overall_Matching": "Provide the overall matching score between the job description summary and the candidate's resume summary.",
                                            "Matching_Hard_Skills": "Provide matching hard skills with their respective matching scores.",
                                            "Non_matching_Hard_Skills": "Provide non-matching hard skills.",
                                            "Matching_Soft_Skills": "Provide matching soft skills with their respective matching scores.",
                                            "Non_matching_Soft_Skills": "Provide non-matching soft skills.",
                                            "Recommendations": "Provide recommendations for the candidate to enhance their hard skills and soft skills, and align better with the job requirements."
                                        }"""
                                        )


                        crew = Crew(agents=[Problem_Agent], tasks=[task_define_problem], verbose=2)
                        result = crew.kickoff()
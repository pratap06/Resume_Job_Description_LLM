import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



result=""""{ "Overall_Matching": "4.5", "Matching_Hard_Skills": { "Python": "5", "Terraform": "5", "Ansible": "5", "Public Cloud Azure": "5", "Jenkins": "5", "CI/CD pipeline": "5", "Azure DevOps": "5", "Azure SQL DB": "5", "Tableau": "4", "Docker": "4", "Kubernetes": "4", "Azure AD": "3", "IaaS": "3", "Containers": "3", "Storage": "3", "Networking": "3" }, "Non_matching_Hard_Skills": { "PowerShell": "0", "Logic Apps": "0", "Azure Monitor": "0", "Dynatrace": "0", "PagerDuty": "0", "Splunk": "0", "Postman": "0", "VS Code": "0", "Infrastructure and Security": "0" }, "Matching_Soft_Skills": { "Collaboration": "5", "Communication": "5", "Problem Solving": "5", "Leadership": "4", "Adaptability": "4", "Time Management": "4" }, "Non_matching_Soft_Skills": { "Project Management": "0" }, "Recommendations": "Consider gaining experience with PowerShell, Logic Apps, Azure Monitor, Dynatrace, PagerDuty, Splunk, Postman, VS Code, and Infrastructure and Security. Additionally, work on project management skills to better align with the job requirements." }

This is the summary of your work so far:

The candidate has strong technical skills in Python, Terraform, Ansible, Azure, Jenkins, CI/CD pipelines, Azure DevOps, Azure SQL DB, Tableau, Docker, and Kubernetes.
The candidate lacks experience in PowerShell, Logic Apps, Azure Monitor, Dynatrace, PagerDuty, Splunk, Postman, VS Code, and Infrastructure and Security. These skills can be learned through online courses, tutorials, or on-the-job training.
The candidate has strong soft skills in collaboration, communication, problem-solving, leadership, adaptability, and time management.
The candidate lacks experience in project management, which can be improved through online courses, certifications, or on-the-job training.
The candidate is recommended to gain experience in the missing hard skills and improve project management skills to better align with the job requirements."""

start_index = result.find('{')

# Find the position of the last curly brace
end_index = result.rfind('}')

# Extract the JSON string
json_data = result[start_index:end_index+1].strip()
# Parse the JSON data
parsed_data = json.loads(json_data)

import json

result='''{
    "Overall_Matching": {
        "Score": "4.5",
        "Remark": "The candidate has strong technical skills and relevant work experience. However, there is a slight mismatch in some of the required soft skills."
    },
    "Matching_Hard_Skills": [
        {
            "Skill": "Python",
            "Matching_Score": "5",
            "Remark": "Python is one of the main technical skills mentioned in the candidate's resume and has been used extensively in past projects and work experience."
        },
        {
            "Skill": "SQL",
            "Matching_Score": "5",
            "Remark": "The candidate has solid experience using SQL, as demonstrated in the work experience and projects sections of the resume."
        },
        {
            "Skill": "Azure DevOps",
            "Matching_Score": "5",
            "Remark": "Azure DevOps is a key skill mentioned in the candidate's resume, with extensive experience in using it for CI/CD pipelines, cloud cost optimization, and managing support tickets."
        },
        {
            "Skill": "Terraform",
            "Matching_Score": "5",
            "Remark": "The candidate has experience using Terraform for automating banking application deployment and optimizing CI/CD pipelines."
        },
        {
            "Skill": "Jenkins",
            "Matching_Score": "4",
            "Remark": "Jenkins is mentioned in the candidate's resume, but the experience seems to be limited to a single project."
        },
        {
            "Skill": "Cloud Provider Experience (AWS)",
            "Matching_Score": "5",
            "Remark": "The candidate has extensive experience working with AWS, as demonstrated in the work experience and projects sections of the resume."
        }
    ],
    "Non_matching_Hard_Skills": [
        {
            "Skill": "Apache Airflow",
            "Matching_Score": "0",
            "Remark": "The candidate does not mention Apache Airflow in their resume."
        },
        {
            "Skill": "Snowflake",
            "Matching_Score": "0",
            "Remark": "The candidate does not mention Snowflake in their resume."
        },
        {
            "Skill": "dbt",
            "Matching_Score": "0",
            "Remark": "The candidate does not mention dbt in their resume."
        }
    ],
    "Matching_Soft_Skills": [
        {
            "Skill": "Collaboration",
            "Matching_Score": "5",
            "Remark": "The candidate has demonstrated the ability to collaborate effectively with various teams, as shown in the work experience section of the resume."
        },
        {
            "Skill": "Problem Solving",
            "Matching_Score": "5",
            "Remark": "The candidate has shown strong problem-solving skills in various projects and work experiences."
        },
        {
            "Skill": "Continuous Learning",
            "Matching_Score": "4",
            "Remark": "The candidate has taken several courses and certifications to improve their skills, but there is no clear evidence of continuous learning in the data space."
        }
    ],
    "Non_matching_Soft_Skills": [
        {
            "Skill": "Leadership",
            "Matching_Score": "0",
            "Remark": "The candidate does not mention any leadership experience in their resume."
        },
        {
            "Skill": "Mentoring",
            "Matching_Score": "0",
            "Remark": "The candidate does not mention any mentoring experience in their resume."
        }
    ],
    "Recommendations": "Consider gaining experience with Apache Airflow, Snowflake, and dbt to better align with the job requirements. Additionally, highlight any leadership or mentoring experience in the resume to improve the soft skills match."
}
'''
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

# Extract Matching Hard Skills
matching_hard_skills_df = pd.DataFrame(data["Matching_Hard_Skills"])

# Extract Matching Soft Skills
matching_soft_skills_df = pd.DataFrame(data["Matching_Soft_Skills"])

# Extract Non-matching Hard Skills
non_matching_hard_skills_df = pd.DataFrame(data.get("Non_matching_Hard_Skills", []))

# Extract Non-matching Soft Skills
non_matching_soft_skills_df = pd.DataFrame(data.get("Non_matching_Soft_Skills", []))

print(matching_hard_skills_df)



# Set Seaborn style
sns.set_theme(style="whitegrid")

# Initialize the matplotlib figure
f, ax = plt.subplots(figsize=(10, 6))
matching_hard_skills_df['Matching_Score'] = matching_hard_skills_df['Matching_Score'].astype(int)

# Plot horizontal bar chart
sns.barplot(x="Matching_Score", y="Skill", data=matching_hard_skills_df, palette="viridis", orient='h')

# Set x-axis limits
plt.xlim(0, 5)

# Add labels and title
plt.xlabel('Matching Score')
plt.ylabel('Skill')
plt.title('Matching Hard Skills')

# Show the plot
plt.show()










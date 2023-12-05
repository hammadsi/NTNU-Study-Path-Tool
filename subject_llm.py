# recommendation_system.py
import os
from flask import Flask, render_template, request, redirect, url_for, session
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from pymongo import MongoClient
import config  # Import config file

# Your MongoDB connection information
mongo_uri = config.MONGO_URI
database_name = "recommendation_system"
collection_name = "users_survey_data"

# Create a MongoClient
client = MongoClient(mongo_uri)

# Connect to the database and collection
db = client[database_name]
collection = db[collection_name]
#user_email=str("test5@gmail.com")

def get_subject_name(user_email,user_course_name,formatted_courses):
    
    # Define a function to extract subject data from your formatted course data
    def get_subject_data(semester: str, course_name: str, subjects: List[dict]) -> List[str]:
        subject_data = []
        for subject in subjects:
            subject_name = subject['subject_name']
            description = subject['description']
            subject_data.append(f"Semester: {semester}, Course Name: {course_name}, Subject Name: {subject_name}, Description: {description}")
        return subject_data
    
    
    def subject_Ai_model(subject_data,choose_flag=True):
        print("subject_data", subject_data)
        # Define a new Pydantic model with field descriptions.
        class CourseUser(BaseModel):

            if  choose_flag :
                subjects: str = Field(description=f"Which subject user will take from this : {user_course_name}")
                explanation: str = Field(description="A longer explanation for why this subject of course is recommended, based on the users input. Refer to the users answers.")
            
            elif choose_flag == False:
                
                subjects: str = Field(description=f"Which two subject user will take separated by comma from this : {user_course_name}")
                explanation: str = Field(description="separate explanation by comma for both two subjects of course is recommended, based on the users input. Refer to the users answers.")
        # Instantiate the parser with the new model.
        parser = PydanticOutputParser(pydantic_object=CourseUser)

        # Create a formatted string from subject_data
        subject_data_str = "\n".join(subject_data)

        # Include subject_data_str in your prompt
        prompt = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    f"Based on the user's answers, recommend a subject of course from the following options:\n{subject_data_str}\n"
                    "Please also explain why you recommend this field based on the user's input.\n{format_instructions}\n{question}"
                )
            ],
            input_variables=["question"],
            partial_variables={
                "format_instructions": parser.get_format_instructions(),
            }
        )

        chat_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=config.OPENAI_API_KEY,
            max_tokens=1000
        )

        # Query the MongoDB collection to get user data
        user_data = collection.find_one({"user_email": user_email})
        print(user_data)
        if user_data:
            # Prepare user's survey data
            initialInterest = user_data.get("initialInterest", "")
            techChallenges = user_data.get("techChallenges", "")
            proudProject = user_data.get("proudProject", "")
            aiInterest = user_data.get("aiInterest", "")
            dbInterest = user_data.get("dbInterest", "")
            seInterest = user_data.get("seInterest", "")
            algoInterest = user_data.get("algoInterest", "")
            longTermGoals = user_data.get("longTermGoals", "")
            
            user_input = f"""
                            What initially drew you to study computer science?
                            Answer: {initialInterest}
                            What kind of technical challenges excite you the most?
                            Answer: {techChallenges}
                            Describe a project you've worked on that you're particularly proud of and would like to do more of.
                            Answer: {proudProject}
                            What are your thoughts on the field of Artificial Intelligence? Does the field interest you? If so, what interests you about it and what do you think we could achieve with AI?
                            Answer: {aiInterest}
                            How important do you think data management is in today's world? Are you interested in databases or search algorithms? How can you see yourself working with data?
                            Answer: {dbInterest}
                            Do you enjoy working on larger projects as part of a team? Are you interested in the software development lifecycle? Do you like being handed specific tasks, and achieve results frequently?
                            Answer: {seInterest}
                            Do you find joy in problem-solving or optimizing for performance? Are you interested in the theoretical aspects of computing? Do you like working in detail for optimization or on a higher level for visible results?
                            Answer: {algoInterest}
                            Long-term Career Goals and Interests?
                            Answer: {longTermGoals}
                            """

            # Generate the input using the updated prompt.
            _input = prompt.format_prompt(question=user_input)

            try:
                output = chat_model(_input.to_messages())
                parsed = parser.parse(output.content)
                print(output)
                # Extracting course name and explanation
                subject_name = parsed.subjects
                explanation = parsed.explanation

                print("choose 2 subject-------------------",subject_name)
                print("choose 2 explaination-----------------",explanation)
         
                return [subject_name, explanation]

            except Exception as e:
                print("An error occurred when calling the OpenAI API:", e)
                return "Error", "Could not fetch recommendation."

    
    
    # Define a function to get recommendations for multiple semesters
    def get_recommendations_for_semesters(formatted_courses):
        # Define a list to store the results
        results = []

        # Iterate through semesters 5 to 9
        for semester_num in range(5, 9):
            # Find the relevant semester data
            semester_data = [entry for entry in formatted_courses if entry['semester'] == f'Semester {semester_num}']
            
            choose_flag=True

            if 'choose_1_subjects' in semester_data[0] and semester_data[0]['choose_1_subjects']:
                # Get subject data for choose_1_subjects
                subject_data = get_subject_data(semester_data[0]['semester'], semester_data[0]['course_name'], semester_data[0]['choose_1_subjects'])

            elif 'choose_2_subjects' in semester_data[0] and semester_data[0]['choose_2_subjects']:
                subject_data = get_subject_data(semester_data[0]['semester'], semester_data[0]['course_name'], semester_data[0]['choose_2_subjects'])
            
                choose_flag=False

            else:
             continue

                # Call your AI model and get subject_name and explanation
            subject_name, explanation = subject_Ai_model(subject_data,choose_flag)

                # Store the results in a dictionary
            result_dict = {
                    "semester": semester_data[0]['semester'],
                    "subject": subject_name,
                    "explanation": explanation
                }

                # Append the result to the results list
            results.append(result_dict)

        return results

    # Call the function with your formatted_courses and user_input
    results = get_recommendations_for_semesters(formatted_courses)

    # Print or use the results as needed
    print(results)

    return results
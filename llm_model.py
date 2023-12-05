import os
from typing import List

import config  # Import config file
from flask import Flask, redirect, render_template, request, session, url_for
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from pydantic import BaseModel, Field
from pymongo import MongoClient

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

def get_course_name(user_email):

    # Define a new Pydantic model with field descriptions.
    class CourseUser(BaseModel):
        course: str = Field(description="Which field of study user will take from this four: 1.Software Engineering 2.Databases and Search 3.Algorithms and Computers 4.Artificial Intelligence  Give any one")
        explanation: str = Field(description="A longer explanation for why this field of study is recommended, based on the users input. Refer to the users answers.")

    # Instantiate the parser with the new model.
    parser = PydanticOutputParser(pydantic_object=CourseUser)

    # Update the prompt to match the new query and desired format.
    prompt = ChatPromptTemplate(
        messages=[
            HumanMessagePromptTemplate.from_template(
                "Based on the user's answers, recommend a field of study from the following options: "
                "1. Software Engineering "
                "2. Databases and Search "
                "3. Algorithms and Computers "
                "4. Artificial Intelligence. "
                "Please also explain why you recommend this field based on the users input.\n{format_instructions}\n{question}"
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
        max_tokens=2000
    )

    # Query the MongoDB collection to get user data
    user_data = collection.find_one({"user_email": user_email})
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

            # Extracting course name and explanation
            course_name = parsed.course
            explanation = parsed.explanation

            return course_name, explanation

        except Exception as e:
            print("An error occurred when calling the OpenAI API:", e)
            return "Error", "Could not fetch recommendation."

def get_subject_name(user_email,user_course_name,formatted_courses):
    def get_semester_subjects(user_email,user_course_name,formatted_courses):
     # Iterate through the data and extract sentences and choose_1_subjects
        data=formatted_courses
        sentences_and_choose_1_subjects = []
        for entry in data:
            semester = entry['semester']
            course_name = entry['course_name']
            
            for subject in entry['mandatory_subjects']:
                subject_name = subject['subject_name']
                description = subject['description']
                sentences_and_choose_1_subjects.append(f"Semester: {semester}, Course Name: {course_name}, Subject Name: {subject_name}, Description: {description}")
            
            for choose_subject in entry['choose_1_subjects']:
                subject_name = choose_subject['subject_name']
                description = choose_subject['description']
                sentences_and_choose_1_subjects.append(f"Semester: {semester}, Course Name: {course_name}, Choose-1 Subject Name: {subject_name}, Description: {description}")


            
            for choose_subject in entry['choose_2_subjects']:
                subject_name = choose_subject['subject_name']
                description = choose_subject['description']
                sentences_and_choose_1_subjects.append(f"Semester: {semester}, Course Name: {course_name}, Choose-1 Subject Name: {subject_name}, Description: {description}")    


        return sentences_and_choose_1_subjects
    
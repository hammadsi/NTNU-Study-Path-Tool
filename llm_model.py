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
        max_tokens=1000
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



user_course_name=" Artificial Intelligence"
formatted_courses=[{'semester': 'Semester 1', 'course_name': 'default', 'mandatory_subjects': [{'subject_name': 'Examen Philosophicum', 'course_code': 'EXPH0006', 'description': 'This is a description of the course Examen Philosophicum.', 'course_link': 'https://www.ntnu.edu/studies/courses/EXPH0600/2023/1#tab=omEmnet'}, {'subject_name': 'Information Technology, basic course', 'course_code': 'TDT4110', 'description': 'This is a description of the course Information Technology, basic course.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4110#tab=omEmnet'}, {'subject_name': 'Mathematics 1', 'course_code': 'TMA4100', 'description': 'This is a description of the course Mathematics 1.', 'course_link': 'https://www.ntnu.edu/studies/courses/TMA4100#tab=omEmnet'}, {'subject_name': 'Discrete Mathematics', 'course_code': 'TMA4140', 'description': 'This is a description of the course Discrete Mathematics.', 'course_link': 'https://www.ntnu.edu/studies/courses/TMA4140#tab=omEmnet'}], 'choose_1_subjects': [], 'choose_2_subjects': []}, {'semester': 'Semester 2', 'course_name': 'default', 'mandatory_subjects': [{'subject_name': 'Object Oriented Programming', 'course_code': 'TDT4100', 'description': 'This is a description of the course Object Oriented Programming.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4100#tab=omEmnet'}, {'subject_name': 'Programming Lab for Computer Technology', 'course_code': 'TDT4112', 'description': 'This is a description of the course Programming Lab for Computer Technology.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4112#tab=omEmnet'}, {'subject_name': 'Circuit and Digital Engineering', 'course_code': 'TFE4101', 'description': 'This is a description of the course Circuit and Digital Engineering.', 'course_link': 'https://www.ntnu.edu/studies/courses/TFE4101#tab=omEmnet'}, {'subject_name': 'Mathematics 3', 'course_code': 'TMA4115', 'description': 'This is a description of the course Mathematics 3.', 'course_link': 'https://www.ntnu.edu/studies/courses/TMA4115#tab=omEmnet'}], 'choose_1_subjects': [], 'choose_2_subjects': []}, {'semester': 'Semester 3', 'course_name': 'default', 'mandatory_subjects': [{'subject_name': 'Computer technology, programming project', 'course_code': 'TDT4113', 'description': 'This is a description of the course Computer technology, programming project.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4113#tab=omEmnet'}, {'subject_name': 'Algorithms and Data Structures', 'course_code': 'TDT4120', 'description': 'This is a description of the course Algorithms and Data Structures.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4120#tab=omEmnet'}, {'subject_name': 'Computers and Digital Technology', 'course_code': 'TDT4160', 'description': 'This is a description of the course Computers and Digital Technology.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4160#tab=omEmnet'}, {'subject_name': 'Statistics', 'course_code': 'TMA4240', 'description': 'This is a description of the course Statistics.', 'course_link': 'https://www.ntnu.edu/studies/courses/TMA4240#tab=omEmnet'}], 'choose_1_subjects': [], 'choose_2_subjects': []}, {'semester': 'Semester 4', 'course_name': 'default', 'mandatory_subjects': [{'subject_name': 'Software Development', 'course_code': 'TDT4140', 'description': 'This is a description of the course Software Development.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4140#tab=omEmnet'}, {'subject_name': 'Data Modeling and Database Systems', 'course_code': 'TDT4145', 'description': 'This is a description of the course Data Modeling and Database Systems.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4145#tab=omEmnet'}, {'subject_name': 'Human Computer Interaction', 'course_code': 'TDT4180', 'description': 'This is a description of the course Human Computer Interaction.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4180#tab=omEmnet'}, {'subject_name': 'Communication Services and Networks', 'course_code': 'TTM4100', 'description': 'This is a description of the course Communication Services and Networks.', 'course_link': 'https://www.ntnu.edu/studies/courses/TTM4100#tab=omEmnet'}], 'choose_1_subjects': [], 'choose_2_subjects': []}, {'semester': 'Semester 5', 'course_name': 'Artificial Intelligence', 'mandatory_subjects': [{'subject_name': 'Introduction to Artificial Intelligence', 'course_code': 'TDT4136', 'description': 'Introduction to the fundamentals of artificial intelligence.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4136#tab=omEmnet'}, {'subject_name': 'Cognitive Architectures', 'course_code': 'TDT4137', 'description': 'Study cognitive architectures and AI systems.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4137#tab=omEmnet'}, {'subject_name': 'Mathematics 4D', 'course_code': 'TMA4135', 'description': 'Advanced mathematics course related to AI.', 'course_link': 'https://www.ntnu.edu/studies/courses/TMA4135#tab=omEmnet'}], 'choose_1_subjects': [{'subject_name': 'Web Development', 'course_code': 'IT2810', 'description': 'Learn web development principles and practices.', 'course_link': 'https://www.ntnu.edu/studies/courses/IT2810#tab=omEmnet'}, {'subject_name': 'Information Retrieval', 'course_code': 'TDT4117', 'description': 'Learn about information retrieval techniques in AI.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4117#tab=omEmnet'}, {'subject_name': 'Programming Language', 'course_code': 'TDT4165', 'description': 'Study various programming languages relevant to AI.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4165#tab=omEmnet'}, {'subject_name': 'Information Systems', 'course_code': 'TDT4175', 'description': 'Learn about information systems used in AI applications.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4175#tab=omEmnet'}], 'choose_2_subjects': []}, {'semester': 'Semester 6', 'course_name': 'Artificial Intelligence', 'mandatory_subjects': [{'subject_name': 'Methods in Artificial Intelligence', 'course_code': 'TDT4171', 'description': 'Explore methods and techniques in artificial intelligence.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4171#tab=omEmnet'}, {'subject_name': 'Operating Systems', 'course_code': 'TDT4186', 'description': 'Study the fundamentals of operating systems.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4186#tab=omEmnet'}, {'subject_name': 'Physics', 'course_code': 'TFY4125', 'description': 'Learn physics concepts relevant to artificial intelligence.', 'course_link': 'https://www.ntnu.edu/studies/courses/TFY4125#tab=omEmnet'}, {'subject_name': 'Technology Management', 'course_code': 'TI04252', 'description': 'Explore technology management principles.', 'course_link': 'https://www.ntnu.edu/studies/courses/TI04252#tab=omEmnet'}], 'choose_1_subjects': [], 'choose_2_subjects': []}, {'semester': 'Semester 7', 'course_name': 'Artificial Intelligence', 'mandatory_subjects': [{'subject_name': 'Complementary Subject', 'course_code': 'COMP000', 'description': 'A complementary subject for the Artificial Intelligence course.', 'course_link': 'https://www.ntnu.edu/studies/courses/COMP000#tab=omEmnet'}, {'subject_name': 'Customer Managed Project', 'course_code': 'TDT4290', 'description': 'A project management course focused on customer needs and solutions.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4290#tab=omEmnet'}, {'subject_name': 'Machine Learning', 'course_code': 'TDT4173', 'description': 'A course that covers machine learning concepts and techniques.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4173#tab=omEmnet'}], 'choose_1_subjects': [], 'choose_2_subjects': []}, {'semester': 'Semester 8', 'course_name': 'Artificial Intelligence', 'mandatory_subjects': [{'subject_name': 'Experts in Teams', 'course_code': 'EIT0001', 'description': 'A course focusing on teamwork and collaboration.', 'course_link': 'https://www.ntnu.edu/studies/courses/EIT0001#tab=omEmnet'}, {'subject_name': 'Engineering Subject from another program', 'course_code': 'ENG0001', 'description': 'A subject from another engineering program.', 'course_link': 'https://www.ntnu.edu/studies/courses/ENG0001#tab=omEmnet'}, {'subject_name': 'Artificial Intelligence Programming', 'course_code': 'IT3105', 'description': 'Introduction to programming for artificial intelligence.', 'course_link': 'https://www.ntnu.edu/studies/courses/IT3105#tab=omEmnet'}], 'choose_1_subjects': [{'subject_name': 'Deep Learning', 'course_code': 'IT3030', 'description': 'In-depth study of deep learning techniques.', 'course_link': 'https://www.ntnu.edu/studies/courses/IT3030#tab=omEmnet'}, {'subject_name': 'Bio-Inspired Artificial Intelligence', 'course_code': 'IT3708', 'description': 'Explore bio-inspired AI concepts and algorithms.', 'course_link': 'https://www.ntnu.edu/studies/courses/IT3708#tab=omEmnet'}, {'subject_name': 'Recommendation Systems', 'course_code': 'TDT4215', 'description': 'Study recommendation system algorithms.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4215#tab=omEmnet'}, {'subject_name': 'Intelligent Text Analysis and Language Comprehension', 'course_code': 'TDT4310', 'description': 'Learn about text analysis and language comprehension in AI.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4310#tab=omEmnet'}], 'choose_2_subjects': []}, {'semester': 'Semester 9', 'course_name': 'default', 'mandatory_subjects': [{'subject_name': 'Computer Science, Specialization Project', 'course_code': 'TDT4501', 'description': 'A project focusing on computer science specialization.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4501#tab=omEmnet'}, {'subject_name': 'Computer Science, Specialization Subject', 'course_code': 'TDT4506', 'description': 'A specialization subject in computer science.', 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4506#tab=omEmnet'}, {'subject_name': 'Complementary Subject', 'course_code': 'COMP001', 'description': 'A complementary subject for Semester 9.', 'course_link': 'https://www.ntnu.edu/studies/courses/COMP001#tab=omEmnet'}], 'choose_1_subjects': [], 'choose_2_subjects': []}, {'semester': 'Semester 10', 'course_name': 'default', 'mandatory_subjects': [{'subject_name': 'Computer Science, Masters Thesis', 'course_code': 'TDT4900', 'description': "A master's thesis in computer science.", 'course_link': 'https://www.ntnu.edu/studies/courses/TDT4900#tab=omEmnet'}], 'choose_1_subjects': [], 'choose_2_subjects': []}]




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
    
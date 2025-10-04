from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import uuid
import chromadb
import json
import tempfile
from web_scraping import Chain

class Resume: # all functions in class need self as first argument
    # Step 4: Scrap text from resume
    def resume_scraping(self, resume_file):

        # Decide extension based on uploaded file
        suffix = ".pdf" if resume_file.name.endswith(".pdf") else ".docx" # add suffix before the file is created cuz after need extra steps, and we dont know the file is pdf or docx 

        # Save uploaded file in a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp: # delete=False: deletes the temp file after close # suffix=resume_file.name: keep the original file extension (.pdf or .docx)
            tmp.write(resume_file.read())   # ✅ Write the uploaded file content to the temp file
            temp_path = tmp.name            # Get the path of the temp file       

        # if pdf use PyPDFLoader
        if temp_path.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
            resume = loader.load().pop().page_content
            
        # if docs use Docx2txtLoader
        elif temp_path.endswith(".docx"):
            loader = Docx2txtLoader(temp_path)
            resume = loader.load().pop().page_content
            
        return resume

    # Step 5: Extract important info from resume
    def extract_resume(self, resume, llm):
        prompt_extract_2 = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM RESUME:
            # {page_data}
            ### INSTRUCTION:
            The scraped text is from the resume uploaded by user in pdf or docs.
            Your job is to extract the resume and return them in JSON format containing the following keys: `education`, `experience` and `skills`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):    
            """
            )
        
        resume_chain_extract = prompt_extract_2 | llm 
        resume = resume_chain_extract.invoke(input={'page_data':resume})
        
        json_parser = JsonOutputParser() # convert output of an LLM call into Json object
        json_resume = json_parser.parse(resume.content) # takes the string output (res.content) and returns a dict
        return json_resume
    
    # Step 6: Store resume in vector DB
    def store_resume(self, json_resume):
        client = chromadb.PersistentClient('vectorstore') 
        collection = client.get_or_create_collection(name="resume")
        
        # Education
        for edu in json_resume.get("education", []): # iterate over the list inside the dictionary
            collection.add(
                documents=[json.dumps(edu)], # store value in education key 
                metadatas=[{"type": "education"}],
                ids=[str(uuid.uuid4())]
            )
            
        # Experience
        for exp in json_resume.get("experience", []): # [] → an empty list. # [{}] → a list containing one empty dictionary.
            collection.add(
                documents=[json.dumps(exp)],
                metadatas=[{"type": "experience"}],
                ids=[str(uuid.uuid4())]
            )

        # skills
        for skill in json_resume.get("skills", []):
            collection.add(
                documents=[json.dumps(skill)],
                metadatas=[{"type": "skills"}],
                ids=[str(uuid.uuid4())]
            )
            
        return collection

    # Step 7: Make query with job skills
    def query_skills(self, json_job, collection):
        education = collection.query(
            query_texts=json_job['skills'],
            n_results=1, 
            where={"type": "education"}
            )
        education = education['documents']
        # 1 skill correspond to 1 result
        
        experience = collection.query(
            query_texts=json_job['skills'],
            n_results=2, 
            where={"type": "experience"}
            )
        experience = experience['documents']

        skills = collection.query(
            query_texts=json_job['skills'],
            n_results=3, 
            where={"type": "skills"}
            )
        skills = skills['documents']

        return education, experience, skills

    # Step 8: Generate email
    def generate_email(self, json_job, education, experience, skills, llm):
        prompt_email = PromptTemplate.from_template(
            """
            ### INSTRUCTION:
            You are the candidate described in the resume.
            Your job is to write a professional and concise job application email to the company regarding the job: {job_description}. 
            You need to include your specific qualifications that make you a good fit for the job.
            You MUST ONLY use information from the candidate's resume.
            
            Include:
            - The company name (if unknown, write [Company Name])
            - Your name (if unknown, write [Your Name])
            - Only use the information provided in the following sections: {education}, {experience}, {skills}

            Important:
            - Do not invent, add, or assume any skills, experiences, or education not in the resume.
            - Ignore job requirements from {job_description} that are not meet in the resume.
            - Keep the email under 300 words.
            - Avoid any preamble or unrelated statements.
            - Produce a proper email format: greeting, body, and closing.
            - Do not provide a preamble.
            - Be honest.

            ### EMAIL (NO PREAMBLE):
        
            """
            )
        
        chain_email = prompt_email | llm
        res = chain_email.invoke({"job_description": str(json_job), "education": education, "experience": experience, "skills": skills})
        email = res.content
        return email
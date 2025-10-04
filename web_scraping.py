from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader, AsyncHtmlLoader, SeleniumURLLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()

class Chain: # all functions in class need self as first argument
    # Step 1: Initialize LLM
    def __init__(self, st_write=None): # __init__ is a special method that is called when an object is instantiated from the class
        self.llm = ChatGroq( # cannot use return, return won't automatically define llm # use self.llm to call llm in other functions
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("groq_api_key"),
            temperature=0, 
            )
        
        self.st_write = st_write # function to write to streamlit app, if not provided, will be None
        
    # Step 2: Web scraping
    def web_scraping(self, url):
        try:
            # Try WebBaseLoader first
            loader = WebBaseLoader(url)
            page_data = loader.load().pop().page_content

            # If WebBaseLoader returned empty/too small, use AsyncHtmlLoader
            if not page_data or len(page_data) < 100 or "not available" in page_data.lower():
                loader = AsyncHtmlLoader(url)
                page_data = loader.load().pop().page_content

            return page_data
        
        except Exception as e:
            self.st_write(f"⚠️ Error during web scraping: {e}")
            return   
            
    # Step 3: Extract inmportant info from job posting
    def extract_job_posting(self, page_data):
        prompt_extract_1 = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the 
            following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):    
            """
            )
        
        # chain_extract = LLMChain(llm=llm, prompt=prompt_extract) <--- same as below
        # Send prompt to LLM
        job_chain_extract = prompt_extract_1 | self.llm # send prompt to LLM 
        job = job_chain_extract.invoke(input={'page_data': page_data})

        # convert output of an LLM into Json object
        json_parser = JsonOutputParser() 
        json_job = json_parser.parse(job.content) # takes the string output (res.content) and returns a dict
        
        # Ensure always a dict
        if isinstance(json_job, list): # if it's a list
            if len(json_job) == 1 and isinstance(json_job[0], dict): # if it's a list with one dict
                json_job = json_job[0]  # take the single dict 
            else: # if it's a list with multiple dicts or other structures, raise an error
                raise ValueError(f"Unexpected JSON list structure: {json_job}")
        elif not isinstance(json_job, dict): # if it's not a dict
            raise ValueError(f"Expected a dict, got {type(json_job)}: {json_job}") 

        return json_job
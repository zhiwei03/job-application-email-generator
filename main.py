import streamlit as st
from web_scraping import Chain
from resume_to_email import Resume

def create_streamlit_app(chain, resume):
    st.title("Job Application Email Generator\u00A0📧")

    # Initialize variables
    url = None
    paste = None

    method = st.radio("Select input method:", ["Job Posting URL", "Paste Job Description"])
    
    # Show input dynamically based on selection
    if method == "Job Posting URL":
        url = st.text_input("Enter the job posting URL:")
    else:
        paste = st.text_area("Paste the job posting text here:", height=200)

    resume_file = st.file_uploader("Upload your Resume (PDF or DOCX):", type=["pdf", "docx"])

    # If button clicked
    if st.button("Generate Email"):
        if not url and not paste:
            st.error("Please provide a job posting URL or paste the job description.")
            return
        if not resume_file:
            st.error("Please upload your resume in PDF or DOCX.")
            return

        with st.spinner("Generating email..."):
            progress_bar = st.progress(0)  # initialize at 0%
            status_text = st.empty()       # placeholder for step text

        # Step 1: Web scraping
        if method == "Job Posting URL":
            page_data = chain.web_scraping(url)
                
            if not page_data:
                st.error("Failed to fetch job posting from URL.")
                return
        else:
            page_data = paste  # use the text directly, no scraping needed

        progress_bar.progress(10)

        # Step 2: Extract important info from job posting
        json_job = chain.extract_job_posting(page_data)

        progress_bar.progress(20)

        # Step 3: Extract important info from resume
        resume_data = resume.resume_scraping(resume_file)

        progress_bar.progress(30)

        # Step 4: Extract important info from resume
        json_resume = resume.extract_resume(resume_data, chain.llm)
        progress_bar.progress(40)

        # Step 4: Store resume in vector DB
        collection = resume.store_resume(json_resume)

        progress_bar.progress(60)

        # Step 5: Make query with job skills
        if json_job.get('skills'):
            education, experience, skills = resume.query_skills(json_job, collection)
        else:
            st.warning("No skills found in the job posting")
            return

        progress_bar.progress(80)

        # Step 6: Generate email
        email = resume.generate_email(json_job, education, experience, skills, chain.llm)
            
        progress_bar.progress(100)

        st.subheader("Generated Job Application Email:")
        st.text_area("Generated Email", value=email, height=500, label_visibility="hidden")

# only create the app if run main.py, not when imported
if __name__ == "__main__":
    chain = Chain(st_write=st.warning)
    resume = Resume()
    create_streamlit_app(chain, resume)
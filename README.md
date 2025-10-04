<img width="1920" height="826" alt="Screenshot (15)" src="https://github.com/user-attachments/assets/e8bc2481-f9e1-4745-87a2-282fbb800fa4" /># Job Application Email Generator

Input:
<img width="1920" height="836" alt="Screenshot (16)" src="https://github.com/user-attachments/assets/106d1f83-785f-4668-964b-6b08a16ffaef" />

Output:
<img width="1920" height="826" alt="Screenshot (15)" src="https://github.com/user-attachments/assets/e501ef67-b986-4998-9897-dbe8238ac74a" />

## Table of Contents
* [General Info](#general-info)
* [Features](#features)
* [Tech stack](#tech-stack)
* [Setup](#setup)
* [Limitations](#limitations)
* [Inspiration](#inspiration)

## General info
This project is a streamlit web application that uses LangChain, Llama-3.3-70b-versatile to generate professional and personalized job application emails.
Users provide their resume and a job URL/description text, and the app will return a tailored application email.

## Features
- User can provide either job URL or paste job description along with their resume
- Automatically generates professional and personalized job application emails
- Copy-ready email output
  
## Tech Stack
- LangChain: framework for connecting the LLM with the database
- Llama-3.3-70b-versatile: Large Language Model hosted on GroqCloud
- Chroma: vector database for semantic search
- Streamlit: Web application framework

## Setup
1. Clone the repository
```
git clone https://github.com/zhiwei03/job-application-email-generator.git
cd job-application-email-generator
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Set up .env file 
```
google_api_key = 'YOUR_GOOGLE_API_KEY'
```
4. Run the app:
```
streamlit run main.py
```

## Limitations
- Websites built with JavaScript cannot be scraped automatically due to lack of JavaScript web scraping tool
- ⚠️ The free tier of Llama-3.3-70b-versatile only allows **100000 tokens per day (TPM)**
- Exceeding this quota may result in errors until the daily quota resets
  
## Inspiration
- This project is inspired by [codebasics YouTube](https://youtu.be/CO4E_9V6li0?si=TXdCB4QEhxRvqVOT)

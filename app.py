# from pydoc import text
from fastapi import FastAPI
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from fastapi.middleware.cors import CORSMiddleware
#For html code...
from langserve import add_routes
import os
from dotenv import load_dotenv
import uvicorn
load_dotenv()


groq_api_key = os.getenv("GROQ_API_KEY")
proxy_username = os.getenv("PROXY_USERNAME")
proxy_password = os.getenv("PROXY_PASSWORD")
proxy_host = os.getenv("PROXY_HOST")
proxy_port = os.getenv("PROXY_PORT")

if proxy_username and proxy_password and proxy_host and proxy_port:
    os.environ['HTTP_PROXY'] = f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
    os.environ['HTTPS_PROXY'] = f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
    print("✓ Proxy configured")
else:
    print("⚠ No proxy configured")


model = ChatGroq(model="llama-3.3-70b-versatile",groq_api_key=groq_api_key)

# 1.Create prompt template
system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("user", '{text}')
])

parser=StrOutputParser()

##create chain
chain=prompt_template|model|parser

## App definition
app=FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API server using Langchain runnable interfaces"
)

#Adding chain routes
add_routes(
    app,
    chain,
    path="/chain"
)


# CORS middleware - Important for HTML file to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#These are the routes created by LangServe automatically
# /chain/invoke
# /chain/stream
# /chain/playground
# /chain/input_schema
# /chain/output_schema

if __name__=="__main__":
    uvicorn.run(app,host="localhost",port=8000)

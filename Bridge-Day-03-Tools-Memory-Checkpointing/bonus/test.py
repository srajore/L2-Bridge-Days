#from dotenv import load_dotenv

#load_dotenv()

MODEL = "gpt-oss:120b-cloud"
#from langchain_groq import ChatGroq
#from langchain_openai import ChatOpenAI

from langchain_ollama import ChatOllama

llm = ChatOllama(
    model=MODEL
)


response = llm.invoke("Hey model ,My name is Sharad and I work with Zensar Technologies")

print(response.content)


response = llm.invoke("Hey model, what is my name?")

print(response.content)
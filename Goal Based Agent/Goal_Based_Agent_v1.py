from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import re, os
load_dotenv()

llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=.2)
memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True)

application_info={
    "name":None,
    "email":None,
    "skills":None
}

def extract_application_info(text):
    name_match=re.search(r"(?:my name is|i am|name)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE)
    email_match=re.search(r"\b[\w.-]+@[\w.-]+\.\w+\b", text)
    skill_match=re.search(r"(?:skills are|i know | i can use|skills|Skills)\s+(.*)", text, re.IGNORECASE)
    
    response=[]
    
    if name_match:
        application_info["name"]=name_match.group(1).title()
        response.append("Name Saved.")
    if email_match:
        application_info["email"]=email_match.group(0)
        response.append("Email Saved.")
    if skill_match:
        application_info["skills"]=skill_match.group(1).strip()
        response.append("Skills Saved.")
    
    if not any([name_match, email_match, skill_match]):
        return "I could`nt extract any Info, Could you please provide your name, email or skills to complete application process"
    else:
        return " ".join(response) + " Let me check what else I need"
        
def check_application_goal(_=None):
    if all(application_info.values()):
        return f"You are ready! Name : {application_info['name']}, Email : {application_info['email']}, Skills : {application_info['skills']}"
    else:
        missing=[k for k,v in application_info.items() if not v]
        return f" Still Need {','.join(missing)}. please ask the user to provide this."
    
#Creating custom tools

tools=[
    Tool(
        name="extract_application_info",
        func=extract_application_info,
        description="use this function to extract name,email and skills from the user`s message/text."
    ),
    Tool(
        name="check_application_goal",
        func=check_application_goal,
        description="Check if name, email and skills are provided.If not, tell the user what is missing.",
        return_direct=True # --important!
    )
]
system_prompt="""
You are a helpful job application assistant.
Your goal is to collect user`s name, email and skills.
use the tools provided to extract this information and check wether all required data is collected.
Once everything is collected, inform the user that the application info is complete and stop. 
"""

#initialize agent
agent=initialize_agent(
    tools=tools,
    llm=llm,
    memory=memory,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message":system_prompt}
)

# Chat Loop
print("Hi! I am your job application assistant. Please tell me your Name, Email and Skills.")

while True:
    user_input=input("You: ")
    if user_input.lower() in ["exit","quit"]:
        print("Bye ! Good Luck.")
        break
    response=agent.invoke({"input":user_input})
    print("Bot: ", response["output"])
    
    #if goal achieved, stop
    if "You are ready!" in response["output"].lower():
        print("Application info completed")
        break
    
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage
from langchain.prompts import PromptTemplate
from langsmith import Client, traceable
from dotenv import load_dotenv

load_dotenv()

# API keys
google_api_key = os.getenv("GOOGLE_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")

# Client and LLM configuration
client = Client(api_key=langsmith_api_key)
model_name = "gemini-1.5-flash"
temperature = 0.7
llm = ChatGoogleGenerativeAI(
    google_api_key=google_api_key,
    model=model_name,
    temperature=temperature
)

# Prompts
crop_care_prompt = PromptTemplate(
    input_variables=["crop", "issue"],
    template="Provide advice for the following crop issue: Crop: {crop}, Issue: {issue}. Include actionable steps and preventive measures."
)
pest_management_prompt = PromptTemplate(
    input_variables=["crop", "pest"],
    template="Suggest pest management techniques for the crop {crop} affected by {pest}. Include chemical and non-chemical solutions."
)
solutions_prompt = PromptTemplate(
    input_variables=["solution_topic"],
    template="Provide detailed insights on the following agricultural solution: {solution_topic}. Include benefits, challenges, and best practices."
)

def format_response(text):
    text = text.replace("**", "<strong>").replace("###", "<h1>")
    paragraphs = text.split("\n\n")
    html = ""
    for paragraph in paragraphs:
        if "\n-" in paragraph:
            intro, *points = paragraph.split("\n")
            html += f"<p>{intro}</p>"
            list_items = "".join(f"<li>{point.strip('- ')}</li>" for point in points if point.strip())
            html += f"<ul>{list_items}</ul>"
        else:
            html += f"<p>{paragraph.replace('\n', '<br>')}</p>"
    return html

def extract_entities(user_message, crops, issues, pests, solutions):
    entities = {"crop": None, "issue": None, "pest": None, "solution_topic": None}
    for word in crops + issues + pests + solutions:
        if word.lower() in user_message.lower():
            if word.lower() in crops:
                entities["crop"] = word
            elif word.lower() in issues:
                entities["issue"] = word
            elif word.lower() in pests:
                entities["pest"] = word
            elif word.lower() in solutions:
                entities["solution_topic"] = word
    return entities

class AgriChatAgent:
    def __init__(self):
        self.client = client
        self.llm = llm
        self.conversation_history = []  # Store the conversation

    @traceable(client=client)
    def get_crop_care_advice(self, crop, issue):
        prompt = crop_care_prompt.format(crop=crop, issue=issue)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        formatted_response = format_response(response.content.strip()) if isinstance(response, AIMessage) else "Unexpected response format."
        self.conversation_history.append({"user_message": f"Crop: {crop}, Issue: {issue}", "response": formatted_response})
        return formatted_response

    @traceable(client=client)
    def get_pest_management_advice(self, crop, pest):
        prompt = pest_management_prompt.format(crop=crop, pest=pest)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        formatted_response = format_response(response.content.strip()) if isinstance(response, AIMessage) else "Unexpected response format."
        self.conversation_history.append({"user_message": f"Crop: {crop}, Pest: {pest}", "response": formatted_response})
        return formatted_response

    @traceable(client=client)
    def get_solutions_info(self, solution_topic):
        prompt = solutions_prompt.format(solution_topic=solution_topic)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        formatted_response = format_response(response.content.strip()) if isinstance(response, AIMessage) else "Unexpected response format."
        self.conversation_history.append({"user_message": f"Solution Topic: {solution_topic}", "response": formatted_response})
        return formatted_response

__all__ = ["AgriChatAgent", "extract_entities"]

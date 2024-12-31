from flask import Flask, request, jsonify, render_template
from agrichatagent import AgriChatAgent
import spacy

app = Flask(__name__)
agri_agent = AgriChatAgent()
nlp = spacy.load("en_core_web_sm")

# Define lists of crops, issues, pests, and solutions
CROPS = ["wheat", "rice", "maize", "cotton", "sugarcane", "barley", "corn"]
ISSUES = ["yellow rust", "stem rust", "root rot", "powdery mildew"]
PESTS = ["brown planthopper", "aphids", "bollworm", "armyworm", "whiteflies", "corn borer"]
SOLUTIONS = ["organic farming", "crop rotation", "drip irrigation", "composting", "precision agriculture"]

# Function to extract entities from the user's message
def extract_entities(user_message):
    entities = {"crop": None, "issue": None, "pest": None, "solution_topic": None}
    for word in CROPS + ISSUES + PESTS + SOLUTIONS:
        if word.lower() in user_message.lower():
            if word.lower() in CROPS:
                entities["crop"] = word
            elif word.lower() in ISSUES:
                entities["issue"] = word
            elif word.lower() in PESTS:
                entities["pest"] = word
            elif word.lower() in SOLUTIONS:
                entities["solution_topic"] = word
    return entities

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/verify", methods=["POST"])
def verify_user():
    """
    Endpoint to verify the user ID.
    """
    data = request.get_json()
    user_id = data.get("user_id", "").strip()

    if agri_agent.verify_user(user_id):
        return jsonify({"status": "success", "message": "User verified successfully!"})
    else:
        return jsonify({"status": "fail", "message": "Invalid user ID. Please try again."})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "default").strip()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please provide a message to continue."})

    # Extract entities and generate a response
    entities = extract_entities(user_message)
    if entities["crop"] and entities["issue"]:
        response = agri_agent.get_crop_care_advice(entities["crop"], entities["issue"], user_id)
    elif entities["crop"] and entities["pest"]:
        response = agri_agent.get_pest_management_advice(entities["crop"], entities["pest"], user_id)
    elif entities["solution_topic"]:
        response = agri_agent.get_solutions_info(entities["solution_topic"], user_id)
    else:
        response = "<p>I'm sorry, I didn't understand that. Could you please clarify?</p>"

    return jsonify({"response": response})

@app.route("/conversation", methods=["GET"])
def get_conversation_history():
    """
    Endpoint to retrieve user-specific conversation history.
    """
    user_id = request.args.get("user_id", "default").strip()
    history = agri_agent.get_conversation_history(user_id)
    return jsonify({"conversation_history": history})

@app.route("/summary", methods=["GET"])
def get_summary():
    """
    Endpoint to generate a summary of the conversation.
    """
    user_id = request.args.get("user_id", "default").strip()
    summary = agri_agent.generate_summary(user_id)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True, port=5001)

import streamlit as st
from agrichatagent import AgriChatAgent, extract_entities
from streamlit_option_menu import option_menu

# Initialize AgriChatAgent
agri_agent = AgriChatAgent()

# Define crops, issues, pests, and solutions
CROPS = ["wheat", "rice", "maize", "cotton", "sugarcane", "barley", "corn"]
ISSUES = ["yellow rust", "stem rust", "root rot", "powdery mildew"]
PESTS = ["brown planthopper", "aphids", "bollworm", "armyworm", "whiteflies", "corn borer"]
SOLUTIONS = ["organic farming", "crop rotation", "drip irrigation", "composting", "precision agriculture"]

# Streamlit page configuration
st.set_page_config(page_title="AgriChat Assistant", page_icon="🌾", layout="wide")

# Sidebar Menu
with st.sidebar:
    selected = option_menu(
        "AgriChat Menu",
        ["Home", "Crop Care", "Pest Management", "Solutions"],
        icons=["house", "seedling", "bug", "lightbulb"],
        menu_icon="menu",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "icon": {"color": "#2A9D8F", "font-size": "20px"},
            "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#E9C46A"},
            "nav-link-selected": {"background-color": "#F4A261"},
        },
    )

# Main Page Header
st.title("🌾 AgriChat Assistant")
st.markdown("""
<div style="background-color:#E76F51;padding:10px;border-radius:10px;">
    <h2 style="color:white;text-align:center;">Your Personalized Farming Companion</h2>
</div>
""", unsafe_allow_html=True)

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Feature: Get Advice Section
if selected == "Home":
    st.subheader("Ask for Farming Advice")
    
    # Display conversation history
    for msg in st.session_state.conversation_history:
        if msg['sender'] == 'user':
            st.markdown(f"<div style='text-align:right; background-color:#E9C46A; padding:8px 16px; border-radius:15px; max-width:80%; margin-bottom: 5px; word-wrap: break-word; margin-left: auto;'>{msg['message']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left; background-color:#F4A261; padding:8px 16px; border-radius:15px; max-width:80%; margin-bottom: 5px; word-wrap: break-word;'>{msg['message']}</div>", unsafe_allow_html=True)
    
    # Input field for user message
    user_message = st.text_input("Enter your query (e.g., 'How to manage yellow rust in wheat?')", "")
    
    # Send button to submit the query
    if st.button("Send") and user_message:
        entities = extract_entities(user_message, CROPS, ISSUES, PESTS, SOLUTIONS)
        if entities["crop"] and entities["issue"]:
            response = agri_agent.get_crop_care_advice(entities["crop"], entities["issue"])
        elif entities["crop"] and entities["pest"]:
            response = agri_agent.get_pest_management_advice(entities["crop"], entities["pest"])
        elif entities["solution_topic"]:
            response = agri_agent.get_solutions_info(entities["solution_topic"])
        else:
            response = "I couldn't understand your question. Please provide more details."
        
        # Add user message and bot response to the conversation history
        st.session_state.conversation_history.append({'sender': 'user', 'message': user_message})
        st.session_state.conversation_history.append({'sender': 'bot', 'message': response})

        # Clear the input field after sending the message
        user_message = ""

        # Display the new bot response in the conversation history
        st.markdown(f"<div style='text-align:left; background-color:#F4A261; padding:8px 16px; border-radius:15px; max-width:80%; margin-bottom: 5px; word-wrap: break-word;'>{response}</div>", unsafe_allow_html=True)
    elif user_message == "":
        st.warning("Please enter your query.")

# Feature: Crop Care Section
elif selected == "Crop Care":
    st.subheader("🌱 Crop Care Advice")
    st.markdown("""
    Learn how to protect and nurture your crops with expert advice on common issues.
    """)
    crop = st.selectbox("Select your crop", CROPS)
    issue = st.selectbox("Select the issue affecting your crop", ISSUES)
    if st.button("Get Crop Care Advice"):
        response = agri_agent.get_crop_care_advice(crop, issue)
        st.session_state.conversation_history.append({'sender': 'user', 'message': f"Crop: {crop}, Issue: {issue}"})
        st.session_state.conversation_history.append({'sender': 'bot', 'message': response})

# Feature: Pest Management Section
elif selected == "Pest Management":
    st.subheader("🐞 Pest Management")
    st.markdown("""
    Discover effective ways to manage pests affecting your crops.
    """)
    crop = st.selectbox("Select your crop", CROPS)
    pest = st.selectbox("Select the pest", PESTS)
    if st.button("Get Pest Management Advice"):
        response = agri_agent.get_pest_management_advice(crop, pest)
        st.session_state.conversation_history.append({'sender': 'user', 'message': f"Crop: {crop}, Pest: {pest}"})
        st.session_state.conversation_history.append({'sender': 'bot', 'message': response})

# Feature: Solutions Section
elif selected == "Solutions":
    st.subheader("💡 Sustainable Solutions")
    st.markdown("""
    Explore sustainable and innovative farming solutions to enhance productivity.
    """)
    solution_topic = st.selectbox("Select a solution topic", SOLUTIONS)
    if st.button("Get Solution Info"):
        response = agri_agent.get_solutions_info(solution_topic)
        st.session_state.conversation_history.append({'sender': 'user', 'message': f"Solution Topic: {solution_topic}"})
        st.session_state.conversation_history.append({'sender': 'bot', 'message': response})

# Button to generate summary
if st.button("Generate Summary Report"):
    summary = "Here is a summary of your conversation:\n"
    for msg in st.session_state.conversation_history:
        summary += f"{msg['sender'].capitalize()}: {msg['message']}\n"
    st.subheader("Conversation Summary")
    st.text(summary)

# Footer
st.markdown("""
<hr style="border:1px solid #E76F51;">
<div style="text-align:center;">
    <p style="font-size:14px;">Powered by AgriChat | Transforming Agriculture with AI</p>
</div>
""", unsafe_allow_html=True)

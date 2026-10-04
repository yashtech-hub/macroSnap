import json
from google import genai
from google.genai import types
import streamlit as st

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT
)

from email_service import send_email


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()

MODEL_NAME = "gemini-3.5-flash"


# ============================================================
# PERSONALIZED NUTRITION CALCULATION
# ============================================================

def calculate_nutrition_targets(weight, goal):

    if goal == "Lose weight":
        calories = weight * 25

    elif goal == "Gain weight":
        calories = weight * 35

    else:
        calories = weight * 30

    protein = weight * 1.5
    fat = weight * 0.8

    carbs = (
        calories
        - (protein * 4)
        - (fat * 9)
    ) / 4

    fiber = 25 + (weight * 0.1)

    return {
        "Calories": round(calories),
        "Protein": round(protein),
        "Carbohydrates": round(carbs),
        "Fat": round(fat),
        "Fiber": round(fiber)
    }


# ============================================================
# MESSAGE FUNCTIONS
# ============================================================

def render_message(message):

    with st.chat_message(message["role"]):

        if message["kind"] == "text":

            st.write(message["content"])

        elif message["kind"] == "image":

            st.image(message["content"])


def add_message(role, kind, content):

    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content
        }
    )

    render_message(
        st.session_state.messages[-1]
    )


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_gemini(parts):

    try:

        return st.session_state.chat.send_message(parts).text

    except Exception as error:

        return f"Error communicating with Gemini API: {error}"


# ============================================================
# ONBOARDING
# ============================================================

if "onboarded" not in st.session_state:

    st.title(
        "MacroSnap - AI Powered Macro Generator"
    )

    st.caption(
        "📸 Snap it  |  📊 Track it  |  📧 Email your nutrition summary"
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Enter your name"
        )

        email = st.text_input(
            "Enter your email address",
            placeholder="example@gmail.com",
            help="This is the email address where your MacroSnap nutrition summary will be sent."
        )

        weight = st.number_input(
            "Enter your weight (kg)",
            min_value=20.0,
            max_value=250.0,
            value=70.0,
            step=0.5
        )

        goal = st.selectbox(
            "What is your goal?",
            [
                "Maintain weight",
                "Lose weight",
                "Gain weight"
            ]
        )

        submitted = st.form_submit_button(
            "Submit"
        )

    if submitted:

        if not name.strip() or not email.strip():

            st.error(
                "Please fill in your name and email."
            )

        else:

            # Save user information
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()
            st.session_state.weight = weight
            st.session_state.goal = goal

            # Calculate personalized targets
            st.session_state.targets = calculate_nutrition_targets(
                weight,
                goal
            )

            # Create Gemini chat
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            # Initially empty chat
            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


# ============================================================
# GET PERSONALIZED TARGETS
# ============================================================

targets = st.session_state.targets


# ============================================================
# MAIN HEADER
# ============================================================

header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)


with header_col:

    st.title(
        "MacroSnap - AI Powered Macro Generator"
    )


# ============================================================
# SEND SUMMARY TO GMAIL
# ============================================================

with button_col:

    send_disabled = len(
        st.session_state.messages
    ) <= 1

    if st.button(
        "📧 Send Summary to Gmail",
        disabled=send_disabled,
        use_container_width=True
    ):

        with st.spinner(
            "Summarizing your day..."
        ):

            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

        success, info = send_email(
            st.session_state.email,
            st.session_state.name,
            summary
        )

        if success:

            st.success(
                "Nutrition summary sent successfully! "
                "Check your email."
            )

        else:

            st.error(
                f"Couldn't send the email: {info}"
            )


# ============================================================
# USER INFORMATION
# ============================================================

st.caption(
    f"Logged in as {st.session_state.name} "
    f"• Email: {st.session_state.email}"
)


# ============================================================
# PERSONALIZED NUTRITION DASHBOARD
# ============================================================

st.subheader(
    "🎯 Personalized Daily Nutrition Target"
)

st.write(
    f"**Weight:** {st.session_state.weight} kg"
)

st.write(
    f"**Goal:** {st.session_state.goal}"
)


st.table(
    {
        "Nutrient": [
            "Calories",
            "Protein",
            "Carbohydrates",
            "Fat",
            "Fiber"
        ],

        "Daily Target": [
            f"{targets['Calories']} kcal",
            f"{targets['Protein']} g",
            f"{targets['Carbohydrates']} g",
            f"{targets['Fat']} g",
            f"{targets['Fiber']} g"
        ]
    }
)


# ============================================================
# INITIAL WELCOME MESSAGE
# ============================================================

if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )

else:

    for message in st.session_state.messages:

        render_message(message)


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal to get started",
    accept_file=True,
    file_type=["png", "jpg", "jpeg"],
)


# ============================================================
# PROCESS USER INPUT
# ============================================================

if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []


    # ========================================================
    # PHOTO INPUT
    # ========================================================

    if photo is not None:

        photo_bytes = photo.getvalue()

        add_message(
            "user",
            "image",
            photo_bytes
        )

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )


    # ========================================================
    # TEXT INPUT
    # ========================================================

    if text:

        add_message(
            "user",
            "text",
            text
        )

        parts.append(
            text
            + """

If this is a food or meal question, analyze the food.

Give the nutrition information in this format:

| Nutrient | Estimated Amount |
|---|---:|
| Food | ... |
| Calories | ... kcal |
| Protein | ... g |
| Carbohydrates | ... g |
| Fat | ... g |
| Fiber | ... g |

Then explain briefly how this food fits into the user's
personalized daily nutrition target.
"""
        )


    # ========================================================
    # PHOTO WITHOUT QUESTION
    # ========================================================

    elif photo is not None:

        parts.append(
            f"""
Analyze this food or meal.

The user weighs {st.session_state.weight} kg.

The user's goal is:
{st.session_state.goal}

The user's personalized daily nutrition targets are:

Calories: {targets['Calories']} kcal
Protein: {targets['Protein']} g
Carbohydrates: {targets['Carbohydrates']} g
Fat: {targets['Fat']} g
Fiber: {targets['Fiber']} g

Give the food analysis using this exact table format:

| Nutrient | Estimated Amount |
|---|---:|
| Food | ... |
| Calories | ... kcal |
| Protein | ... g |
| Carbohydrates | ... g |
| Fat | ... g |
| Fiber | ... g |

After the table, explain briefly:

1. Whether this food fits the user's daily target.
2. Which nutrient is relatively high or low.
3. Whether the user should consider a smaller or larger portion.
4. Suggest a healthier alternative if appropriate.

Do not make medical claims.
"""
        )


    # ========================================================
    # GEMINI RESPONSE
    # ========================================================

    with st.spinner(
        "Analyzing your food and generating personalized nutrition..."
    ):

        answer = ask_gemini(parts)


    # ========================================================
    # SHOW FOOD ANALYSIS
    # ========================================================

    st.subheader(
        "🍽️ Food Nutrition Analysis"
    )

    st.write(answer)


    # ========================================================
    # SHOW PERSONALIZED TARGET AGAIN
    # ========================================================

    st.subheader(
        "🎯 Your Personalized Daily Target"
    )

    st.table(
        {
            "Nutrient": [
                "Calories",
                "Protein",
                "Carbohydrates",
                "Fat",
                "Fiber"
            ],

            "Daily Target": [
                f"{targets['Calories']} kcal",
                f"{targets['Protein']} g",
                f"{targets['Carbohydrates']} g",
                f"{targets['Fat']} g",
                f"{targets['Fiber']} g"
            ]
        }
    )


    # ========================================================
    # ADD GEMINI RESPONSE TO CHAT
    # ========================================================

    add_message(
        "assistant",
        "text",
        answer
    )
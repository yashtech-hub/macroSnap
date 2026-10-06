import re

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
MODEL_NAME = "gemini-3.5-flash-lite"


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


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


# ============================================================
# NUTRITION TRACKING FUNCTIONS
# ============================================================

def extract_nutrition(answer):
    """
    Extract nutrition values from Gemini's requested table.
    Returns None if the response does not look like a food analysis.
    """

    patterns = {
        "Calories": r"\|\s*Calories\s*\|\s*([\d,]+(?:\.\d+)?)",
        "Protein": r"\|\s*Protein\s*\|\s*([\d,]+(?:\.\d+)?)",
        "Carbohydrates": r"\|\s*Carbohydrates\s*\|\s*([\d,]+(?:\.\d+)?)",
        "Fat": r"\|\s*Fat\s*\|\s*([\d,]+(?:\.\d+)?)",
        "Fiber": r"\|\s*Fiber\s*\|\s*([\d,]+(?:\.\d+)?)"
    }

    nutrition = {}

    for nutrient, pattern in patterns.items():
        match = re.search(pattern, answer, re.IGNORECASE)
        if match:
            nutrition[nutrient] = float(
                match.group(1).replace(",", "")
            )

    # Calories + at least one macro means this is likely a meal analysis.
    if "Calories" not in nutrition:
        return None

    if not any(
        nutrient in nutrition
        for nutrient in ["Protein", "Carbohydrates", "Fat"]
    ):
        return None

    food_match = re.search(
        r"\|\s*Food\s*\|\s*([^|\n]+)",
        answer,
        re.IGNORECASE
    )

    food_name = (
        food_match.group(1).strip()
        if food_match
        else "Analyzed meal"
    )

    return {
        "Food": food_name,
        "Calories": nutrition.get("Calories", 0),
        "Protein": nutrition.get("Protein", 0),
        "Carbohydrates": nutrition.get("Carbohydrates", 0),
        "Fat": nutrition.get("Fat", 0),
        "Fiber": nutrition.get("Fiber", 0)
    }


def add_meal_to_tracker(nutrition):
    st.session_state.meal_history.append(nutrition)

    for nutrient in [
        "Calories",
        "Protein",
        "Carbohydrates",
        "Fat",
        "Fiber"
    ]:
        st.session_state.daily_totals[nutrient] += nutrition[nutrient]


def get_remaining_targets():
    targets = st.session_state.targets
    totals = st.session_state.daily_totals

    return {
        nutrient: max(
            0,
            targets[nutrient] - totals[nutrient]
        )
        for nutrient in targets
    }


def get_goal_fit(nutrition):
    remaining = get_remaining_targets()

    if nutrition["Calories"] <= remaining["Calories"]:
        calorie_status = "Fits within your remaining daily calories."
    else:
        calorie_status = "This meal is higher than your remaining daily calories."

    if nutrition["Protein"] >= 20:
        protein_status = "It provides a useful amount of protein."
    else:
        protein_status = "Consider adding a protein-rich food if needed."

    if nutrition["Calories"] <= remaining["Calories"] and nutrition["Protein"] >= 20:
        overall = "Good fit"
    elif nutrition["Calories"] <= remaining["Calories"]:
        overall = "Moderate fit"
    else:
        overall = "Higher than remaining target"

    return overall, calorie_status, protein_status


def show_tracking_dashboard():
    targets = st.session_state.targets
    totals = st.session_state.daily_totals
    remaining = get_remaining_targets()

    st.subheader("Today's Nutrition Progress")

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
            ],
            "Consumed": [
                f"{round(totals['Calories'])} kcal",
                f"{round(totals['Protein'])} g",
                f"{round(totals['Carbohydrates'])} g",
                f"{round(totals['Fat'])} g",
                f"{round(totals['Fiber'])} g"
            ],
            "Remaining": [
                f"{round(remaining['Calories'])} kcal",
                f"{round(remaining['Protein'])} g",
                f"{round(remaining['Carbohydrates'])} g",
                f"{round(remaining['Fat'])} g",
                f"{round(remaining['Fiber'])} g"
            ]
        }
    )


def show_meal_history():
    if not st.session_state.meal_history:
        return

    st.subheader("Today's Meal History")

    for index, meal in enumerate(
        st.session_state.meal_history,
        start=1
    ):
        st.write(
            f"**{index}. {meal['Food']}** — "
            f"{round(meal['Calories'])} kcal | "
            f"Protein: {round(meal['Protein'])} g | "
            f"Carbs: {round(meal['Carbohydrates'])} g | "
            f"Fat: {round(meal['Fat'])} g"
        )


def show_next_meal_suggestion():
    remaining = get_remaining_targets()

    st.subheader("What Could You Eat Next?")

    if remaining["Calories"] <= 0:
        st.info(
            "Your estimated daily calorie target has been reached. "
            "If you eat again, consider a lighter option."
        )
        return

    if remaining["Protein"] >= 30:
        suggestion = (
            "Your remaining protein target is relatively high. "
            "Consider a protein-rich meal such as eggs, chicken, "
            "fish, paneer, tofu, curd, or another protein source "
            "that fits your preferences."
        )
    elif remaining["Carbohydrates"] >= 50:
        suggestion = (
            "You still have room for carbohydrates. "
            "Consider a balanced meal with a whole-grain or rice-based "
            "carbohydrate source, vegetables, and a protein source."
        )
    else:
        suggestion = (
            "You have a smaller amount remaining today. "
            "Consider a lighter balanced meal with vegetables and "
            "a suitable protein source."
        )

    st.info(suggestion)


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)

        if response is None:
            return False, "Gemini returned an empty response."

        if not response.text:
            return False, "Gemini returned an empty response."

        return True, response.text

    except Exception as error:
        return False, str(error)


# ============================================================
# INITIAL SESSION STATE
# ============================================================

if "onboarded" not in st.session_state:
    st.session_state.onboarded = False


# ============================================================
# ONBOARDING PAGE
# ============================================================

if not st.session_state.onboarded:

    st.title(
        "MacroSnap - AI Nutrition Vision Chatbot"
    )

    st.caption(
        "Snap it | Track it | Email your nutrition summary"
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Enter your name"
        )

        email = st.text_input(
            "Enter your email address",
            placeholder="example@gmail.com",
            help=(
                "This is the email address where your "
                "MacroSnap nutrition summary will be sent."
            )
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
            "Submit",
            use_container_width=True
        )

    if submitted:

        if not name.strip():
            st.error("Please enter your name.")
            st.stop()

        if not email.strip():
            st.error("Please enter your email address.")
            st.stop()

        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(email_pattern, email.strip()):
            st.error(
                "Please enter a valid email address."
            )
            st.stop()

        try:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()
            st.session_state.weight = weight
            st.session_state.goal = goal

            st.session_state.targets = calculate_nutrition_targets(
                weight,
                goal
            )

            st.session_state.daily_totals = {
                "Calories": 0.0,
                "Protein": 0.0,
                "Carbohydrates": 0.0,
                "Fat": 0.0,
                "Fiber": 0.0
            }

            st.session_state.meal_history = []

            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )

            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()

        except Exception as error:
            st.error(
                "Unable to start MacroSnap."
            )
            st.code(
                str(error)
            )

    st.stop()


# ============================================================
# GET USER DATA
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
        "MacroSnap - AI Nutrition Vision Chatbot"
    )


# ============================================================
# SEND SUMMARY TO GMAIL
# ============================================================

with button_col:

    send_disabled = (
        len(st.session_state.messages) <= 1
    )

    if st.button(
        "Send Summary to Gmail",
        disabled=send_disabled,
        use_container_width=True
    ):

        tracking_context = f"""
Include these current MacroSnap tracking details in the summary:

Daily target:
Calories: {targets['Calories']} kcal
Protein: {targets['Protein']} g
Carbohydrates: {targets['Carbohydrates']} g
Fat: {targets['Fat']} g
Fiber: {targets['Fiber']} g

Consumed so far:
Calories: {round(st.session_state.daily_totals['Calories'])} kcal
Protein: {round(st.session_state.daily_totals['Protein'])} g
Carbohydrates: {round(st.session_state.daily_totals['Carbohydrates'])} g
Fat: {round(st.session_state.daily_totals['Fat'])} g
Fiber: {round(st.session_state.daily_totals['Fiber'])} g
"""

        with st.spinner(
            "Generating your nutrition summary..."
        ):
            gemini_success, summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT + tracking_context]
            )

        if not gemini_success:
            st.error(
                f"Unable to generate the summary: {summary}"
            )

        else:
            try:
                email_success, email_info = send_email(
                    st.session_state.email,
                    "Your MacroSnap Nutrition Summary",
                    summary
                )

                if email_success:
                    st.success(
                        "Nutrition summary sent successfully! "
                        "Check your email."
                    )
                else:
                    st.error(
                        f"Couldn't send the email: {email_info}"
                    )

            except Exception as error:
                st.error(
                    f"Couldn't send the email: {error}"
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
    "Personalized Daily Nutrition Target"
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
# DAILY TRACKING
# ============================================================

show_tracking_dashboard()

if st.session_state.meal_history:
    show_next_meal_suggestion()

    if st.button(
        "Clear Today's Meal Tracking",
        use_container_width=True
    ):
        st.session_state.daily_totals = {
            "Calories": 0.0,
            "Protein": 0.0,
            "Carbohydrates": 0.0,
            "Fat": 0.0,
            "Fiber": 0.0
        }
        st.session_state.meal_history = []
        st.rerun()


# ============================================================
# WELCOME MESSAGE
# ============================================================

if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    render_message(message)


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal to get started",
    accept_file=True,
    file_type=["png", "jpg", "jpeg"]
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
    # CHECK INPUT
    # ========================================================

    if not parts:

        st.warning(
            "Please enter a question or upload a food image."
        )

        st.stop()

    # ========================================================
    # GEMINI RESPONSE
    # ========================================================

    with st.spinner(
        "Analyzing your food and generating personalized nutrition..."
    ):

        gemini_success, answer = ask_gemini(parts)

    if not gemini_success:

        st.error(
            f"Unable to get a response from Gemini: {answer}"
        )

    else:

        # ----------------------------------------------------
        # SAVE GEMINI RESPONSE
        # ----------------------------------------------------

        add_message(
            "assistant",
            "text",
            answer
        )

        # ----------------------------------------------------
        # ADD MEAL TO DAILY TRACKING
        # ----------------------------------------------------

        nutrition = extract_nutrition(answer)

        if nutrition is not None:

            add_meal_to_tracker(nutrition)

            overall, calorie_status, protein_status = get_goal_fit(
                nutrition
            )

            st.session_state.last_goal_fit = {
                "overall": overall,
                "calorie_status": calorie_status,
                "protein_status": protein_status
            }

        # ----------------------------------------------------
        # RERUN
        # ----------------------------------------------------

        st.rerun()


# ============================================================
# LAST MEAL GOAL FIT
# ============================================================

if "last_goal_fit" in st.session_state:

    st.subheader("How This Meal Fits Your Goal")

    fit = st.session_state.last_goal_fit

    st.write(
        f"**Goal Fit:** {fit['overall']}"
    )

    st.write(
        f"• {fit['calorie_status']}"
    )

    st.write(
        f"• {fit['protein_status']}"
    )


# ============================================================
# MEAL HISTORY
# ============================================================

show_meal_history()

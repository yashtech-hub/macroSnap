# MacroSnap – AI Nutrition Vision Chatbot

MacroSnap is an AI-powered nutrition chatbot that analyzes food images and provides estimated nutritional information. Users can upload a meal image, get calories and macronutrient estimates, set a nutrition goal based on their weight, track their meals, ask follow-up questions, and receive their nutrition summary through email.

## Features

* Upload a food or meal image
* Identify food items using AI
* Estimate calories, protein, carbohydrates, fat, and fiber
* View nutrition information in a structured table
* Set personalized nutrition targets based on weight and fitness goal
* Track daily calories and macronutrients
* View remaining daily nutrition targets
* Maintain a session-based meal history
* Check whether a meal fits the user's current nutrition goal
* Get suggestions for what to eat next based on remaining targets
* Ask follow-up questions through the chatbot
* Generate a personalized nutrition summary
* Send the nutrition summary through email
* Simple and interactive web interface using Streamlit

## Technologies Used

* Python
* Streamlit
* Google Gemini API
* Google GenAI SDK
* JSON
* Regular Expressions
* SMTP / Gmail
* Git and GitHub

## Project Structure

```text
macroSnap/
│
├── app.py
├── prompts.py
├── email_service.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── secrets.toml.example
```

## How the Application Works

### 1. User Setup

The user provides:

* Name
* Email address
* Weight
* Fitness goal

The available goals are used to calculate personalized daily nutrition targets.

### 2. Food Image Analysis

The user uploads an image of a food or meal.

The image is sent to the Google Gemini model, which analyzes the meal and estimates:

* Calories
* Protein
* Carbohydrates
* Fat
* Fiber

The results are displayed in a structured nutrition table.

### 3. Personalized Nutrition Targets

MacroSnap calculates estimated daily nutrition targets based on the user's weight and selected goal.

The application provides different calorie targets for:

* Weight loss
* Weight gain
* Maintaining weight

Protein and fat targets are also calculated based on body weight, with carbohydrates calculated from the remaining calories.

### 4. Daily Nutrition Tracking

After a meal is analyzed, its nutritional values are added to the daily tracker.

The dashboard displays:

| Nutrient      | Daily Target | Consumed       | Remaining |
| ------------- | ------------ | -------------- | --------- |
| Calories      | User target  | Current intake | Remaining |
| Protein       | User target  | Current intake | Remaining |
| Carbohydrates | User target  | Current intake | Remaining |
| Fat           | User target  | Current intake | Remaining |
| Fiber         | Estimated    | Current intake | Remaining |

This allows the user to see how much of their daily target has been consumed.

### 5. Meal History

MacroSnap keeps a session-based history of analyzed meals.

For each meal, the application records information such as:

* Food name
* Calories
* Protein
* Carbohydrates
* Fat
* Fiber

Users can analyze multiple meals during the same session and see how their total nutrition changes.

### 6. Goal-Fit Analysis

After analyzing a meal, MacroSnap compares the meal's estimated nutrition with the user's remaining daily targets.

It provides a simple indication of whether the meal fits well with the selected nutrition goal.

### 7. Next Meal Suggestion

Based on the user's remaining calories and macronutrient targets, MacroSnap provides a simple suggestion for what type of food or meal could be considered next.

### 8. Nutrition Chatbot

Users can continue asking questions about food and nutrition after analyzing a meal.

For example:

* "Is this good for weight loss?"
* "What is a high-protein alternative?"
* "How much protein do I need?"
* "What can I eat for dinner?"

The chatbot uses Google Gemini to generate responses based on the application's nutrition context.

### 9. Email Summary

Users can request a nutrition summary and provide an email address.

MacroSnap generates a summary containing relevant nutrition information and sends it through Gmail SMTP.

## Nutrition Target Calculation

MacroSnap uses a simple weight-based calculation for estimated daily targets.

### Calories

* Weight loss: `weight × 25`
* Weight maintenance: `weight × 30`
* Weight gain: `weight × 35`

### Protein

```text
Protein = weight × 1.5 grams
```

### Fat

```text
Fat = weight × 0.8 grams
```

### Carbohydrates

Carbohydrates are calculated from the remaining calories after accounting for protein and fat.

These calculations are intended as simple estimates for the project and should not be considered professional dietary recommendations.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yashtech-hub/macroSnap.git
cd macroSnap
```

### 2. Create a Virtual Environment

For Windows:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Configure Secrets

Create the following file:

```text
.streamlit/secrets.toml
```

Add your Gemini API key:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

For email functionality, also add:

```toml
GMAIL_ADDRESS = "your_gmail_address@gmail.com"
GMAIL_APP_PASSWORD = "your_gmail_app_password"
```

The Gmail App Password should be generated from your Google account's App Password settings.

Do not upload the actual `secrets.toml` file to GitHub.

The repository contains:

```text
.streamlit/secrets.toml.example
```

as a template for the required configuration.

## Run the Application Locally

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

## Deployment

MacroSnap is deployed using Streamlit Community Cloud.

Live application:

https://macrosnap-mlmxjnnn7wrahbdeqi766j.streamlit.app/

### Deploying Your Own Version

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Select the GitHub repository.
4. Select `app.py` as the main application file.
5. Add the required secrets in the Streamlit Cloud Secrets section.
6. Deploy the application.

For Streamlit Cloud, the secrets should contain:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
GMAIL_ADDRESS = "your_gmail_address@gmail.com"
GMAIL_APP_PASSWORD = "your_gmail_app_password"
```

## Security

Sensitive credentials are not included in the GitHub repository.

The following files and directories are ignored by Git:

```text
.streamlit/secrets.toml
venv/
__pycache__/
*.pyc
```

Only the example secrets file is included in the repository.

Never commit:

* Gemini API keys
* Gmail passwords
* Gmail App Passwords
* Other private credentials

## Limitations

The nutritional values provided by MacroSnap are estimates. Results can vary depending on:

* Food type
* Ingredients
* Portion size
* Preparation method
* Image quality
* Accuracy of AI-based food recognition

The daily nutrition targets are simple project-level calculations based on body weight and selected goals. They are not medical or professional dietary recommendations.

Meal tracking is currently session-based, so the tracking data is not stored permanently in a database.

The application should be used for general informational purposes and is not a replacement for professional medical or dietary advice.

## Future Improvements

Possible future improvements include:

* Improve food and portion-size detection
* Add persistent user accounts
* Store meal history in a database
* Add weekly and monthly nutrition reports
* Add graphical nutrition dashboards
* Improve personalized meal recommendations
* Add more detailed fitness and nutrition goals
* Improve nutrition estimation accuracy
* Add barcode-based food recognition
* Add a mobile-friendly version
* Add integration with fitness and health tracking platforms

## Author

**Yashwanth Chigullapally**

GitHub:

https://github.com/yashtech-hub

MacroSnap Repository:

https://github.com/yashtech-hub/macroSnap

Live Demo:

https://macrosnap-mlmxjnnn7wrahbdeqi766j.streamlit.app/

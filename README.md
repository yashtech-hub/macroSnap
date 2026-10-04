# MacroSnap

MacroSnap is an AI-based nutrition assistant that analyzes food images and provides estimated nutritional information. Users can upload an image of their meal, ask questions about the food, view estimated calories and macronutrients, and receive a nutrition summary through email.

## Features

* Upload a food or meal image
* Identify food items using AI
* Estimate calories and macronutrients
* Ask follow-up questions through the chatbot
* Generate a nutrition summary
* Send the nutrition summary through email
* Simple web interface using Streamlit

## Technologies Used

* Python
* Streamlit
* Google Gemini API
* Google GenAI SDK
* JSON
* Email / SMTP

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

1. The user uploads an image of a food or meal.
2. The image is sent to the Gemini AI model for analysis.
3. The application identifies the food items in the image.
4. The AI provides estimated calories, protein, carbohydrates, and fat.
5. The user can ask additional questions about the meal.
6. A final nutrition summary can be generated and sent through email.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yashtech-hub/macroSnap.git
cd macroSnap
```

### 2. Create a virtual environment

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install the required packages

```bash
pip install -r requirements.txt
```

### 4. Configure the API key

Create the following file:

```text
.streamlit/secrets.toml
```

Add your Gemini API key:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

If email functionality requires additional credentials, add the required email configuration to the same file.

Do not upload `secrets.toml` to GitHub. The repository contains `secrets.toml.example` as a template.

## Run the Application

Run the following command:

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

## Deployment

The application can be deployed using Streamlit Community Cloud.

To deploy:

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Select the MacroSnap repository.
4. Select `app.py` as the main application file.
5. Add the required secrets in the Streamlit Cloud Secrets section.
6. Deploy the application.

## Security

The actual API keys and other sensitive information are not included in the repository.

The following files are ignored by Git:

```text
.streamlit/secrets.toml
venv/
__pycache__/
*.pyc
```

Only the example secrets file is included in the repository.

## Limitations

The nutritional values provided by the application are estimates. Results can vary depending on the type of food, ingredients, portion size, preparation method, and image quality.

The application is intended for general informational purposes and is not a replacement for professional medical or dietary advice.

## Future Improvements

* Improve food and portion-size detection
* Add daily and weekly nutrition tracking
* Add user-specific nutrition goals
* Add nutrition history
* Add meal recommendations
* Add a dashboard for tracking nutrition
* Improve the accuracy of nutritional estimates

## Author

Yashwanth Chigullapally

GitHub: https://github.com/yashtech-hub

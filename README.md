# Rasa NLU 🤖 + Google Calendar 📅 API Integration 🔄

This program integrates Rasa NLU with the Google Calendar API, allowing you to efficiently manage your events. 📝

## 📝 Description
The Rasa NLU + Google Calendar API integration program provides a user-friendly interface to schedule events, retrieve event lists, and check for available free time slots. With the power of natural language understanding and seamless Google Calendar integration, you can effortlessly manage your busy schedule. ✨

## 🎥 Demo
[Google-Events-Chatbot.webm](https://github.com/kamya-ai/Google-Events-Calendar/assets/139073975/1151648b-0714-4fb6-b2c9-222d7b8c3c70)

## ⭐️ Features

Welcome to our awesome program! Here's a brief overview of what this 🆒 application can do for you:

📆 1. Schedule Events:
   ✏️ Prompt: You can specify your event details, including the name and time.
   ✅ Function: The program will schedule your event as per the specified time. 🎉
   ⚠️ Conflict Handling: If there is a scheduling conflict, it will notify you and provide details of the conflicting events and their timings.
   💼 Free Time Slots: Additionally, it will present the available free time slots for the same day. 🕓

📋 2. Get Event List:
   📅 Prompt: You can specify a day to retrieve a list of events scheduled.
   ✅ Function: The program will fetch a list of events scheduled on the specified day. 📝

⏰ 3. Get Free Slots:
   📅 Prompt: You can specify a day to check for available free time slots.
   ✅ Function: The program will provide you with a list of free time slots for the specified day. 🆓

Let's get started and have a great time managing your events with ease! 🎈

🚧 Note: Make sure you have a valid Google Calendar API key and the necessary Rasa NLU dependencies installed to ensure smooth execution. If you face any issues or have questions, feel free to reach out for assistance. 🙌

## 📋 Requirements
To use this program, you need the following:

- Python 3.6+
- Rasa NLU library
- Google Calendar API credentials (API key or OAuth 2.0 credentials)

## 🔧 Installation
1. Clone this repository:
   ```
   git clone https://github.com/kamya-ai/Google-Events-Chatbot.git
   cd Rasa-Google-Events
   ```

2. Create an anaconda environment with python version 3.8 (As this program is prepared on python v3.8):

    ```
    conda create -n rasaenv python=3.8
    conda activate rasaenv
    ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up Google Calendar API credentials:
   - If using an API key, follow the instructions [here](https://developers.google.com/calendar/quickstart/python#step_1_turn_on_the).
   - If using OAuth 2.0 credentials, follow the instructions [here](https://developers.google.com/calendar/quickstart/python#step_1_turn_on_the) and download the credentials JSON file.

5. Rename the downloaded credentials JSON file to `credentials.json` and place it in the project directory.

## ▶️ Usage
1. Make sure you have completed the installation steps.

2. Run the following two processes in two seperate terminals:
   ```
   rasa run actions
   ```
   ```
   sudo docker run -p 8000:8000 rasa/duckling
   ```

3. In a seperate third terminal, run the following command to have a chat with the chatbot.
    ```
    rasa shell
    ```

3. Follow the prompts to schedule events, retrieve event lists, or check for free time slots.

4. Enjoy managing your events effortlessly!

Note: Here, the model given is working for the tasks specified above. But to train newer models, some files are not given fully. To get them and have a customized chatbot with some added customization, you can contact through the given website or the below given email-id:-
info@kamyawebdesigners.com

## 🔍 Troubleshooting
- **API Key/OAuth 2.0 Credentials:** Ensure that you have a valid Google Calendar API key or OAuth 2.0 credentials and have correctly placed the `credentials.json` file in the project directory.
- **Dependency Issues:** If you encounter any dependency-related issues, make sure you have installed the required dependencies by running `pip install -r requirements.txt`.

👥 Contributions
Contributions to this project are welcome. If you find any bugs or have suggestions for improvements, please create an issue on the project repository: https://github.com/kamya-ai/Google-Events-Chatbot/issues

🚧 Note: The program requires a stable internet connection to interact with the Google Calendar API.

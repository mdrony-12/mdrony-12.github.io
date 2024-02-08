from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit 
import speech_recognition as sr
import datetime
import webbrowser
import requests
import urllib.parse
import subprocess

app = Flask(__name__)
socketio = SocketIO(app)


def get_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # You can change this to "imperial" for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            weather_response = f"The current weather in {city} is {temperature}°C with {description}."
            return weather_response
        else:
            error_message = data.get('message', 'Unknown error')
            weather_response = f"Failed to retrieve weather information: {error_message}"
            return weather_response
    except Exception as e:
        return f"Error fetching weather information: {str(e)}"

OPENWEATHERMAP_API_KEY = '67d0624cb54e99c56bb814ddffcd864e'

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        print("Please Wait...")
        text1 = recognizer.recognize_google(audio)
        text = text1.lower()
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand.")
        return None
    except sr.RequestError as e:
        print(f"Error with the speech recognition service; {e}")
        return None
    
def get_joke():
    joke_url = "https://v2.jokeapi.dev/joke/Any"
    try:
        response = requests.get(joke_url)
        data = response.json()

        if response.status_code == 200:
            if 'joke' in data:
                return data['joke']
            elif 'setup' in data and 'delivery' in data:
                return f"{data['setup']} {data['delivery']}"
            else:
                return "Unable to fetch a joke at the moment."
        else:
            return "Failed to retrieve a joke."
    except Exception as e:
        return f"Error fetching joke: {str(e)}"
    
def process_joke_command():
    joke = get_joke()
    return joke

def greet():
    print("Hello, I am Jarvis. How can I assist you today?")
    return "Hello, I am Jarvis. How can I assist you today?"

def get_time():
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    print("Current time is : "+ str(current_time))
    return f"The current time is {current_time}"

def search_google(api_key, cx, query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200 and 'items' in data:
            search_results = data['items']
            return search_results
        else:
            return None
    except Exception as e:
        return None

def open_application(application_name):
    if "chrome" in application_name.lower():
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        try:
            subprocess.Popen([chrome_path])
            print("Opening Chrome")
        
        except Exception as e:
            print(f"Error opening Chrome: {e}")
            
    else:
        try:
            subprocess.Popen([application_name], shell=True)
            print(f"Opening {application_name}")
            op = f"Opening {application_name}"
            
        except Exception as e:
            print(f"Error opening {application_name}: {e}")
            qu2 = f"Error opening {application_name}"

def get_latest_news(api_key):
    news_url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "country": "us",  # Change the country code as needed
    }

    try:
        response = requests.get(news_url, params=params)
        data = response.json()

        if response.status_code == 200:
            articles = data.get('articles', [])
            if articles:
                news_response = "Here are the latest news headlines:\n"
                for article in articles[:5]:  # Displaying the first 5 articles
                    news_response += f"- {article['title']}\n"
                return news_response
            else:
                return "No news articles found."
        else:
            return "Failed to retrieve news information."
    except Exception as e:
        return f"Error fetching news: {str(e)}"

def play_song():
    # Add your logic to play a song here
    return "Playing your favorite song!"
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('voice_input')
def handle_voice_input():
    data = request.get_json()
    command = data.get('command')

    if command:
        emit('response', {'response': command})

@app.route('/process_command', methods=['POST'])
def process_command():
    data = request.get_json()
    command = data.get('command')

    if command:
        if "time" in command:
            time_response = get_time()
            return time_response
        elif "who are you" in command:
            response = "I am Voogle Assistant, your virtual assistant created by Rony."
            return response
        elif "Search for something" in command:
            response = "Type [Search for 'your query'] and hit enter"
            return response
        elif "play a song" in command:
            song_response = play_song()
            return song_response
        elif "joke" in command:
            joke_response = process_joke_command()
            return joke_response
        elif "search" in command:
            search_query = command.replace("search for", "").strip()
            if search_query:
                search_results = search_google('AIzaSyD6H4H16nWyFNRGUqFI6sCXsEVdVevjszg', '87baaa18d59d44e88', search_query)
                if search_results:
                    return search_results
        
        elif "who made you" in command:
            response = "I was created by Rony."
            return response

        elif "your name" in command:
            response = "My name is Voogle Assistant."
            return response
        elif "news" in command:
            news_response = get_latest_news("9e538a8f03fd404a9ed428dee72601b3")
            return news_response
        elif "be my friend" in command:
            response = "Certainly! I'm here to assist and chat with you."
            return response

        elif "how are you" in command:
            response = "I'm just a computer program, but I'm here and ready to help you!"
            return response

        elif "fine" in command:
            response = "Great to hear! Is there anything specific you'd like assistance with?"
            return response
        
        elif "weather" in command:
            # Replace 'CityName' with the actual city name (e.g., 'New York')
            weather_response = get_weather(OPENWEATHERMAP_API_KEY, 'Dhaka')
            return weather_response

        elif "your friend" in command:
            response = "Absolutely! You and all users are valued friends to me."
            return response

        elif "my name" in command:
            response = "I don't know your name. Please tell me your name."
            # Get user input for name
            name = recognize_speech()
            return f"Nice to meet you, {name}!"

        elif "f***" in command or "fuck" in command:
            response = "I'm sorry to hear that you're feeling upset. If there's anything I can do to help, please let me know."
            return response
        elif "who is" in command:
            search_query = command.replace("who is", "").strip()
            if search_query:
                search_google(search_query)
                print(f"Searching Google for {search_query}")
                qu1 = f"Searching Google for {search_query}"
    
                return qu1  # Added this line to return a response
        elif "search" in command:
            search_query = command.replace("search for", "").strip()
            if search_query:
                search_google(search_query)
                response = f"Searching Google for {search_query}"
                return response
            else:
                response = "Please provide a search query."
                return response
        elif "open" in command:
            app_name = command.replace("open", "").strip()
            if app_name:
                open_application(app_name)
                response = f"Opening {app_name}"
        
        
        else:
            response = "Sorry, I don't understand that command."
    
            return response
    else:
        response = "Please provide a command."
     
        return response

if __name__ == "__main__":
    app.template_folder = 'templates'
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
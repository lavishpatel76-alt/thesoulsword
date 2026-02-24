from flask import Flask, render_template, request, redirect, jsonify
import csv
import os
import google.generativeai as genai

app = Flask(__name__)
DATA_FILE = 'stories.csv'
ADMIN_PASSWORD = "iitj" 

# Configure Gemini API
# You will set 'GEMINI_API_KEY' in Render's Environment Variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# Change this line in your chat function
model = genai.GenerativeModel('gemini-pro')

def read_stories():
    stories = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stories.append(row)
    return stories[::-1]

@app.route('/')
def home():
    all_stories = read_stories()
    return render_template('index.html', stories=all_stories)

@app.route('/post', methods=['POST'])
def post_story():
    user_pass = request.form.get('admin_pass')
    if user_pass != ADMIN_PASSWORD:
        return "Unauthorized!", 403
    
    title = request.form.get('story_title')
    content = request.form.get('story_content')
    image = request.form.get('story_image')
    
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['title', 'content', 'image']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'title': title, 'content': content, 'image': image})
    return redirect('/')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Force the key to load INSIDE the function so it's always fresh
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"response": "AI: I can't find my API Key in Render settings!"})
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    persona = "You are an AI version of Lavish, a student at IIT Jodhpur..."
    
    try:
        response = model.generate_content(f"{persona}\nUser: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"AI Error: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
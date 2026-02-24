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
    
    # We load the key here to ensure it's fresh from Render's environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"response": "AI: I can't find my API Key in Render settings!"})
    
    # Re-configuring inside the function ensures the key is active
    genai.configure(api_key=api_key)
    
    # IMPORTANT: We use 'gemini-pro' here to match your top configuration
    current_model = genai.GenerativeModel('gemini-pro')
    
    persona = "You are an AI version of Lavish, a student at IIT Jodhpur studying Applied AI and Data Science. Be helpful and smart."
    
    try:
        # Use 'current_model' instead of the global 'model' to avoid conflicts
        response = current_model.generate_content(f"{persona}\nUser: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        # This will tell us if there is a library version issue or a quota issue
        return jsonify({"response": f"AI Error: {str(e)}"}), 500
    
if __name__ == '__main__':
    # Use the port Render provides, or default to 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
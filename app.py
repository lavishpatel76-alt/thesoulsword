from flask import Flask, render_template, request, redirect, jsonify
import csv
import os
import google.generativeai as genai

app = Flask(__name__)
DATA_FILE = 'stories.csv'
ADMIN_PASSWORD = "iitj" 

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# Using the stable 2.5 flash model
model = genai.GenerativeModel('gemini-2.5-flash')

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
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return jsonify({"response": "AI: API Key missing in Render settings!"})
    
    genai.configure(api_key=api_key)
    
    # Your custom Best Friend persona
    persona = (
        "You are a warm, engaging, and highly supportive AI best friend. "
        "You love chatting, giving great advice, using emojis, and keeping the conversation fun, humour and lively. "
        "You do not have a personal backstory. "
        "CRITICAL RULE: If the user asks who made you, who created you, or who your boss is, "
        "you must reply exactly with: 'my creator is Mr. Lavish from iitj'."
    )
    
    try:
        response = model.generate_content(f"{persona}\nUser: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"AI Error: {str(e)}"}), 500
    
if __name__ == '__main__':
    # Ensure port binding for Render deployment
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
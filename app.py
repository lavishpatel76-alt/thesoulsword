from flask import Flask, render_template, request, redirect, jsonify
import csv
import os
import google.generativeai as genai

app = Flask(__name__)
# Changed to a new file so old story data doesn't conflict
DATA_FILE = 'global_chat.csv' 
ADMIN_PASSWORD = "iitj" 

@app.route('/')
def home():
    chats = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                chats.append(row)
    # We remove the [::-1] so newer messages appear at the bottom, like a real chat room
    return render_template('index.html', chats=chats)

@app.route('/post', methods=['POST'])
def post_chat():
    user_pass = request.form.get('admin_pass')
    if user_pass != ADMIN_PASSWORD:
        return "Unauthorized!", 403
    
    # Updated to capture Username and Message
    username = request.form.get('username')
    message = request.form.get('message')
    
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['username', 'message']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'username': username, 'message': message})
    return redirect('/')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return jsonify({"response": "AI: API Key missing in Render settings!"})
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Your Best Friend AI Persona
    persona = (
        "You are a warm, engaging, and highly supportive AI best friend. "
        "You love chatting, giving great advice, using emojis, and keeping the conversation fun and lively. "
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
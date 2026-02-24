from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)
DATA_FILE = 'stories.csv'

# Set your secret password here
ADMIN_PASSWORD = "iitj" 

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
    # Password check logic
    user_pass = request.form.get('admin_pass')
    if user_pass != ADMIN_PASSWORD:
        return "<h1>Unauthorized!</h1><p>Incorrect password. Go back and try again.</p>", 403

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

@app.route('/delete', methods=['POST'])
def delete_story():
    # Added password check for delete as well to keep it secure
    user_pass = request.form.get('admin_pass')
    if user_pass != ADMIN_PASSWORD:
        return "<h1>Unauthorized!</h1>", 403

    title_to_delete = request.form.get('story_title')
    stories = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            stories = [row for row in reader if row['title'] != title_to_delete]
            
    with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['title', 'content', 'image']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stories)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
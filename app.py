from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)
# IMPORTANT: Ensure this matches the file name in your sidebar
DATA_FILE = 'stories.csv'

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
    title = request.form.get('story_title')
    content = request.form.get('story_content')
    image = request.form.get('story_image')
    
    # This block creates the file if it doesn't exist
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['title', 'content', 'image']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader() # Writes the top row (headers)
        writer.writerow({'title': title, 'content': content, 'image': image})
    
    return redirect('/')

@app.route('/delete', methods=['POST'])
def delete_story():
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
   
    
    
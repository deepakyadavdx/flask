# from flask import Flask, jsonify, request, render_template_string

# app = Flask(__name__)

# # A simple in-memory structure to store tasks
# tasks = []

# @app.route('/', methods=['GET'])
# def home():
#     # Display existing tasks and a form to add a new task
#     html = '''
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Todo List</title>
# </head>
# <body>
#     <h1>Todo List</h1>
#     <form action="/add" method="POST">
#         <input type="text" name="task" placeholder="Enter a new task">
#         <input type="submit" value="Add Task">
#     </form>
#     <ul>
#         {% for task in tasks %}
#         <li>{{ task }} <a href="/delete/{{ loop.index0 }}">x</a></li>
#         {% endfor %}
#     </ul>
# </body>
# </html>
# '''
#     return render_template_string(html, tasks=tasks)

# @app.route('/add', methods=['POST'])
# def add_task():
#     # Add a new task from the form data
#     task = request.form.get('task')
#     if task:
#         tasks.append(task)
#     return home()

# @app.route('/delete/<int:index>', methods=['GET'])
# def delete_task(index):
#     # Delete a task based on its index
#     if index < len(tasks):
#         tasks.pop(index)
#     return home()



from flask import Flask, request, render_template, jsonify
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import FireCrawlLoader

app = Flask(__name__)

urls = [
"https://consultquark.com/THA_Act_1996.pdf"
]

docs = [FireCrawlLoader (api_key="fc-d49c1c3467fb4e15b6713ff0bbb5cbf6", url=url, mode="scrape").load() for url in urls]
# Split documents
docs_list = [item for sublist in docs for item in sublist]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():

    chunk_size = int(request.form.get('chunk_size', 250))
    chunk_overlap = int(request.form.get('chunk_overlap', 0))

    try:
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size, chunk_overlap=0
        )
        doc_splits = text_splitter.split_documents(docs_list)
        #Filter out complex metadata and ensure proper document formatting
        filtered_docs = []
        for doc in doc_splits:
            if isinstance(doc, Document) and hasattr(doc, 'metadata'):
                clean_metadata = {
                    k: v for k, v in doc.metadata.items()
                    if isinstance(v, (str, int, float, bool))
                }
                filtered_docs.append({
                    'content': doc.page_content,
                    'chunk': len(doc.page_content)
                    # 'metadata': clean_metadata
                })

        # Return processed chunks as JSON
        return jsonify({'chunks': filtered_docs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    # Here you would implement your patent search logic
    results = []  # Dummy placeholder for search results
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
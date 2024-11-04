from flask import Flask

app = Flask(__name__)

#definir rota raiz
@app.route('/teste')
def home():
    return 'Hello, World!'
if __name__ == "__main__":
    app.run(debug=True)

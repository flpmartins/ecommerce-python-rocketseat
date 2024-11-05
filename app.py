from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, login_manager, login_required, logout_user

# Configurar o Flask para usar o SQLite como banco de dados
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_maneger = login_manager()

db = SQLAlchemy(app)
login_maneger.init_app(app)
login_maneger.login_view = "login"
CORS(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(10), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

@login_required.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return {"message": "Logged out successfully!"}

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(name=data['username']).first()

    if user and data.get('password') == user.password:
        login_user(user)  # Autentica o usuário
        return {"message": "Login successfully!"}
    return jsonify({"message": "unathorized login failed"}), 401


# Rota para adicionar produto
@app.route('/api/products/add', methods=['POST'])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return {"data": data, "message": 'Product added successfully!'}
    return jsonify({"message": "Invalid product data"}), 400

# Rota para deletar produto
@app.route('/api/product/delete/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted successfully!"}
    return jsonify({"message": "Product not found!"}), 404

@app.route('/api/product/list/<int:product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
    return jsonify({"message": "Product not found!"}), 404

@app.route('/api/product/list', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = []
    if products:
        for product in products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                }
            product_list.append(product_data)
        return jsonify({"products": product_list})
    return jsonify({"message": "Product not found!"}), 404


@app.route('/api/product/update/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found!"}), 404
    data = request.json
    if 'name' in data:
        product.name = data["name"]

    if 'price' in data:
        product.price = data["price"]

    if 'description' in data:
        product.description = data["description"]
    db.session.commit()
    return jsonify({"data": data, "message": "Product updated successfully!"})

# Rota raiz
@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == "__main__":
    app.run(debug=True)

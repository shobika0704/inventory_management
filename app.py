from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name, price, stock = db.Column(db.String(50)), db.Column(db.Float), db.Column(db.Integer)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name, phone = db.Column(db.String(50)), db.Column(db.String(20))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity, total = db.Column(db.Integer), db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now)
    customer, product = db.relationship('Customer'), db.relationship('Product')

with app.app_context(): db.create_all()

@app.route('/')
def home():
    p, c, o = Product.query.all(), Customer.query.all(), Order.query.order_by(Order.date.desc()).all()
    return render_template('dashboard.html', prods=p, custs=c, ords=o, sales=sum(x.total for x in o), low=sum(1 for x in p if x.stock < 10))

@app.route('/product/add', methods=['POST'])
def add_p():
    db.session.add(Product(name=request.form['name'], price=float(request.form['price']), stock=int(request.form['stock'])))
    db.session.commit(); return redirect('/')

@app.route('/product/del/<int:id>')
def del_p(id):
    p = db.session.get(Product, id)
    if p: db.session.delete(p); db.session.commit()
    return redirect('/')

@app.route('/customer/add', methods=['POST'])
def add_c():
    db.session.add(Customer(name=request.form['name'], phone=request.form['phone']))
    db.session.commit(); return redirect('/')

@app.route('/customer/del/<int:id>')
def del_c(id):
    c = db.session.get(Customer, id)
    if c: db.session.delete(c); db.session.commit()
    return redirect('/')

@app.route('/order/add', methods=['POST'])
def add_o():
    p, q = db.session.get(Product, request.form['product_id']), int(request.form['qty'])
    if p and p.stock >= q:
        p.stock -= q
        db.session.add(Order(customer_id=request.form['customer_id'], product_id=p.id, quantity=q, total=p.price * q))
        db.session.commit()
    return redirect('/')

@app.route('/order/del/<int:id>')
def del_o(id):
    o = db.session.get(Order, id)
    if o:
        p = db.session.get(Product, o.product_id)
        if p: p.stock += o.quantity
        db.session.delete(o); db.session.commit()
    return redirect('/')

if __name__ == '__main__': app.run(debug=True)

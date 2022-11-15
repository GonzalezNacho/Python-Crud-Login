from flask import Flask, render_template , request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from decouple import config

# Models: 
from models.modelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)


app.config['MYSQL_HOST'] = config('MYSQL_HOST')
app.config['MYSQL_USER'] = config('MYSQL_USER') 
app.config['MYSQL_PASSWORD'] = config('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = config('MYSQL_DB') 
mysql = MySQL(app)
loginManagerApp = LoginManager(app)

app.secret_key = 'mysecretkey'

@loginManagerApp.user_loader
def load_user(id):
    return ModelUser.getById(mysql, id)

@app.route('/')
def index():
    return redirect(url_for('Home'))

@app.route('/home')
#@login_required
def Home():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM products')
    data = cur.fetchall()
    return render_template('index.html', products = data)
    

@app.route('/add_product', methods =['POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        discount = request.form['discount']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO products (name, description, discount) VALUES (%s,%s,%s);',(name, description, discount))
        mysql.connection.commit()
        flash('Product Added successfully')
        return redirect(url_for('Home'))

@app.route('/edit/<id>')
def get_product(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM products WHERE id = %s', (id))
    data = cur.fetchall()
    return render_template('edit-product.html', product = data[0])

@app.route('/update/<string:id>', methods = ['POST'])
def update_product(id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        discount = request.form['discount']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE products
            SET name = %s,
                discount = %s,
                description = %s
            WHERE id = %s; 
        """, (name, discount, description, id))
        mysql.connection.commit()
        flash('Product Update Successfully')
        return redirect(url_for('Home'))

@app.route('/delete/<string:id>')
def delete_product(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM products WHERE id = {0};'.format(id))
    mysql.connection.commit()
    flash('Product Removed successfully')
    return redirect(url_for('Home'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        userForm = request.form['user']
        passwordForm = request.form['password']
        user = User(0,userForm, passwordForm)
        loggedUser = ModelUser.login(mysql, user)
        if loggedUser != None:
            if loggedUser.password:
                login_user(loggedUser)
                return redirect(url_for('Home'))
            else:
                flash("Invalid password ...")
                return render_template('login.html')    
        else:
            flash("User not found ...")
            return render_template('login.html')
    return render_template('login.html')
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Home'))

def status401(error):
    return redirect(url_for('login'))

def status404(error):
    return "<h1>Página no encontrada</h1>", 404

    
if __name__ == '__main__':
    app.register_error_handler(401, status401)
    app.register_error_handler(404, status404)
    app.run(port = 3000, debug = True)
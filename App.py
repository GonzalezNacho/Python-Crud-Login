from flask import Flask, render_template , request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required

#Configuración
from config import myConfig

# Modelos: 
from models.modelUser import ModelUser

# Entidades:
from models.entities.User import User

app = Flask(__name__)

csrf = CSRFProtect()
mysql = MySQL(app)
loginManagerApp = LoginManager(app)

#Rutas
@loginManagerApp.user_loader
def load_user(id):
    return ModelUser.getById(mysql, id)

@app.route('/')
def index():
    return redirect(url_for('Home'))

@app.route('/home')
def Home():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM products')
    data = cur.fetchall()
    return render_template('index.html', products = data)
    

@app.route('/add_product', methods =['POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        discount = request.form['discount']
        discountCode = request.form['discountCode']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO products (name, description, discount, discount_code) VALUES (%s,%s,%s, %s);',(name, description, discount, discountCode))
        mysql.connection.commit()
        flash('Product Added successfully')
        return redirect(url_for('Home'))

@app.route('/edit/<id>')
@login_required
def get_product(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM products WHERE id = %s', (id))
    data = cur.fetchall()
    return render_template('edit-product.html', product = data[0])

@app.route('/update/<string:id>', methods = ['POST'])
@login_required
def update_product(id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        discount = request.form['discount']
        discountCode = request.form['discountCode']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE products
            SET name = %s,
                discount = %s,
                description = %s,
                discount_code = %s
            WHERE id = %s; 
        """, (name, discount, description, discountCode, id))
        mysql.connection.commit()
        flash('Product Update Successfully')
        return redirect(url_for('Home'))

@app.route('/delete/<string:id>')
@login_required
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
                pagina = redirect(url_for('Home'))
            else:
                flash("Invalid password ...")
                pagina = render_template('login.html')    
        else:
            flash("User not found ...")
            pagina = render_template('login.html')
    else:
        pagina = render_template('login.html')
    return pagina
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Home'))

# definicion de funciones para codigos de estado de respuesta http

# error 401: Unauthorized, Es necesario autenticar para obtener la respuesta solicitada. Redirige al login
def status401(error):
    return redirect(url_for('login'))

# error 404: El servidor no pudo encontrar el contenido solicitado. . Devuelve el mensaje "Página no encontrada" y el codigo de estado 404
def status404(error):
    return "<h1>Página no encontrada</h1>", 404

# manejo de los codigos de error con sus respectivas funciones
app.register_error_handler(401, status401)
app.register_error_handler(404, status404)

#se aplica configuración a la app desde el diccionario myConfig 
app.config.from_object(myConfig['configfromEnv'])

#para evitar cross site request forgery (falsificacion de formularios)
csrf.init_app(app)
    
if __name__ == '__main__':
    app.run(port = 3000, debug = True)
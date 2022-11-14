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
    return redirect(url_for('login'))

@app.route('/home')
#@login_required
def Home():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts')
    data = cur.fetchall()
    return render_template('index.html', contacts = data)
    

@app.route('/add_contact', methods =['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO contacts (fullname, phone, email) VALUES (%s,%s,%s);',(fullname, phone, email))
        mysql.connection.commit()
        flash('Contact Added successfully')
        return redirect(url_for('Home'))

@app.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id))
    data = cur.fetchall()
    return render_template('edit-contact.html', contact = data[0])

@app.route('/update/<string:id>', methods = ['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE contacts
            SET fullname = %s,
                email = %s,
                phone = %s
            WHERE id = %s; 
        """, (fullname, email, phone, id))
        mysql.connection.commit()
        flash('Contact Update Successfully')
        return redirect(url_for('Home'))

@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0};'.format(id))
    mysql.connection.commit()
    flash('Contact Removed successfully')
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
    return redirect(url_for('login'))

def status401(error):
    return redirect(url_for('login'))

def status404(error):
    return "<h1>Página no encontrada</h1>", 404

    
if __name__ == '__main__':
    app.register_error_handler(401, status401)
    app.register_error_handler(404, status404)
    app.run(port = 3000, debug = True)
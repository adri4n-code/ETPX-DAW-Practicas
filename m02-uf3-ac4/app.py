"""
Adrian Fernandez Roa 
ETPX
"""

# Importación de módulos externosç
import bcrypt
import mysql.connector
from flask import Flask,render_template,request;

# Funciones de backend #############################################################################

# connectBD: conecta a la base de datos users en MySQL
def connectBD():
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "04112002Aa",
        database = "users"
    )
    return db

# initBD: crea una tabla en la BD users, con un registro, si está vacía
def initBD():
    bd=connectBD()
    cursor=bd.cursor()
    
    # cursor.execute("DROP TABLE IF EXISTS users;")
    # Operación de creación de la tabla users (si no existe en BD)
    query="CREATE TABLE IF NOT EXISTS users(\
            user varchar(30) primary key,\
            password varchar(72),\
            name varchar(30), \
            surname1 varchar(30), \
            surname2 varchar(30), \
            age integer, \
            genre enum('H','D','NS/NC')); "
    cursor.execute(query)
            
    # Operación de inicialización de la tabla users (si está vacía)
    query="SELECT count(*) FROM users;"
    cursor.execute(query)
    count = cursor.fetchall()[0][0]
    if(count == 0):
        query = "INSERT INTO users \
            VALUES('user01','admin','Ramón','Sigüenza','López',35,'H');"
        cursor.execute(query)

    bd.commit()
    bd.close()
    return

# checkUser: comprueba si el par usuario-contraseña existe en la BD
# Caso 1: La contraseña no esta hasheada, es para el caso de ejemplo que se propone en el ej.
# def checkUser(user,password):
#     bd=connectBD()
#     cursor=bd.cursor()
    
#     query=f"SELECT user,name,surname1,surname2,age,genre FROM users WHERE user=%s\
#         AND password=%s"

#     valo=(user,password)
#     cursor.execute(query,valo)
#     userData = cursor.fetchall()

#     bd.close()
#     if userData == []:
#         return False
#     else:
#         return userData[0]


# Caso 2: La contraseña esta hasheada y se tiene que validar, y con la explicación del paso a paso de como lo he echo.

def checkUser (user,password):
    bd=connectBD()
    cursor = bd.cursor()
# Hacemos la consulta en la base de datos para obtener el registro del usuario.
    query= "SELECT user,password,name,surname1,surname2,age,genre FROM users WHERE user=%s"
    valo=(user,)
    cursor.execute(query, valo)
    userData = cursor.fetchone()
# El metodo fetchone es que se utiliza por solo nos va a devolver solo la fila sobre que se hace hace la consulta,
# en canvio si fuese con el metodo fetchall nos dovolvería una lista que contiene todas las filas.
    if userData is None:
        return False
    
# Extraemos la contraseña hasheada de la base de datos 
    paswordhash = userData[1]

# Hacemos la verificación de la contraseña que nos pasa el usuario con la que tenemos en la base de datos
    
    if bcrypt.checkpw(password.encode('utf-8'), paswordhash.encode('utf-8')):
        return userData
    else:
        return False


# cresteUser: crea un nuevo usuario en la BD
def createUser(user,passwordhash,name,surname1,surname2,age,genre):
    bd=connectBD()
    cursor=bd.cursor()
    query = f"insert into users(user,password,name,surname1,surname2,age,genre) VALUES(%s,%s,%s,%s,%s,%s,%s);"
    valores=(user, passwordhash,name,surname1,surname2,age,genre)
    cursor.execute(query,valores)
    bd.commit()
    bd.close()
    return

# Secuencia principal: configuración de la aplicación web ##########################################
# Instanciación de la aplicación web Flask
app = Flask(__name__)

# Declaración de rutas de la aplicación web
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    initBD()
    return render_template("login.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/results",methods=('GET', 'POST'))
def results():
    if request.method == ('POST'):
        formData = request.form
        user=formData['usuario']
        password=formData['contrasena']
        userData = checkUser(user,password)
# Results sin passwordhash
        # if userData == False:
        #     return render_template("results.html",login=False)
        # else:
        #     return render_template("results.html",login=True,userData=userData)
# Results con el hash
        if userData == False:
            return render_template("resultshash.html",login=False)
        else:
            return render_template("resultshash.html",login=True,userData=userData)

            

@app.route("/newUser",methods=('GET', 'POST'))
def newUser():
    if request.method == ('POST'):
        formData = request.form
        user=formData['user']
        password=formData['contrasena']
        password= password.encode()
        sal=bcrypt.gensalt()
        passwordhash=bcrypt.hashpw(password,sal)
        name=formData['Name']
        surname1=formData['Surname 1']
        surname2=formData['Surname 2']
        age=formData['Age']
        genre=formData['Genre']
        
        nuevouser =createUser(user,passwordhash,name,surname1,surname2,age,genre)
        if nuevouser == False:
            return render_template("newUser.html",login=False)
        else:
            return render_template("newUser.html",login=True)
   
    
# Configuración y arranque de la aplicación web
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run(host='localhost', port=5000, debug=True)
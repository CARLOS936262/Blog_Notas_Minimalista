from flask import Flask, render_template, request, redirect, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "clave_super_secreta"


# CONEXIÓN MONGODB
cliente = MongoClient("mongodb://localhost:27017/")

db = cliente["bloc_notas"]

usuarios = db["usuarios"]
tareas = db["tareas"]


# INICIO
@app.route("/")
def inicio():

    if "usuario" in session:
        return redirect("/tareas")

    return render_template("login.html")


# REGISTRO
@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        correo = request.form["correo"]
        clave = request.form["clave"]

        usuario_existente = usuarios.find_one({
            "correo": correo
        })

        if usuario_existente:

            flash("El usuario ya existe")
            return redirect("/registro")

        nuevo_usuario = {
            "correo": correo,
            "clave": clave
        }

        usuarios.insert_one(nuevo_usuario)

        flash("Cuenta creada correctamente")
        return redirect("/")

    return render_template("registro.html")


# LOGIN
@app.route("/login", methods=["POST"])
def login():

    correo = request.form["correo"]
    clave = request.form["clave"]

    usuario = usuarios.find_one({
        "correo": correo,
        "clave": clave
    })

    if usuario:

        session["usuario"] = correo

        flash("Bienvenido")
        return redirect("/tareas")

    flash("Correo o contraseña incorrectos")
    return redirect("/")


# TAREAS
@app.route("/tareas")
def ver_tareas():

    if "usuario" not in session:
        return redirect("/")

    lista_tareas = tareas.find({
        "usuario": session["usuario"]
    })

    return render_template(
        "tareas.html",
        tareas=lista_tareas
    )


# AGREGAR TAREA
@app.route("/agregar", methods=["POST"])
def agregar():

    if "usuario" not in session:
        return redirect("/")

    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]

    nueva_tarea = {
        "titulo": titulo,
        "descripcion": descripcion,
        "usuario": session["usuario"]
    }

    tareas.insert_one(nueva_tarea)

    flash("Nota agregada")
    return redirect("/tareas")


# ELIMINAR
@app.route("/eliminar/<id>")
def eliminar(id):

    tareas.delete_one({
        "_id": ObjectId(id)
    })

    flash("Nota eliminada")

    return redirect("/tareas")


# EDITAR
@app.route("/editar/<id>", methods=["GET", "POST"])
def editar(id):

    tarea = tareas.find_one({
        "_id": ObjectId(id)
    })

    if request.method == "POST":

        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]

        tareas.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "titulo": titulo,
                    "descripcion": descripcion
                }
            }
        )

        flash("Nota actualizada")

        return redirect("/tareas")

    return render_template(
        "editar.html",
        tarea=tarea
    )


# SALIR
@app.route("/salir")
def salir():

    session.clear()

    flash("Sesión cerrada")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
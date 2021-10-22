from flask_restful import Resource

from ..modelos import db, Usuario, Tarea, TareaSchema
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
from celery import Celery
from flask import send_from_directory

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'mp3', 'aac', 'wav'}
RUTA_UPLOAD = "./static"

class VistaRegistro(Resource):
    def post(self):
        contrasena1 = request.json["password1"]
        contrasena2 = request.json["password2"]
        if contrasena1 == contrasena2:

            nuevo_usuario = Usuario(nombre=request.json["username"],contrasena = contrasena1,
                                    correo=request.json["email"])
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {"mensaje": "usuario creado exitosamente"}
        else:
            return {"mensaje":"el usuario no se creo, clave no coincide"}

class VistaAutenticador(Resource):
    def post(self):
        u_nombre = request.json["username"]
        u_contrasena = request.json["password"]
        usuario = Usuario.query.filter_by(nombre=u_nombre, contrasena=u_contrasena).first()
        if usuario:
            token_de_acceso = create_access_token(identity=usuario.id)
            data = {'estado': 'ok', 'token':token_de_acceso}
            return data, 200
        else:
            data = {'estado': 'Nok'}
            return data, 404


class VistaTareas(Resource):
    def __init__(self):
        self.tarea_schema = TareaSchema()

    @jwt_required()
    def post(self):
        filename = subir_archivo()
        if filename != "404":
            current_user_id = get_jwt_identity()
            newformat = "wma" ## TODO request.args.get('newformat')
            nueva_tarea = Tarea(filename=filename,
                                newformat=newformat,
                                usuario_id=current_user_id,
                                timestamp=datetime.now(),
                                status="UPLOADED")
            db.session.add(nueva_tarea)
            db.session.commit()
            data = {'estado': 'La tarea se creo'}
            return data, 200
        else:
            data = {'estado': 'Archivo no subido, tarea no se creo'}
            return data, 404



    @jwt_required()
    def get(self):
        ##RECUPERA EL USUARIO A PARTIR DE JWT
        current_user_id = get_jwt_identity()
        print(current_user_id)

        return [self.tarea_schema.dump(ca) for ca in Tarea.query.filter_by(usuario_id=current_user_id).all()]

class VistaTarea(Resource):
    def __init__(self):
        self.tarea_schema = TareaSchema()

    @jwt_required()
    def put(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        tarea.newformat = request.json.get("newformat", tarea.newformat)
        tarea.status = "UPLOADED"
        db.session.commit()
        return self.tarea_schema.dump(tarea)

    @jwt_required()
    def get(self,id_task):
        return TareaSchema().dump(Tarea.query.get_or_404(id_task))

    @jwt_required()
    def delete(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        db.session.delete(tarea)
        db.session.commit()
        return 200



class VistaConversor(Resource):
    ##descargar el archivo
    def get(self, filename):
        working_directory = os.getcwd()
        return send_from_directory(working_directory + "/archivos/", filename)

    def extensionpermitida(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def subir_archivo():
    print("Funciona")
    files = request.files.getlist("archivoup")
    for file in files:
        filename = secure_filename(file.filename)
        try:
            working_directory = os.getcwd()
            file.save(working_directory + "/archivos/" + filename)
        except FileNotFoundError :
            return "404"
    return filename




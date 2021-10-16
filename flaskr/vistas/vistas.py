from flask_restful import Resource

from ..modelos import db, Usuario
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token
from datetime import datetime
from celery import Celery


class VistaRegistro(Resource):
    def post(self):
        return 200

class VistaTareas(Resource):
    @jwt_required()
    def post(self):
        return 200

    def get(self):
        return 200

class VistaTarea(Resource):
    @jwt_required()
    def put(self):
        return 200

    def get(self):
        return 200

    def delete(self):
        return 200

class VistaAutenticador(Resource):
    def post(self):
        u_nombre = request.json["nombre"]
        u_contrasena = request.json["contrasena"]
        usuario = Usuario.query.filter_by(nombre=u_nombre, contrasena=u_contrasena).all()
        if usuario:
            token_de_acceso = create_access_token(identity=request.json["nombre"])
            data = {'estado': 'ok', 'token':token_de_acceso}
            return data, 200
        else:
            data = {'estado': 'Nok'}
            return data, 404

class VistaConversor(Resource):
    def get(self):
        return 200


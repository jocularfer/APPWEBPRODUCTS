import database
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


class Usercliente(database.Base, UserMixin):
    __tablename__ = 'Usuario'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_cliente = Column(Boolean, default=False)
    is_proveedor = Column(Boolean, default=False)

    def __init__(self, name, password, is_admin, is_cliente, is_proveedor):
        self.name = name
        self.password = password
        self.is_admin = is_admin
        self.is_cliente = is_cliente
        self.is_proveedor = is_proveedor

    def check_password(hashedpass, password):
        return check_password_hash(hashedpass, password)


class Producto(database.Base):
    __tablename__ = "Producto"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    stock = Column(Integer, nullable=False)
    stock_maximo = Column(Integer, nullable=False)
    ventas = Column(Integer, default=0)
    precio = Column(String(200), nullable=False)

    def __init__(self, nombre, stock, precio, stock_maximo):
        self.nombre = nombre
        self.stock = stock
        self.precio = precio
        self.stock_maximo = stock_maximo

    def __repr__(self):
        return "Producto {}: {} ({})".format(self.id, self.nombre, self.precio, self.stock, self.ventas, self.stock_maximo)

    def __str__(self):
        return "Producto {}: {} ({})".format(self.id, self.nombre, self.precio, self.stock, self.ventas, self.stock_maximo)


class Abastecimiento(database.Base):
    __tablename__ = "Abastecer"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    stock = Column(Integer, nullable=False)
    name_empresa = Column(String(120), nullable=False)
    precio = Column(String(200), nullable=False)

    def __init__(self, nombre, stock, precio, name_empresa):
        self.nombre = nombre
        self.stock = stock
        self.precio = precio
        self.name_empresa = name_empresa

    def __repr__(self):
        return "Abastecer {}: {} ({})".format(self.id, self.nombre, self.precio, self.stock, self.name_empresa)

    def __str__(self):
        return "Abastecer {}: {} ({})".format(self.id, self.nombre, self.precio, self.stock, self.name_empresa)


class Datosproveedor(database.Base, UserMixin):
    __tablename__ = 'Datos'
    id = Column(Integer, primary_key=True)
    name_empresa = Column(Integer, ForeignKey('Abastecer.name_empresa'))
    empresa = relationship("Abastecimiento")
    direccion = Column(String(128), nullable=False)
    telefono = Column(String(128), nullable=False)
    facturacion = Column(String(128), nullable=False)
    porcentaje_descuento = Column(String(128), nullable=False)

    def __init__(self, name_empresa, direccion, telefono, facturacion, porcentaje_descuento):
        self.name_empresa = name_empresa
        self.direccion = direccion
        self.telefono = telefono
        self.facturacion = facturacion
        self.porcentaje_descuento = porcentaje_descuento

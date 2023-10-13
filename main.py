import base64
import io
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import database
from models import Producto, Usercliente, Abastecimiento, Datosproveedor
import matplotlib.pyplot as plt
import numpy as np
app = Flask(__name__)
app.secret_key = 'root22'
login_manager_app = LognManager(app)


@login_manager_app.user_loader
def load_user(user_id):
    return database.session.query(Usercliente).filter_by(id=user_id).first()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usercliente(request.form['username'], request.form['password'], 0, 0, 0)
        logged_user = database.session.query(Usercliente).filter_by(name=user.name).first()
        if logged_user is not None:
            if Usercliente.check_password(logged_user.password, user.password):
                login_user(logged_user)
                if logged_user.is_cliente:
                    return redirect(url_for('home_cliente'))
                if logged_user.is_proveedor:
                    return redirect(url_for('home_proveedor'))
                else:
                    return redirect(url_for('acceso_admin'))
            else:
                flash("Contraseña incorrecta")
                return render_template('login.html')
        else:
            flash("Usuario no encontrado")
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home_cliente')
@login_required
def home_cliente():
    if current_user.is_cliente or current_user.is_admin:
        todos_los_productos = database.session.query(Producto).all()
        nombre_productos = []
        venta_productos = []
        fig, ax = plt.subplots()
        ax.set_ylabel('Ventas')
        ax.set_title('Ventas por producto')
        for producto in todos_los_productos:
            nombre_productos.append(producto.nombre)
            venta_productos.append(producto.ventas)
        output = io.BytesIO()
        plt.bar(nombre_productos, venta_productos)
        plt.savefig(output, format='png')
        output.seek(0)
        plot_url = base64.b64encode(output.getvalue()).decode()
        return render_template("clientes.html", imagen={'imagen': plot_url}, todos_los_productos=todos_los_productos)
    else:
        abort(404)


@app.route('/comprar-producto', methods=['POST'])
@login_required
def compra():
    producto = database.session.query(Producto).filter_by(nombre=request.form['contenido_nombreid']).first()
    venta = int(request.form['contenido_ventas'])
    if venta <= producto.stock:
        total = producto.ventas + venta
        stock_nuevo = producto.stock - venta
        database.session.query(Producto).filter_by(nombre=request.form['contenido_nombreid']).update(
            {Producto.ventas: total})
        database.session.query(Producto).filter_by(nombre=request.form['contenido_nombreid']).update(
            {Producto.stock: stock_nuevo})
        database.session.commit()
        return redirect(url_for("home_cliente"))
    else:
        flash("No hay suficientes productos disponibles")
        return redirect(url_for("home_cliente"))


@app.route('/comprar-exitosa')
@login_required
def compra_exitosa():
    flash("Se ha realizado una compra exitosa, se le contactará pronto")
    return redirect(url_for("login"))


@app.route('/home_proveedor')
@login_required
def home_proveedor():
    if current_user.is_proveedor or current_user.is_admin:
        todos_los_productos = database.session.query(Producto).all()
        todos_abastecidos = database.session.query(Abastecimiento).all()
        nombre_productos = []
        venta_productos = []
        fig, ax = plt.subplots()
        ax.set_ylabel('Compras')
        ax.set_title('Compra requerida por producto')
        for producto in todos_los_productos:
            nombre_productos.append(producto.nombre)
            venta_productos.append(producto.ventas)
        output = io.BytesIO()
        plt.bar(nombre_productos, venta_productos)
        plt.savefig(output, format='png')
        output.seek(0)
        plot_url = base64.b64encode(output.getvalue()).decode()
        return render_template("proveedor.html", imagen={'imagen': plot_url}, todos_los_productos=todos_los_productos, todos_abastecidos = todos_abastecidos)
    else:
        abort(404)


@app.route('/abastecer-producto', methods=['POST'])
@login_required
def abastecer():
    todos_los_productos = database.session.query(Producto).all()
    abastecer = Abastecimiento(nombre=request.form['contenido_nombre'], precio=request.form['contenido_precio'],
                        stock=request.form['contenido_stock'], name_empresa=request.form['contenido_empresa'])

    for producto in todos_los_productos:
        if abastecer.nombre == producto.nombre:
            if producto.stock < 100:
                flash("Producto encontrado y sin almacen lleno")
                database.session.add(abastecer)
                database.session.commit()
            else:
                flash("Almacen lleno")
    return redirect(url_for("home_proveedor"))


@app.route('/abastecer_datos/<empresa>')
@login_required
def abastecer_datos(empresa):
    if current_user.is_proveedor or current_user.is_admin:
        todos_los_productos = database.session.query(Producto).all()
        todos_abastecidos = database.session.query(Abastecimiento).all()
        nombre_productos = []
        venta_productos = []
        fig, ax = plt.subplots()
        ax.set_ylabel('Compras')
        ax.set_title('Compra requerida por producto')
        for producto in todos_los_productos:
            nombre_productos.append(producto.nombre)
            venta_productos.append(producto.ventas)
        output = io.BytesIO()
        plt.bar(nombre_productos, venta_productos)
        plt.savefig(output, format='png')
        output.seek(0)
        plot_url = base64.b64encode(output.getvalue()).decode()
        return render_template("datosproveedor.html", imagen={'imagen': plot_url}, todos_abastecidos=todos_abastecidos, empresa=empresa)
    else:
        abort(404)


@app.route('/contacto/<empresa>', methods=['POST'])
@login_required
def contacto(empresa):
    contactar = Datosproveedor(name_empresa=empresa,direccion=request.form['contenido_direccion'],
        telefono=request.form['contenido_telefono'], facturacion=request.form['contenido_factura'],
                               porcentaje_descuento=request.form['contenido_descuento'])
    database.session.add(contactar)
    database.session.commit()
    return redirect(url_for('abastecer_datos', empresa=empresa))


@app.route('/eliminar-contacto/<empresa>')
@login_required
def eliminar_contacto(empresa):
    contactos = database.session.query(Abastecimiento).filter_by(name_empresa=empresa).delete()
    database.session.commit()
    abastecio = database.session.query(Datosproveedor).filter_by(name_empresa=empresa).delete()
    database.session.commit()
    return redirect(url_for('acceso_admin', empresa=empresa))


@app.route('/envio_datos')
@login_required
def envio_datos():
    flash("Se ha enviado tu contacto exitosamente")
    return redirect(url_for("login"))


@app.route('/acceso_admin')
@login_required
def acceso_admin():
    if current_user.is_admin:
        todos_los_productos = database.session.query(Producto).all()
        todos_abastecidos = database.session.query(Abastecimiento).all()
        todos_contactos = database.session.query(Datosproveedor).all()
        nombre_productos = []
        venta_productos = []
        fig, ax = plt.subplots()
        ax.set_ylabel('Vendidos')
        ax.set_title('Beneficios por producto')
        for producto in todos_los_productos:
            nombre_productos.append(producto.nombre)
            venta_productos.append(producto.ventas)
        output = io.BytesIO()
        plt.bar(nombre_productos, venta_productos)
        plt.savefig(output, format='png')
        output.seek(0)
        plot_url = base64.b64encode(output.getvalue()).decode()
        return render_template("admin.html", imagen={'imagen': plot_url}, todos_los_productos=todos_los_productos, todos_abastecidos=todos_abastecidos,  todos_contactos=todos_contactos)
    else:
        abort(404)


@app.route('/crear-producto', methods=['POST'])
@login_required
def crear():
    producto = Producto(nombre=request.form['contenido_nombre'], precio=request.form['contenido_precio'],
                        stock=request.form['contenido_stock'], stock_maximo=request.form['contenido_stock_maximo'])
    database.session.add(producto)
    database.session.commit()
    return redirect(url_for("acceso_admin"))


@app.route('/venta-hecha/<id>')
@login_required
def venta_hecha(id):
    producto = database.session.query(Producto).filter_by(id=int(id)).first()
    producto.ventas = 0
    database.session.query(Producto).filter_by(id=int(id)).update({Producto.ventas: producto.ventas})
    database.session.commit()
    return redirect(url_for("acceso_admin"))


@app.route('/eliminar-producto/<id>')
def eliminar(id):
    producto = database.session.query(Producto).filter_by(id =int(id)).delete()
    database.session.commit()
    return redirect(url_for("acceso_admin"))


if __name__ == '__main__':
    database.Base.metadata.create_all(database.engine)
    app.run(debug=True, port=5000, host='0.0.0.0')
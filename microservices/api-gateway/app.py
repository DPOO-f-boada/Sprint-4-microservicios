"""
API Gateway para enrutar peticiones a los microservicios
"""
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import requests
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'gateway-secret-key')
CORS(app, supports_credentials=True)

AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:8001')
PRODUCTS_SERVICE_URL = os.environ.get('PRODUCTS_SERVICE_URL', 'http://products-service:8002')
INVENTORY_SERVICE_URL = os.environ.get('INVENTORY_SERVICE_URL', 'http://inventory-service:8003')
ORDERS_SERVICE_URL = os.environ.get('ORDERS_SERVICE_URL', 'http://orders-service:8004')
SHIPPING_SERVICE_URL = os.environ.get('SHIPPING_SERVICE_URL', 'http://shipping-service:8005')

TIMEOUT = 10

def forward_request(service_url, path, method='GET', data=None, headers=None):
    """Reenvía una petición a un microservicio"""
    url = f"{service_url}{path}"
    try:
        if method == 'GET':
            response = requests.get(url, params=request.args, headers=headers, timeout=TIMEOUT)
        elif method == 'POST':
            response = requests.post(url, json=data or request.json, headers=headers, timeout=TIMEOUT)
        elif method == 'PUT':
            response = requests.put(url, json=data or request.json, headers=headers, timeout=TIMEOUT)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=TIMEOUT)
        else:
            return jsonify({'error': 'Método no soportado'}), 405
        
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error al comunicarse con el servicio: {str(e)}'}), 503

@app.route('/api/auth/login/', methods=['POST'])
def login():
    """Login de usuarios"""
    return forward_request(AUTH_SERVICE_URL, '/api/auth/login/', 'POST')

@app.route('/api/auth/logout/', methods=['POST'])
def logout():
    """Logout de usuarios"""
    return forward_request(AUTH_SERVICE_URL, '/api/auth/logout/', 'POST')

@app.route('/api/auth/profile/', methods=['GET'])
def profile():
    """Perfil del usuario autenticado"""
    return forward_request(AUTH_SERVICE_URL, '/api/auth/profile/', 'GET')

@app.route('/api/auth/verify/', methods=['GET'])
def verify_token():
    """Verificar token de autenticación"""
    return forward_request(AUTH_SERVICE_URL, '/api/auth/verify/', 'GET')

@app.route('/api/products/', methods=['GET'])
def product_list():
    """Listar productos"""
    return forward_request(PRODUCTS_SERVICE_URL, '/api/products/', 'GET')

@app.route('/api/products/<int:product_id>/', methods=['GET'])
def product_detail(product_id):
    """Detalles de un producto"""
    return forward_request(PRODUCTS_SERVICE_URL, f'/api/products/{product_id}/', 'GET')

@app.route('/api/products/create/', methods=['POST'])
def product_create():
    """Crear un producto"""
    return forward_request(PRODUCTS_SERVICE_URL, '/api/products/create/', 'POST')

@app.route('/api/products/name/<path:product_name>/', methods=['GET'])
def product_by_name(product_name):
    """Producto por nombre"""
    return forward_request(PRODUCTS_SERVICE_URL, f'/api/products/name/{product_name}/', 'GET')

@app.route('/api/suppliers/', methods=['GET'])
def supplier_list():
    """Listar proveedores"""
    return forward_request(PRODUCTS_SERVICE_URL, '/api/suppliers/', 'GET')

@app.route('/api/variables/', methods=['GET'])
def variable_list():
    """Listar variables"""
    return forward_request(PRODUCTS_SERVICE_URL, '/api/variables/', 'GET')

@app.route('/api/warehouses/', methods=['GET'])
def warehouse_list():
    """Listar bodegas"""
    return forward_request(INVENTORY_SERVICE_URL, '/api/warehouses/', 'GET')

@app.route('/api/warehouses/<int:warehouse_id>/', methods=['GET'])
def warehouse_detail(warehouse_id):
    """Detalles de una bodega"""
    return forward_request(INVENTORY_SERVICE_URL, f'/api/warehouses/{warehouse_id}/', 'GET')

@app.route('/api/inventory/<path:product_name>/', methods=['GET'])
def inventory_by_product(product_name):
    """Inventario de un producto"""
    return forward_request(INVENTORY_SERVICE_URL, f'/api/inventory/{product_name}/', 'GET')

@app.route('/api/inventory/<path:product_name>/restock/', methods=['POST'])
def inventory_restock(product_name):
    """Reabastecer inventario"""
    return forward_request(INVENTORY_SERVICE_URL, f'/api/inventory/{product_name}/restock/', 'POST')

@app.route('/api/measurements/', methods=['GET'])
def measurement_list():
    """Listar mediciones"""
    return forward_request(INVENTORY_SERVICE_URL, '/api/measurements/', 'GET')

@app.route('/api/orders/', methods=['GET'])
def order_list():
    """Listar pedidos"""
    return forward_request(ORDERS_SERVICE_URL, '/api/orders/', 'GET')

@app.route('/api/orders/<int:order_id>/', methods=['GET'])
def order_detail(order_id):
    """Detalles de un pedido"""
    return forward_request(ORDERS_SERVICE_URL, f'/api/orders/{order_id}/', 'GET')

@app.route('/api/orders/<path:product_name>/', methods=['POST'])
def place_order(product_name):
    """Crear un pedido"""
    return forward_request(ORDERS_SERVICE_URL, f'/api/orders/{product_name}/', 'POST')

@app.route('/api/orders/create/', methods=['POST'])
def create_order():
    """Crear una orden automática"""
    return forward_request(ORDERS_SERVICE_URL, '/api/orders/create/', 'POST')

@app.route('/api/carriers/', methods=['GET'])
def carrier_list():
    """Listar transportadoras"""
    return forward_request(SHIPPING_SERVICE_URL, '/api/carriers/', 'GET')

@app.route('/api/carriers/<int:carrier_id>/', methods=['GET'])
def carrier_detail(carrier_id):
    """Detalles de una transportadora"""
    return forward_request(SHIPPING_SERVICE_URL, f'/api/carriers/{carrier_id}/', 'GET')

@app.route('/api/shipping/guides/', methods=['GET'])
def shipping_guide_list():
    """Listar guías de envío"""
    return forward_request(SHIPPING_SERVICE_URL, '/api/guides/', 'GET')

@app.route('/api/shipping/guides/<int:guide_id>/', methods=['GET'])
def shipping_guide_detail(guide_id):
    """Detalles de una guía de envío"""
    return forward_request(SHIPPING_SERVICE_URL, f'/api/guides/{guide_id}/', 'GET')

@app.route('/api/shipping/guides/order/<int:order_id>/', methods=['GET'])
def shipping_guide_by_order(order_id):
    """Guías de envío de un pedido"""
    return forward_request(SHIPPING_SERVICE_URL, f'/api/guides/order/{order_id}/', 'GET')

@app.route('/api/shipping/guides/generate/', methods=['POST'])
def generate_guide():
    """Generar una guía de envío"""
    return forward_request(SHIPPING_SERVICE_URL, '/api/guides/generate/', 'POST')

@app.route('/api/shipping/guides/statistics/', methods=['GET'])
def guide_statistics():
    """Estadísticas de generación de guías"""
    return forward_request(SHIPPING_SERVICE_URL, '/api/guides/statistics/', 'GET')

@app.route('/health/', methods=['GET'])
def health():
    """Health check del API Gateway"""
    return jsonify({'status': 'ok', 'service': 'api-gateway'}), 200

@app.route('/')
def index():
    """Servir el frontend"""
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except:
        return jsonify({'message': 'Frontend no disponible. Usa los endpoints de la API.'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


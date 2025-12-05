"""Módulo para integración con transportadoras."""
import time
import random
import requests
from django.conf import settings
from django.utils import timezone
from .models import Carrier, ShippingGuide

def generate_guide_number(carrier_name, order_id):
    """Genera un número de guía único"""
    prefix = carrier_name[:3].upper()
    timestamp = int(timezone.now().timestamp())
    return f"{prefix}{order_id:06d}{timestamp % 10000:04d}"

def simulate_carrier_api_call(carrier, shipping_data, timeout=8):
    """
    Simula una llamada a la API de una transportadora.
    En producción, esto se reemplazaría con llamadas reales a las APIs.
    
    Args:
        carrier: Instancia de Carrier
        shipping_data: Diccionario con datos del envío
        timeout: Tiempo máximo de espera en segundos
    
    Returns:
        dict: Respuesta de la transportadora con tracking_number y otros datos
    """
    start_time = time.time()
    base_time = carrier.response_time_avg
    variation = random.uniform(0.5, 1.5)
    simulated_time = base_time * variation
    
    if simulated_time > timeout:
        simulated_time = timeout - 0.5
    
    time.sleep(min(simulated_time, timeout - 0.1))
    elapsed = time.time() - start_time
    
    if random.random() < 0.05:
        raise Exception("Error de conexión con la transportadora")
    
    guide_number = generate_guide_number(carrier.name, shipping_data.get('order_id', 0))
    tracking_number = f"TRACK{random.randint(1000000, 9999999)}"
    
    return {
        'success': True,
        'guide_number': guide_number,
        'tracking_number': tracking_number,
        'carrier_reference': f"{carrier.name.upper()}-{guide_number}",
        'estimated_delivery_days': random.randint(2, 7),
        'response_time': elapsed,
        'carrier_response': {
            'status': 'accepted',
            'message': 'Guía generada exitosamente',
            'service_type': 'Estándar',
            'cost': float(shipping_data.get('declared_value', 0)) * 0.05
        }
    }

def call_real_carrier_api(carrier, shipping_data, timeout=8):
    """
    Llama a la API real de una transportadora.
    Si carrier.api_endpoint está configurado, hace la llamada real.
    De lo contrario, simula la respuesta.
    """
    if not carrier.api_endpoint or not carrier.api_key:
        return simulate_carrier_api_call(carrier, shipping_data, timeout)
    
    try:
        payload = {
            'origin': shipping_data.get('origin_address'),
            'destination': shipping_data.get('destination_address'),
            'recipient': {
                'name': shipping_data.get('recipient_name'),
                'phone': shipping_data.get('recipient_phone'),
                'document': shipping_data.get('recipient_document', '')
            },
            'package': {
                'weight_kg': float(shipping_data.get('weight_kg', 0)),
                'dimensions': shipping_data.get('dimensions', ''),
                'declared_value': float(shipping_data.get('declared_value', 0))
            }
        }
        
        response = requests.post(
            carrier.api_endpoint,
            json=payload,
            headers={
                'Authorization': f'Bearer {carrier.api_key}',
                'Content-Type': 'application/json'
            },
            timeout=timeout
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error de la transportadora: {response.status_code}")
            
    except requests.exceptions.Timeout:
        raise Exception("Timeout al comunicarse con la transportadora")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error de conexión: {str(e)}")

def generate_shipping_guide(carrier_id, shipping_data, timeout=8):
    """
    Genera una guía de envío con una transportadora.
    Garantiza respuesta en máximo 8 segundos según ASR.
    
    Args:
        carrier_id: ID de la transportadora
        shipping_data: Diccionario con datos del envío
        timeout: Tiempo máximo en segundos (default: 8 según ASR)
    
    Returns:
        tuple: (ShippingGuide, success: bool, error_message: str)
    """
    from django.utils import timezone
    import time
    
    start_time = time.time()
    
    try:
        carrier = Carrier.objects.get(id=carrier_id, is_active=True)
    except Carrier.DoesNotExist:
        return None, False, "Transportadora no encontrada o inactiva"
    
    shipping_guide = ShippingGuide.objects.create(
        order_id=shipping_data.get('order_id'),
        carrier=carrier,
        origin_address=shipping_data.get('origin_address'),
        destination_address=shipping_data.get('destination_address'),
        recipient_name=shipping_data.get('recipient_name'),
        recipient_phone=shipping_data.get('recipient_phone'),
        recipient_document=shipping_data.get('recipient_document', ''),
        weight_kg=shipping_data.get('weight_kg', 0),
        dimensions=shipping_data.get('dimensions', ''),
        declared_value=shipping_data.get('declared_value', 0),
        status=ShippingGuide.PENDING
    )
    
    try:
        response = call_real_carrier_api(carrier, shipping_data, timeout)
        elapsed = time.time() - start_time
        
        shipping_guide.guide_number = response.get('guide_number')
        shipping_guide.carrier_tracking_number = response.get('tracking_number')
        shipping_guide.carrier_response = response
        shipping_guide.status = ShippingGuide.GENERATED
        shipping_guide.generation_time_seconds = round(elapsed, 3)
        shipping_guide.meets_performance_ASR = elapsed <= timeout
        shipping_guide.generated_at = timezone.now()
        shipping_guide.save()
        
        return shipping_guide, True, None
        
    except Exception as e:
        elapsed = time.time() - start_time
        
        if elapsed >= timeout:
            shipping_guide.status = ShippingGuide.TIMEOUT
            error_msg = f"Timeout: La transportadora no respondió en {timeout} segundos"
        else:
            shipping_guide.status = ShippingGuide.FAILED
            error_msg = str(e)
        
        shipping_guide.error_message = error_msg
        shipping_guide.generation_time_seconds = round(elapsed, 3)
        shipping_guide.meets_performance_ASR = False
        shipping_guide.save()
        
        return shipping_guide, False, error_msg


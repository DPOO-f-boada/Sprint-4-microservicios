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

def simulate_carrier_api_call(carrier, shipping_data):
    """Simula una llamada a la API de una transportadora."""
    base_time = carrier.response_time_avg
    variation = random.uniform(0.5, 1.5)
    simulated_time = base_time * variation
    time.sleep(simulated_time)
    
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
        'carrier_response': {
            'status': 'accepted',
            'message': 'Guía generada exitosamente',
            'service_type': 'Estándar',
            'cost': float(shipping_data.get('declared_value', 0)) * 0.05
        }
    }

def call_real_carrier_api(carrier, shipping_data):
    """Llama a la API real de una transportadora o simula la respuesta."""
    if not carrier.api_endpoint or not carrier.api_key:
        return simulate_carrier_api_call(carrier, shipping_data)
    
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
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error de la transportadora: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error de conexión: {str(e)}")

def generate_shipping_guide(carrier_id, shipping_data):
    """Genera una guía de envío con una transportadora."""
    from django.utils import timezone
    
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
        response = call_real_carrier_api(carrier, shipping_data)
        
        shipping_guide.guide_number = response.get('guide_number')
        shipping_guide.carrier_tracking_number = response.get('tracking_number')
        shipping_guide.carrier_response = response
        shipping_guide.status = ShippingGuide.GENERATED
        shipping_guide.generated_at = timezone.now()
        shipping_guide.save()
        
        return shipping_guide, True, None
        
    except Exception as e:
        shipping_guide.status = ShippingGuide.FAILED
        shipping_guide.error_message = str(e)
        shipping_guide.save()
        
        return shipping_guide, False, str(e)


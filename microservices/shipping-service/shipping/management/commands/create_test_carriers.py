"""Comando para crear transportadoras de prueba."""
from django.core.management.base import BaseCommand
from shipping.models import Carrier

class Command(BaseCommand):
    help = 'Crea transportadoras de prueba'

    def handle(self, *args, **options):
        carriers_data = [
            {
                'name': 'Servientrega',
                'api_endpoint': None,
                'api_key': None,
                'response_time_avg': 2.5,
                'is_active': True
            },
            {
                'name': 'Coordinadora',
                'api_endpoint': None,
                'api_key': None,
                'response_time_avg': 3.0,
                'is_active': True
            },
            {
                'name': 'Interrapidisimo',
                'api_endpoint': None,
                'api_key': None,
                'response_time_avg': 2.8,
                'is_active': True
            },
            {
                'name': 'DHL',
                'api_endpoint': None,
                'api_key': None,
                'response_time_avg': 4.0,
                'is_active': True
            },
        ]
        
        created = 0
        for carrier_data in carriers_data:
            carrier, created_flag = Carrier.objects.get_or_create(
                name=carrier_data['name'],
                defaults=carrier_data
            )
            if created_flag:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Transportadora creada: {carrier.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Transportadora ya existe: {carrier.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Proceso completado. {created} transportadoras creadas.')
        )


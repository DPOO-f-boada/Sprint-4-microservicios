from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Crea usuarios de prueba (admin, operario, cliente) con roles predefinidos."

    def handle(self, *args, **options):
        users_to_create = [
            {
                "username": "admin",
                "email": "admin@logistica.com",
                "password": "admin123",
                "role": User.ADMIN,
                "first_name": "Administrador",
                "last_name": "Sistema",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "operario",
                "email": "operario@logistica.com",
                "password": "operario123",
                "role": User.OPERARIO,
                "first_name": "Juan",
                "last_name": "Perez",
                "phone": "3001234567",
            },
            {
                "username": "cliente",
                "email": "cliente@logistica.com",
                "password": "cliente123",
                "role": User.CLIENTE,
                "first_name": "Maria",
                "last_name": "Garcia",
                "phone": "3009876543",
                "address": "Calle 123 #45-67, Bogota",
            },
        ]

        created_count = 0
        skipped_count = 0

        for user_data in users_to_create:
            username = user_data["username"]
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'Usuario "{username}" ya existe, saltando...'))
                skipped_count += 1
                continue

            password = user_data.pop("password")
            user = User.objects.create_user(**user_data)
            user.set_password(password)
            user.save()
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'[OK] Usuario "{username}" creado ({user.get_role_display()})')
            )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Usuarios creados: {created_count}"))
        self.stdout.write(f"Usuarios existentes: {skipped_count}")
        self.stdout.write("=" * 50)
        if created_count:
            self.stdout.write("Credenciales:")
            self.stdout.write('  - admin / admin123')
            self.stdout.write('  - operario / operario123')
            self.stdout.write('  - cliente / cliente123')

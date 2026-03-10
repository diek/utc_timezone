from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random


class Command(BaseCommand):
    help = "Create 20 fake users with Faker data"

    def handle(self, *args, **kwargs):
        fake = Faker()
        Faker.seed(12345)  # Ensures reproducibility

        for _ in range(20):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}"
            email = fake.email()

            # Avoid duplicate usernames
            if User.objects.filter(username=username).exists():
                username = f"{username}{random.randint(1, 1000)}"

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password="password123",  # or generate a random password if desired
            )
            self.stdout.write(f"Created user: {user.username}")

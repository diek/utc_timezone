from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Update all employee emails to match first_name.last_name@mail.com"

    # Now you can use the User model

    def handle(self, *args, **kwargs):
        User = get_user_model()
        users = User.objects.all()
        for user in users:
            # Generate email based on first_name and last_name
            email = f"{user.first_name.lower()}.{user.last_name.lower()}@issa.mail.com"
            user.email = email
            user.save(update_fields=["email"])

        self.stdout.write(
            self.style.SUCCESS("Successfully updated all employee emails")
        )

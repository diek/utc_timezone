# Employees
from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

DEFAULT_GEOGRAPHY_NAME = "NS"


class Geography(models.Model):
    """
    Area in which a company operates.
    """

    name = models.CharField(
        verbose_name="name",
        max_length=100,
        unique=True,
    )
    timezone = models.CharField(
        verbose_name="time zone",
        max_length=100,
    )

    class Meta:
        verbose_name = "geography"
        verbose_name_plural = "geographies"

    def __str__(self):
        return self.name


class Geographical(models.Model):
    """
    Mixin to associate objects to a geography.
    """

    geography = models.ForeignKey(
        to=Geography,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="geography",
    )

    class Meta:
        abstract = True


class Position(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [UniqueConstraint(Lower("name"), name="unique_position_name_ci")]

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Employee(Geographical, models.Model):
    surname = models.CharField(max_length=150)
    given_name = models.CharField(max_length=150)
    position = models.ForeignKey(Position, models.PROTECT, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    user = models.OneToOneField(User, models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.surname}, {self.given_name}"

# tests/factories.py
import factory
from app.models import DBUser

class UserFactory(factory.Factory):
    class Meta:
        model = DBUser

    id = factory.Sequence(lambda n: n + 1)
    email = factory.Sequence(lambda n: f"user{n}@example.com")

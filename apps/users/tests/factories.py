import factory
from django.contrib.auth import get_user_model

User = get_user_model()

DEFAULT_PASSWORD = 'string1234'

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User 

    email = factory.declarations.Sequence(lambda n: f'user{n}@example.com')
    # password = factory.declarations.PostGenerationMethodCall('set_password', DEFAULT_PASSWORD)
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs.setdefault('password', DEFAULT_PASSWORD)
        return model_class.objects.create_user(*args, **kwargs)
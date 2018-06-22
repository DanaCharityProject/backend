import factory

from faker import Faker

from app.models.community_resource import CommunityResource

fake = Faker()

class CommunityResourceFactory(factory.Factory):
    class Meta:
        model = CommunityResource

    charity_number = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda a: "Charity {}".format(a.charity_number))
    coordinates = factory.LazyFunction(lambda:"SRID=4326; POINT({} {})".format(fake.geo_coordinate(center=43.65707099999999, radius=0.01), fake.geo_coordinate(center=-79.40551399999998, radius=0.01)))
    contact_name = factory.Faker("name")
    email = factory.Faker("email")
    phone_number = factory.Faker("phone_number")
    address = factory.Faker("street_address")
    website = "https://danaproject.org"
    image_uri = "https://danaproject.org"
    verified = True

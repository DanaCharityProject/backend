from . import db

class CommunityResource(db.Model):
    __tablename__ = "community resources"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True,
                       nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    contact_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)

    @property
    def location(self):
        return self.lat, self.lon


    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "verified": self.verified
        }


    @staticmethod
    def get_resource_by_number(number):
        return CommunityResource.query.filter_by(number=number).first()


    @staticmethod
    def add_community_resource(resource):
        if CommunityResource.get_resource_by_number(resource.number) is not None:
            return None

        db.session.add(resource)
        db.session.commit()
        return resource
    
from . import db

class RadioStation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False, unique=True)
    genre = db.Column(db.String(50))
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(200))

    def __repr__(self):
        return f'<RadioStation {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'genre': self.genre,
            'description': self.description,
            'logo_url': self.logo_url
        }

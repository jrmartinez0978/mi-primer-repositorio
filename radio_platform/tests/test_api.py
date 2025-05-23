import unittest
import json
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import RadioStation

class APITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_station(self):
        """Test creating a new radio station."""
        payload = {
            'name': 'Test Station',
            'url': 'http://teststation.com',
            'genre': 'Test Genre',
            'description': 'A test station.',
            'logo_url': 'http://teststation.com/logo.png'
        }
        response = self.client.post('/api/stations',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], payload['name'])
        self.assertEqual(data['url'], payload['url'])
        
        with app.app_context():
            station = RadioStation.query.filter_by(url=payload['url']).first()
            self.assertIsNotNone(station)
            self.assertEqual(station.name, payload['name'])

    def test_create_station_missing_fields(self):
        """Test creating a station with missing required fields."""
        # Missing URL
        payload_no_url = {'name': 'Test Station No URL'}
        response = self.client.post('/api/stations',
                                    data=json.dumps(payload_no_url),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing required fields: name and url')

        # Missing Name
        payload_no_name = {'url': 'http://teststationnourl.com'}
        response = self.client.post('/api/stations',
                                    data=json.dumps(payload_no_name),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing required fields: name and url')

        # Missing Name and URL (empty payload)
        response = self.client.post('/api/stations',
                                    data=json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing required fields: name and url')

    def test_create_station_duplicate_url(self):
        """Test creating a station with a duplicate URL."""
        payload1 = {'name': 'Test Station 1', 'url': 'http://teststation.com'}
        self.client.post('/api/stations', data=json.dumps(payload1), content_type='application/json')

        payload2 = {'name': 'Test Station 2', 'url': 'http://teststation.com'} # Same URL
        response = self.client.post('/api/stations', data=json.dumps(payload2), content_type='application/json')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Station with this URL already exists')

    def _create_dummy_station(self, name="Test Station", url="http://test.com"):
        """Helper method to create a station and return its ID."""
        station = RadioStation(name=name, url=url, genre="Test")
        with app.app_context():
            db.session.add(station)
            db.session.commit()
            return station.id

    def test_get_all_stations(self):
        """Test retrieving all stations."""
        self._create_dummy_station(name="Station A", url="http://a.com")
        self._create_dummy_station(name="Station B", url="http://b.com")

        response = self.client.get('/api/stations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], "Station A")
        self.assertEqual(data[1]['name'], "Station B")

    def test_get_one_station(self):
        """Test retrieving a single station by its ID."""
        station_id = self._create_dummy_station(name="Specific Station", url="http://specific.com")
        
        response = self.client.get(f'/api/stations/{station_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Specific Station")
        self.assertEqual(data['url'], "http://specific.com")

    def test_get_one_station_not_found(self):
        """Test retrieving a non-existent station."""
        response = self.client.get('/api/stations/999') # Assuming 999 does not exist
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Station not found')

    def test_update_station(self):
        """Test updating an existing station."""
        station_id = self._create_dummy_station()
        update_payload = {
            'name': 'Updated Station Name',
            'genre': 'Updated Genre'
        }
        response = self.client.put(f'/api/stations/{station_id}',
                                   data=json.dumps(update_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated Station Name')
        self.assertEqual(data['genre'], 'Updated Genre')

        with app.app_context():
            updated_station = RadioStation.query.get(station_id)
            self.assertEqual(updated_station.name, 'Updated Station Name')
            self.assertEqual(updated_station.genre, 'Updated Genre')

    def test_update_station_not_found(self):
        """Test updating a non-existent station."""
        update_payload = {'name': 'Trying to update'}
        response = self.client.put('/api/stations/999',
                                   data=json.dumps(update_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Station not found')

    def test_update_station_duplicate_url(self):
        """Test updating a station to have a URL that already exists."""
        station1_id = self._create_dummy_station(name="Station One", url="http://one.com")
        station2_id = self._create_dummy_station(name="Station Two", url="http://two.com")

        update_payload = {'url': 'http://one.com'} # URL of station1
        response = self.client.put(f'/api/stations/{station2_id}',
                                   data=json.dumps(update_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Another station with this URL already exists')

    def test_delete_station(self):
        """Test deleting an existing station."""
        station_id = self._create_dummy_station()
        
        response_delete = self.client.delete(f'/api/stations/{station_id}')
        self.assertEqual(response_delete.status_code, 200)
        data_delete = json.loads(response_delete.data)
        self.assertEqual(data_delete['message'], 'Station deleted successfully')

        # Verify it's actually deleted
        response_get = self.client.get(f'/api/stations/{station_id}')
        self.assertEqual(response_get.status_code, 404)

if __name__ == '__main__':
    unittest.main()

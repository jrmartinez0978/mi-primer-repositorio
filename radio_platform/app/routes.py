from flask import request, jsonify, render_template
from app import app, db
from app.models import RadioStation

# Create a new radio station
@app.route('/api/stations', methods=['POST'])
def create_station():
    data = request.get_json()
    if not data or not 'name' in data or not 'url' in data:
        return jsonify({'error': 'Missing required fields: name and url'}), 400

    if RadioStation.query.filter_by(url=data['url']).first():
        return jsonify({'error': 'Station with this URL already exists'}), 409

    new_station = RadioStation(
        name=data['name'],
        url=data['url'],
        genre=data.get('genre'),
        description=data.get('description'),
        logo_url=data.get('logo_url')
    )
    db.session.add(new_station)
    db.session.commit()
    return jsonify(new_station.to_dict()), 201

# Get all radio stations
@app.route('/api/stations', methods=['GET'])
def get_stations():
    stations = RadioStation.query.all()
    return jsonify([station.to_dict() for station in stations]), 200

# Get a specific radio station by ID
@app.route('/api/stations/<int:id>', methods=['GET'])
def get_station(id):
    station = RadioStation.query.get(id)
    if station is None:
        return jsonify({'error': 'Station not found'}), 404
    return jsonify(station.to_dict()), 200

# Update a radio station
@app.route('/api/stations/<int:id>', methods=['PUT'])
def update_station(id):
    station = RadioStation.query.get(id)
    if station is None:
        return jsonify({'error': 'Station not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided for update'}), 400

    # Check for URL conflict if URL is being updated
    if 'url' in data and data['url'] != station.url:
        if RadioStation.query.filter(RadioStation.id != id, RadioStation.url == data['url']).first():
            return jsonify({'error': 'Another station with this URL already exists'}), 409
        station.url = data['url']

    station.name = data.get('name', station.name)
    # station.url handled above
    station.genre = data.get('genre', station.genre)
    station.description = data.get('description', station.description)
    station.logo_url = data.get('logo_url', station.logo_url)

    db.session.commit()
    return jsonify(station.to_dict()), 200

# Delete a radio station
@app.route('/api/stations/<int:id>', methods=['DELETE'])
def delete_station(id):
    station = RadioStation.query.get(id)
    if station is None:
        return jsonify({'error': 'Station not found'}), 404

    db.session.delete(station)
    db.session.commit()
    return jsonify({'message': 'Station deleted successfully'}), 200

# Admin panel route
@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

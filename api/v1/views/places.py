#!/usr/bin/python3
"""Places module for the HBNB API"""

from flask import jsonify, request, abort, make_response
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.state import State
from models.amenity import Amenity
from api.v1.views import app_views


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places(city_id):
    """Retrieves the list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def post_place(city_id):
    """Creates a Place"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if request.is_json:
        data = request.get_json()
        if "user_id" not in data:
            abort(400, "Missing user_id")
        user = storage.get(User, data['user_id'])
        if user is None:
            abort(404)
        if "name" not in data:
            abort(400, "Missing name")
        data['city_id'] = city_id
        new_place = Place(**data)
        storage.new(new_place)
        new_place.save()
        return jsonify(new_place.to_dict()), 201
    else:
        abort(400, "Not a JSON")


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def put_place(place_id):
    """Updates a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if request.is_json:
        data = request.get_json()
        for key, value in data.items():
            if key not in ['id', 'user_id', 'city_id', 'created_at',
                           'updated_at']:
                setattr(place, key, value)
        place.save()
        return jsonify(place.to_dict()), 200
    else:
        abort(400, "Not a JSON")


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def post_places_search():
    """Searches for places"""
    if request.get_json() is None:
        abort(400, "Not a JSON")

    data = request.get_json()

    if data and len(data):
        states = data.get('states', [])
        cities = data.get('cities', [])
        amenities = data.get('amenities', [])

    if not data or not len(data) or (
        not states and
        not cities and
        not amenities
    ):
        places = storage.all(Place).values()
        list_places = []
        for place in places:
            list_places.append(place.to_dict())
        return jsonify(list_places)

    list_places = []
    if states:
        states_obj = [storage.get(State, state_id) for state_id in states]
        for state in states_obj:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            list_places.append(place)

    if cities:
        cities_obj = [storage.get(City, city_id) for city_id in cities]
        for city in cities_obj:
            if city:
                for place in city.places:
                    if place not in list_places:
                        list_places.append(place)

    if amenities:
        if not list_places:
            list_places = storage.all(Place).values()
        amenities_obj = [storage.get(Amenity, amenity_id)
                         for amenity_id in amenities]
        list_places = [place for place in list_places
                       if all(amenity in place.amenities
                              for amenity in amenities_obj)]

    places = []
    for place in list_places:
        dv = place.to_dict()
        dv.pop('amenities', None)
        places.append(dv)
    return jsonify(places)

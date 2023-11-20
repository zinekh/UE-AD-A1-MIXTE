from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the User service!</h1>", 200)

@app.route("/users/<userId>/bookings", methods=['GET'])
def getUserBookings(userId):
    # URL du service Booking
    print("coucou")
    booking_service_url = "http://localhost:3201/bookings/{}".format(userId)

    try:
        # Appel au service Booking
        response = requests.get(booking_service_url)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<userId>/bookings/movies", methods=['GET'])
def getUserBookingMovies(userId):
    # URL du service Booking
    booking_service_url = "http://localhost:3201/bookings/{}".format(userId)

    try:
        # Appel au service Booking
        booking_response = requests.get(booking_service_url)
        if booking_response.status_code == 200:
            bookings_data = booking_response.json()
            movie_details = []

            # URL de base du service Movie GraphQL
            movie_service_url = "http://127.0.0.1:3001/graphql"

            for booking in bookings_data:
                for date in booking['dates']:
                    for movie_id in date['movies']:
                        # Construction de la requête GraphQL
                        graphql_query = """
                            query getMovieById($movieId: String!) {
                                movie_by_id(id: $movieId) {
                                    id
                                    title
                                    director
                                    rating
                                }
                            }
                        """
                        variables = {"movieId": movie_id}

                        # Appel au service Movie pour chaque ID de film
                        movie_response = requests.post(
                            movie_service_url,
                            json={'query': graphql_query, 'variables': variables}
                        )
                        if movie_response.status_code == 200:
                            movie_details.append(movie_response.json()['data']['movie_by_id'])

            return jsonify(movie_details), 200
        else:
            return jsonify({"error": "User or booking not found"}), 404
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
import requests
import uuid

# Base URL of the Flask API
BASE_URL = 'http://localhost:5000/api'

# Generate a unique username and email using UUID to prevent conflicts
unique_id = str(uuid.uuid4())[:8]  # Shorten UUID for simplicity
USERNAME = f'user_{unique_id}'
EMAIL = f'user_{unique_id}@example.com'
PASSWORD = 'securepassword'


def register_user():
    """
    Registers a new user by sending a POST request to /api/users.
    """
    url = f'{BASE_URL}/users'
    payload = {
        'username': USERNAME,
        'email': EMAIL,
        'password': PASSWORD
    }
    response = requests.post(url, json=payload)

    if response.status_code == 201:
        print('✅ User registered successfully.')
        user_data = response.json()
        print('User Data:', user_data)
        return user_data['id']
    elif response.status_code == 400:
        print('⚠️ Registration failed:', response.json()['message'])
    else:
        print('❌ Unexpected error during registration:', response.text)


def obtain_token():
    """
    Obtains an authentication token by sending a POST request to /api/tokens using Basic Auth.
    """
    url = f'{BASE_URL}/tokens'
    response = requests.post(url, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        token = response.json()['token']
        print('✅ Token obtained successfully.')
        print('Token:', token)
        return token
    elif response.status_code == 400:
        print('⚠️ Token retrieval failed:', response.json()['message'])
    elif response.status_code == 401:
        print('⚠️ Unauthorized:', response.json()['message'])
    else:
        print('❌ Unexpected error during token retrieval:', response.text)


def create_movie(token, name, year, oscars, genre=None):
    """
    Creates a new movie by sending a POST request to /api/movies with the provided token.
    """
    url = f'{BASE_URL}/movies'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'name': name,
        'year': year,
        'oscars': oscars
    }
    if genre:
        payload['genre'] = genre
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print('✅ Movie created successfully.')
        movie_data = response.json()
        print('Movie Data:', movie_data)
        return movie_data['id']
    elif response.status_code == 400:
        print('⚠️ Movie creation failed:', response.json()['message'])
    elif response.status_code == 401:
        print('⚠️ Unauthorized:', response.json()['message'])
    else:
        print('❌ Unexpected error during movie creation:', response.text)


def get_movies(token):
    """
    Retrieves all movies by sending a GET request to /api/movies with the provided token.
    """
    url = f'{BASE_URL}/movies'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        movies = response.json()['movies']
        print('✅ Retrieved movies successfully.')
        for movie in movies:
            genre = movie.get('genre', 'N/A')
            print(
                f"ID: {movie['id']}, Name: {movie['name']}, Year: {movie['year']}, Oscars: {movie['oscars']}, Genre: {genre}")
    elif response.status_code == 401:
        print('⚠️ Unauthorized:', response.json()['message'])
    else:
        print('❌ Unexpected error during fetching movies:', response.text)


def main():
    print('--- API Testing Script Started ---\n')

    print('1. Registering a new user...')
    user_id = register_user()
    if not user_id:
        print('\n⏭️ Exiting script due to registration failure.')
        return

    print('\n2. Obtaining authentication token...')
    token = obtain_token()
    if not token:
        print('\n⏭️ Exiting script due to token retrieval failure.')
        return

    print('\n3. Creating a new movie with genre...')
    movie_id = create_movie(token, name='Inception', year=2010, oscars=4, genre='Sci-Fi')
    if not movie_id:
        print('\n⏭️ Exiting script due to movie creation failure.')
        return

    print('\n4. Retrieving all movies...')
    get_movies(token)

    print('\n--- API Testing Script Completed ---')


if __name__ == '__main__':
    main()

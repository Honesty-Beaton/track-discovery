### INF601 - Advanced Programming in Python
### Honesty Beaton
### Final Project


# ⭐ Track Discovery --- Final Project ⭐

## Description & Overview
In this project, I utilize Django and the Spotipy API to create a Track Discovery game.

## Features
 * User authentication (login, register, logout) 
 * Guess the Album Cover or Song Snippet
 * Easy, Normal and Hard Difficulties


This project uses the package Django.

## Getting Started
1) Clone this project
Install the required Python packages using pip
2) ```pip install -r requirements.txt ```
Setting up the Spotipy API
3) Create a new account or log into https://developers.spotify.com/
4) Go to the Dashboard, create a new app
5) Set the redirect url on the app you just created to http://127.0.0.1:8000/spotify/callback/
6) Get your ID and Secret Key, put these variables in settings.py in the variables SPOTIPY_CLIENT_ID and
SPOTIPY_CLIENT_SECRET
7) Set up the database using ```python manage.py makemigrations```
8) Apply database changes using ```python manage.py migrate```
9) Enable access to the Django admin panel by creating a superuser account: ```python manage.py createsuperuser```
10) Run the development server using ```python manage.py runserver```. If this does not work, ensure you are in the trackdiscovery directory 
11) Head to the index page using the localhost/ or the admin page using /admin/

### Dependencies
```
pip  install -r requirements.txt

```

### Executing program
Run the development server using 
```
python manage.py runserver
```

## Output

A Django-based web application where users can guess the artist from song snippet or guess the artist from an album cover!

## Authors

[@Honesty Beaton](https://github.com/Honesty-Beaton)


## Version History

* See [commit change]()

## License

No license for this project.

## Acknowledgements
* [Django](https://docs.djangoproject.com/en/4.2/intro/tutorial01/)
* [Spotipy](https://pypi.org/project/spotipy/)
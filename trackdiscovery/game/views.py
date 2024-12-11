from django.shortcuts import render, redirect
from .models import GameSession, Question
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from spotipy.oauth2 import SpotifyOAuth
import random
from .utils import *

# Create your views here.
def register(request):
    if  request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('game:login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})



@login_required(login_url='/login/')
def startGame(request):
    if request.method == 'POST':
        difficulty = request.POST['difficulty']
        gameMode = request.POST['gameMode']

        session = GameSession.objects.create(user=request.user, difficulty=difficulty, gameMode=gameMode)

        # Redirect the user to Spotify login if not already authenticated
        if not request.session.get('access_token'):
            return redirect('game:spotifyLogin')
        return redirect('game:play', session_id=session.id)

    return render(request, 'game/start.html')


@login_required(login_url='/login/')
def playGame(request, session_id=None):
    session = GameSession.objects.get(id=session_id, user=request.user)

    # Set the number of questions based on the difficulty
    num_questions = 10 if session.difficulty == 'Hard' else 6 if session.difficulty == 'Normal' else 3

    # Check how many questions are created
    print(f"Current number of questions: {session.questions.count()}, Target: {num_questions}")

    # If there are less than the required number of questions, create more
    if session.questions.count() < num_questions:
        game_mode = session.gameMode
        difficulty = session.difficulty
        content_type = 'song' if game_mode == 'Song Snippet' else 'album'

        print(f"Creating new question, Content type: {content_type}, Game mode: {game_mode}")

        # Create a new question based on the selected content type (song or album)
        if content_type == 'song':
            snippet_data = getRandomArtistSnippet(request, difficulty=difficulty)
            if snippet_data:
                snippet_url = snippet_data['preview_url']
                correct_answer = snippet_data['artist']
                print(f"Creating song question for artist: {correct_answer}")

                Question.objects.create(
                    session=session,
                    snippetUrl=snippet_url,
                    correctAnswer=correct_answer
                )
            else:
                return render(request, 'game/error.html', {"message": "Could not fetch preview snippets based on your top artists. Please try again."})
        else:
            album_data_list = getRandomArtistAlbum(request, difficulty=difficulty)
            if album_data_list:
                for album_data in album_data_list:
                    # Ensure that we don't exceed the required number of questions for the session
                    if session.questions.count() < num_questions:
                        album_url = album_data['image_url']
                        correct_answer = album_data['artist']
                        print(f"Creating album question for artist: {correct_answer}")

                        Question.objects.create(
                            session=session,
                            snippetUrl=album_url,
                            correctAnswer=correct_answer
                        )
            else:
                return render(request, 'game/error.html', {"message": "Could not fetch album cover. Please try again."})

        print(f"New questions created, total: {session.questions.count()}")

    # If there are no unanswered questions, redirect to the results
    unanswered_questions = session.questions.filter(userAnswer__isnull=True)
    if not unanswered_questions.exists():
        print("All questions have been answered, redirecting to results.")
        return redirect('game:results', session_id=session.id)

    # Get the next unanswered question
    question = unanswered_questions.first()

    # Process the user's answer to the current question
    if request.method == 'POST':
        user_answer = request.POST['answer']

        question.userAnswer = user_answer
        question.isCorrect = user_answer.lower() == question.correctAnswer.lower()
        question.save()

        # Update score
        session.score += 1 if question.isCorrect else 0
        session.save()

        print(f"User answer is {'correct' if question.isCorrect else 'incorrect'}, score: {session.score}")

        # Redirect to the next unanswered question
        return redirect('game:play', session_id=session.id)

    # Display the current question in the template
    return render(request, 'game/play.html', {
        'question': question,
        'game_mode': session.gameMode
    })


@login_required(login_url='/login/')
def results(request, session_id):
    session = GameSession.objects.get(id=session_id, user=request.user)
    return render(request, 'game/results.html', {'session': session})

# Spotipy Authorization
def spotifyLogin(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read"
    )

    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def spotifyCallback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read"
    )
    token_info = sp_oauth.get_access_token(request.GET['code'])

    if 'access_token' in token_info:
        # Store access token in the session
        request.session['access_token'] = token_info['access_token']
    else:
        print("Error: No access token in response.")
        return redirect('game:startGame')  # Or show an error message to the user

    return redirect('game:startGame')

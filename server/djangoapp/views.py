from django.shortcuts import render
from .models import CarMake, CarModel
from django.http import JsonResponse
from .populate import initiate
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from .restapis import get_request, analyze_review_sentiments, post_review
import json
import logging

def get_cars(request):
    # If no CarMakes exist, populate database
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = []

    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    return JsonResponse({"CarModels": cars})

def get_dealerships(request, state="All"):
    """
    Returns a list of all dealerships, or by state if provided
    """
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

def get_dealer_details(request, dealer_id):
    """
    Returns details of a single dealer based on dealer_id
    """
    endpoint = f"/fetchDealer/{dealer_id}"
    dealer = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealer})

def get_dealer_reviews(request, dealer_id):
    """
    Returns reviews for a dealer along with sentiment analysis
    """
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)

    review_list = []

    if reviews:
        for review in reviews:
            sentiment = analyze_review_sentiments(review.get("review", ""))
            review_detail = {
                "review": review.get("review", ""),
                "name": review.get("name", ""),
                "purchase": review.get("purchase", False),
                "purchase_date": review.get("purchase_date", ""),
                "car_make": review.get("car_make", ""),
                "car_model": review.get("car_model", ""),
                "car_year": review.get("car_year", ""),
                "sentiment": sentiment.get("sentiment", "neutral") if sentiment else "neutral"
            }
            review_list.append(review_detail)

    return JsonResponse({"status": 200, "reviews": review_list})

# Logger
logger = logging.getLogger(__name__)

# -----------------------------
# Login View
# -----------------------------
@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('userName')
            password = data.get('password')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"status": "Invalid request"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        else:
            return JsonResponse({"userName": username, "status": "Failed"}, status=401)
    else:
        return JsonResponse({"status": "Invalid method"}, status=405)

# -----------------------------
# Logout View
# -----------------------------
@csrf_exempt
def logout_request(request):
    if request.method == "GET":
        logout(request)  # Terminate user session
        data = {"userName": ""}  # Return empty username
        return JsonResponse(data)
    else:
        return JsonResponse({"status": "Invalid method"}, status=405)


# -----------------------------
# Registration View (Placeholder)
# -----------------------------
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Already Registered", "status": False})
        
        # Create the user
        user = User.objects.create_user(username=username, password=password,
                                        first_name=first_name, last_name=last_name, email=email)
        login(request, user)
        return JsonResponse({"userName": username, "status": True})
    
    return JsonResponse({"error": "Invalid request", "status": False})

# -----------------------------
# Dealership & Review Views (Placeholders)
# -----------------------------
def get_dealerships(request):
    # TODO: Fetch and return list of dealerships
    return JsonResponse({"status": "Not implemented"}, status=501)

def get_dealer_reviews(request, dealer_id):
    # TODO: Fetch reviews for a specific dealer
    return JsonResponse({"status": "Not implemented"}, status=501)

def get_dealer_details(request, dealer_id):
    # TODO: Fetch dealer details
    return JsonResponse({"status": "Not implemented"}, status=501)

@csrf_exempt
def add_review(request):
    # TODO: Add review logic
    return JsonResponse({"status": "Not implemented"}, status=501)

def add_review(request):
    """
    Handles posting a dealer review.
    Only authenticated users can post.
    """
    if not request.user.is_anonymous:
        try:
            data = json.loads(request.body)
            response = post_review(data)
            if response:
                return JsonResponse({"status": 200, "message": "Review posted successfully"})
            else:
                return JsonResponse({"status": 500, "message": "Failed to post review"})
        except Exception as e:
            return JsonResponse({"status": 401, "message": f"Error in posting review: {e}"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

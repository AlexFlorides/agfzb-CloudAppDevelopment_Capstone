import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    api_key = kwargs.get("api_key")
    try:
        if (api_key):
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(json_payload["review"])
    response = requests.post(url, json=json_payload["review"], params=kwargs)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    if ('state' in kwargs):
        json_result = get_request(url, state=kwargs['state'])
    if ('dealerId' in kwargs):
        json_result = get_request(url, id=kwargs['dealerId'])
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   state=dealer_doc["state"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=kwargs['dealerId'])
    if json_result:
        if 'error' in json_result:
            return json_result.get("error")
        # Get the row list in JSON as reviews
        reviews = json_result
        # For each dealer object
        for review in reviews:
            # Create a DealerReview object with values in `doc` object
            dealership = rev = name = purchase = purchase_date = car_make = car_model = car_year = sentiment = id = ""
            if "review" in review:
                rev = review["review"]
                sentiment = analyze_review_sentiments(rev)
            if "dealership" in review:
                dealership = review["dealership"]
            if "name" in review:
                name = review["name"]
            if "purchase" in review:
                purchase = review["purchase"]
            if "purchase_date" in review:
                purchase_date = review["purchase_date"]
            if "car_make" in review:
                car_make = review["car_make"]
            if "car_model" in review:
                car_model = review["car_model"]
            if "car_year" in review:
                car_year = review["car_year"]
            if "id" in review:
                id = review["id"]
            review_obj = DealerReview(
                dealership=dealership, 
                name=name, purchase=purchase,
                review=rev, 
                purchase_date=purchase_date, 
                car_make=car_make,
                car_model=car_model,
                car_year=car_year,
                sentiment=sentiment,
                id=id)
            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    NLU_URL = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/2a4ea076-715d-4e57-8a36-1a02961adaf3"
    API_KEY = "0kZ-CgD_Op2d3t84KSagTTnf-JSpR3bVuBuqaPDY4Nlu"
    # json_result = get_request(NLU_URL, api_key=API_KEY)

    authenticator = IAMAuthenticator(API_KEY)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01', authenticator=authenticator)
    natural_language_understanding.set_service_url(NLU_URL)
    response = natural_language_understanding.analyze(
        text=dealerreview, 
        language="en",
        features=Features(
        sentiment=SentimentOptions(targets=[dealerreview]))).get_result()
    label = json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    return label
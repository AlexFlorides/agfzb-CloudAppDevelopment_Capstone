from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30)
    description = models.CharField(null=True, max_length=200)

    def __str__(self):
        return self.name


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    name = models.CharField(null=False, max_length=30)
    dealerId = models.IntegerField()

    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "Wagon"

    TYPE_CHOICES = [
        (SEDAN, "Sedan"),
        (SUV, "SUV"),
        (WAGON, "Wagon"),
    ]

    car_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    year = models.DateField(null=True)
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)

    def __str__(self):
        return "Model Name: " + self.name + ", " + \
               "Dealer ID: " + str(self.dealerId) + ", " + \
               "Car Type: " + self.car_type + ", " + \
               "Year: " + str(self.year)


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, state, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state code
        self.st = st
        # Dealer state
        self.state = state
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:

    def __init__(self, id, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, sentiment
):
        # Dealer dealership
        self.dealership = dealership
        # Dealer name
        self.name = name
        # Purchase
        self.purchase = purchase
        # Dealer review
        self.review = review
        # Location purchase_date
        self.purchase_date = purchase_date
        # Location car_make
        self.car_make = car_make
        # Dealer car_model
        self.car_model = car_model
        # Dealer car_year
        self.car_year = car_year
        # Dealer sentiment
        self.sentiment = sentiment
        # Dealer id
        self.id = id

    def __str__(self):
        return "Review: " + self.review + ", Sentiment: " + self.sentiment

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                            sort_keys=True, indent=4)
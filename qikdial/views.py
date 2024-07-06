from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework import status

from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login, logout 

from django.contrib.sessions.models import Session
from django.db.models import Max, Count, Min, Sum, Avg
from django.db.models import Q

from .models import *
from .serializer import *

import jwt, random
import datetime
from dotenv import load_dotenv
import os


load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')

# ============================================================Basics============================================================


@api_view(["GET"])   
def Tester(request):
    print(request.META.get("HTTP_COOKIE"))
    return Response({"Message" : "Working"})

def token_generator(id):
    return(jwt.encode({"id" : id, "time" : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, SECRET_KEY, algorithm="HS256"))

# ============================================================Login/Logout============================================================

@api_view(["POST"])
def Loginer(request):
    user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
    if not user:
        return Response({"logged" : "Fail"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        login(request, user)
        token = token_generator(user.pk)
        token_all = TokenModel.objects.filter(user = user).first()
        if(token_all is not None):
            token_all.token = token
            token_all.save()
        else:
            toke = TokenModel(user=user, token = token)
            toke.save()
        return Response({"logged" : "Success", "merchant" : user.is_merchant, "admin" : user.is_staff, "token" : token}, headers={"Set-Cookie" : f'my_token={token}'}, status=status.HTTP_201_CREATED)
    
@api_view(["POST"])
def Logouter(request):
    logout(request)
    return Response({"Message" : "OK"}, status=status.HTTP_200_OK)

@api_view(["POST"])
def token_checker(request):
    token = request.data.get("token")
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except:
        return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
    else:
        current_time = datetime.datetime.now()
        diff = str(current_time - datetime.datetime.strptime(user_data["time"],'%Y-%m-%d %H:%M:%S'))
        if(int(diff.split(",")[-1].split(":")[0]) > 2):
            return Response({"Message" : "Session Ended"})   
        else:
            user = UserModel.objects.get(pk=user_data["id"])
            user_token = TokenModel.objects.get(user=user)
            if(user_token.token == token):
                return Response({"Message" : "Valid","merchant" : user.is_merchant, "admin" : user.is_staff, "city" : user.city})
            else:
                return Response({"Message" : "Old Token"},status=status.HTTP_401_UNAUTHORIZED)

# ============================================================Signup============================================================

@api_view(["POST"])
def Signup(request):
    try:
        user = UserModel.objects.create_user(name=request.data.get("name"), email=request.data.get("email"), password=request.data.get("password"), phone=request.data.get("phone"), city=request.data.get("city"), is_merchant=request.data.get("is_merchant"))
        login(request, user)
        token = token_generator(user.pk)
        toke = TokenModel(user=user, token = token)
        toke.save()
        return Response({'message': 'User created successfully',"token" : token}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ============================================================Amenities============================================================
class AmenitiesView(APIView):
    def get(self,request):
        vals = AmenityModel.objects.all().values()
        serializer = AmenityGetSerializer(data = vals, many=True)
        return Response(serializer.initial_data,status=status.HTTP_200_OK)


    def post(self, request):
        serializer = AmenityPostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Message" : "OK"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Message" : "Failed"}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        val = AmenityModel.objects.get(pk=request.query_params.get("id"))
        if(val.status == 1):
            val.status = 0
        else:
            val.status = 1
        val.save()
        return Response({"Message" : "OK"},status=status.HTTP_200_OK)
 
@api_view(["POST"])
def AminityImageEdit(request):
    val = AmenityModel.objects.get(pk=request.data.get("id"))
    serializer = AmenityImagePutSerializer(val, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Message" : "OK"},status=status.HTTP_201_CREATED)
    else:
        return Response({"Message" : "Failed"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def AminityNameEdit(request):
    val = AmenityModel.objects.get(pk=request.data.get("id"))
    val.name = request.data.get("name")
    val.save()
    return Response({"Message" : "OK"},status=status.HTTP_200_OK)

@api_view(["GET"])
def AminityGet(request):
        vals = AmenityModel.objects.filter(status=1).values()
        serializer = AmenityGetSerializer(data = vals, many=True)
        return Response(serializer.initial_data)

# ============================================================Categories============================================================

class CategoryView(APIView):
    def get(self,request):
        vals = CategoryModel.objects.all().values()
        serializer = CategoryGetSerializer(data = vals, many=True)
        return Response(serializer.initial_data)

    def post(self, request):
        serializer = CategoryPostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Message" : "OK"}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"Message" : "Failed"}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        val = CategoryModel.objects.get(pk=request.query_params.get("id"))
        if(val.status == 1):
            val.status = 0
        else:
            val.status = 1
        val.save()
        return Response({"Message" : "OK"},status=status.HTTP_200_OK)
    
    def put(self,request):
        val = CategoryModel.objects.get(pk=request.data.get("id"))

        if(request.data.get("parent") == ''):
            val.parent = None
            val.parent_name = ''
        else:
            val.parent = CategoryModel.objects.get(parent=request.data.get("parent"))
            val.parent_name = CategoryModel.objects.get(parent=request.data.get("parent")).name
        val.name = request.data.get("name")

        val.save()
        
        return Response({"Message" : "OK"},status=status.HTTP_200_OK)

    
@api_view(["POST"])
def CategoryImageEdit(request):
    val = CategoryModel.objects.get(pk=request.data.get("id"))
    serializer = CategoryPutImageSerializer(val, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Message" : "OK"},status=status.HTTP_200_OK)
    else:
        return Response({"Message" : "Failed"}, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(["GET"])
def CategoryGet(request):
    categories = CategoryModel.objects.filter(status=1).annotate(
        total_listings=Count('listingmodel')
    ).values()
    return Response({"Message" : "OK" ,"data" : list(categories)},status=status.HTTP_200_OK)


# ============================================================City============================================================

class CityView(APIView):

    def get(self,request):
        vals = CityModel.objects.all().values()
        serializer = CityGetSerializer(data = vals, many= True)
        return Response(serializer.initial_data,status=status.HTTP_200_OK)

    def post(self,request):
        serializer = CityPostSerializer(data = request.data)
        if serializer.is_valid():
            city_id = serializer.save()
            return Response({"Message" : "OK","id" : city_id.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Message" : "Failed"}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request):
        val = CityModel.objects.get(pk=request.data.get("id"))
        val.name = request.data.get("name")
        val.save()
        return Response({"Message" : "OK"},status=status.HTTP_200_OK)
    
    def delete(self,request):
        val = CityModel.objects.get(pk=request.query_params.get("id"))
        if(val.status == 1):
            val.status = 0
        else:
            val.status = 1
        val.save()
        return Response({"Message" : "OK"},status=status.HTTP_200_OK)

@api_view(["GET"])
def CityGet(request):
        vals = CityModel.objects.filter(status=1).values()
        serializer = CityGetSerializer(data = vals, many=True)
        return Response(serializer.initial_data)

# ============================================================Listings============================================================

class ListingView(APIView):
    def post(self,request):
        token = request.data.get("token")
        try:
            user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except:
            return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = user_data["id"]
            updated_data = request.data.copy()
            updated_data.update({"user" : user_id})

            if(request.data.get("listing_type") == "1"):            
                serializer = ListingProductPostSerializer(data = updated_data)
                if serializer.is_valid():
                    listing = serializer.save()
                    updated_data.update({"listing" : listing.pk})

                    for j in request.data.get("amenities").split(","):
                        amenitylist = ListingAmenityModel.objects.create(amenity=AmenityModel.objects.get(pk=int(j)), listing=listing)
                        amenitylist.save()
                    if(request.data.get("availability") != "1"):
                        for i in (request.data.get("cities").split(",")):
                            citylist = CityListingModel.objects.create(city=CityModel.objects.get(pk=int(i)), listing=listing)
                            citylist.save()

                    imageserialiser = ListingImagePostSerialiser(data=updated_data)
                    if imageserialiser.is_valid():
                        imageserialiser.save()           
                        return Response({"Message" : "OK"}, status=status.HTTP_201_CREATED)

                    else:
                        print(imageserialiser.errors)
                        return Response({"Message" : "Image not added"},status=status.HTTP_400_BAD_REQUEST)

                else:
                    print(serializer.errors)
                    return Response({"Message" : "Listing not added"},status=status.HTTP_400_BAD_REQUEST)
            
            elif(request.data.get("listing_type") == "2"):
                serializer = ListingServicePostSerializer(data = updated_data)
                if serializer.is_valid():
                    listing = serializer.save()
                    updated_data.update({"listing" : listing.pk})

                    for j in request.data.get("amenities").split(","):
                        amenitylist = ListingAmenityModel.objects.create(amenity=AmenityModel.objects.get(pk=int(j)), listing=listing)
                        amenitylist.save()
                    if(request.data.get("availability") != "1"):
                        for i in (request.data.get("cities").split(",")):
                            citylist = CityListingModel.objects.create(city=CityModel.objects.get(pk=int(i)), listing=listing)
                            citylist.save()

                    imageserialiser = ListingImagePostSerialiser(data=updated_data)
                    if imageserialiser.is_valid():
                        imageserialiser.save()
                        return Response({"Message" : "OK"}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"Message" : "Image not added"},status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({"Message" : "Listing not added"},status=status.HTTP_400_BAD_REQUEST)
            
            else:
                serializer = ListingBusinessPostSerializer(data = updated_data)
                if serializer.is_valid():
                    print("in")
                    listing = serializer.save()
                    updated_data.update({"listing" : listing.pk})

                    for j in request.data.get("amenities").split(","):
                        amenitylist = ListingAmenityModel.objects.create(amenity=AmenityModel.objects.get(pk=int(j)), listing=listing)
                        amenitylist.save()
                    if(request.data.get("availability") != "1"):
                        for i in (request.data.get("cities").split(",")):
                            citylist = CityListingModel.objects.create(city=CityModel.objects.get(pk=int(i)), listing=listing)
                            citylist.save()

                    imageserialiser = ListingImagePostSerialiser(data=updated_data)
                    if imageserialiser.is_valid():
                        imageserialiser.save()
                        return Response({"Message" : "OK"}, status=status.HTTP_201_CREATED)

                    else:
                        print(imageserialiser.errors)
                        return Response({"Message" : "Image not added"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    print(serializer.errors)
                    return Response({"Message" : "Listing not added"},status=status.HTTP_400_BAD_REQUEST)        

    def get(self,request):
            
        all_listings = ListingModel.objects.all()

        listings = []
        for listing in all_listings:
            total_views = ListingViewsModel.objects.filter(listing = listing.pk).aggregate(total_count = Sum("count"))
            total_ratings = RatingModel.objects.filter(listing = listing.pk)
            avg_rating =total_ratings.aggregate(avg_rating = Avg("rating"))
            total_comments = len(ListingViewsModel.objects.filter(listing = listing.pk).values())

            listi = model_to_dict(listing)
            the_image = ImageModel.objects.filter(listing = listing.pk).values()[0] if ImageModel.objects.filter(listing = listing.pk).exists() else ''
            listi.update({
                "category_id" : { "id" : listing.category.pk, "name" : listing.category.name},
                "image" : the_image,
                "amenities" : list(ListingAmenityModel.objects.filter(listing = listing.pk).values()),
                "cities" : list(CityListingModel.objects.filter(listing = listing.pk).values()),
                "enquiries" : list(EnquiryModel.objects.filter(listing = listing.pk).values()),
                "offers" : list(OfferModel.objects.filter(listing = listing.pk).values()),
                "views" : 0 if total_views["total_count"] is None else total_views["total_count"],
                "avg_rating" : 0 if avg_rating["avg_rating"] is None else avg_rating["avg_rating"],
                "total_ratings" : len(total_ratings),
                "total_comments" : 0 if total_comments is None else total_comments
                
            })

            listings.append(listi)
        
        return Response({"Message" : "OK","data" : {"categories" : CategoryModel.objects.all().values_list("id", "name"), "listings" : listings, "cities" : CityModel.objects.all().values_list("id", "name")}})

    def delete(self,request):
        val = ListingModel.objects.get(pk=request.query_params.get("id"))
        if(val.status == 1):
            val.status = 0
        else:
            val.status = 1
        val.save()
        return Response({"Message" : "OK"},status=status.HTTP_200_OK)
    
@api_view(["GET"])
def ListingGetSpecific(request):

    if(request.query_params.get("id") == None):return Response({"Message" : "Listing Id Required"},status.HTTP_406_NOT_ACCEPTABLE)

    image_vals = []
    amenity_vals = []
    city_vals = []
    rating_vals = []
    offer_vals = []
    enquiry_vals = []



    all_vals = ListingModel.objects.filter(pk=request.query_params.get("id")).values()[0]
    all_images = ImageModel.objects.filter(listing = request.query_params.get("id"))
    all_amenities = ListingAmenityModel.objects.filter(listing = request.query_params.get("id"))
    all_cities = CityListingModel.objects.filter(listing = request.query_params.get("id"))
    all_ratings = RatingModel.objects.filter(listing = request.query_params.get("id"))
    all_offers = OfferModel.objects.filter(listing = request.query_params.get("id"))
    all_enquiries = EnquiryModel.objects.filter(listing = request.query_params.get("id"))
    avg_rating = RatingModel.objects.filter(listing = request.query_params.get("id")).aggregate(avg_rating = Avg("rating"))


    total_views = ListingViewsModel.objects.filter(listing=request.query_params.get("id")).aggregate(total_view = Sum("count"))




    for image in all_images:
        image_vals.append({"image" : image.image.name, "id" : image.pk})

    for amenity in all_amenities:
        amenity_vals.append({"amenity" : amenity.amenity.name, "id" : amenity.amenity.pk})

    for city in all_cities:
        city_vals.append({"city" : city.city.name, "id" : city.city.pk})

    for rating in all_ratings:
        rating_vals.append({
            "rating" : rating.rating, 
            "id" : rating.pk, 
            "comment" : rating.description, 
            "posted_at": rating.created_at,
            "user" : {
                "id" : rating.user.pk,
                "name" : rating.user.name,
                "contact" : rating.user.phone,
                "photo" : None if rating.user.photo == "" else rating.user.photo.name
                }})
        
    for enquiry in all_enquiries:
        enquiry_vals.append({
            "id" : enquiry.user.pk,
            "name" : enquiry.user.name,
            "mobile" : enquiry.user.phone,
            "photo" : None if enquiry.user.photo == "" else enquiry.user.photo.name

        })

    for offer in all_offers:
        offer_vals.append({
            "id" : offer.pk,
            "offer" : offer.offer,
            "description" : offer.description,
            "status" : offer.status
        })


    all_vals.update({
        "category_id" : {
            "id" : all_vals["category_id"],
            "name" : CategoryModel.objects.get(pk = all_vals["category_id"]).name
        },
        "user_id" : {
            "id" : all_vals["user_id"],
            "name" : UserModel.objects.filter(pk = all_vals["user_id"]).first().name if UserModel.objects.filter(pk = all_vals["user_id"]).exists() else None,
            "mobile" : UserModel.objects.filter(pk = all_vals["user_id"]).first().phone if UserModel.objects.filter(pk = all_vals["user_id"]).exists() else None,

        },
        "images" : image_vals,
        "amenities" : amenity_vals,
        "cities" : city_vals,
        "ratings" : rating_vals,
        "avg_rating" : avg_rating,
        "ratings_split" : [len(all_ratings), len(all_ratings.filter(rating = 1)), len(all_ratings.filter(rating = 2)), len(all_ratings.filter(rating = 3)), len(all_ratings.filter(rating = 4)), len(all_ratings.filter(rating = 5))],
        "enquiries" : enquiry_vals,
        "offers" : offer_vals,
        "total_views" : 0 if total_views["total_view"] is None else total_views["total_view"],
        "categories" : CategoryModel.objects.all().values(),
        "favorites_count" : len(FavoriteModel.objects.filter(listing = request.query_params.get("id")))

    })

    return Response({"Message" : "OK","data" : all_vals})

@api_view(["POST"])
def ListingHardDelete(request):
    if(request.data.get("token") == None) : return Response({"Message" : "Token Absent"},status=status.HTTP_406_NOT_ACCEPTABLE)

    token = request.data.get("token")
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except:
        return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
    else:
        is_admin = UserModel.objects.filter(pk = user_data["id"]).values()[0]["is_staff"]
        if(is_admin):
            ListingModel.objects.get(pk =request.data.get("id") ).delete()
            return Response({"Mesaage" : "Deleted"},status=status.HTTP_200_OK)
        else:
            return Response({"Mesaage" : "Only Admin can Delete"},status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
def ListingGetUserSpecific(request):

    if(request.data.get("token") == None) : return Response({"Message" : "Token Absent"},status=status.HTTP_406_NOT_ACCEPTABLE)

    token = request.data.get("token")
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except:
        return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
    else:
        all_listings = ListingModel.objects.filter(user=user_data["id"]).values()

        all_vals = []

        for one_listing in all_listings:

            image_vals = []
            amenity_vals = []
            city_vals = []
            rating_vals = []
            offer_vals = []
            enquiry_vals = []


            all_images = ImageModel.objects.filter(listing = one_listing["id"])
            all_amenities = ListingAmenityModel.objects.filter(listing = one_listing["id"])
            all_cities = CityListingModel.objects.filter(listing = one_listing["id"])
            all_ratings = RatingModel.objects.filter(listing = one_listing["id"])
            all_offers = OfferModel.objects.filter(listing = one_listing["id"])
            all_enquiries = EnquiryModel.objects.filter(listing = one_listing["id"])
            avg_rating = RatingModel.objects.filter(listing = one_listing["id"]).aggregate(avg_rating = Avg("rating"))

            
            total_views = ListingViewsModel.objects.filter(listing=one_listing["id"]).aggregate(total_view = Sum("count"))

            for enquiry in all_enquiries:
                enquiry_vals.append({
                    "id" : enquiry.user.pk,
                    "name" : enquiry.user.name,
                    "mobile" : enquiry.user.phone,
                    "photo" : None if enquiry.user.photo == "" else enquiry.user.photo.name,
                    
                })

            for offer in all_offers:
                offer_vals.append({
                    "id" : offer.pk,
                    "offer" : offer.offer,
                    "description" : offer.description,
                    "status" : offer.status
                })

            for image in all_images:
                image_vals.append({"image" : image.image.name, "id" : image.pk})

            for amenity in all_amenities:
                amenity_vals.append({"amenity" : amenity.amenity.name, "id" : amenity.amenity.pk})

            for city in all_cities:
                city_vals.append({"city" : city.city.name, "id" : city.city.pk})

            for rating in all_ratings:
                rating_vals.append({
                    "rating" : rating.rating, 
                    "id" : rating.pk, 
                    "comment" : rating.description, 
                    "posted_at": rating.created_at,
                    "user" : {
                        "id" : rating.user.pk,
                        "name" : rating.user.name,
                        "contact" : rating.user.phone,
                        "photo" : None if rating.user.photo == "" else rating.user.photo.name,

                        }})
                
            
            one_listing.update({
                "category_id" : {
                    "id" : one_listing["category_id"],
                    "name" : CategoryModel.objects.get(pk = one_listing["category_id"]).name
                },
                "user_id" : {
                    "id" : one_listing["user_id"],
                    "name" : UserModel.objects.get(pk = one_listing["user_id"]).name,
                },
                "images" : image_vals,
                "amenities" : amenity_vals,
                "cities" : city_vals,
                "ratings" : rating_vals,
                "avg_ratings" : avg_rating,
                "enquiries" : enquiry_vals,
                "offers" : offer_vals,
                "total_views" : 0 if total_views["total_view"] is None else total_views["total_view"]
            })

            all_vals.append(one_listing)

        return Response({"Message" : "OK","data" : all_vals})

# Listing Editors ========================================================
@api_view(["POST"])
def BasicInfoEditor(request):
    print(type(request.data.get("availability")))
    listing = ListingModel.objects.get(pk = request.data.get("listing"))
    serializer = BasicInfoSerialiser(listing, data=request.data)
    if serializer.is_valid():
        serializer.save()
        if(request.data.get("availability") == "1"):
            CityListingModel.objects.filter(listing = listing).delete()
        elif(request.data.get("availability") == "3"):
            CityListingModel.objects.filter(listing = listing).delete()
            user_city = listing.user.city
            user_city_creator, created = CityModel.objects.get_or_create(name = user_city)
            listing_city, created = CityListingModel.objects.get_or_create(listing = listing, city = user_city_creator)

        return Response({"Message" : "Edited"},status=status.HTTP_200_OK)
    else:
        print(serializer.errors)
        return Response({"Message" : "Failed"},status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def OtherInfoEditor(request):
    listing = ListingModel.objects.get(pk = request.data.get("listing"))
    serializer = OtherInfoSerialiser(listing, data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Message" : "Edited"},status=status.HTTP_200_OK)
    else:
        print(serializer.errors)
        return Response({"Message" : "Failed"},status=status.HTTP_400_BAD_REQUEST)




@api_view(["POST"])
def AmenityInfoEditor(request):
    listing_amenities = ListingAmenityModel.objects.filter(listing = request.data.get("listing")).values()
    listing_amenity_id = []
    amenity_id = []

    for single_val in listing_amenities:
        listing_amenity_id.append(single_val["id"])
        amenity_id.append(single_val["amenity_id"])

    for amenity in request.data.get("amenities"): #add
        if(amenity not in amenity_id):
            creator = ListingAmenityModel.objects.create(amenity = AmenityModel.objects.get(pk=amenity), listing = ListingModel.objects.get(pk=request.data.get("listing")))
            creator.save()
    
    for amenity in amenity_id:
        if(amenity not in request.data.get("amenities")): #delete
            print(listing_amenity_id[amenity_id.index(amenity)])
            ListingAmenityModel.objects.get(pk=listing_amenity_id[amenity_id.index(amenity)]).delete()

    return Response({"Message" : "OK"},status=status.HTTP_200_OK)

@api_view(["POST"])
def CityInfoEditor(request):
    listing_cities = CityListingModel.objects.filter(listing = request.data.get("listing")).values()
    listing_city_id = []
    city_id = []

    for single_val in listing_cities:
        listing_city_id.append(single_val["id"])
        city_id.append(single_val["city_id"])

    for city in request.data.get("cities"): #add
        if(city not in city_id):
            creator = CityListingModel.objects.create(city = CityModel.objects.get(pk=city), listing = ListingModel.objects.get(pk=request.data.get("listing")))
            creator.save()
    
    for city in city_id:
        if(city not in request.data.get("cities")): #delete
            print(listing_city_id[city_id.index(city)])
            CityListingModel.objects.get(pk=listing_city_id[city_id.index(city)]).delete()

    return Response({"Message" : "OK"},status=status.HTTP_200_OK)

# ============================================================Listing Images============================================================

class ListingImageView(APIView):
    def post(self,request):
        serializer = ListingImagePostSerialiser(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Message" : "OK"},status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({"Message" : "Error"},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        ImageModel.objects.get(pk=request.query_params.get("id")).delete()
        return Response({"Message" : "Deleted"},status=status.HTTP_200_OK)


# ============================================================Ratings============================================================

class RatingView(APIView):
    def get(self,request):
        return Response(list(RatingModel.objects.all().values()))
    
    def post(self,request):
        token = request.data.get("token")
        try:
            user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except:
            return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(user_data["id"] == ListingModel.objects.get(pk=request.data.get("listing")).user.pk or UserModel.objects.get(pk=user_data["id"]).is_staff):
                return Response({"Message" : "Owner Cannot post a Review"},status=status.HTTP_403_FORBIDDEN)
            
            if(len(RatingModel.objects.filter(user=user_data["id"], listing= request.data.get("listing")).values()) > 0):
                previous_val = RatingModel.objects.get(user=user_data["id"], listing= request.data.get("listing"))
                previous_val.description = request.data.get("description")
                previous_val.rating = request.data.get("rating")
                previous_val.save()
                return Response({"Message" : "OK"},status=status.HTTP_201_CREATED)

            else:
                updated_data = request.data.copy()
                updated_data.update({"user" : user_data["id"]})
                serializer = RatingPostSerializer(data=updated_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"Message" : "OK"},status=status.HTTP_201_CREATED)
                else:
                    print(serializer.errors)
                    return Response({"Message" : "Error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def RatingsUserSpecific(request):
    token = request.data.get("token")
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except:
        return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
    else:
        vals = RatingModel.objects.filter(user = user_data["id"]).values()
        for val in vals:
            val.update({"listing" : ListingModel.objects.filter(pk = val["listing_id"]).values()[0], "image" : ImageModel.objects.filter(listing = val["listing_id"]).values()[0]})
            
        return Response({"Message" : "OK", "data" : list(vals)})
# ============================================================Listviews============================================================

class ListingViewsView(APIView):
    def get(self,request):
        return Response(list(ListingViewsModel.objects.all().values()))
    
    def post(self,request):
        token = request.data.get("token")
        if(token == None):
            check = ListingViewsModel.objects.filter(user=None, listing = request.data.get("listing")).values()
            if(len(check) == 0):
                ListingViewsModel.objects.create(listing = ListingModel.objects.get(pk=request.data.get("listing")))
                return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)
            else:
                checked_data = ListingViewsModel.objects.get(user=None, listing = request.data.get("listing"))
                checked_data.count += 1
                checked_data.save()
                return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)
        else:
            try:
                user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
            except:
                return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
            else:
                check = ListingViewsModel.objects.filter(user=user_data["id"], listing = request.data.get("listing")).values()
                if(len(check) == 0):
                    ListingViewsModel.objects.create(user = UserModel.objects.get(pk=user_data["id"]), listing = ListingModel.objects.get(pk=request.data.get("listing")))
                    return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)
                else:
                    checked_data = ListingViewsModel.objects.get(user=user_data["id"], listing = request.data.get("listing"))
                    checked_data.count += 1
                    checked_data.save()
                    return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)

# ============================================================Favorites============================================================

class FavoritesView(APIView):
    def post(self,request):
        token = request.data.get("token")
        print(token, request.data.get("listing"))

        try:
            user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except:
            return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            pre_val = FavoriteModel.objects.filter(listing = request.data.get("listing"), user = user_data["id"])
            if(len(pre_val) == 0):
                FavoriteModel.objects.create(listing = ListingModel.objects.get(pk = request.data.get("listing")), user = UserModel.objects.get(pk = user_data["id"]))
                return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)

            else:
                FavoriteModel.objects.get(listing = request.data.get("listing"), user = user_data["id"]).delete()
                return Response({"Message" : "Deleted"}, status=status.HTTP_201_CREATED)
    
    def delete(self,request):
        FavoriteModel.objects.get(id= request.query_params.get('id')).delete()
        return Response({"Message" : "Deleted"})

@api_view(["POST"])
def GetFavorites(request):
    token = request.data.get("token")
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except:
        return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
    else:
        if(request.query_params.get("id") is not None):
            val = FavoriteModel.objects.filter(user = user_data["id"], listing = request.query_params.get("id"))
            if(len(val) > 0):
                return Response({"Message" : "OK", "data" : 1})
            else:
                return Response({"Message" : "OK", "data" : 0})
        else:
            all_vals = []
            vals = FavoriteModel.objects.filter(user = user_data["id"]).values()
            for val in vals:
                listing = ListingModel.objects.filter(pk=val["listing_id"]).values()[0]
                image = ImageModel.objects.filter(listing = val["listing_id"]).values()[0]
                val.update({"listing" : listing, "image" : image})

                all_vals.append(val)
            return Response({"Message" : "OK", "data" : all_vals})

# ============================================================Blogs and Blog Comments============================================================

class BlogView(APIView):
    def get(self,request):
        if(request.query_params.get("status") == "1"):
            return Response(list(BlogModel.objects.filter(status = 1).values()))
        return Response(list(BlogModel.objects.all().values()))
    
    def post(self,request):
        serialiser = BlogPostSerializer(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)
        else:
            print(serialiser.errors)
            return Response({"Message" : "Error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self,request):
        val = BlogModel.objects.get(pk=request.query_params.get("id"))

        if(request.query_params.get("delete") == 'true'):
            val.delete()
        else:
            if(val.status == 1):
                val.status = 0
            else:
                val.status = 1
            val.save()

        return Response({"Message" : "OK"},status=status.HTTP_200_OK)

@api_view(["GET"])
def GetSpecificBlog(request):
    id = request.query_params.get("id")
    user = request.query_params.get("user")
    blog = BlogModel.objects.filter(pk=id).values()
    one_blog = BlogModel.objects.get(pk=id)
    comments = CommentModel.objects.filter(blog=id)

    all_comments = []
    if(user == "user"):
        one_blog.views += 1
        one_blog.save()
    for comment in comments:
        all_comments.append({"name" : comment.name, "email" : comment.email, "number" : comment.number, "subject" : comment.subject, "comment" : comment.comment, "posted_on" : comment.created_at})

    return Response({"Message" : "OK", "data" : {"blog" : blog, "comments" : all_comments}})

@api_view(["GET"])
def GetPopularBlogs(reuest):
    blogs = BlogModel.objects.order_by("-views")[:3]
    return Response({"Message" : "OK", "data" : list(blogs.values())},status=status.HTTP_200_OK)

class BlogCommentsView(APIView):
    def get(self,request):
        return Response(list(CommentModel.objects.all().values()))
    
    def post(self,request):
        serializer = BlogCommentPostSerializer(data = request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"Message" : "Error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================Offers============================================================

class OffersView(APIView):
    def get(self,request):
        all_vals = []
        if(request.query_params.get("id") == "1"):
            vals = OfferModel.objects.filter(status = 1).values()
        else:
            vals = OfferModel.objects.all().values()
        
        for val in vals:
            val.update({"listing_id" : {
                "id" : ListingModel.objects.get(pk=val.get("listing_id")).pk,
                "name" : ListingModel.objects.get(pk=val.get("listing_id")).name,
                "company_name" : ListingModel.objects.get(pk=val.get("listing_id")).company_name,
                "status" : ListingModel.objects.get(pk=val.get("listing_id")).status,
                "user_id" : ListingModel.objects.get(pk=val.get("listing_id")).user.pk,
                "user_name" : ListingModel.objects.get(pk=val.get("listing_id")).user.name,
                "user_type" : ListingModel.objects.get(pk=val.get("listing_id")).user.is_staff,
                "user_email" : ListingModel.objects.get(pk=val.get("listing_id")).user.email,
                }})
            all_vals.append(val)
        return Response({"Message" : "OK", "data" : all_vals},status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = OfferSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"Message" : "Error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self,request):
        val = OfferModel.objects.get(pk=request.query_params.get("id"))

        if(request.query_params.get("delete") == 'true'):
            val.delete()
        else:
            if(val.status == 1):
                val.status = 0
            else:
                val.status = 1
            val.save()

        return Response({"Message" : "OK"},status=status.HTTP_200_OK)

# ============================================================Enquiry============================================================

class EnquiryView(APIView):
    def get(self,request):
        if(request.query_params.get("id") is not None):
            vals = EnquiryModel.objects.filter(listing = request.query_params.get("id")).values()
        else:
            vals = EnquiryModel.objects.all().values()

        for val in vals:
            val.update({
                "listing" : ListingModel.objects.filter(pk = val["listing_id"]).values()[0],
                "user" : UserModel.objects.filter(pk = val["user_id"]).values()[0],
            })
        return Response(list(vals))
    
    def post(self,request):
        token = request.data.get("token")
        try:
            user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except:
            return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(UserModel.objects.get(pk=user_data["id"]).is_merchant):
                return Response({"Message" : "Merchant cannot Enquire"})
            if(len(EnquiryModel.objects.filter(listing = request.data.get("listing"), user = user_data["id"]).values()) > 0):
                return Response({"Message" : "Already enquired"})
            else:
                updated_data = request.data.copy()
                updated_data.update({"user" : user_data["id"]})
                print(updated_data)
                serializer = EnquirySerializer(data=updated_data)
                if(serializer.is_valid()):
                    serializer.save()
                    return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)
                else:
                    print(serializer.errors)
                    return Response({"Message" : "Error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def GetUserEnquries(request):
        token = request.data.get("token")
        try:
            user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except:
            return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(UserModel.objects.get(pk = user_data["id"]).is_merchant):
                vals = EnquiryModel.objects.filter(listing_id__user_id = user_data["id"]).values()
            else:
                vals = EnquiryModel.objects.filter(user = user_data["id"]).values()
            
            for val in vals:
                val.update({"listing" : ListingModel.objects.filter(pk = val["listing_id"]).values()[0], "user" : UserModel.objects.filter(pk = val["user_id"]).values()[0]})
            
            return Response({"Message" : "OK", "data" : list(vals)})



# ============================================================Contact US============================================================

class ContactsView(APIView):
    def get(self,request):
        return Response(list(ContactsModel.objects.all().values()))
    
    def post(self,request):
        serializer = ContactsSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response({"Message" : "Created"}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"Message" : "Error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# ============================================================User get============================================================

class UserView(APIView):
    def post(self,request):
        token = request.data.get("token")
        try:
            user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except:
            return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            val = UserModel.objects.filter(pk = user_data["id"]).values()[0]
            my_val = {
                "name" : val.get("name"),
                "email" : val.get("email"),
                "photo" : val.get("photo"),
                "phone" : val.get("phone"),
                "city" : val.get("city"),
            }
            return Response({"Message"  : "OK", "data" : my_val}, status=status.HTTP_200_OK)
    
    def put(self,request):
        token = request.data.get("token")
        try:
            user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except:
            return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            val = UserModel.objects.get(pk=user_data["id"])
            serializer = UserEditSerializer(val, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"Message" : "OK"},status=status.HTTP_200_OK)
            else:
                return Response({"Message" : "Failed"}, status=status.HTTP_400_BAD_REQUEST)
            
@api_view(["POST"])
def EditProfilePhoto(request):
    token = request.data.get("token")
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except:
        return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
    else:
        val = UserModel.objects.get(pk=user_data["id"])
        serializer = UserImageEditSerializer(val, data=request.data)
        if serializer.is_valid():
           serializer.save()
           return Response({"Message" : "OK"},status=status.HTTP_200_OK)
        else:
            return Response({"Message" : "Failed"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def PwdChanger(request):
    token = request.data.get("token")
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except:
        return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
    else:
        user_valid = authenticate(email=UserModel.objects.get(pk=user_data["id"]).email, password=request.data.get("old_password"))
        if not user_valid:
            return Response({"Message" : "Password Incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user = UserModel.objects.get(pk=user_data["id"])
            user.set_password(request.data.get("new_password"))
            user.save()
        return Response({"Message" : "OK"})

@api_view(["POST"])
def GetTheUsers(request):
    token = request.data.get("token")
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except:
        return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
    else:
        if(UserModel.objects.get(pk = user_data["id"]).is_staff):
            if(request.data.get("type") == "user"):
                vals = UserModel.objects.filter(is_merchant = False).values()
                for val in vals:
                    val.update({"Enquries" : list(EnquiryModel.objects.filter(user = val["id"]).values_list("listing","listing__name")),
                                "Reviews" : list(RatingModel.objects.filter(user = val["id"]).values_list("listing","listing__name", "rating"))})
                return Response({"Message" : "OK", "data" : list(vals)})
            else:
                vals = UserModel.objects.filter(is_merchant = True, is_staff = False).values()
                for val in vals:
                    val.update({"listings" : list(ListingModel.objects.filter(user = val["id"]).values_list("id", "name"))})
                return Response({"Message" : "OK", "data" : list(vals)})

# ============================================================Dashboard============================================================
class Dashboard(APIView):
    def post(self,request):
        token = request.data.get("token")
        try:
            user_data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except:
            return Response({"Message" : "Invalid Token"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            is_admin = UserModel.objects.filter(pk = user_data["id"]).values()[0]["is_staff"]
            if(is_admin):
                all_listings = ListingModel.objects.all().values()

                #Listing count, Merchant count, User count, Enquiry count
                listing_count = len(all_listings)
                merchant_count = len(UserModel.objects.filter(is_merchant = True).values())
                user_count = len(UserModel.objects.filter(is_merchant = False).values())
                enquiry_count = len(EnquiryModel.objects.all().values())

                #recents
                recent_contacts = ContactsModel.objects.order_by("-created_at").values()[:3]

                #Graphs
                graph_val = []
                for listing in all_listings:
                    graph_val.append({
                        "listing" : listing,
                        "total_views" : ListingViewsModel.objects.filter(listing = listing["id"]).aggregate(total_count = Sum("count"))["total_count"],
                        "total_enquiries" : len(EnquiryModel.objects.filter(listing = listing["id"]).values()),
                    })
                
                #populars
                populars = []
                popular_views = ListingViewsModel.objects.order_by("-count")[:5]
                for popular in popular_views:
                    one_list = {
                            "listing" : {
                            "id" : popular.listing.pk,
                            "name" : popular.listing.name,
                            "status" : popular.listing.status,
                            "listing_type" : popular.listing.listing_type,
                            "created_at" : popular.listing.created_at

                        },
                        "image" : list(ImageModel.objects.filter(listing = popular.listing.pk).values())
                    }
                    if(one_list not in populars):
                        populars.append(one_list)

                return Response({"Message" : "OK", "data" : {
                    "admin" : is_admin,
                    "listing_count" : listing_count,
                    "merchant_count" : merchant_count,
                    "user_count" : user_count,
                    "enquiry_count" : enquiry_count,
                    "graph" : graph_val,
                    "contacts" : list(recent_contacts),
                    "populars" : populars
                }},status=status.HTTP_200_OK)
            
            else:
                all_listings = ListingModel.objects.filter(user = user_data["id"]).values()
                #Listing count, views count, likes count, Enquiry count
                listing_count = len(all_listings)
                views_count = 0
                likes_count = 0
                enquiry_count = 0
                # Recents
                recent_ratings = []
                recent_reviews = RatingModel.objects.filter(listing__user_id = user_data["id"]).order_by("-created_at").values()[:3]
                for review in recent_reviews:
                    recent_ratings.append({
                        "id" : review["id"],
                        "listing_id" : review["listing_id"],
                        "listing" : ListingModel.objects.filter(pk = review["listing_id"]).values()[0]["name"],
                        "user" :{
                            "photo" : UserModel.objects.filter(pk = review["user_id"]).values()[0]["photo"],
                            "name" : UserModel.objects.filter(pk = review["user_id"]).values()[0]["name"],
                        },
                        "description" : review["description"],
                        "rating" : review["rating"],
                        "created_at" : review["created_at"]
                    })

                #Graphs
                graph_val = []
                for listing in all_listings:
                    enquiry_count += len(EnquiryModel.objects.filter(listing = listing["id"]).values())
                    likes_count += len(FavoriteModel.objects.filter(listing = listing["id"]).values())
                    views_count += ListingViewsModel.objects.filter(listing = listing["id"]).aggregate(total_count = Sum("count"))["total_count"]
                    graph_val.append({
                        "listing" : listing,
                        "total_views" : ListingViewsModel.objects.filter(listing = listing["id"]).aggregate(total_count = Sum("count"))["total_count"],
                        "total_enquiries" : len(EnquiryModel.objects.filter(listing = listing["id"]).values()),
                    })

                #populars
                populars = []
                popular_views = ListingViewsModel.objects.filter(listing__user_id = user_data["id"]).order_by("-count")[:5]

                for popular in popular_views:
                    one_list = {
                            "listing" : {
                            "id" : popular.listing.pk,
                            "name" : popular.listing.name,
                            "status" : popular.listing.status,
                            "listing_type" : popular.listing.listing_type,
                            "created_at" : popular.listing.created_at
                        },
                        "image" : list(ImageModel.objects.filter(listing = popular.listing.pk).values())
                    }
                    if(one_list not in populars):
                        populars.append(one_list)

                return Response({"Message" : "OK", "data" : {
                    "admin" : is_admin,
                    "listing_count" : listing_count,
                    "views_count" : views_count,
                    "likes_count" : likes_count,
                    "enquiry_count" : enquiry_count,
                    "graph" : graph_val,
                    "ratings" : recent_ratings,
                    "populars" : populars
                }},status=status.HTTP_200_OK)
                    
# ============================================================Filter============================================================
# class Filter(APIView):
#     def post(self,request):
#         city_val = request.data.get("city")
#         category_val = request.data.get("category")
#         type_val = request.data.get("type")
        
#         # print(city_val, category_val, type_val )

#         queryset = ListingModel.objects.all()

#         if city_val != "0":
#             queryset = queryset.filter(city__name=city_val)

#         if category_val != "0":
#             queryset = queryset.filter(category=category_val)

#         if type_val != "0":
#             queryset = queryset.filter(listing_type=type_val)

#         # vals = []
#         # if(city_val != "0"):
#         #     print("city!0")
#         #     city_listings = CityListingModel.objects.filter(city = city_val).values()

#         #     for val in city_listings:
#         #         if(category_val != "0" and type_val != "0"):
#         #             print("1both!0")
#         #             vals.append(ListingModel.objects.filter(pk=val["listing_id"], category = category_val, listing_type = type_val).values())
#         #         elif(category_val != "0"):
#         #             print("1cat!0")
#         #             vals.append(ListingModel.objects.filter(pk=val["listing_id"], category = category_val).values())
#         #         elif(type_val != "0"):
#         #             print("1type!0")
#         #             vals.append(ListingModel.objects.filter(pk=val["listing_id"], listing_type = type_val).values())
#         #         else:
#         #             print("1both0")
#         #             vals.append(ListingModel.objects.filter(pk=val["listing_id"]).values())
#         # else:
#         #     if(category_val != "0" and type_val != "0"):
#         #         print("2both!0")
#         #         vals.append(ListingModel.objects.filter(category = category_val, listing_type = type_val).values())
#         #     elif(category_val != "0"):
#         #         print("2cat!0")
#         #         vals.append(ListingModel.objects.filter(category = category_val).values())
#         #     elif(type_val != "0"):
#         #         print("2type!0")
#         #         vals.append(ListingModel.objects.filter(listing_type = type_val).values())
#         #     else:
#         #         print("2both0")
#         #         vals.append(ListingModel.objects.all().values())

#         # print(vals) 
#         return Response({"Message" : "OK", "data" : list(queryset.values())})


#     def put(self,request): #forSearch
#         pass

class Filter(APIView):
    def post(self, request):
        city_val = request.data.get("city")
        category_val = request.data.get("category")
        type_val = request.data.get("type")

        # Print the received filter values
        print(city_val, category_val, type_val)

        # Start with an empty Q object
        query = Q()

        # Add city filter if applicable
        if city_val != "0":
            city_listings_ids = CityListingModel.objects.filter(city=city_val).values_list('listing_id', flat=True)
            query &= Q(pk__in=city_listings_ids)

        # Add category filter if applicable
        if category_val != "0":
            query &= Q(category=category_val)

        # Add type filter if applicable
        if type_val != "0":
            query &= Q(listing_type=type_val)

        # Execute the query and get the values
        listings = ListingModel.objects.filter(query).values()

        for listing in listings:
            image_val = ImageModel.objects.filter(listing=listing["id"]).values()[0]
            total_views = ListingViewsModel.objects.filter(listing = listing["id"]).aggregate(total_count = Sum("count"))
            avg_rating = RatingModel.objects.filter(listing = listing["id"]).aggregate(avg_rating = Avg("rating"))
            total_comments = len(RatingModel.objects.filter(listing = listing["id"]).values())
            listing.update({"category_id" : {
                "id" : listing["category_id"],
                "name" : CategoryModel.objects.get(pk=listing["category_id"]).name
            },
            "views" : 0 if total_views["total_count"] is None else total_views["total_count"],
            "avg_rating" : 0 if avg_rating["avg_rating"] is None else avg_rating["avg_rating"],
            "total_ratings" : len(RatingModel.objects.filter(listing = listing["id"]).values()),
            "total_comments" : 0 if total_comments is None else total_comments ,
            "image" : image_val
            })

        # Return the response with consistent data structure
        return Response({"Message": "OK", "data": list(listings)})

# modi
@api_view(["GET"])
def homepage(request):
    categories = CategoryModel.objects.filter(status=1).annotate(total_listings=Count('listingmodel')).values()

    category_ids = []

    for category in categories:
        category_ids.append({"id" : category['id'], "name" : category["name"]})

    if len(category_ids) >= 4:
        random_categories = random.sample(category_ids, len(category_ids))
    else:
        random_categories = category_ids

    all_data = {}

    for category in random_categories:
        all_listings = ListingModel.objects.filter(category = category["id"])

        all_cat_lists = []

        for listing in all_listings:

            total_views = ListingViewsModel.objects.filter(listing = listing.pk).aggregate(total_count = Sum("count"))
            total_ratings = RatingModel.objects.filter(listing = listing.pk)
            avg_rating =total_ratings.aggregate(avg_rating = Avg("rating"))
            total_comments = len(ListingViewsModel.objects.filter(listing = listing.pk).values())

            listi = model_to_dict(listing)
            the_image = ImageModel.objects.filter(listing = listing.pk).values()[0] if ImageModel.objects.filter(listing = listing.pk).exists() else ''
            listi.update({
                "category_id" : { "id" : listing.category.pk, "name" : listing.category.name},
                "image" : the_image,
                "amenities" : list(ListingAmenityModel.objects.filter(listing = listing.pk).values()),
                "cities" : list(CityListingModel.objects.filter(listing = listing.pk).values()),
                "enquiries" : list(EnquiryModel.objects.filter(listing = listing.pk).values()),
                "offers" : list(OfferModel.objects.filter(listing = listing.pk).values()),
                "views" : 0 if total_views["total_count"] is None else total_views["total_count"],
                "avg_rating" : 0 if avg_rating["avg_rating"] is None else avg_rating["avg_rating"],
                "total_ratings" : len(total_ratings),
                "total_comments" : 0 if total_comments is None else total_comments
                
            })

            all_cat_lists.append(listi)
            
        all_data.update({category["name"] : all_cat_lists})

    return Response({"message" : "success", "data" : {
        "categories" : list(categories),
        "listings" : all_data,
        "cities" : CityModel.objects.all().values_list("id", "name")
    }})

@api_view(['POST'])
def new_filter(request):
    data = request.data

    all_listings = ListingModel.objects.all()

    if(len(data.get("cities")) != 0):
        # all_city_listings = CityListingModel.objects.filter(city__in = data.get("cities")).values_list("listing", flat=True)
        all_listings = all_listings.filter(citylistingmodel__city__in = data.get("cities"))
        available_listings = ListingModel.objects.filter(availability = 1)

        all_listings = all_listings | available_listings
    
    if(len(data.get("categories")) != 0):
        all_listings = all_listings.filter(category__in = data.get("categories"))
    
    if(len(data.get("listingTypes")) != 0):
        all_listings = all_listings.filter(listing_type__in = data.get("listingTypes"))
    
    if(int(data.get('mos')) != -1):
        all_listings = all_listings.filter(mode_of_service = int(data.get('mos')))
    
    if(data.get("text") != ''):
        all_listings = all_listings.filter(name__icontains = data.get("text"))

    if(data.get("sort_order") != '0'):
        if(data.get("sort_order") == 'latest'):
            all_listings = all_listings.order_by('-created_at')
        if(data.get("sort_order") == 'verified'):
            all_listings = all_listings.order_by('-verified')


    listings = []
        
    for listing in all_listings:

        total_views = ListingViewsModel.objects.filter(listing = listing.pk).aggregate(total_count = Sum("count"))
        total_ratings = RatingModel.objects.filter(listing = listing.pk)
        avg_rating =total_ratings.aggregate(avg_rating = Avg("rating"))
        total_comments = len(ListingViewsModel.objects.filter(listing = listing.pk).values())

        listi = model_to_dict(listing)
        the_image = ImageModel.objects.filter(listing = listing.pk).values()[0] if ImageModel.objects.filter(listing = listing.pk).exists() else ''
        listi.update({
            "category_id" : { "id" : listing.category.pk, "name" : listing.category.name},
            "image" : the_image,
            "amenities" : list(ListingAmenityModel.objects.filter(listing = listing.pk).values_list("amenity__id", "amenity__name")),
            "cities" : list(CityListingModel.objects.filter(listing = listing.pk).values_list("city__id", "city__name")),
            "enquiries" : list(EnquiryModel.objects.filter(listing = listing.pk).values()),
            "offers" : list(OfferModel.objects.filter(listing = listing.pk).values()),
            "views" : 0 if total_views["total_count"] is None else total_views["total_count"],
            "avg_rating" : 0 if avg_rating["avg_rating"] is None else avg_rating["avg_rating"],
            "total_ratings" : len(total_ratings),
            "total_comments" : 0 if total_comments is None else total_comments   
        })

        listings.append(listi)

    if(data.get("sort_order") != '0'):
        if(data.get("sort_order") == 'popular'):
            listings = sorted(listings, key=lambda x : x['views'])
        if(data.get("sort_order") == 'high'):
            listings = sorted(listings, key=lambda x : x['avg_rating'], reverse=True)
        if(data.get("sort_order") == 'low'):
            listings = sorted(listings, key=lambda x : x['avg_rating'])

    
    return Response({"message" : "success", "data" : listings})
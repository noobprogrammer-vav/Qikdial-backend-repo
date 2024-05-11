from rest_framework import serializers
from .models import *

# class UserSerialiser

# ============================================================Amenities============================================================
class AmenityPostSerializer(serializers.ModelSerializer):
    class Meta :
        model = AmenityModel
        fields = ["name","image"]

class AmenityImagePutSerializer(serializers.ModelSerializer):
    class Meta :
        model = AmenityModel
        fields = ["image"]

class AmenityGetSerializer(serializers.ModelSerializer):
    class Meta :
        model = AmenityModel
        fields = '__all__'

# ============================================================Categories============================================================
class CategoryPostSerializer(serializers.ModelSerializer):
    class Meta :
        model = CategoryModel
        fields = ["parent","name","image","parent_name"]

class CategoryPutSerializer(serializers.ModelSerializer):
    class Meta :
        model = CategoryModel
        fields = ["parent","name","parent_name"]

class CategoryPutImageSerializer(serializers.ModelSerializer):
    class Meta :
        model = CategoryModel
        fields = ["image"]

class CategoryGetSerializer(serializers.ModelSerializer):
    class Meta :
        model = CategoryModel
        fields = '__all__'

# ============================================================Cities============================================================
class CityPostSerializer(serializers.ModelSerializer):
    class Meta :
        model = CityModel
        fields = ["name"]

class CityGetSerializer(serializers.ModelSerializer):
    class Meta :
        model = CityModel
        fields = '__all__'

# ============================================================Listings============================================================
class ListingGetSerializer(serializers.ModelSerializer):
    category = CategoryGetSerializer()
    class Meta :
        model = ListingModel
        fields = '__all__'

class ListingProductPostSerializer(serializers.ModelSerializer):
    class Meta :
        model = ListingModel
        fields = ["category", "user", "name", "company_name", "listing_type", "availability", "summary", "established_on", "description","address", "map_address", "mobile", "price", "gstin", "height", "width", "weight", "color", "delivery_duration", "refund"]

        # fields = ["category", "user", "name", "company_name", "listing_type", "availability", "summary", "established_on", "description", "timings", "address", "map_address", "mobile", "website", "gstin", "price"]

class ListingServicePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingModel
        fields = ["category", "user", "name", "company_name", "listing_type", "availability", "summary", "established_on", "description", "address", "map_address", "mobile", "website", "timings", "mode_of_service", "delivery_duration", "refund"]

class ListingBusinessPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingModel
        fields = ["category", "user", "name", "company_name", "listing_type", "availability", "summary", "established_on", "description","address", "map_address", "mobile", "website", "timings", "gstin"]
# category, user, name, company_name, listing_type, availability, summary, established_on, description, timings, address, mobile, website, gstin, price, verified

# ============================================================Listing Image============================================================

class ListingImagePostSerialiser(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ["listing", "image"]

# ============================================================City Listing============================================================

class CityListingPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityListingModel
        fields = ["listing", "city"]

# ============================================================Rating============================================================

class RatingPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingModel
        fields = ["listing", "user", "rating", "description"]

# ============================================================Blogs, BlogComments============================================================

class BlogGetSerializer(serializers.Serializer):
    class Meta:
        model = BlogModel
        fields = "__all__"

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogModel
        fields = ["title", "author", "description", "image", "summary"]

class BlogCommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ["blog", "name", "email", "number", "subject", "comment"]

# ============================================================Offers============================================================

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferModel
        fields = ["listing", "offer", "description"]

class OfferGetSerializer(serializers.ModelSerializer):
    listing_id = ListingGetSerializer()
    class Meta:
        model = OfferModel
        fields = "__all__"
# ============================================================Enquiry============================================================

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryModel
        fields = ["listing", "user"]

# ============================================================Contact us============================================================

class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactsModel
        fields = ["name", "email", "mobile", "subject", "message"]

# ============================================================Users============================================================

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["name", "email", "phone", "city"]

class UserImageEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["photo"]

# ============================================================Listing Edits============================================================

class BasicInfoSerialiser(serializers.ModelSerializer):
    class Meta:
        model = ListingModel
        fields = ["name", "company_name", "listing_type", "category", "availability", "established_on", "address", "map_address", "mobile", "summary", "description"]

class OtherInfoSerialiser(serializers.ModelSerializer):
    class Meta:
        model = ListingModel
        fields = ["price", "gstin", "height", "width", "weight", "color", "delivery_duration", "refund", "mode_of_service", "website", "timings",]

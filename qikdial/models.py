from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, password, **extra_fields):
        if not email:
            raise ValueError(_("User must have a valid Email address"))
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, name, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_merchant', True)



        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(name, email, password, **extra_fields)

class UserModel(AbstractBaseUser):  
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='qikdial/uploads/profile')
    phone = models.CharField(max_length=100) #""
    city = models.CharField(max_length=100)
    is_merchant = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.name
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class TokenModel(models.Model):
    user = models.ForeignKey(UserModel,on_delete=models.CASCADE, unique=True)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.name

class   CategoryModel(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='qikdial/uploads/categories', null=True) #""
    # cover_image = models.ImageField(upload_to='qikdial/uploads/categories/cover', )
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class ListingModel(models.Model):
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    listing_type = models.IntegerField(default=1) #1,2,3 = product,service,business
    availability = models.IntegerField(default=1) #1,2,3 = all over india, Specific City, Local only
    summary = models.TextField()
    established_on = models.CharField(max_length=100, null=True)
    description = models.TextField()
    timings = models.TextField(null=True, blank=True)
    address = models.TextField(null=True)
    map_address = models.TextField(null=True, blank=True)
    mobile = models.CharField(max_length=100,null=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    gstin = models.CharField(max_length=100, null=True, blank=True)
    price = models.CharField(max_length = 100, null=True, blank=True)

    height = models.CharField(max_length=100,blank=True, null=True)
    width = models.CharField(max_length=100,blank=True, null=True)
    weight = models.CharField(max_length=100,blank=True, null=True)
    color = models.CharField(max_length=100,blank=True, null=True)
    delivery_duration = models.CharField(max_length=100 ,blank=True, null=True)
    refund = models.TextField(blank=True, null=True)
    mode_of_service  = models.CharField(max_length=100,default="1",blank=True, null=True) #1,2 online, offline
    verified = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class ImageModel(models.Model):
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='qikdial/uploads/listings') #""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __int__(self) -> int:
        return self.pk

class AmenityModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="qikdial/uploads/amenities") #""
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

    def __str__(self) -> str:
        return self.name

class ListingAmenityModel(models.Model):
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE)
    amenity = models.ForeignKey(AmenityModel,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __int__(self) -> int:
        return self.listing.name

class OfferModel(models.Model):
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE)
    offer = models.FloatField()
    description = models.TextField()
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.description

class RatingModel(models.Model):
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, blank=True, null=True)

    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __int__(self) -> int:
        return self.rating

class FavoriteModel(models.Model):
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __int__(self) -> int:
        return self.pk

class ListingViewsModel(models.Model):
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __int__(self) -> int:
        return self.pk

class EnquiryModel(models.Model):
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default=None, null=True)
    email = models.EmailField(max_length=254, default=None, null=True)
    mobile = models.CharField(max_length=100, default=None, null=True)
    message = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __int__(self) -> int:
        return self.pk
 
class BlogModel(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    summary = models.TextField(default=None)
    description = models.TextField()
    image = models.ImageField(upload_to="qikdial/uploads/blogs")
    views = models.IntegerField(default=0)  #""
    status = models.IntegerField(default=1)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

class CommentModel(models.Model):
    blog = models.ForeignKey(BlogModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.subject

class ContactsModel(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    email = models.CharField(max_length=100, unique=True)   
    mobile = models.CharField(max_length=100, null=True, default=None)   
    subject = models.CharField(max_length=255, null=True, default=None)   
    message = models.TextField(null=True, default=None)   
    created_at = models.DateTimeField(auto_now_add=True)


class CityModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
class CityListingModel(models.Model):
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE)
    city = models.ForeignKey(CityModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.city.name
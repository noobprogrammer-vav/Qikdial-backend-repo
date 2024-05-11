from django.urls import path
# from django.contrib.auth.views import LoginView, LogoutView
from .views import *

urlpatterns = [
# ==========================================================Basics==========================================================

    path("test", Tester),
    path("login", Loginer),
    path("logout",Logouter),
    path("signup",Signup),
    path("checker", token_checker),

# ==========================================================Amenities==========================================================

    path("amenity/",AmenitiesView.as_view()),
    path("amenity/edit/name",AminityNameEdit),
    path("amenity/edit/image",AminityImageEdit),
    path("amenity/get",AminityGet),

# ==========================================================Categories==========================================================

    path("category/",CategoryView.as_view()),
    path("category/edit/image",CategoryImageEdit),
    path("category/get",CategoryGet),

# ==========================================================Cities==========================================================

    path("city/",CityView.as_view()),
    path("city/get",CityGet),

# ==========================================================Listings==========================================================

    path("listings/",ListingView.as_view()),
    path("listings/get/",ListingGetSpecific),
    path("listings/userget",ListingGetUserSpecific),
    path("listings/delete",ListingHardDelete),

    path("listings/edit/basicinfo",BasicInfoEditor),
    path("listings/edit/otherinfo",OtherInfoEditor),
    path("listings/edit/amenities",AmenityInfoEditor),
    path("listings/edit/cities",CityInfoEditor),
    path("listings/image/",ListingImageView.as_view()),




# ==========================================================Ratings and Listings views==========================================================

    path("rating/",RatingView.as_view()), 
    path("rating/get",RatingsUserSpecific),
    path("views",ListingViewsView.as_view()),

# ==========================================================Favorites==========================================================

    path("favorites/",FavoritesView.as_view()),
    path("favorites/get/",GetFavorites),

# ==========================================================Blogs and comments==========================================================

    path("blogs/",BlogView.as_view()),
    path("blogs/getspecific/",GetSpecificBlog),
    path("blogs/populars",GetPopularBlogs),

    path("blogs/comments/",BlogCommentsView.as_view()),


# ==========================================================Offers, Enquiry, Contacts==========================================================

    path("offers/",OffersView.as_view()),
    path("enquiry/",EnquiryView.as_view()),
    path("enquries",GetUserEnquries),
    path("contacts",ContactsView.as_view()),

# ==========================================================Users==========================================================
    
    path("useredit/",UserView.as_view()),
    path("useredit/image",EditProfilePhoto),
    path("useredit/pwd",PwdChanger),
    path("adminpage/getusers",GetTheUsers),


# ==========================================================Dashboard and Filter==========================================================

    path("dashboard", Dashboard.as_view()),
    path("filter",Filter.as_view())
    
]

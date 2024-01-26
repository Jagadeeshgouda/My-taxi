from django.urls import path,include
from .  import views
from.views import SearchResultsView


urlpatterns = [
    path('home',views.home,name='home'),
    path('',views.createUser),
    path('login',views.login_form),
    path('logout',views.logout_form),
    path('changepassword',views.changepassword),
    path('cars',views.getcars,name='cars'),
    path('moredetails/<int:car_id>/', views.more_details_view, name='moredetails'),
    path('verify/',views.verifyUser,name="verify"),
    path('success/',views.success,name="success"),
    path('invoice', views.info, name='invoice'),
    path('search',SearchResultsView.as_view(),name='search'),
    path('search1',SearchResultsView.as_view(),name='search1'),
    path('booking_confirmation_email',views.send_booking_confirmation_email),
    path('drivers',views.driverss),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
	path('index', views.homepage, name='index'),
	path('paymenthandler/', views.paymenthandler, name='paymenthandler'),

]

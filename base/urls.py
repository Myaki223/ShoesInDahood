from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
	
urlpatterns = [
	path('', views.home, name="index"),
	path('adminpage/', views.adminpanel, name="admin"),
    path('add_product/', views.add_product, name="add_product"),
	path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
	path('form/', views.form, name="form"),
	path('login/', views.signin, name="login"),
  path('logout/', views.user_logout, name='user_logout'),
	path('profile/', views.profile, name="profile"),
	path('update_user/', views.update_user, name="update_user"),
	path('update_info/', views.update_info, name="update_info"),
	path('reciept/', views.reciept, name="reciept"),
	path('register/', views.register, name="register"),
	path('shop/', views.shop, name="shop"),
	path('utilities_animation/', views.utilities_animation, name="utilities_animation"),
 path('item_item/', views.item_item, name="item_item"),
 path('user_user/', views.user_user, name="user_user"),
path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

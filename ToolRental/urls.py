
from django.contrib import admin
from django.urls import path
from Rental import views

urlpatterns = [

    # Admin
    path('admin/', admin.site.urls),

    # User
    path('register/', views.SignUpView.as_view(), name='register'),
    path('users/', views.UserListView.as_view(), name='users'),

    # Tools
    path('tools/', views.ToolsListCreateView.as_view(), name='tools'),
    path('tools/<int:pk>/', views.ToolsRetrieveUpdateDeleteView.as_view(), name='tool-detail'),

    # Rental
    path('rentals/', views.RentalListCreateView.as_view(), name='rentals'),
    path('rentals/<int:pk>/', views.RentalRetrieveUpdateView.as_view(), name='rental-detail'),

    # Complaint
    path('complaints/', views.ComplaintListCreateView.as_view(), name='complaints'),
    path('complaints/<int:pk>/', views.ComplaintRetrieveUpdateDeleteView.as_view(), name='complaint-detail'),

    # Payment
    path('payments/', views.PaymentListCreateView.as_view(), name='payments'),
    path('payments/<int:pk>/', views.PaymentRetrieveView.as_view(), name='payment-detail'),

]

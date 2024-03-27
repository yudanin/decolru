from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("resources", views.resources, name="resources"),
    path("resources/<slug:slug>/", views.resource_details, name="resource-details"),
    path("resources/langs", views.SelectLanguageView.as_view()),
    path("resources/suggest", views.SuggestResourceView.as_view(), name="suggest-resource"),
    path("thank-you", views.ThankYouView.as_view(), name="thankyou"),
    path("resources/review", views.ReviewSuggestions.as_view(), name="review-suggestions")
]
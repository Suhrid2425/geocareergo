from django.urls import path

from . import views


app_name = "exam_tests"


urlpatterns = [

    path(
        "",
        views.test_home,
        name="test_home"
    ),

    path(
        "<int:test_id>/",
        views.test_detail,
        name="test_detail"
    ),

    path(
        "<int:test_id>/start/",
        views.start_test,
        name="start_test"
    ),

    path(
        "attempt/<int:attempt_id>/",
        views.take_test,
        name="take_test"
    ),

    path(
        "attempt/<int:attempt_id>/submit/",
        views.submit_test,
        name="submit_test"
    ),

    path(
        "attempt/<int:attempt_id>/result/",
        views.test_result,
        name="test_result"
    ),
    path(
    "practice/<str:category>/",
    views.practice_quiz,
    name="practice_quiz"
),
    path(
    "my-results/",
    views.my_results,
    name="my_results"
),

]
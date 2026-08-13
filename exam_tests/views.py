from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Test, TestAttempt, TestAnswer, Question


# ==========================================================
# TEST HOME
# ==========================================================

def test_home(request):

    free_tests = Test.objects.filter(
        is_active=True,
        is_free=True
    ).order_by("-created_at")

    paid_tests = Test.objects.filter(
        is_active=True,
        is_free=False
    ).order_by("-created_at")

    practice_tests = Test.objects.filter(
        is_active=True,
        test_type="practice"
    ).order_by("-created_at")

    return render(
        request,
        "exam_tests/test_home.html",
        {
            "free_tests": free_tests,
            "paid_tests": paid_tests,
            "practice_tests": practice_tests,
        }
    )


# ==========================================================
# TEST DETAIL
# ==========================================================

def test_detail(request, test_id):

    test = get_object_or_404(
        Test,
        id=test_id,
        is_active=True
    )

    return render(
        request,
        "exam_tests/test_detail.html",
        {
            "test": test,
        }
    )


# ==========================================================
# START TEST
# ==========================================================

@login_required
def start_test(request, test_id):

    test = get_object_or_404(
        Test,
        id=test_id,
        is_active=True
    )

    # Premium tests are disabled for now.
    # Payment/access system will be added later.

    if not test.is_free:

        return render(
            request,
            "exam_tests/premium_test.html",
            {
                "test": test,
            }
        )

    attempt = TestAttempt.objects.create(
        user=request.user,
        test=test
    )

    return redirect(
        "exam_tests:take_test",
        attempt_id=attempt.id
    )


# ==========================================================
# TAKE TEST
# ==========================================================

@login_required
def take_test(request, attempt_id):

    attempt = get_object_or_404(
        TestAttempt,
        id=attempt_id,
        user=request.user,
        is_completed=False
    )

    test = attempt.test

    questions = test.questions.all()

    return render(
        request,
        "exam_tests/take_test.html",
        {
            "attempt": attempt,
            "test": test,
            "questions": questions,
        }
    )


# ==========================================================
# SUBMIT TEST
# ==========================================================

@login_required
def submit_test(request, attempt_id):

    attempt = get_object_or_404(
        TestAttempt,
        id=attempt_id,
        user=request.user,
        is_completed=False
    )

    test = attempt.test

    questions = test.questions.all()

    score = 0

    for question in questions:

        selected_answer = request.POST.get(
            f"question_{question.id}",
            ""
        )

        is_correct = (
            selected_answer == question.correct_answer
        )

        if is_correct:

            marks = question.marks

        elif selected_answer:

            marks = -question.negative_marks

        else:

            marks = 0

        score += marks

        TestAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct,
            marks_obtained=marks
        )

    # Save score

    attempt.score = score

    # Calculate percentage

    if test.total_marks > 0:

        attempt.percentage = (
            float(score)
            /
            float(test.total_marks)
        ) * 100

    else:

        attempt.percentage = 0

    # Complete attempt

    attempt.is_completed = True

    attempt.submitted_at = timezone.now()

    attempt.save()

    # Go to result page

    return redirect(
        "exam_tests:test_result",
        attempt_id=attempt.id
    )


# ==========================================================
# TEST RESULT
# ==========================================================

@login_required
def test_result(request, attempt_id):

    attempt = get_object_or_404(
        TestAttempt,
        id=attempt_id,
        user=request.user,
        is_completed=True
    )

    answers = attempt.answers.select_related(
        "question"
    ).all()

    # Correct answers

    correct_count = answers.filter(
        is_correct=True
    ).count()

    # Incorrect answers
    # is_correct=False AND user actually selected something

    incorrect_count = answers.filter(
        is_correct=False
    ).exclude(
        selected_answer=""
    ).count()

    # Unanswered questions

    unanswered_count = answers.filter(
        selected_answer=""
    ).count()

    return render(
        request,
        "exam_tests/test_result.html",
        {
            "attempt": attempt,
            "test": attempt.test,
            "answers": answers,

            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "unanswered_count": unanswered_count,
        }
    )

# ==========================================================
# MY TEST RESULTS
# ==========================================================

@login_required
def my_results(request):

    attempts = TestAttempt.objects.filter(
        user=request.user,
        is_completed=True
    ).select_related(
        "test"
    ).order_by(
        "-submitted_at"
    )

    return render(
        request,
        "exam_tests/my_results.html",
        {
            "attempts": attempts,
        }
    )

# ==========================================================
# FREE PRACTICE QUIZ
# ==========================================================

def practice_quiz(request, category):

    allowed_categories = [
        "reasoning",
        "aptitude",
        "verbal",
    ]

    if category not in allowed_categories:

        return redirect(
            "exam_tests:test_home"
        )

    questions = Question.objects.filter(
        test__category=category,
        test__test_type="practice",
        test__is_free=True,
        test__is_active=True
    )

    total_questions = questions.count()

    if total_questions == 0:

        question = None

    else:

        # Pick a random question

        question = questions.order_by("?").first()

    return render(
        request,
        "exam_tests/practice_quiz.html",
        {
            "category": category,
            "question": question,
            "total_questions": total_questions,
        }
    )
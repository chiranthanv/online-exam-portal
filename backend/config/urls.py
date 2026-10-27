from django.urls import path
from portal import auth_views as auth
from portal import views

urlpatterns = [
    path("health", views.HealthView.as_view()),
    path("api/v1/auth/csrf", auth.CsrfView.as_view()),
    path("api/v1/auth/login", auth.LoginView.as_view()),
    path("api/v1/auth/refresh", auth.RefreshView.as_view()),
    path("api/v1/auth/logout", auth.LogoutView.as_view()),
    path("api/v1/auth/me", auth.MeView.as_view()),
    path("api/v1/auth/reset-password/confirm", auth.ResetConfirmView.as_view()),
    path("api/v1/auth/students/<uuid:pk>/reset-password", auth.ResetRequestView.as_view()),
    path("api/v1/students", views.StudentList.as_view()),
    path("api/v1/students/bulk-import", views.BulkImport.as_view()),
    path("api/v1/batches", views.BatchList.as_view()),
    path("api/v1/batches/<uuid:pk>/students", views.BatchStudents.as_view()),
    path("api/v1/questions", views.QuestionList.as_view()),
    path("api/v1/questions/<uuid:pk>", views.QuestionDetail.as_view()),
    path("api/v1/exams", views.ExamList.as_view()),
    path("api/v1/exams/available", views.AvailableExams.as_view()),
    path("api/v1/exams/<uuid:pk>/attempt", views.StartAttempt.as_view()),
    path("api/v1/attempts/<uuid:pk>/submit", views.SubmitAttempt.as_view()),
    path("api/v1/attempts/<uuid:pk>/result", views.AttemptResult.as_view()),
    path("api/v1/attempts/<uuid:pk>/proctoring-events", views.AttemptProctoringEvent.as_view()),
    path("api/v1/admin/attempts", views.AdminAttemptList.as_view()),
    path("api/v1/admin/attempts/<uuid:pk>/override", views.AdminAttemptOverride.as_view()),
    path("api/v1/exams/<uuid:pk>", views.ExamDetail.as_view()),
    path("api/v1/exams/<uuid:pk>/questions", views.ExamQuestions.as_view()),
    path("api/v1/exams/<uuid:pk>/batches", views.ExamBatches.as_view()),
    path("api/v1/audit-logs", views.AuditList.as_view()),
]

from django.urls import path

from . import views

urlpatterns = [
    # ex: /allvm/
    path('', views.index, name='index'),
    # ex: /allvm/pdf
    path('pdf/', views.render_to_pdf, name='render_to_pdf'),
    #path('memory/', views.memory, name='memory'),
    # ex: /polls/5/
    #path('<int:question_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    #path('<int:question_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    #path('<int:question_id>/vote/', views.vote, name='vote'),
]

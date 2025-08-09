from django.urls import path
from . import views
from wagtail.images.views.serve import ServeView
from django.urls import path, include
from .views import chatbot_conversar, chatbot_config, chatbot_status


from django.conf import settings



urlpatterns = [
	# ...
	path("teste-login-sso/", views.teste_login_sso, name="teste_login_sso"),
	path("login-sso/", views.login_sso, name="login_sso"),
	path("pt/elasticsearch/callback/", views.callback_sso, name="callback_sso"),
	path("logout/", views.logout_view, name="logout"),
    path('salvar-contato/', views.salvar_contato, name='salvar_contato'),
    path('salvar-resposta-formulario/', views.salvar_resposta_formulario, name='salvar_resposta_formulario'),
    path('exportar-respostas/', views.exportar_respostas_csv, name='exportar_respostas_csv'),
    
	path('chatbot/api/conversar/', chatbot_conversar, name='chatbot_conversar'),
    path('chatbot/api/config/', chatbot_config, name='chatbot_config'),
    path('chatbot/api/status/', chatbot_status, name='chatbot_status'),
    

	# API endpoints para o formulário
    path('api/validate-field/', views.validate_field_ajax, name='validate_field'),
    path('api/upload-file/', views.upload_file_ajax, name='upload_file'),
    
    # Visualização de submissões
    path('submission/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('submissions/export/<int:page_id>/', views.export_submissions, name='export_submissions'),
    path('images/<int:id>/<str:filter_spec>/<str:filename>', ServeView.as_view(action='serve'), name='wagtailimages_serve'),

    # Relatórios
    path('reports/form/<int:page_id>/', views.form_report, name='form_report'),
]

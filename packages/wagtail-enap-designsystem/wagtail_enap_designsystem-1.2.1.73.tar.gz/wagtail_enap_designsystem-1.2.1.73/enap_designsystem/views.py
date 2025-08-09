import uuid
import requests
import time
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from .utils.decorators import aluno_login_required
from .utils.sso import get_valid_access_token
from wagtail.models import Page
from django.shortcuts import redirect
from django.contrib import messages
from .models import Contato
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse 
from django.core.mail import send_mail
from .models import Contato, FormularioSnippet, RespostaFormulario
from django.shortcuts import redirect, get_object_or_404, render
import csv
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid

from .services.chatbot_service import ChatbotService
from .models import ChatbotConfig, ChatbotWidget
from django.shortcuts import render
from django.http import Http404
from wagtail.models import Site, Page

from django.views import View
from django.views.decorators.http import require_http_methods
from django.apps import apps
from django.db.models import Count, Sum, Avg, Q
from django.core.cache import cache
import requests

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
import re
from .blocks.form import FormularioPage, FormularioSubmission


def teste_login_sso(request):
	return render(request, "teste_login_sso.html")

def login_sso(request):
	redirect_uri = request.build_absolute_uri(settings.SSO_REDIRECT_PATH)

	# Gera state único para segurança (proteção CSRF)
	state = str(uuid.uuid4())

	# print("Redirect URI gerado:", redirect_uri)
	# Monta query com todos os parâmetros
	query = {
		"client_id": settings.SSO_CLIENT_ID,
		"redirect_uri": redirect_uri,
		"response_type": "code",
		"scope": "openid",
		"state": state,
	}

	# Monta URL final do SSO
	sso_login_url = f"{settings.SSO_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in query.items())}"
	return redirect(sso_login_url)

def callback_sso(request):
	code = request.GET.get("code")
	if not code:
		return HttpResponseBadRequest("Código de autorização ausente.")

	# 🛑 IMPORTANTE: esta URL precisa ser exatamente igual à registrada no Keycloak
	redirect_uri = request.build_absolute_uri(settings.SSO_REDIRECT_PATH)

	data = {
		"grant_type": "authorization_code",
		"code": code,
		"redirect_uri": redirect_uri,
		"client_id": settings.SSO_CLIENT_ID,
		"client_secret": settings.SSO_CLIENT_SECRET,
	}
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}

	# ⚠️ Desativa verificação SSL apenas em DEV
	verify_ssl = not settings.DEBUG

	# 🔐 Solicita o token
	print("📥 Enviando para /token:", data)
	token_response = requests.post(
		settings.SSO_TOKEN_URL,
		data=data,
		headers=headers,
		verify=verify_ssl
	)
	print("🧾 TOKEN RESPONSE:", token_response.status_code, token_response.text)

	if token_response.status_code != 200:
		return HttpResponse("Erro ao obter token", status=token_response.status_code)

	access_token = token_response.json().get("access_token")
	if not access_token:
		return HttpResponse("Token de acesso não recebido.", status=400)

	# 🔍 Pega dados do usuário
	userinfo_headers = {
		"Authorization": f"Bearer {access_token}"
	}
	user_info_response = requests.get(
		settings.SSO_USERINFO_URL,
		headers=userinfo_headers,
		verify=verify_ssl
	)

	if user_info_response.status_code != 200:
		return HttpResponse("Erro ao obter informações do usuário.", status=400)

	user_info = user_info_response.json()
	email = user_info.get("email")
	nome = user_info.get("name")
	cpf = user_info.get("cpf")
	print("user_info", user_info)
	if not email or not nome:
		return HttpResponse("Informações essenciais ausentes no SSO.", status=400)

	# 🧠 Armazena na sessão para uso em /area-do-aluno
	request.session["aluno_sso"] = {
		"email": email,
		"nome": nome,
		"cpf": cpf,
		"access_token": access_token,
		"refresh_token": token_response.json().get("refresh_token"),
		"access_token_expires_at": int(time.time()) + token_response.json().get("expires_in", 300),
	}

	return redirect(get_area_do_aluno_url())

def logout_view(request):
	request.session.flush()
	return render(request, "logout_intermediario.html")

def get_area_do_aluno_url():
	try:
		page = Page.objects.get(slug="area-do-aluno").specific
		return page.url
	except Page.DoesNotExist:
		return "/"
	
@aluno_login_required
def area_do_aluno(request):
	token = get_valid_access_token(request.session)
	if not token:
		return redirect("/")

	# Exemplo: usar o token para chamar API externa
	response = requests.get("https://api.enap.gov.br/aluno", headers={
		"Authorization": f"Bearer {token}"
	})
	aluno_dados = response.json()

	return render(request, "area_do_aluno.html", {
		"aluno": request.session["aluno_sso"],
		"dados": aluno_dados,
	})






def salvar_contato(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        mensagem = request.POST.get('mensagem')
        
        # Salva no banco
        Contato.objects.create(
            nome=nome,
            email=email,
            mensagem=mensagem
        )
        
        messages.success(request, 'Mensagem enviada com sucesso!')
        return redirect(request.META.get('HTTP_REFERER', '/'))
	



def salvar_resposta_formulario(request):
    """Salva resposta do formulário snippet"""
    if request.method == 'POST':
        try:
            formulario_id = request.POST.get('formulario_id')
            nome = request.POST.get('nome', '').strip()
            email = request.POST.get('email', '').strip()
            telefone = request.POST.get('telefone', '').strip()
            assunto = request.POST.get('assunto', '').strip()
            mensagem = request.POST.get('mensagem', '').strip()
            
            # Validação básica
            if not formulario_id or not nome or not email or not assunto or not mensagem:
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor, preencha todos os campos obrigatórios.'
                })
            
            # Busca o formulário
            formulario = get_object_or_404(FormularioSnippet, id=formulario_id, ativo=True)
            
            # Função para pegar IP
            def get_client_ip(request):
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                return ip
            
            # Salva no banco
            resposta = RespostaFormulario.objects.create(
                formulario=formulario,
                nome=nome,
                email=email,
                telefone=telefone,
                assunto=assunto,
                mensagem=mensagem,
                ip_address=get_client_ip(request)
            )
            
            # Envia email (opcional - pode comentar se não quiser)
            try:
                send_mail(
                    subject=f"[{formulario.nome}] {assunto}",
                    message=f"""
Nova mensagem recebida através do formulário "{formulario.nome}":

Nome: {nome}
Email: {email}
Telefone: {telefone}
Assunto: {assunto}

Mensagem:
{mensagem}

---
Enviado em: {resposta.data.strftime('%d/%m/%Y às %H:%M')}
IP: {resposta.ip_address}
                    """,
                    from_email='noreply@enap.gov.br',  # Ajuste conforme necessário
                    recipient_list=[formulario.email_destino],
                    fail_silently=True,
                )
            except Exception as email_error:
                print(f"Erro ao enviar email: {email_error}")
                # Não quebra o formulário se der erro no email
                pass
            
            return JsonResponse({
                'success': True,
                'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.'
            })
            
        except FormularioSnippet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Formulário não encontrado ou inativo.'
            })
        except Exception as e:
            print(f"Erro ao salvar formulário: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erro interno. Tente novamente.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido.'
    })







@staff_member_required
def exportar_respostas_csv(request):
    """View para exportar respostas em CSV"""
    
    # Pega filtro de formulário se houver
    formulario_id = request.GET.get('formulario')
    
    if formulario_id:
        respostas = RespostaFormulario.objects.filter(formulario_id=formulario_id)
        filename = f"respostas_formulario_{formulario_id}_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    else:
        respostas = RespostaFormulario.objects.all()
        filename = f"todas_respostas_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    
    # Cria resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # BOM para UTF-8
    response.write('\ufeff')
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow([
        'Formulário',
        'Nome', 
        'Email',
        'Telefone',
        'Assunto',
        'Mensagem',
        'Data/Hora',
        'IP'
    ])
    
    # Dados
    for resposta in respostas:
        writer.writerow([
            resposta.formulario.nome,
            resposta.nome,
            resposta.email,
            resposta.telefone,
            resposta.assunto,
            resposta.mensagem,
            resposta.data.strftime('%d/%m/%Y %H:%M'),
            resposta.ip_address or ''
        ])
    
    return response





@staff_member_required
def exportar_respostas_csv(request):
    """View para exportar respostas em CSV com filtro de formulário"""
    
    # Se é GET, mostra página de escolha
    if request.method == 'GET' and not request.GET.get('formulario'):
        formularios = FormularioSnippet.objects.filter(ativo=True)
        context = {
            'formularios': formularios,
            'total_respostas': RespostaFormulario.objects.count()
        }
        return render(request, 'admin/exportar_respostas.html', context)
    
    # Se tem filtro ou é POST, exporta
    formulario_id = request.GET.get('formulario') or request.POST.get('formulario')
    
    if formulario_id:
        formulario = FormularioSnippet.objects.get(id=formulario_id)
        respostas = RespostaFormulario.objects.filter(formulario_id=formulario_id)
        filename = f"respostas_{formulario.nome.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    else:
        respostas = RespostaFormulario.objects.all()
        filename = f"todas_respostas_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    
    # Cria resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # BOM para UTF-8
    response.write('\ufeff')
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow([
        'Formulário',
        'Nome', 
        'Email',
        'Telefone',
        'Assunto',
        'Mensagem',
        'Data/Hora',
        'IP'
    ])
    
    # Dados
    for resposta in respostas.order_by('-data'):
        writer.writerow([
            resposta.formulario.nome,
            resposta.nome,
            resposta.email,
            resposta.telefone,
            resposta.assunto,
            resposta.mensagem,
            resposta.data.strftime('%d/%m/%Y %H:%M'),
            resposta.ip_address or ''
        ])
    
    return response










@csrf_exempt
@require_http_methods(["POST"])
def chatbot_conversar(request):
    """API endpoint para conversar com o chatbot"""
    try:
        data = json.loads(request.body)
        pergunta = data.get('pergunta', '').strip()
        sessao_id = data.get('sessao_id') or str(uuid.uuid4())
        
        if not pergunta:
            return JsonResponse({
                'erro': 'Pergunta não pode estar vazia'
            }, status=400)
        
        if len(pergunta) > 500:
            return JsonResponse({
                'erro': 'Pergunta muito longa. Máximo 500 caracteres.'
            }, status=400)
        
        # Pega IP do usuário
        user_ip = request.META.get('REMOTE_ADDR')
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            user_ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
        
        # Inicializa serviço do chatbot
        chatbot_service = ChatbotService()
        
        # Gera resposta
        resultado = chatbot_service.gerar_resposta(pergunta, sessao_id, user_ip)
        
        return JsonResponse({
            'resposta': resultado['resposta'],
            'paginas_relacionadas': resultado['paginas'],
            'sessao_id': sessao_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'erro': 'JSON inválido'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'erro': 'Erro interno do servidor'
        }, status=500)


@require_http_methods(["GET"])
def chatbot_config(request):
    """Retorna configurações do chatbot para o frontend"""
    try:
        config = ChatbotConfig.objects.first()
        chatbot_widget = ChatbotWidget.objects.filter(ativo=True).first()
        
        if not config or not config.ativo:
            return JsonResponse({'ativo': False})
        
        return JsonResponse({
            'ativo': True,
            'nome': config.nome,
            'mensagem_boas_vindas': config.mensagem_boas_vindas,
            'widget': {
                'titulo': chatbot_widget.titulo_widget if chatbot_widget else 'Assistente Virtual ENAP',
                'cor_primaria': chatbot_widget.cor_primaria if chatbot_widget else '#0066cc',
                'cor_secundaria': chatbot_widget.cor_secundaria if chatbot_widget else '#ffffff',
                'posicao': chatbot_widget.posicao if chatbot_widget else 'bottom-right',
                'icone': chatbot_widget.icone_chatbot if chatbot_widget else '🤖',
                'mobile': chatbot_widget.mostrar_em_mobile if chatbot_widget else True,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'ativo': False, 
            'erro': 'Erro ao carregar configurações'
        })


@require_http_methods(["GET"]) 
def chatbot_status(request):
    """Status do chatbot para debugging"""
    try:
        from .models import PaginaIndexada, ConversaChatbot
        
        config = ChatbotConfig.objects.first()
        total_paginas = PaginaIndexada.objects.count()
        total_conversas = ConversaChatbot.objects.count()
        
        return JsonResponse({
            'configurado': bool(config and config.api_key_google),
            'ativo': bool(config and config.ativo),
            'paginas_indexadas': total_paginas,
            'total_conversas': total_conversas,
            'modelo_ia': config.modelo_ia if config else None,
        })
        
    except Exception as e:
        return JsonResponse({
            'erro': str(e)
        })
    





def validate_field_ajax(request):
    """Validação AJAX de campos individuais"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        field_type = data.get('field_type')
        value = data.get('value', '')
        
        errors = []
        
        # Validações por tipo
        if field_type == 'email_field' and value:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                errors.append('Email inválido')
        
        elif field_type == 'cpf_field' and value:
            cpf_digits = re.sub(r'[^0-9]', '', value)
            if len(cpf_digits) != 9:
                errors.append('CPF deve ter exatamente 9 dígitos')
        
        elif field_type == 'phone_field' and value:
            phone_digits = re.sub(r'[^0-9]', '', value)
            if len(phone_digits) not in [10, 11]:
                errors.append('Telefone deve ter 10 ou 11 dígitos')
        
        return JsonResponse({
            'valid': len(errors) == 0,
            'errors': errors
        })
    
    except Exception as e:
        return JsonResponse({'error': 'Erro na validação'}, status=400)


@require_POST
@csrf_exempt
def upload_file_ajax(request):
    """Upload de arquivo via AJAX"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'Nenhum arquivo enviado'}, status=400)
        
        uploaded_file = request.FILES['file']
        max_size = int(request.POST.get('max_size', 5)) * 1024 * 1024  # MB para bytes
        allowed_types = request.POST.get('allowed_types', '').split(',')
        
        # Verificar tamanho
        if uploaded_file.size > max_size:
            return JsonResponse({
                'error': f'Arquivo muito grande. Máximo permitido: {max_size//1024//1024}MB'
            }, status=400)
        
        # Verificar tipo
        file_extension = uploaded_file.name.lower().split('.')[-1]
        type_mapping = {
            'pdf': ['pdf'],
            'doc': ['doc', 'docx'],
            'image': ['jpg', 'jpeg', 'png', 'gif'],
            'excel': ['xls', 'xlsx']
        }
        
        allowed_extensions = []
        for allowed_type in allowed_types:
            allowed_extensions.extend(type_mapping.get(allowed_type, []))
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'error': f'Tipo de arquivo não permitido. Permitidos: {", ".join(allowed_extensions)}'
            }, status=400)
        
        # Em produção, salvar o arquivo em storage adequado
        # Por ora, retornamos sucesso com informações do arquivo
        return JsonResponse({
            'success': True,
            'file_info': {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'type': uploaded_file.content_type
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': 'Erro no upload'}, status=500)


def submission_detail(request, submission_id):
    """Visualizar detalhes de uma submissão"""
    submission = get_object_or_404(FormularioSubmission, id=submission_id)
    
    # Verificar permissões (apenas staff ou criador da página)
    if not request.user.is_staff:
        return render(request, '403.html', status=403)
    
    context = {
        'submission': submission,
        'page': submission.page
    }
    
    return render(request, 'home/submission_detail.html', context)


@staff_member_required
def export_submissions(request, page_id):
    """Exportar submissões para CSV"""
    page = get_object_or_404(FormularioPage, id=page_id)
    submissions = FormularioSubmission.objects.filter(page=page).order_by('-submit_time')
    
    # Criar resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="submissoes_{page.slug}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    # Adicionar BOM para Excel reconhecer UTF-8
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Cabeçalhos
    headers = ['Data/Hora', 'IP do Usuário']
    
    # Coletar todos os campos únicos
    all_fields = set()
    for submission in submissions:
        all_fields.update(submission.form_data.keys())
    
    # Ordenar campos por nome
    sorted_fields = sorted(all_fields)
    headers.extend([field.replace('_', ' ').title() for field in sorted_fields])
    
    writer.writerow(headers)
    
    # Dados
    for submission in submissions:
        row = [
            submission.submit_time.strftime('%d/%m/%Y %H:%M:%S'),
            submission.user_ip or 'N/A'
        ]
        
        # Adicionar dados dos campos
        for field in sorted_fields:
            value = submission.form_data.get(field, '')
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            row.append(str(value))
        
        writer.writerow(row)
    
    return response


@staff_member_required
def form_report(request, page_id):
    """Relatório analítico do formulário"""
    page = get_object_or_404(FormularioPage, id=page_id)
    
    # Estatísticas básicas
    total_submissions = FormularioSubmission.objects.filter(page=page).count()
    
    # Submissões por dia (últimos 30 dias)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_submissions = (
        FormularioSubmission.objects
        .filter(page=page, submit_time__gte=thirty_days_ago)
        .extra(select={'day': 'date(submit_time)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    
    # Submissões por hora do dia
    hourly_submissions = (
        FormularioSubmission.objects
        .filter(page=page)
        .extra(select={'hour': 'extract(hour from submit_time)'})
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )
    
    # Análise de campos mais preenchidos
    field_analysis = {}
    submissions = FormularioSubmission.objects.filter(page=page)
    
    for submission in submissions:
        for field_name, value in submission.form_data.items():
            if field_name not in field_analysis:
                field_analysis[field_name] = {
                    'total': 0,
                    'filled': 0,
                    'empty': 0
                }
            
            field_analysis[field_name]['total'] += 1
            if value and str(value).strip():
                field_analysis[field_name]['filled'] += 1
            else:
                field_analysis[field_name]['empty'] += 1
    
    # Calcular percentuais
    for field_name, data in field_analysis.items():
        if data['total'] > 0:
            data['fill_rate'] = (data['filled'] / data['total']) * 100
        else:
            data['fill_rate'] = 0
    
    # Dispositivos mais usados
    device_stats = {
        'desktop': 0,
        'mobile': 0,
        'tablet': 0,
        'unknown': 0
    }
    
    for submission in submissions:
        user_agent = submission.user_agent.lower()
        if 'mobile' in user_agent:
            device_stats['mobile'] += 1
        elif 'tablet' in user_agent:
            device_stats['tablet'] += 1
        elif user_agent:
            device_stats['desktop'] += 1
        else:
            device_stats['unknown'] += 1
    
    context = {
        'page': page,
        'total_submissions': total_submissions,
        'daily_submissions': list(daily_submissions),
        'hourly_submissions': list(hourly_submissions),
        'field_analysis': field_analysis,
        'device_stats': device_stats,
        'recent_submissions': submissions.order_by('-submit_time')[:10]
    }
    
    return render(request, 'home/form_report.html', context)


def get_form_statistics(page):
    """Função auxiliar para obter estatísticas do formulário"""
    submissions = FormularioSubmission.objects.filter(page=page)
    
    stats = {
        'total_submissions': submissions.count(),
        'today_submissions': submissions.filter(
            submit_time__date=timezone.now().date()
        ).count(),
        'week_submissions': submissions.filter(
            submit_time__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'month_submissions': submissions.filter(
            submit_time__gte=timezone.now() - timedelta(days=30)
        ).count(),
    }
    
    # Taxa de conversão (assumindo visitantes únicos por IP)
    unique_ips = submissions.values('user_ip').distinct().count()
    stats['conversion_rate'] = (
        (stats['total_submissions'] / max(unique_ips, 1)) * 100
        if unique_ips > 0 else 0
    )
    
    # Tempo médio de preenchimento (estimativa baseada em dados)
    # Em uma implementação real, você capturaria timestamps de início
    stats['avg_completion_time'] = '3-5 minutos'  # Placeholder
    
    # Campos com maior taxa de abandono
    abandonment_fields = []
    for submission in submissions:
        filled_count = sum(1 for v in submission.form_data.values() if v and str(v).strip())
        total_fields = len(submission.form_data)
        if total_fields > 0:
            completion_rate = (filled_count / total_fields) * 100
            if completion_rate < 80:  # Menos de 80% preenchido
                abandonment_fields.append(submission.form_data.keys())
    
    stats['abandonment_fields'] = abandonment_fields
    
    return stats


# Função para validar dados do formulário de forma mais robusta
def validate_form_data_advanced(page, form_data, files_data=None):
    """Validação avançada dos dados do formulário"""
    errors = {}
    warnings = []
    
    # Obter todos os campos de todas as etapas
    all_fields = []
    for step in page.get_all_steps():
        all_fields.extend(step['fields'])
    
    for block in all_fields:
        if block.block_type in ['info_text', 'divider']:
            continue
            
        field_id = f"{block.block_type}_{block.id}"
        value = form_data.get(field_id, '')
        field_config = block.value
        
        # Validação de campos obrigatórios
        if field_config.get('required', False):
            if not value or (isinstance(value, list) and not any(value)):
                errors[field_id] = 'Este campo é obrigatório'
                continue
        
        # Validações específicas por tipo de campo
        if value:  # Só validar se há valor
            if block.block_type == 'email_field':
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                    errors[field_id] = 'Formato de email inválido'
            
            elif block.block_type == 'cpf_field':
                cpf_clean = re.sub(r'[^0-9]', '', value)
                if len(cpf_clean) != 9:
                    errors[field_id] = 'CPF deve ter exatamente 9 dígitos'
                elif not cpf_clean.isdigit():
                    errors[field_id] = 'CPF deve conter apenas números'
            
            elif block.block_type == 'phone_field':
                phone_clean = re.sub(r'[^0-9]', '', value)
                if len(phone_clean) not in [10, 11]:
                    errors[field_id] = 'Telefone deve ter 10 ou 11 dígitos'
                elif not phone_clean.isdigit():
                    errors[field_id] = 'Telefone deve conter apenas números'
            
            elif block.block_type == 'number_field':
                try:
                    num_value = float(value)
                    min_val = field_config.get('min_value')
                    max_val = field_config.get('max_value')
                    
                    if min_val is not None and num_value < min_val:
                        errors[field_id] = f'Valor deve ser maior ou igual a {min_val}'
                    if max_val is not None and num_value > max_val:
                        errors[field_id] = f'Valor deve ser menor ou igual a {max_val}'
                        
                except ValueError:
                    errors[field_id] = 'Valor deve ser um número válido'
            
            elif block.block_type == 'checkbox_multiple_field':
                min_selections = field_config.get('min_selections', 1)
                if isinstance(value, list) and len(value) < min_selections:
                    errors[field_id] = f'Selecione pelo menos {min_selections} opções'
            
            elif block.block_type == 'textarea_field':
                if len(value) > 5000:  # Limite de caracteres
                    warnings.append(f'Campo "{field_config.get("label", field_id)}" muito longo')
            
            elif block.block_type == 'date_field':
                try:
                    datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    errors[field_id] = 'Data inválida'
        
        # Validação de arquivos
        if block.block_type == 'file_upload_field' and files_data:
            file_field = files_data.get(field_id)
            if file_field:
                max_size = field_config.get('max_size_mb', 5) * 1024 * 1024
                if hasattr(file_field, 'size') and file_field.size > max_size:
                    errors[field_id] = f'Arquivo muito grande (máximo {field_config.get("max_size_mb", 5)}MB)'
                
                # Verificar tipo de arquivo
                allowed_types = field_config.get('allowed_types', [])
                if allowed_types and hasattr(file_field, 'name'):
                    file_ext = file_field.name.lower().split('.')[-1]
                    type_extensions = {
                        'pdf': ['pdf'],
                        'doc': ['doc', 'docx'],
                        'image': ['jpg', 'jpeg', 'png', 'gif'],
                        'excel': ['xls', 'xlsx']
                    }
                    
                    valid_extensions = []
                    for allowed_type in allowed_types:
                        valid_extensions.extend(type_extensions.get(allowed_type, []))
                    
                    if file_ext not in valid_extensions:
                        errors[field_id] = f'Tipo de arquivo não permitido'
    
    return {
        'errors': errors,
        'warnings': warnings,
        'is_valid': len(errors) == 0
    }




def formulario_page_view(request, slug):
    page = get_object_or_404(FormularioPage, slug=slug)

    context = {
        'page': page,
        'all_steps': page.get_all_steps(),  # Certifique-se de que isso está definido no model
        'form_success': request.GET.get('success') == '1'
    }

    return render(request, 'home/formulario_page.html', context)










def custom_404_view(request, exception=None):
    """View personalizada para página 404"""
    
    try:
        # Pegar o site atual
        site = Site.find_for_request(request)
        
        # Pegar a página raiz para links
        root_page = site.root_page
        
        # Contexto para o template
        context = {
            'request': request,
            'site': site,
            'root_page': root_page,
            'page_title': 'Página não encontrada',
        }
        
        return render(request, '404.html', context, status=404)
        
    except:
        # Fallback simples caso algo dê errado
        return render(request, '404.html', {}, status=404)
    











# enap_designsystem/views.py (arquivo existente)

# ... seu código existente ...

# ADICIONAR NO FINAL DO ARQUIVO:

# ===============================================
# ADMIN META TAGS - Function-based views
# ===============================================

import json
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db import transaction

# Imports compatíveis com diferentes versões do Wagtail
try:
    from wagtail.admin import messages as wagtail_messages
    from wagtail.models import Page
except ImportError:
    try:
        from wagtail.wagtailadmin import messages as wagtail_messages
        from wagtail.core.models import Page
    except ImportError:
        # Versão muito antiga
        from wagtail.wagtailadmin.utils import send_notification
        from wagtail.wagtailcore.models import Page
        
        class wagtail_messages:
            @staticmethod
            def success(request, message):
                messages.success(request, message)
            
            @staticmethod
            def error(request, message):
                messages.error(request, message)

@staff_member_required
def meta_tags_manager(request):
    """View principal para gerenciar meta tags"""
    context = get_meta_stats()
    
    if request.method == 'POST':
        return handle_meta_form(request)
    
    return render(request, 'admin/meta_tags_manager.html', context)

@staff_member_required
def preview_meta_changes(request):
    """Preview das mudanças que serão feitas"""
    if request.method != 'POST':
        return redirect('meta_tags_manager')
    
    force_update = request.POST.get('force_update') == 'on'
    page_type_filter = request.POST.get('page_type', '')
    
    pages = get_filtered_pages(page_type_filter)
    
    preview_data = []
    for page in pages[:50]:
        needs_update = page_needs_update(page, force_update)
        
        if needs_update:
            preview_data.append({
                'id': page.id,
                'title': page.title,
                'url': getattr(page, 'url', '#'),
                'page_type': page.__class__.__name__,
                'current_seo': page.seo_title or '(vazio)',
                'current_description': page.search_description or '(vazio)',
                'new_seo': generate_seo_title(page) if not page.seo_title or force_update else page.seo_title,
                'new_description': generate_meta_description(page) if not page.search_description or force_update else page.search_description,
            })
    
    context = get_meta_stats()
    context.update({
        'preview_data': preview_data,
        'total_to_update': len(preview_data),
        'showing_preview': True,
        'force_update': force_update,
        'page_type_filter': page_type_filter,
    })
    
    return render(request, 'admin/meta_tags_manager.html', context)

@staff_member_required
def apply_meta_tags(request):
    """Aplica meta tags em páginas"""
    if request.method != 'POST':
        return redirect('meta_tags_manager')
    
    action_type = request.POST.get('action_type', 'all')
    force_update = request.POST.get('force_update') == 'on'
    page_type_filter = request.POST.get('page_type', '')
    
    try:
        if action_type == 'selected':
            selected_ids = request.POST.getlist('selected_pages')
            if not selected_ids:
                wagtail_messages.warning(request, "⚠️ Nenhuma página selecionada.")
                return redirect('meta_tags_manager')
            pages = Page.objects.filter(id__in=selected_ids)
            force_update = True
        else:
            pages = get_filtered_pages(page_type_filter)
        
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for page in pages:
                try:
                    if update_page_meta(page, force_update):
                        updated_count += 1
                except Exception as e:
                    errors.append(f"Erro na página '{page.title}': {str(e)}")
        
        if updated_count > 0:
            wagtail_messages.success(request, f"✅ Meta tags atualizadas em {updated_count} páginas!")
        else:
            wagtail_messages.info(request, "ℹ️ Nenhuma página precisava de atualização.")
        
        if errors:
            for error in errors[:5]:
                wagtail_messages.error(request, error)
    
    except Exception as e:
        wagtail_messages.error(request, f"❌ Erro durante a aplicação: {str(e)}")
    
    return redirect('meta_tags_manager')

def handle_meta_form(request):
    """Processa diferentes ações do formulário"""
    action = request.POST.get('action')
    
    if action == 'preview':
        return preview_meta_changes(request)
    elif action == 'apply_all':
        request.POST = request.POST.copy()
        request.POST['action_type'] = 'all'
        return apply_meta_tags(request)
    elif action == 'apply_selected':
        request.POST = request.POST.copy()
        request.POST['action_type'] = 'selected'
        return apply_meta_tags(request)
    
    return redirect('meta_tags_manager')

# UTILITY FUNCTIONS
def get_meta_stats():
    """Retorna estatísticas das meta tags"""
    all_pages = Page.objects.live().exclude(depth=1)
    
    pages_without_seo = all_pages.filter(seo_title__isnull=True).count() + \
                       all_pages.filter(seo_title='').count()
    
    pages_without_description = all_pages.filter(search_description__isnull=True).count() + \
                               all_pages.filter(search_description='').count()
    
    pages_with_meta = all_pages.exclude(seo_title__isnull=True)\
                               .exclude(seo_title='')\
                               .exclude(search_description__isnull=True)\
                               .exclude(search_description='').count()
    
    return {
        'total_pages': all_pages.count(),
        'pages_without_seo': pages_without_seo,
        'pages_without_description': pages_without_description,
        'pages_with_meta': pages_with_meta,
    }

def get_filtered_pages(page_type_filter=''):
    """Obtém páginas filtradas"""
    pages = Page.objects.live().exclude(depth=1).order_by('title')
    
    if page_type_filter:
        pages = pages.filter(content_type__model=page_type_filter.lower())
    
    return pages

def page_needs_update(page, force=False):
    """Verifica se página precisa de atualização"""
    if force:
        return True
    return not page.seo_title or not page.search_description

def update_page_meta(page, force=False):
    """Atualiza meta tags de uma página"""
    updated = False
    
    if not page.seo_title or force:
        page.seo_title = generate_seo_title(page)
        updated = True
    
    if not page.search_description or force:
        page.search_description = generate_meta_description(page)
        updated = True
    
    if updated:
        page.save()
    
    return updated

def generate_seo_title(page):
    """Gera SEO title para página"""
    site_name = "ENAP"
    max_length = 60
    
    title = page.title
    available_space = max_length - len(f" | {site_name}")
    
    if len(title) > available_space:
        title = title[:available_space].rsplit(' ', 1)[0] + '...'
    
    return f"{title} | {site_name}"

def generate_meta_description(page):
    """Gera meta description para página"""
    max_length = 160
    
    # Tentar extrair do conteúdo
    description = extract_page_description(page)
    
    if not description:
        description = get_default_description(page)
    
    if len(description) > max_length:
        description = description[:max_length].rsplit(' ', 1)[0] + '...'
    
    return description

def extract_page_description(page):
    """Extrai descrição do conteúdo da página"""
    try:
        content_fields = ['introduction', 'intro', 'resumo', 'descricao', 'body', 'content', 'texto']
        
        for field_name in content_fields:
            if hasattr(page, field_name):
                field_value = getattr(page, field_name)
                if field_value:
                    if hasattr(field_value, 'stream_data') or hasattr(field_value, '__iter__'):
                        text = extract_from_streamfield(field_value)
                        if text:
                            return text
                    else:
                        text = clean_html(str(field_value))
                        if text and len(text.strip()) > 30:
                            return text[:200]
        
        return None
    except Exception:
        return None

def extract_from_streamfield(streamfield):
    """Extrai texto de StreamField"""
    try:
        text_blocks = ['paragraph', 'texto', 'paragrafo', 'rich_text', 'text']
        combined_text = []
        
        for block in streamfield:
            block_type = getattr(block, 'block_type', str(type(block).__name__).lower())
            
            if block_type in text_blocks:
                text = clean_html(str(block.value))
                if text:
                    combined_text.append(text)
            
            if len(' '.join(combined_text)) > 200:
                break
        
        return ' '.join(combined_text) if combined_text else None
        
    except Exception:
        return None

def clean_html(text):
    """Remove tags HTML"""
    if not text:
        return ""
    
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', str(text))
    text = ' '.join(text.split())
    
    return text.strip()

def get_default_description(page):
    """Descrição padrão baseada no tipo"""
    defaults = {
        'HomePage': 'Portal da ENAP - Escola Nacional de Administração Pública',
        'BlogPage': f'Artigo sobre {page.title} no blog da ENAP',
        'EventPage': f'Evento: {page.title} - ENAP',
        'CoursePage': f'Curso {page.title} oferecido pela ENAP',
    }
    
    page_type = page.__class__.__name__
    return defaults.get(page_type, f'{page.title} - ENAP - Escola Nacional de Administração Pública')
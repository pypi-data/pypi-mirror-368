from wagtail import hooks
from django.utils.html import format_html
from django.templatetags.static import static
from enap_designsystem.blocks import ENAPNoticia
from django.urls import reverse



# home/wagtail_hooks.py
import csv
from django.http import HttpResponse
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from .blocks.form import FormularioSubmission, FormularioPage





@hooks.register('insert_global_admin_css')
def global_admin_css():
	return format_html(
		'<link rel="stylesheet" href="{}"><link rel="stylesheet" href="{}">',
		static('css/main_layout.css'),
		static('css/mid_layout.css')
	)

@hooks.register('insert_global_admin_js')
def global_admin_js():
	return format_html(
		'<script src="{}"></script><script src="{}"></script>',
		static('js/main_layout.js'),
		static('js/mid_layout.js')
	)

@hooks.register("before_create_page")
def set_default_author_on_create(request, parent_page, page_class):
	if page_class == ENAPNoticia:
		def set_author(instance):
			instance.author = request.user
		return set_author
	




@hooks.register('register_admin_menu_item')
def register_export_menu_item():
    from wagtail.admin.menu import MenuItem
    
    return MenuItem(
        '📊 Exportar Respostas', 
        '/exportar-respostas/',
        icon_name='download',
        order=1000
    )

# Hook para adicionar botão na página de snippets
@hooks.register('insert_global_admin_js')
def add_export_button():
    return format_html(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Adiciona botão de exportar na página de respostas
            if (window.location.href.includes('/admin/snippets/enap_designsystem/respostaformulario/')) {{
                const header = document.querySelector('.content-wrapper h1, .content-wrapper h2');
                if (header) {{
                    const exportBtn = document.createElement('a');
                    exportBtn.href = '/admin/exportar-respostas/';
                    exportBtn.className = 'button button-small button-secondary';
                    exportBtn.style.marginLeft = '10px';
                    exportBtn.innerHTML = '📊 Exportar CSV';
                    exportBtn.target = '_blank';
                    header.appendChild(exportBtn);
                }}
            }}
        }});
        </script>
        """
    )







# Adicionar item no menu do admin do Wagtail
@hooks.register('register_admin_menu_item')
def register_csv_export_menu():
    return MenuItem(
        'Exportar Submissões', 
        reverse('wagtail_csv_export'), 
        icon_name='download',
        order=200
    )

# Registrar URLs no admin do Wagtail
@hooks.register('register_admin_urls')
def register_csv_urls():
    return [
        path('export-csv/', csv_export_view, name='wagtail_csv_export'),
        path('export-csv/<int:page_id>/', download_csv, name='download_csv'),
    ]

def csv_export_view(request):
    """
    Página para escolher qual formulário exportar
    """
    from django.shortcuts import render
    
    # Pegar formulários do usuário
    formularios = FormularioPage.objects.live()
    if not request.user.is_superuser:
        formularios = formularios.filter(owner=request.user)
    
    # Contar submissões para cada formulário
    formularios_data = []
    for form in formularios:
        count = FormularioSubmission.objects.filter(page=form).count()
        formularios_data.append({
            'form': form,
            'count': count,
            'last_submission': FormularioSubmission.objects.filter(page=form).first()
        })
    
    return render(request, 'wagtailadmin/csv_export.html', {
        'formularios': formularios_data,
    })

def extract_user_info(form_data):
    """
    Extrai informações básicas do usuário dos dados do formulário
    """
    if not form_data:
        return {'nome': '', 'email': '', 'cpf': '', 'telefone': ''}
    
    user_info = {'nome': '', 'email': '', 'cpf': '', 'telefone': ''}
    
    for field_id, value in form_data.items():
        if not value:
            continue
        
        field_lower = field_id.lower()
        
        # Detectar email
        if 'email' in field_lower:
            user_info['email'] = str(value)
        
        # Detectar nome
        elif any(keyword in field_lower for keyword in ['nome', 'name']):
            user_info['nome'] = str(value)
        
        # Detectar CPF
        elif 'cpf' in field_lower:
            user_info['cpf'] = str(value)
        
        # Detectar telefone
        elif any(keyword in field_lower for keyword in ['telefone', 'phone', 'celular']):
            user_info['telefone'] = str(value)
    
    return user_info

def clean_field_name(field_name):
    """
    Limpa o nome do campo para deixar mais legível no CSV
    """
    # Remove prefixos técnicos
    prefixes = [
        'text_field_', 'email_field_', 'phone_field_', 'cpf_field_',
        'textarea_field_', 'dropdown_field_', 'radio_field_',
        'checkbox_field_', 'checkbox_multiple_field_', 'number_field_',
        'date_field_', 'file_upload_field_', 'rating_field_', 'nome_completo_field_'
    ]
    
    clean_name = field_name
    for prefix in prefixes:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
            break
    
    # Remove IDs numéricos
    import re
    clean_name = re.sub(r'_\d+$', '', clean_name)
    
    # Converte para formato legível
    clean_name = clean_name.replace('_', ' ').title()
    
    return clean_name

def download_csv(request, page_id):
    """
    Download do CSV para um formulário específico - COM LINKS DOS ARQUIVOS
    """
    page = get_object_or_404(FormularioPage, id=page_id)
    submissions = FormularioSubmission.objects.filter(page=page).order_by('-submit_time')
    
    # Criar resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="submissoes_{page.slug}_{page.id}.csv"'
    
    # BOM para Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    if not submissions.exists():
        writer.writerow(['Nenhuma submissão encontrada para este formulário'])
        return response
    
    # Coletar todos os campos únicos de todas as submissões
    all_fields = set()
    file_fields = set()  # ← NOVO: campos de arquivo
    
    for submission in submissions:
        if submission.form_data:
            all_fields.update(submission.form_data.keys())
        # ← NOVO: identificar campos de arquivo
        if submission.uploaded_files:
            file_fields.update(submission.uploaded_files.keys())
    
    # Organizar campos - colocar campos importantes primeiro
    priority_fields = []
    other_fields = []
    
    for field in sorted(all_fields):
        field_lower = field.lower()
        if any(keyword in field_lower for keyword in ['nome', 'name', 'email', 'cpf', 'telefone', 'phone']):
            priority_fields.append(field)
        else:
            other_fields.append(field)
    
    sorted_fields = priority_fields + other_fields
    
    # ← NOVO: Criar cabeçalhos incluindo arquivos
    clean_headers = ['Data/Hora', 'IP do Usuário']
    
    # Adicionar campos normais (exceto arquivos)
    for field in sorted_fields:
        if field not in file_fields:
            clean_headers.append(clean_field_name(field))
    
    # Adicionar colunas específicas para arquivos
    for file_field in sorted(file_fields):
        clean_name = clean_field_name(file_field)
        clean_headers.extend([
            f'{clean_name} - Nome do Arquivo',
            f'{clean_name} - Link para Download',
            f'{clean_name} - Tamanho (bytes)'
        ])
    
    writer.writerow(clean_headers)
    
    # Escrever dados das submissões
    for submission in submissions:
        row = [
            submission.submit_time.strftime('%d/%m/%Y %H:%M:%S'),
            submission.user_ip or 'N/A',
        ]
        
        # Adicionar dados dos campos normais (não arquivos)
        for field in sorted_fields:
            if field in file_fields:
                continue  # Pular arquivos aqui
                
            value = submission.form_data.get(field, '') if submission.form_data else ''
            
            # Tratar diferentes tipos de dados
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value if v)
            elif isinstance(value, dict):
                # Se ainda houver dict aqui, converter para string simples
                if 'filename' in value:
                    value = value.get('filename', '')
                else:
                    value = str(value)
            elif value is None:
                value = ''
            else:
                value = str(value)
            
            row.append(value)
        
        # ← NOVO: Adicionar dados dos arquivos
        for file_field in sorted(file_fields):
            # Dados do arquivo no form_data (metadados)
            form_file_data = submission.form_data.get(file_field, {}) if submission.form_data else {}
            
            # Dados do arquivo no uploaded_files (caminho)
            file_path = submission.uploaded_files.get(file_field, '') if submission.uploaded_files else ''
            
            # Dados detalhados no files_data
            file_metadata = submission.files_data.get(file_field, {}) if submission.files_data else {}
            
            # Nome do arquivo
            if isinstance(form_file_data, dict):
                filename = form_file_data.get('filename', '')
            else:
                filename = file_metadata.get('original_name', '')
            
            # Link para download
            if file_path:
                # Construir URL completa
                download_link = f"http://{request.get_host()}/media/{file_path}"
            else:
                download_link = ''
            
            # Tamanho do arquivo
            if isinstance(form_file_data, dict):
                file_size = form_file_data.get('size', '')
            else:
                file_size = file_metadata.get('size', '')
            
            # Adicionar as 3 colunas para este arquivo
            row.extend([
                filename,
                download_link,
                str(file_size) if file_size else ''
            ])
        
        writer.writerow(row)
    
    return response












# enap_designsystem/wagtail_hooks.py

from django.urls import path, reverse

try:
    from wagtail import hooks
    from wagtail.admin.menu import MenuItem
except ImportError:
    from wagtail.wagtailadmin import hooks
    from wagtail.wagtailadmin.menu import MenuItem

@hooks.register('register_admin_urls')
def register_admin_urls():
    """Registra URLs do gerenciador de meta tags"""
    from .views import meta_tags_manager, preview_meta_changes, apply_meta_tags
    
    return [
        path('meta-tags/', meta_tags_manager, name='meta_tags_manager'),
        path('meta-tags/preview/', preview_meta_changes, name='meta_tags_preview'),
        path('meta-tags/apply/', apply_meta_tags, name='meta_tags_apply'),
    ]

@hooks.register('register_admin_menu_item')
def register_meta_tags_menu():
    """Adiciona menu no Wagtail Admin"""
    return MenuItem(
        '🏷️ Meta Tags', 
        reverse('meta_tags_manager'),
        classnames='icon icon-cog',
        order=800
    )
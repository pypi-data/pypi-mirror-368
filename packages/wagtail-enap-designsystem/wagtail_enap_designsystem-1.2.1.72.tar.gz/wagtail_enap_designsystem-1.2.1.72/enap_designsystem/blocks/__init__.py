"""
Ponto de partida do módulo de blocos. Usado para limpar e organizar
os blocos em arquivos individuais baseados na proposta.
Mas fornece todos via o módulo "blocks"
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from .html_blocks import CarouselResponsivoSnippetBlock

from .html_blocks import (
    SimpleDashboardChartBlock,
    SimpleKPICardBlock, 
    SimpleDashboardRowBlock,
    SimpleDashboardContainerBlock,
    HTMLCustomBlock,
    SuapCourseBlock,
    SuapEventsBlock,
    SuapCardCursoBlock,
    GaleriaImagensBlock,
    APISuapCourseBlock,
    TimelineEtapaBlock,
    TimelineBlock,
)

from .semana_blocks import (
    ImageBlock, ParticipanteBlock, StatBlock, GaleriaFotoBlock,
    FAQItemBlock, FAQTabBlock, AtividadeBlock, HospitalityCardBlock,
    VideoBlock, CertificadoBlock, NewsletterBlock, ContatoBlock, FooterBlock, BannerConcurso, MaterialApioBlock, SecaoPatrocinadoresBlock, SecaoApresentacaoBlock, SecaoCategoriasBlock, CronogramaBlock, SecaoPremiosBlock, SecaoFAQBlock, SecaoContatoBlock, MenuNavigationBlock, BannerResultadoBlock,
    PodcastSpotifyBlock,
    SecaoHeroBannerBlock,
    SecaoEstatisticasBlock,
    SecaoCardsBlock,
    SecaoTestemunhosBlock, SecaoTimelineBlock, GaleriaBlock
)
from .html_blocks import OuvidoriaBlock
from .chatbot_blocks import ChatbotBlock
from .html_blocks import EnapSectionCarouselBlock
from .html_blocks import ProgramaCardsBlock
from .content_blocks import BreadcrumbBlock, AutoBreadcrumbBlock
from .layout_blocks import HeroBlock 
from .content_blocks import FormularioBlock
from .layout_blocks import GridBlock, TimelineContainerBlock
from .layout_blocks import DashboardGridWrapperBlock
from .layout_blocks import CardGridBlock
from .layout_blocks import EnapCardGridBlock
from .layout_blocks import EnapBannerBlock
from .layout_blocks import EnapFooterGridBlock
from .layout_blocks import EnapFooterSocialGridBlock
from .layout_blocks import EnapSectionBlock
from enap_designsystem.blocks.base_blocks import CarouselSlideBlock
from enap_designsystem.blocks.base_blocks import ButtonGroupBlock
from enap_designsystem.blocks.base_blocks import CarouselBlock
from .base_blocks import FormularioSnippetBlock, ButtonCenter

from .content_blocks import CardBlock
from .content_blocks import EnapBannerLogoBlock
from .content_blocks import EnapCardBlock
from .content_blocks import EnapAccordionBlock
from .html_blocks import EnapCarouselImagesBlock
from .content_blocks import FeatureImageTextBlock
from .content_blocks import EnapFooterLinkBlock
from .content_blocks import EnapAccordionPanelBlock
from .content_blocks import EnapAccordionBlock
from .content_blocks import EnapNavbarLinkBlock
from .html_blocks import CourseIntroTopicsBlock
from .html_blocks import LegislacaoBlock
from .html_blocks import WhyChooseEnaptBlock
from .html_blocks import CourseFeatureBlock
from .html_blocks import CourseModulesBlock
from .html_blocks import ProcessoSeletivoBlock
from .html_blocks import TeamCarouselBlock
from .html_blocks import TestimonialsCarouselBlock
from .html_blocks import PreviewCoursesBlock
from .html_blocks import SectionCardTitleCenterBlock
from .html_blocks import SectionTabsCardsBlock
from .html_blocks import CTAImagemBlock
from .html_blocks import ContainerInfo
from .html_blocks import ContatoBlock
from .html_blocks import FormContato
from .html_blocks import SobreLinhas
from .html_blocks import EventoBlock
from .html_blocks import HeroAnimadaBlock
from .html_blocks import BannerSearchBlock
from .html_blocks import NavbarComponent
from .html_blocks import SecaoAdesaoBlock
from .html_blocks import TextoImagemBlock
from .html_blocks import CardCursoBlock
from .html_blocks import NavbarBlockv3
from .html_blocks import HeroBlockv3
from .html_blocks import AccordionItemBlock
from .html_blocks import AvisoBlock
from .html_blocks import GalleryModernBlock
from .html_blocks import TeamModern
from .html_blocks import CTA2Block
from .html_blocks import CarrosselCursosBlock
from .html_blocks import CitizenServerBlock
from .html_blocks import ServiceCardsBlock
from .html_blocks import FeatureListBlock
from .html_blocks import CarouselGreen
from .html_blocks import TopicLinksBlock
from .html_blocks import Banner_Image_cta
from .html_blocks import FeatureWithLinksBlock
from .html_blocks import QuoteBlockModern
from .html_blocks import BannerTopicsBlock
from .html_blocks import LocalizacaoBlock
from .html_blocks import CtaDestaqueBlock
from .html_blocks import ENAPNoticia
from .html_blocks import ENAPNoticiaImportada
from .html_blocks import HolofoteCarouselBlock
from .html_blocks import DestaqueMainTabBlock
from .html_blocks import ButtonBlock
from .html_blocks import DownloadBlock
from .html_blocks import ImageBlock
from .html_blocks import ImageLinkBlock
from .html_blocks import QuoteBlock
from .html_blocks import RichTextBlock
from .html_blocks import PageListBlock
from .html_blocks import NewsCarouselBlock
from .html_blocks import CoursesCarouselBlock
from .html_blocks import SuapCourseBlock
from .html_blocks import SuapEventsBlock
from .html_blocks import EventsCarouselBlock
from .html_blocks import DropdownBlock
from .html_blocks import ClientesBlock

HTML_STREAMBLOCKS = [
    ("text", RichTextBlock(icon="cr-font")),
    ("button", ButtonBlock()),
    ("image", ImageBlock()),
    ("image_link", ImageLinkBlock()),
    (
        "html",
        blocks.RawHTMLBlock(
            icon="code",
            form_classname="monospace",
            label=_("HTML"),
        ),
    ),
    ("download", DownloadBlock()),
    ("quote", QuoteBlock()),
]


CONTENT_STREAMBLOCKS = HTML_STREAMBLOCKS + [
    ("accordion", EnapAccordionBlock()),
    ("card", CardBlock()),
    ("card2", EnapCardBlock()),

]

"""
Exemplo de estrutura no codered
    (
        "hero",
        HeroBlock(
            [
                ("row", GridBlock(CONTENT_STREAMBLOCKS)),
                (
                    "cardgrid",
                    CardGridBlock(
                        [
                            ("card", CardBlock()),
                        ]
                    ),
                ),
                (
                    "html",
                    blocks.RawHTMLBlock(
                        icon="code", form_classname="monospace", label=_("HTML")
                    ),
                ),
            ]
        ),
    ),
"""

LAYOUT_STREAMBLOCKS = [
    # ===== DASHBOARD SIMPLES =====
    ("dashboard_chart", SimpleDashboardChartBlock()),
    ("kpi_card", SimpleKPICardBlock()),
    ("dashboard_row", SimpleDashboardRowBlock()),
    ("dashboard_container", SimpleDashboardContainerBlock()),

    ("carousel_responsivo", CarouselResponsivoSnippetBlock()),

    ("suap_courses", SuapCourseBlock()),

    ("banner_logo", EnapBannerLogoBlock()),

    ("suap_events", SuapEventsBlock()),

    ("api_suap_courses", APISuapCourseBlock()),

    ("suap_card_curso", SuapCardCursoBlock()),

    ("galeria_imagens", GaleriaImagensBlock()),


    # DASHBOARD GRID COM TODOS OS COMPONENTES
    (
        "dashboard_section", 
        DashboardGridWrapperBlock([
            ("dashboard_chart", SimpleDashboardChartBlock()),
            ("kpi_card", SimpleKPICardBlock()),
            ("dashboard_row", SimpleDashboardRowBlock()),
            ("dashboard_container", SimpleDashboardContainerBlock()),
            # Pode adicionar outros blocks aqui
            ("heading", blocks.CharBlock(template='blocks/heading.html')),
            ("paragraph", blocks.RichTextBlock(template='blocks/paragraph.html')),
        ])
    ),

    # =============================================================================
    (
        "enap_herobanner", EnapBannerBlock()
    ),
    ('formulario_snippet', FormularioSnippetBlock()),
    
    ("chatbot_ia", ChatbotBlock()),

    ("timeline", TimelineBlock()),

    ("timeline_container", TimelineContainerBlock()),

    ("html", HTMLCustomBlock()),

    ("grid", GridBlock(CONTENT_STREAMBLOCKS + HTML_STREAMBLOCKS)),

    ("cronograma", CronogramaBlock()),

    ('buttoncenter', ButtonCenter()),

    ("edital", LegislacaoBlock()),

    ("ouvidoria", OuvidoriaBlock()),

    ("clientes", ClientesBlock()),

    ("section_carousel", EnapSectionCarouselBlock()),

    ("enap_carousel", EnapCarouselImagesBlock()), 

    ("programa_cards", ProgramaCardsBlock()),

    ('formulario', FormularioBlock()),

    ("cpnu_dashboard", DestaqueMainTabBlock()), 

    ("carousel_option", CarouselSlideBlock()),

    ("cta_destaque", CtaDestaqueBlock()),

    ("loc", LocalizacaoBlock()),

    ('carousel', CarouselBlock()),

    ("navbarflutuante", NavbarBlockv3()),

    ("bannertopics", BannerTopicsBlock()),

    ('QuoteModern', QuoteBlockModern()),

    ('carousel_green', CarouselGreen()),

    ('feature_list_text', FeatureWithLinksBlock()), 

    ('banner_image_cta', Banner_Image_cta()),

    ('hero', HeroBlockv3()),

    ('feature_list', FeatureListBlock()),

    ('service_cards', ServiceCardsBlock()),

    ('topic_links', TopicLinksBlock()),

    ('citizen_server', CitizenServerBlock()),

    ('accordion', AccordionItemBlock()),

    ('aviso', AvisoBlock()),

    ("carrossel_cursos", CarrosselCursosBlock()),

    ('galeria_moderna', GalleryModernBlock()),

    ('team_moderna', TeamModern()),

    ('cta_2', CTA2Block()),

    ("accordion", EnapAccordionBlock()),

    ("section_card_title_center", SectionCardTitleCenterBlock()),

    ("section_tabs_cards", SectionTabsCardsBlock()),

    ('cta_imagem', CTAImagemBlock()),

    ('container_info', ContainerInfo()),

    ('sobre_linhas', SobreLinhas()),

    ('contato', ContatoBlock()),

    ('form_contato', FormContato()),

    ('evento', EventoBlock()),

    ('hero_animada', HeroAnimadaBlock()),

    ('banner_search', BannerSearchBlock()),

    ('navbar', NavbarComponent()),

    ('secao_adesao', SecaoAdesaoBlock()),

    ('texto_imagem', TextoImagemBlock()),

    (
        "enap_herofeature", FeatureImageTextBlock()
    ),
    ("enap_herofeature", FeatureImageTextBlock()),

    ("banner", EnapBannerBlock()),

    ('feature_course', CourseFeatureBlock()),

    ('feature_processo_seletivo', ProcessoSeletivoBlock()),

    ('team_carousel', TeamCarouselBlock()),

    ('testimonials_carousel', TestimonialsCarouselBlock()),

    ('why_choose', WhyChooseEnaptBlock()),

    ("enap_accordion", EnapAccordionBlock()),

    ('button_group', ButtonGroupBlock()),

    ('dropdown', DropdownBlock()),

    ("courses_carousel", CoursesCarouselBlock()),

    ('course_intro_topics', CourseIntroTopicsBlock()),

    ('why_choose', WhyChooseEnaptBlock()),

    ('testimonials_carousel', TestimonialsCarouselBlock()),

    ("preview_courses", PreviewCoursesBlock()),

    ('feature_processo_seletivo', ProcessoSeletivoBlock()),

    ('team_carousel', TeamCarouselBlock()),

    ("breadcrumb", BreadcrumbBlock()),

    ("auto_breadcrumb", AutoBreadcrumbBlock()),

    ('feature_estrutura', CourseModulesBlock()),   
    
    ("hero_banner", SecaoHeroBannerBlock()),           
    ('banner_resultado', BannerResultadoBlock()),      
    ('video', VideoBlock()),                          
    ('estatisticas', SecaoEstatisticasBlock()),        
    ('newsletter', NewsletterBlock()),              
    ('podcast_spotify', PodcastSpotifyBlock()),      
    ('patrocinadores', SecaoPatrocinadoresBlock()),   
    ('contato', SecaoContatoBlock()), 

    ('carousel', CarouselBlock()),
    ("download", DownloadBlock()),
    ("noticias_carousel", NewsCarouselBlock()),
    ("eventos_carousel", EventsCarouselBlock()),

    ("enap_section", EnapSectionBlock([
    ("enap_cardgrid", EnapCardGridBlock([
        ("enap_card", EnapCardBlock()),
        ('card_curso', CardCursoBlock()),
    ])),
    ("enap_accordion", EnapAccordionBlock()),  # Adicionada a vírgula aqui
    ("richtext", RichTextBlock()),  # Corrigida a formatação aqui
    ("button", ButtonBlock()),
    ("image", ImageBlock()),
    ("quote", QuoteBlock()),
    ("preview_courses", PreviewCoursesBlock()),
    ("noticias_carousel", NewsCarouselBlock()),
    ("enap_herofeature", FeatureImageTextBlock()),
    ('feature_course', CourseFeatureBlock()),
    ('feature_estrutura', CourseModulesBlock()),
    ("section_card_title_center", SectionCardTitleCenterBlock()),
    ("accordion", EnapAccordionBlock()),

    ("section_card_title_center", SectionCardTitleCenterBlock()),

    ("section_tabs_cards", SectionTabsCardsBlock()),

    ('cta_imagem', CTAImagemBlock()),

    ('container_info', ContainerInfo()),

    ('sobre_linhas', SobreLinhas()),

    ('contato', ContatoBlock()),

    ('form_contato', FormContato()),

    ('evento', EventoBlock()),

    ('hero_animada', HeroAnimadaBlock()),

    ('banner_search', BannerSearchBlock()),

    ('texto_imagem', TextoImagemBlock()),

    ('hero', HeroBlockv3()),

    ('accordion', AccordionItemBlock()),
    
    ('aviso', AvisoBlock()),

    ('galeria_moderna', GalleryModernBlock()),

    ('team_moderna', TeamModern()),

    ('cta_2', CTA2Block()),
])
    )
]




DYNAMIC_CARD_STREAMBLOCKS = [
    (
        "enap_section", EnapSectionBlock([
            ("enap_cardgrid", EnapCardGridBlock([
                ("enap_card", EnapCardBlock()),
            ])),
            ('holofote_carousel', HolofoteCarouselBlock()),
        ])
    ),

    ("page_list", PageListBlock()),
]


CARD_CARDS_STREAMBLOCKS = [
    (
        "enap_section", EnapSectionBlock([
            ("enap_cardgrid", EnapCardGridBlock([
                ("enap_card", EnapCardBlock()),
            ]))
        ])
    )
]




SEMANA_INOVACAO_STREAMBLOCKS = [
    
    ("hero_banner", SecaoHeroBannerBlock()),
    ('galeria_fotos', GaleriaBlock()),
    ("banner_concurso", BannerConcurso()),
    ("secao_apresentacao", SecaoApresentacaoBlock()),
    ("secao_categorias", SecaoCategoriasBlock()),
    ("material_apoio", MaterialApioBlock()),
    ("cronograma", CronogramaBlock()),
    ("secao_premios", SecaoPremiosBlock()),
    ("secao_faq", SecaoFAQBlock()),
    ("secao_contato", SecaoContatoBlock()),
    ("banner_resultado", BannerResultadoBlock()),
    ("podcast_spotify", PodcastSpotifyBlock()),
    ("secao_hero_banner", SecaoHeroBannerBlock()),
    ("secao_apresentacao", SecaoApresentacaoBlock()),
    ("secao_cards", SecaoCardsBlock()),
    ("secao_testemunhos", SecaoTestemunhosBlock()),
    ("secao_estatisticas", SecaoEstatisticasBlock()),
    ("secao_timeline", SecaoTimelineBlock()),
    ("secao_contato", SecaoContatoBlock()),
    ("newsletter", NewsletterBlock()),
    ("hero_banner", SecaoHeroBannerBlock()),
    ("cronograma", CronogramaBlock()),
    ("participantes", ParticipanteBlock()),
    ("atividades", AtividadeBlock()),
    ("hospitality", HospitalityCardBlock()),
    ("galeria", GaleriaFotoBlock()),
    ("certificado", CertificadoBlock()),
    ("image_block", ImageBlock()),
    ("participante", ParticipanteBlock()),
    ("stat_block", StatBlock()),
    ("galeria_foto", GaleriaFotoBlock()),
    ("video_block", VideoBlock()),
    ("certificado", CertificadoBlock()),
    ("newsletter", NewsletterBlock()),
    ("contato", ContatoBlock()),
    ("footer_block", FooterBlock()),
    
    # =============================================================================
    # COMPONENTES DE FAQ E NAVEGAÇÃO
    # =============================================================================
    ("faq_item", FAQItemBlock()),
    ("faq_tab", FAQTabBlock()),
    ("menu_navigation", MenuNavigationBlock()),
    
    # =============================================================================
    # COMPONENTES DE ATIVIDADES E EVENTOS
    # =============================================================================
    ("atividade", AtividadeBlock()),
    ("hospitality_card", HospitalityCardBlock()),
    
    # =============================================================================
    # SEMANA DE INOVAÇÃO - COMPONENTES ESPECIALIZADOS
    # =============================================================================
    ("banner_concurso", BannerConcurso()),
    ("material_apoio", MaterialApioBlock()),
    ("secao_patrocinadores", SecaoPatrocinadoresBlock()),
    ("secao_apresentacao", SecaoApresentacaoBlock()),
    ("secao_categorias", SecaoCategoriasBlock()),
    ("cronograma", CronogramaBlock()),
    ("secao_premios", SecaoPremiosBlock()),
    ("secao_faq", SecaoFAQBlock()),
    ("secao_contato", SecaoContatoBlock()),
    ("banner_resultado", BannerResultadoBlock()),
    ("podcast_spotify", PodcastSpotifyBlock()),
    
    # =============================================================================
    # COMPONENTES DE LAYOUT E ORGANIZAÇÃO
    # =============================================================================
    ("secao_hero_banner", SecaoHeroBannerBlock()),
    ("secao_estatisticas", SecaoEstatisticasBlock()),
    ("secao_cards", SecaoCardsBlock()),
    ("secao_testemunhos", SecaoTestemunhosBlock()),
    ("secao_timeline", SecaoTimelineBlock()),
    
    # =============================================================================
    # COMPONENTES PARA SNIPPETS E REUTILIZAÇÃO
    # =============================================================================
    # Nota: Estes são snippets registrados, mas podem ser usados em StreamFields
    # através de SnippetChooserBlock quando necessário
    
    # =============================================================================
    # SEÇÃO EXEMPLO DE USO ANINHADO
    # =============================================================================
    (
        "enap_section", 
        EnapSectionBlock([
            ("enap_cardgrid", EnapCardGridBlock([
                ("enap_card", EnapCardBlock()),
                ("participante_card", ParticipanteBlock()),
                ("stat_card", StatBlock()),
                ("hospitality_card", HospitalityCardBlock()),
            ]))
        ])
    ),
    
    # =============================================================================
    # COMPONENTES DE ALTA COMPLEXIDADE
    # =============================================================================
    (
        "semana_inovacao_completa",
        SecaoHeroBannerBlock()  # Pode conter outros blocks aninhados
    ),
    
    (
        "material_apoio_completo",
        MaterialApioBlock()  # Com botões e configurações avançadas
    ),
    
    (
        "banner_resultado_completo", 
        BannerResultadoBlock()  # Com StreamField de botões flexíveis
    ),
    
    # =============================================================================
    # COMPONENTES PARA DIFERENTES CONTEXTOS
    # =============================================================================
    
    # Para páginas de eventos
    ("cronograma_evento", CronogramaBlock()),
    ("secao_premios_evento", SecaoPremiosBlock()),
    
    # Para páginas institucionais
    ("secao_apresentacao_institucional", SecaoApresentacaoBlock()),
    ("secao_testemunhos_institucional", SecaoTestemunhosBlock()),
    
    # Para páginas de conteúdo
    ("secao_cards_conteudo", SecaoCardsBlock()),
    ("secao_timeline_conteudo", SecaoTimelineBlock()),
    
    # Para podcasts e mídia
    ("podcast_spotify_completo", PodcastSpotifyBlock()),
    ("video_completo", VideoBlock()),
    
    # =============================================================================
    # COMPONENTES DE FORMULÁRIOS E INTERAÇÃO
    # =============================================================================
    ("formulario_contato", SecaoContatoBlock()),
    ("newsletter_inscricao", NewsletterBlock()),
    
    # =============================================================================
    # COMPONENTES DE BRANDING E IDENTIDADE
    # =============================================================================
    ("banner_branded", BannerConcurso()),
    ("secao_patrocinadores_branded", SecaoPatrocinadoresBlock()),
    
    # =============================================================================
    # COMPONENTES PARA DIFERENTES TIPOS DE PÁGINA
    # =============================================================================
    
    # Para home pages
    ("hero_home", SecaoHeroBannerBlock()),
    ("estatisticas_home", SecaoEstatisticasBlock()),
    ("testemunhos_home", SecaoTestemunhosBlock()),
    
    # Para páginas de sobre
    ("apresentacao_sobre", SecaoApresentacaoBlock()),
    ("timeline_sobre", SecaoTimelineBlock()),
    
    # Para páginas de FAQ
    ("faq_completo", SecaoFAQBlock()),
    ("faq_simples", FAQTabBlock()),
    
    # Para páginas de contato
    ("contato_completo", SecaoContatoBlock()),
    ("contato_simples", ContatoBlock()),
]

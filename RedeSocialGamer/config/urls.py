from django.contrib import admin
from django.urls import include, path
from app import views
from app.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', views.inicio, name='inicio'),

    path('cadastro/', views.cadastro, name='cadastro'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path(
        'perfil/<int:id>/',
        views.perfil,
        name='perfil'
    ),
    path(
        'jogadores/',
        views.buscar_jogadores,
        name='buscar_jogadores'
),

    path(
        'publicacao/criar/',
        views.criar_publicacao,
        name='criar_publicacao'
    ),

    path(
        'publicacao/<int:id>/excluir/',
        views.excluir_publicacao,
        name='excluir_publicacao'
    ),

    path(
        'publicacao/<int:id>/curtir/',
        views.curtir,
        name='curtir'
    ),

    path(
        'publicacao/<int:id>/comentar/',
        views.comentar,
        name='comentar'
    ),

    path(
        'jogos/',
        views.lista_jogos,
        name='lista_jogos'
    ),

    path(
        'jogo/<int:jogo_id>/favoritar/',
        views.adicionar_favorito,
        name='adicionar_favorito'
    ),

    path(
        'jogo/<int:jogo_id>/remover-favorito/',
        views.remover_favorito,
        name='remover_favorito'
    ),

    path(
        'amizade/<int:perfil_id>/enviar/',
        views.enviar_amizade,
        name='enviar_amizade'
    ),

    path(
        'amizade/<int:amizade_id>/aceitar/',
        views.aceitar_amizade,
        name='aceitar_amizade'
    ),

    path(
        'amizade/<int:amizade_id>/recusar/',
        views.recusar_amizade,
        name='recusar_amizade'
    ),

    path(
        'ranking/',
        views.ranking,
        name='ranking'
    ),
    path(
        'amizade/<int:perfil_id>/enviar/',
        views.enviar_amizade,
        name='enviar_amizade'
    ),

    path(
        'amizade/<int:amizade_id>/aceitar/',
        views.aceitar_amizade,
        name='aceitar_amizade'
    ),

    path(
        'amizade/<int:amizade_id>/recusar/',
        views.recusar_amizade,
        name='recusar_amizade'
    ),
    path(
        'jogos/cadastrar/', 
        views.cadastrar_jogo, 
        name='cadastrar_jogo'),
    path(
        'amizade/<int:amizade_id>/cancelar/',
        views.cancelar_amizade,
        name='cancelar_amizade'
    ),

    path(
        'perfil/bio/atualizar/',
        views.atualizar_bio,
        name='atualizar_bio'
    ),

    path(
        'perfil/bio/excluir/',
        views.excluir_bio,
        name='excluir_bio'
    ),
    path(
        'publicacao/<int:id>/editar/',
        views.editar_publicacao,
        name='editar_publicacao'
    ),
    path(
    'jogo/<int:jogo_id>/editar/',
    views.editar_jogo,
    name='editar_jogo'
),

    path(
        'jogo/<int:jogo_id>/excluir/',
        views.excluir_jogo,
        name='excluir_jogo'
    ),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

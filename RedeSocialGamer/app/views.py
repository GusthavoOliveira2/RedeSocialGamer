
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from .models import (
    Perfil,
    Jogo,
    JogoFavorito,
    Amizade,
    Publicacao,
    Comentario,
    Curtida
)


# FUNÇÃO AUXILIAR
def obter_perfil(usuario):
    perfil, criado = Perfil.objects.get_or_create(usuario=usuario)
    return perfil


# PÁGINA INICIAL
def inicio(request):
    publicacoes = Publicacao.objects.all().annotate(
        total_curtidas=Count('curtidas', distinct=True),
        total_comentarios=Count('comentarios', distinct=True)
    ).order_by(
        '-total_curtidas',
        '-total_comentarios',
        '-data_criacao'
    )

    return render(request, 'inicio.html', {
        'publicacoes': publicacoes
    })


# CADASTRO
def cadastro(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha')
        foto = request.FILES.get('foto')

        if not username or not senha:
            return render(request, 'cadastro.html', {
                'erro': 'Preencha o usuário e a senha.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'cadastro.html', {
                'erro': 'Este nome de usuário já existe.'
            })

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )

        perfil = obter_perfil(usuario)
        perfil.foto = foto
        perfil.save()

        return redirect('login')

    return render(request, 'cadastro.html')


# LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        senha = request.POST.get('senha', '')

        usuario = authenticate(
            request,
            username=username,
            password=senha
        )

        if usuario is not None:
            login(request, usuario)
            obter_perfil(usuario)
            return redirect('inicio')

        return render(request, 'login.html', {
            'erro': 'Usuário ou senha incorretos.'
        })

    return render(request, 'login.html')


# LOGOUT
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# PERFIL
@login_required
def perfil(request, id):
    jogador = get_object_or_404(Perfil, id=id)

    publicacoes = jogador.publicacoes.all().order_by('-data_criacao')
    jogos_favoritos = jogador.jogos_favoritos.all()

    solicitacoes = Amizade.objects.filter(
        destinatario=jogador,
        status='pendente'
    )

    amizades_enviadas = Amizade.objects.filter(
        solicitante=jogador,
        status='aceita'
    ).select_related('destinatario__usuario')

    amizades_recebidas = Amizade.objects.filter(
        destinatario=jogador,
        status='aceita'
    ).select_related('solicitante__usuario')

    amigos_dict = {}

    for amizade in amizades_enviadas:
        amigo = amizade.destinatario
        amigos_dict[amigo.id] = amigo

    for amizade in amizades_recebidas:
        amigo = amizade.solicitante
        amigos_dict[amigo.id] = amigo

    amigos = list(amigos_dict.values())

    return render(request, 'perfil.html', {
        'jogador': jogador,
        'publicacoes': publicacoes,
        'jogos_favoritos': jogos_favoritos,
        'solicitacoes': solicitacoes,
        'amigos': amigos
    })


# CRIAR PUBLICAÇÃO
@login_required
@require_POST
def criar_publicacao(request):
    perfil_atual = obter_perfil(request.user)

    titulo = request.POST.get('titulo', '').strip()
    texto = request.POST.get('texto', '').strip()
    imagem = request.FILES.get('imagem')

    if not titulo or not texto:
        messages.error(
            request,
            'Preencha o título e o texto da publicação.'
        )
        return redirect('inicio')

    Publicacao.objects.create(
        autor=perfil_atual,
        titulo=titulo,
        texto=texto,
        imagem=imagem
    )

    perfil_atual.adicionar_pontos(10)

    messages.success(request, 'Publicação criada com sucesso!')
    return redirect('inicio')


# EXCLUIR PUBLICAÇÃO
@login_required
@require_POST
def excluir_publicacao(request, id):
    perfil_atual = obter_perfil(request.user)

    publicacao = get_object_or_404(Publicacao, id=id)

    if (
        publicacao.autor != perfil_atual
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            'Você não tem permissão para excluir esta publicação.'
        )
        return redirect('inicio')

    publicacao.delete()

    messages.success(request, 'Publicação excluída com sucesso!')
    return redirect('inicio')


# EDITAR PUBLICAÇÃO
@login_required
@require_POST
def editar_publicacao(request, id):
    perfil_atual = obter_perfil(request.user)

    publicacao = get_object_or_404(Publicacao, id=id)

    if (
        publicacao.autor != perfil_atual
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            'Você não tem permissão para editar esta publicação.'
        )
        return redirect('inicio')

    titulo = request.POST.get('titulo', '').strip()
    texto = request.POST.get('texto', '').strip()
    imagem = request.FILES.get('imagem')

    if not titulo or not texto:
        messages.error(request, 'Preencha o título e o texto.')
        return redirect('inicio')

    publicacao.titulo = titulo
    publicacao.texto = texto

    if imagem:
        publicacao.imagem = imagem

    publicacao.save()

    messages.success(request, 'Publicação editada com sucesso!')
    return redirect('inicio')


# COMENTAR
@login_required
@require_POST
def comentar(request, id):
    publicacao = get_object_or_404(Publicacao, id=id)

    texto = (
        request.POST.get('texto')
        or request.POST.get('conteudo', '')
    ).strip()

    if texto:
        perfil_atual = obter_perfil(request.user)

        Comentario.objects.create(
            publicacao=publicacao,
            autor=perfil_atual,
            texto=texto
        )

        perfil_atual.adicionar_pontos(3)

    return redirect('perfil', id=publicacao.autor.id)


# CURTIR
@login_required
@require_POST
def curtir(request, id):
    publicacao = get_object_or_404(Publicacao, id=id)
    perfil_atual = obter_perfil(request.user)

    curtida = Curtida.objects.filter(
        publicacao=publicacao,
        usuario=perfil_atual
    ).first()

    if curtida:
        curtida.delete()

        publicacao.autor.pontos = max(
            0,
            publicacao.autor.pontos - 5
        )

        publicacao.autor.nivel = (
            publicacao.autor.pontos // 100
        ) + 1

        publicacao.autor.save()

    else:
        Curtida.objects.create(
            publicacao=publicacao,
            usuario=perfil_atual
        )

        publicacao.autor.adicionar_pontos(5)

    return redirect('perfil', id=publicacao.autor.id)


# ADICIONAR FAVORITO
@login_required
def adicionar_favorito(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)
    perfil_atual = obter_perfil(request.user)

    favorito, criado = JogoFavorito.objects.get_or_create(
        perfil=perfil_atual,
        jogo=jogo
    )

    if criado:
        perfil_atual.adicionar_pontos(2)

    return redirect('perfil', id=perfil_atual.id)


# REMOVER FAVORITO
@login_required
@require_POST
def remover_favorito(request, jogo_id):
    perfil_atual = obter_perfil(request.user)
    jogo = get_object_or_404(Jogo, id=jogo_id)

    JogoFavorito.objects.filter(
        perfil=perfil_atual,
        jogo=jogo
    ).delete()

    origem = request.POST.get('origem', 'jogos')

    if origem == 'perfil':
        return redirect('perfil', id=perfil_atual.id)

    return redirect('lista_jogos')


# ENVIAR AMIZADE
@login_required
def enviar_amizade(request, perfil_id):
    solicitante = obter_perfil(request.user)

    destinatario = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    if solicitante == destinatario:
        messages.error(
            request,
            'Você não pode adicionar a si mesmo.'
        )
        return redirect('perfil', id=perfil_id)

    amizade_existente = Amizade.objects.filter(
        Q(
            solicitante=solicitante,
            destinatario=destinatario
        ) |
        Q(
            solicitante=destinatario,
            destinatario=solicitante
        ),
        status__in=['pendente', 'aceita']
    ).exists()

    if amizade_existente:
        messages.info(
            request,
            'Já existe um pedido de amizade ou vocês já são amigos!'
        )
    else:
        Amizade.objects.create(
            solicitante=solicitante,
            destinatario=destinatario,
            status='pendente'
        )

        messages.success(
            request,
            'Pedido de amizade enviado com sucesso!'
        )

    return redirect('perfil', id=perfil_id)


# ACEITAR AMIZADE
@login_required
@require_POST
def aceitar_amizade(request, amizade_id):
    perfil_atual = obter_perfil(request.user)

    amizade = get_object_or_404(
        Amizade,
        id=amizade_id
    )

    if (
        amizade.destinatario == perfil_atual
        or request.user.is_superuser
    ):
        if amizade.status == 'pendente':
            amizade.status = 'aceita'
            amizade.save()

            amizade.destinatario.adicionar_pontos(5)
            amizade.solicitante.adicionar_pontos(5)

        return redirect('perfil', id=amizade.destinatario.id)

    messages.error(request, 'Você não pode aceitar esta solicitação.')
    return redirect('perfil', id=perfil_atual.id)


# RECUSAR AMIZADE
@login_required
@require_POST
def recusar_amizade(request, amizade_id):
    perfil_atual = obter_perfil(request.user)

    amizade = get_object_or_404(
        Amizade,
        id=amizade_id
    )

    if (
        amizade.destinatario == perfil_atual
        or request.user.is_superuser
    ):
        amizade.status = 'recusada'
        amizade.save()

        return redirect('perfil', id=amizade.destinatario.id)

    messages.error(request, 'Você não pode recusar esta solicitação.')
    return redirect('perfil', id=perfil_atual.id)


# CANCELAR OU REMOVER AMIZADE
@login_required
@require_POST
def cancelar_amizade(request, amizade_id):
    perfil_atual = obter_perfil(request.user)

    amizade = get_object_or_404(
        Amizade,
        id=amizade_id
    )

    if (
        amizade.solicitante == perfil_atual
        or amizade.destinatario == perfil_atual
        or request.user.is_superuser
    ):
        if request.user.is_superuser:
            perfil_id = amizade.destinatario.id
        elif amizade.solicitante == perfil_atual:
            perfil_id = amizade.destinatario.id
        else:
            perfil_id = amizade.solicitante.id

        amizade.delete()

        return redirect('perfil', id=perfil_id)

    messages.error(request, 'Você não pode remover esta amizade.')
    return redirect('perfil', id=perfil_atual.id)


# RANKING
@login_required
def ranking(request):
    jogadores = Perfil.objects.all().order_by('-pontos')

    return render(request, 'ranking.html', {
        'jogadores': jogadores
    })


# LISTA DE JOGOS
@login_required
def lista_jogos(request):
    busca = request.GET.get('busca', '').strip()

    jogos = Jogo.objects.all().order_by('nome')

    if busca:
        jogos = jogos.filter(
            Q(nome__icontains=busca) |
            Q(genero__icontains=busca)
        )

    perfil_atual = obter_perfil(request.user)

    favoritos_ids = JogoFavorito.objects.filter(
        perfil=perfil_atual
    ).values_list('jogo_id', flat=True)

    return render(request, 'jogos.html', {
        'jogos': jogos,
        'favoritos_ids': favoritos_ids,
        'busca': busca
    })


# BUSCAR JOGADORES
@login_required
def buscar_jogadores(request):
    busca = request.GET.get('busca', '').strip()
    perfil_atual = obter_perfil(request.user)

    jogadores = Perfil.objects.exclude(
        id=perfil_atual.id
    )

    if busca:
        jogadores = jogadores.filter(
            usuario__username__icontains=busca
        )

    return render(request, 'buscar_jogadores.html', {
        'jogadores': jogadores,
        'busca': busca
    })


# CADASTRAR JOGO
@login_required
@require_POST
def cadastrar_jogo(request):
    perfil_atual = obter_perfil(request.user)

    nome = request.POST.get('nome', '').strip()
    genero = request.POST.get('genero', '').strip()
    descricao = request.POST.get('descricao', '').strip()
    capa = request.FILES.get('capa')

    if not nome or not genero:
        messages.error(
            request,
            'Preencha o nome e o gênero do jogo.'
        )
        return redirect('lista_jogos')

    if Jogo.objects.filter(nome__iexact=nome).exists():
        messages.error(
            request,
            f'O jogo "{nome}" já está cadastrado na comunidade!'
        )
        return redirect('lista_jogos')

    Jogo.objects.create(
        nome=nome,
        genero=genero,
        descricao=descricao,
        capa=capa,
        cadastrado_por=perfil_atual
    )

    messages.success(
        request,
        f'Jogo "{nome}" cadastrado com sucesso!'
    )

    return redirect('lista_jogos')


# EDITAR JOGO
@login_required
@require_POST
def editar_jogo(request, jogo_id):
    perfil_atual = obter_perfil(request.user)
    jogo = get_object_or_404(Jogo, id=jogo_id)

    if (
        jogo.cadastrado_por != perfil_atual
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            'Você não tem permissão para editar este jogo.'
        )
        return redirect('lista_jogos')

    nome = request.POST.get('nome', '').strip()
    genero = request.POST.get('genero', '').strip()
    descricao = request.POST.get('descricao', '').strip()
    capa = request.FILES.get('capa')

    if not nome or not genero:
        messages.error(
            request,
            'Preencha o nome e o gênero do jogo.'
        )
        return redirect('lista_jogos')

    jogo_existente = Jogo.objects.filter(
        nome__iexact=nome
    ).exclude(id=jogo.id).exists()

    if jogo_existente:
        messages.error(
            request,
            'Já existe outro jogo com esse nome.'
        )
        return redirect('lista_jogos')

    jogo.nome = nome
    jogo.genero = genero
    jogo.descricao = descricao

    if capa:
        jogo.capa = capa

    jogo.save()

    messages.success(
        request,
        'Jogo atualizado com sucesso!'
    )

    return redirect('lista_jogos')


# EXCLUIR JOGO
@login_required
@require_POST
def excluir_jogo(request, jogo_id):
    perfil_atual = obter_perfil(request.user)
    jogo = get_object_or_404(Jogo, id=jogo_id)

    if (
        jogo.cadastrado_por != perfil_atual
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            'Você não tem permissão para excluir este jogo.'
        )
        return redirect('lista_jogos')

    nome = jogo.nome
    jogo.delete()

    messages.success(
        request,
        f'O jogo "{nome}" foi excluído com sucesso!'
    )

    return redirect('lista_jogos')


# ATUALIZAR BIOGRAFIA
@login_required
@require_POST
def atualizar_bio(request):
    perfil_atual = obter_perfil(request.user)

    perfil_atual.bio = request.POST.get('bio', '').strip()
    perfil_atual.save(update_fields=['bio'])

    return redirect('perfil', id=perfil_atual.id)


# EXCLUIR BIOGRAFIA
@login_required
@require_POST
def excluir_bio(request):
    perfil_atual = obter_perfil(request.user)

    perfil_atual.bio = ''
    perfil_atual.save(update_fields=['bio'])

    return redirect('perfil', id=perfil_atual.id)

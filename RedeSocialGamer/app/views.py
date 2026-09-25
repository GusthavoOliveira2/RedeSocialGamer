from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import *

def inicio(request):
    publicacoes = Publicacao.objects.all().order_by('-data_criacao')

    return render(request, 'inicio.html', {
        'publicacoes': publicacoes
    })


def cadastro(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        senha = request.POST['senha']

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )

        Perfil.objects.create(
            usuario=usuario
        )

        return redirect('login')

    return render(request, 'cadastro.html')


def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        senha = request.POST['senha']

        usuario = authenticate(
            request,
            username=username,
            password=senha
        )

        if usuario is not None:
            login(request, usuario)

            return redirect('inicio')

    return render(request, 'login.html')


@login_required
def logout_view(request):

    logout(request)

    return redirect('login')


@login_required
def perfil(request, id):

    jogador = get_object_or_404(
        Perfil,
        id=id
    )

    publicacoes = jogador.publicacoes.all().order_by(
        '-data_criacao'
    )

    jogos_favoritos = jogador.jogos_favoritos.all()

    solicitacoes = Amizade.objects.filter(
        destinatario=jogador,
        status='pendente'
    )

    amigos_enviados = Amizade.objects.filter(
        solicitante=jogador,
        status='aceita'
    )

    amigos_recebidos = Amizade.objects.filter(
        destinatario=jogador,
        status='aceita'
    )

    return render(request, 'perfil.html', {
        'jogador': jogador,
        'publicacoes': publicacoes,
        'jogos_favoritos': jogos_favoritos,
        'solicitacoes': solicitacoes,
        'amigos_enviados': amigos_enviados,
        'amigos_recebidos': amigos_recebidos
    })


@login_required
def criar_publicacao(request):

    perfil = request.user.perfil

    if request.method == 'POST':

        titulo = request.POST['titulo']
        texto = request.POST['texto']
        imagem = request.FILES.get('imagem')

        Publicacao.objects.create(
            autor=perfil,
            titulo=titulo,
            texto=texto,
            imagem=imagem
        )

        perfil.adicionar_pontos(10)

        return redirect('inicio')

    return render(request, 'criar_publicacao.html')


@login_required
def excluir_publicacao(request, id):

    publicacao = get_object_or_404(
        Publicacao,
        id=id
    )

    if publicacao.autor == request.user.perfil:

        publicacao.delete()

    return redirect('inicio')


@login_required
def comentar(request, id):

    publicacao = get_object_or_404(
        Publicacao,
        id=id
    )

    if request.method == 'POST':

        texto = request.POST['texto']

        Comentario.objects.create(
            publicacao=publicacao,
            autor=request.user.perfil,
            texto=texto
        )

        request.user.perfil.adicionar_pontos(3)

    return redirect('inicio')


@login_required
def curtir(request, id):

    publicacao = get_object_or_404(
        Publicacao,
        id=id
    )

    perfil = request.user.perfil

    curtida = Curtida.objects.filter(
        publicacao=publicacao,
        usuario=perfil
    ).first()

    if curtida:

        curtida.delete()

        publicacao.autor.pontos -= 5

        if publicacao.autor.pontos < 0:
            publicacao.autor.pontos = 0

        publicacao.autor.nivel = (
            publicacao.autor.pontos // 100
        ) + 1

        publicacao.autor.save()

    else:

        Curtida.objects.create(
            publicacao=publicacao,
            usuario=perfil
        )

        publicacao.autor.adicionar_pontos(5)

    return redirect('inicio')


@login_required
def adicionar_favorito(request, jogo_id):

    jogo = get_object_or_404(
        Jogo,
        id=jogo_id
    )

    perfil = request.user.perfil

    favorito = JogoFavorito.objects.filter(
        perfil=perfil,
        jogo=jogo
    ).first()

    if not favorito:

        JogoFavorito.objects.create(
            perfil=perfil,
            jogo=jogo
        )

        perfil.adicionar_pontos(2)

    return redirect('perfil', id=perfil.id)


@login_required
def remover_favorito(request, jogo_id):

    jogo = get_object_or_404(
        Jogo,
        id=jogo_id
    )

    perfil = request.user.perfil

    favorito = JogoFavorito.objects.filter(
        perfil=perfil,
        jogo=jogo
    ).first()

    if favorito:

        favorito.delete()

        perfil.pontos -= 2

        if perfil.pontos < 0:
            perfil.pontos = 0

        perfil.nivel = (
            perfil.pontos // 100
        ) + 1

        perfil.save()

    return redirect('perfil', id=perfil.id)


@login_required
def enviar_amizade(request, perfil_id):

    destinatario = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    solicitante = request.user.perfil

    if solicitante != destinatario:

        amizade_existente = Amizade.objects.filter(
            solicitante=solicitante,
            destinatario=destinatario
        ).exists()

        if not amizade_existente:

            Amizade.objects.create(
                solicitante=solicitante,
                destinatario=destinatario
            )

    return redirect('perfil', id=perfil_id)


@login_required
def aceitar_amizade(request, amizade_id):

    amizade = get_object_or_404(
        Amizade,
        id=amizade_id
    )

    if amizade.destinatario == request.user.perfil:

        amizade.status = 'aceita'
        amizade.save()

        amizade.destinatario.adicionar_pontos(5)
        amizade.solicitante.adicionar_pontos(5)

    return redirect('perfil', id=request.user.perfil.id)


@login_required
def recusar_amizade(request, amizade_id):

    amizade = get_object_or_404(
        Amizade,
        id=amizade_id
    )

    if amizade.destinatario == request.user.perfil:

        amizade.status = 'recusada'
        amizade.save()

    return redirect('perfil', id=request.user.perfil.id)


@login_required
def ranking(request):

    jogadores = Perfil.objects.all().order_by(
        '-pontos'
    )

    return render(request, 'ranking.html', {
        'jogadores': jogadores
    })


@login_required
def lista_jogos(request):

    jogos = Jogo.objects.all().order_by('nome')

    return render(request, 'jogos.html', {
        'jogos': jogos
    })

@login_required
def enviar_amizade(request, perfil_id):

    solicitante = request.user.perfil

    destinatario = get_object_or_404(
        Perfil,
        id=perfil_id
    )

    if solicitante != destinatario:

        amizade = Amizade.objects.filter(
            solicitante=solicitante,
            destinatario=destinatario
        ).first()

        if not amizade:

            Amizade.objects.create(
                solicitante=solicitante,
                destinatario=destinatario
            )

    return redirect('perfil', id=perfil_id)

@login_required
def aceitar_amizade(request, amizade_id):

    amizade = get_object_or_404(
        Amizade,
        id=amizade_id
    )

    if amizade.destinatario == request.user.perfil:

        amizade.status = 'aceita'
        amizade.save()

        amizade.solicitante.adicionar_pontos(5)
        amizade.destinatario.adicionar_pontos(5)

    return redirect(
        'perfil',
        id=request.user.perfil.id
    )

@login_required
def recusar_amizade(request, amizade_id):

    amizade = get_object_or_404(
        Amizade,
        id=amizade_id
    )

    if amizade.destinatario == request.user.perfil:

        amizade.status = 'recusada'
        amizade.save()

    return redirect(
        'perfil',
        id=request.user.perfil.id
    )
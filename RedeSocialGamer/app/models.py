from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfis/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    nivel = models.IntegerField(default=1)
    pontos = models.IntegerField(default=0)

    def adicionar_pontos(self, quantidade):
        self.pontos += quantidade

        self.nivel = (self.pontos // 100) + 1

        self.save()

    def __str__(self):
        return self.usuario.username


class Jogo(models.Model):
    nome = models.CharField(max_length=100)
    genero = models.CharField(max_length=50)
    descricao = models.TextField(blank=True, null=True)
    capa = models.ImageField(upload_to='jogos/', blank=True, null=True)

    def __str__(self):
        return self.nome


class JogoFavorito(models.Model):
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='jogos_favoritos'
    )
    jogo = models.ForeignKey(
        Jogo,
        on_delete=models.CASCADE,
        related_name='favoritado_por'
    )

    class Meta:
        unique_together = ('perfil', 'jogo')

    def __str__(self):
        return f'{self.perfil} - {self.jogo}'


class Amizade(models.Model):
    solicitante = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='amizades_enviadas'
    )
    destinatario = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='amizades_recebidas'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('aceita', 'Aceita'),
            ('recusada', 'Recusada'),
        ],
        default='pendente'
    )

    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.solicitante} -> {self.destinatario}'


class Publicacao(models.Model):
    autor = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='publicacoes'
    )
    titulo = models.CharField(max_length=150)
    texto = models.TextField()
    imagem = models.ImageField(
        upload_to='publicacoes/',
        blank=True,
        null=True
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    autor = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.autor} - {self.publicacao}'


class Curtida(models.Model):
    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name='curtidas'
    )
    usuario = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='curtidas'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('publicacao', 'usuario')

    def __str__(self):
        return f'{self.usuario} curtiu {self.publicacao}'
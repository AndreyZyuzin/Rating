from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


class Team(models.Model):
    """Модель футбольных команд."""

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'
        ordering = ('name', )

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text='Название команды',
        verbose_name='Название',
    )

    def __str__(self):
        return f'{self.name}'


class Tournament(models.Model):
    """Модель футбольных турниров."""

    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'
        ordering = ('title', )

    title = models.CharField(
        max_length=100,
        unique=True,
        help_text='Название турнира',
        verbose_name='Название',
    )

    def __str__(self):
        return f'{self.title}'


class Match(models.Model):
    """Модель футбольного матча."""

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
        ordering = ('-date', )

    date = models.DateField(help_text='Дата матча', verbose_name='Дата')
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.SET_NULL,
        help_text='Турнир',
        verbose_name='Турнир',
        related_name='matches',
        null=True,
    )
    team1 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text='Первая команда',
        verbose_name='Команда 1',
        related_name='matches1',
    )
    team2 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text='Вторая команда',
        verbose_name='Команда 2',
        related_name='matches2',
    )
    goals1 = models.PositiveSmallIntegerField(
        help_text='Голы первой команды',
        verbose_name='Голы 1',
        default=0,
    )
    goals2 = models.PositiveSmallIntegerField(
        help_text='Голы второй команды',
        verbose_name='Голы 2',
        default=0,
    )
    is_neutral = models.BooleanField(
        help_text='Нейтральное ли поле',
        verbose_name='Нейтральность',)
    country = models.CharField(
        max_length=50,
        help_text='Страна проведения',
        verbose_name='Старана',
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=50,
        help_text='Город проведения',
        verbose_name='Город',
        null=True,
        blank=True,
    )

    def clean(self) -> None:
        if self.team1_id and self.team2_id and self.team1_id == self.team2_id:
            name = self.team1.name
            raise ValidationError(
                f'Недопустимо, чтобы команда {name} играла сама с собой.')

    def __str__(self):
        return f'{self.team1}-{self.team2}'


class Shootout(models.Model):
    """Модель пенальти после матча."""

    class Meta:
        verbose_name = 'Пенальти'
        verbose_name_plural = 'Пенальти'

    match = models.OneToOneField(
        Match,
        help_text='Матч',
        verbose_name='Матч',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='shootout'
    )
    numb_winner = models.SmallIntegerField(
        help_text='Победитель',
        verbose_name='Победитель',
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )

    def __winner(self):
        if self.numb_winner == 1:
            return self.match.team1
        if self.numb_winner == 2:
            return self.match.team2
        return 'Unknow'

    winner = property(__winner)

    def __str__(self):
        return f'{self.match}'

from typing import Iterable, Optional
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

    coefficient = models.FloatField(
        help_text='Коэффициент - вес турнира',
        verbose_name='Коэф.',
        default=1,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f'{self.title}'


class Match(models.Model):
    """Модель футбольного матча."""

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
        ordering = ('-date', )
        constraints = [
            models.UniqueConstraint(
                fields=('date', 'team1', 'team2'),
                name='unique_match',
            )
        ]

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
        verbose_name='Нейтральность',
    )
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

    class Winner(models.IntegerChoices):
        UNKNOWN = 0, 'Unknown'
        FIRST = 1, 'First'
        SECOND = 2, 'Second'

    class Meta:
        verbose_name = 'Послематчевые пенальти'
        verbose_name_plural = 'Пенальти'

    match = models.OneToOneField(
        Match,
        help_text='Матч',
        verbose_name='Матч',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='shootout',
    )
    choice_winner = models.SmallIntegerField(
        help_text='Победитель',
        verbose_name='Победитель',
        choices=Winner.choices,
        default=Winner.UNKNOWN,
    )

    def __winner(self):
        if self.choice_winner == Shootout.Winner.FIRST:
            return self.match.team1
        if self.choice_winner == Shootout.Winner.SECOND:
            return self.match.team2
        return Shootout.Winner.UNKNOWN.label

    winner = property(__winner)

    def __str__(self):
        print(hasattr(self, 'match'))
        return f'id {self.pk}: {self.match}' if hasattr(self, 'match') else ''


class Goal(models.Model):
    """Модель кто забил голы."""

    class FromTeam(models.IntegerChoices):
        FIRST = 1, 'First'
        SECOND = 2, 'Second'

    class Meta:
        verbose_name = 'Гол'
        verbose_name_plural = 'Голы'

    match = models.ForeignKey(
        Match,
        help_text='Матч',
        verbose_name='Матч',
        on_delete=models.CASCADE,
        related_name='goalscore',
    )
    scorer = models.CharField(
        max_length=50,
        help_text='Имя бомбардира',
        verbose_name='Имя',
    )
    minute = models.PositiveSmallIntegerField(
        help_text='На какой минуте',
        verbose_name='Минута',
        default=0,
    )
    choice_team = models.SmallIntegerField(
        help_text='Из какой команды',
        verbose_name='Команда',
        choices=FromTeam.choices,
    )

    def __team(self):
        if self.choice_team == Goal.FromTeam.FIRST:
            return self.match.team1
        if self.choice_team == Goal.FromTeam.SECOND:
            return self.match.team2
        return None

    team = property(__team)

    def __str__(self):
        return f'{self.scorer}'


class Note(models.Model):
    """Модель примечания голу."""

    class Type(models.IntegerChoices):
        NONE = 0, 'None'
        PENALTY = 1, 'Penalty'
        OWN = 2, 'Own goal'

    goal = models.OneToOneField(
        Goal,
        help_text='Гол',
        verbose_name='Голы',
        on_delete=models.CASCADE,
        related_name='note',
        primary_key=True,
    )

    type = models.SmallIntegerField(
        help_text='Примечание',
        verbose_name='Прим.',
        choices=Type.choices,
        default=Type.NONE,
    )

    def __str__(self):
        return f'{self.pk}'

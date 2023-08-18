from django.contrib import admin
from django.contrib.auth.models import Group, User

from kaggle.models import Goal, Match, Shootout, Team, Tournament


class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'coefficient')
    list_display_links = ('title',)
    list_editable = ('coefficient',)
    search_fields = ('title',)
    ordering = ('-coefficient', 'title')
    actions = ('export_csv',)

    def export_csv(self, request, quuryset):
        pass
    export_csv.short_description = 'Экспортировать выбранное в tournament.csv'


class ShootoutInline(admin.StackedInline):
    model = Shootout
    can_delete = True
    extra = 0


class GoalInline(admin.TabularInline):
    model = Goal
    extra = 0


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'tournament', 'result', 'location',
                    'addition')
    list_display_links = list_display
    list_filter = ('tournament', 'date')
    search_fields = ('tournament__title',)
    ordering = ('-date',)
    fieldsets = (
        ('Турнир', {
            'fields': ('tournament',)
        }),
        ('Дата и местоположение', {
            'fields': ('date', ('country', 'city',),)
        }),
        ('Участники матча', {
            'fields': ('is_neutral', ('team1', 'team2'), ('goals1', 'goals2'))
        }),
    )
    inlines = (ShootoutInline, GoalInline,)

    def result(self, match):
        return f'{match} - {match.goals1}:{match.goals2}'
    result.short_description = 'Матч'

    def location(self, match):
        return f'{match.city}({match.country})'
    location.short_description = 'Место встречи'

    def addition(self, match):
        notes = []
        if hasattr(match, 'shootout'):
            notes.append(f'пен: {match.shootout.winner}')
        if match.is_neutral:
            notes.append('нейтр.')
        return ', '.join(notes)
    addition.short_description = 'Разное'


class ShootoutAdmin(admin.ModelAdmin):
    list_display = ('match', 'winner',)


admin.site.register(Shootout, ShootoutAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team)
admin.site.unregister(User)
admin.site.unregister(Group)

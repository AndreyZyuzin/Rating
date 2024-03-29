from django.contrib import admin
from django.contrib.auth.models import Group, User

from kaggle.models import (AliasTeam, Goal, Match, Shootout, Team, Tournament,
                           Note,)


class AliasTeamInline(admin.TabularInline):
    model = AliasTeam
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('alias',)
    inlines = AliasTeamInline,

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from pprint import pprint
        if db_field.name == "alias":
            kwargs['queryset'] = AliasTeam.objects.filter(
                team_id=request.resolver_match.kwargs['object_id']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



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
    # list_display = ('id', 'match', 'choice_winner')
    model = Shootout


class NoteInline(admin.TabularInline):
    model = Note


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('id', 'scorer', 'get_match',
                    'minute', 'choice_team', 'get_note',)
    list_display_links = list_display
    inlines = NoteInline,

    def get_note(self, goal):
        if hasattr(goal, 'note'):
            return goal.note.get_type_display()
    get_note.short_description = 'Прим.'

    def get_match(self, goal):
        return f'{goal.match.id}: {goal.match}'
    get_match.short_description = 'Матч'


class GoalLinkInline(admin.TabularInline):
    model = Goal
    extra = 0
    show_change_link = True
    fields = ('scorer', 'minute', 'choice_team', 'get_note',)
    readonly_fields = ('get_note',)

    def get_note(self, goal):
        return goal.note.get_type_display() if hasattr(goal, 'note') else ''
    get_note.short_description = 'Прим.'


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'tournament', 'result', 'location',
                    'addition', 'goals',)
    list_display_links = list_display
    list_filter = ('tournament', 'date')
    search_fields = ('tournament__title',)
    ordering = ('-date', '-tournament__coefficient')
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
    inlines = (ShootoutInline, GoalLinkInline,)
    list_per_page = 30
    save_on_top = True

    def result(self, match):
        return f'{match} - {match.goals1}:{match.goals2}'
    result.short_description = 'Матч'

    def location(self, match):
        city, country = match.city, match.country
        if city and country:
            return f'{match.city}({match.country})'
        if city is None and country is None:
            return '---'
        if city is None:
            return f'{country}'
        return f'{city}'
    location.short_description = 'Место встречи'

    def addition(self, match):
        notes = []
        if hasattr(match, 'shootout'):
            notes.append(f'пен: {match.shootout.winner}')
        if match.is_neutral:
            notes.append('нейтр.')
        return ', '.join(notes)
    addition.short_description = 'Разное'

    def goals(self, match):
        scorers = list(match.goalscore.order_by('minute')
                       .values_list('scorer', flat=True))
        print(scorers)
        res = '…, ' if len(scorers) > 3 else ''
        res += ', '.join(scorers[-3:])
        print(res)
        return res


admin.site.register(Tournament, TournamentAdmin)

admin.site.unregister(User)
admin.site.unregister(Group)

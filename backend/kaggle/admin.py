from django.contrib import admin

from .models import Tournament, Team, Match, Shootout


admin.site.register(Tournament)
admin.site.register(Team)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'tournament', 'result', 'location',
                    'addition')
    list_display_links = list_display
    list_filter = ('tournament', 'date')
    search_fields = ('tournament__title',)
    ordering = ('-date',)

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
    list_display = ('match', 'winner')


admin.site.register(Shootout, ShootoutAdmin)

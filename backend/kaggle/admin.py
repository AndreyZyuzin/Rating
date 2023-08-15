from django.contrib import admin

from .models import Tournament, Team, Match, Shootout


admin.site.register(Tournament)
admin.site.register(Team)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'tournament', 'team1', 'team2',
                    'goals1', 'goals2', 'country', 'city', 'is_neutral')
    list_filter = ('tournament', 'team1__name', 'team2__name', 'date')
    search_fields = ('tournament', 'team1__name', 'team2__name')
    ordering = ('-date',)


class ShootoutAdmin(admin.ModelAdmin):
    list_display = ('match', 'winner')


admin.site.register(Shootout, ShootoutAdmin)

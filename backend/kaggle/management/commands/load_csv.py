"""Скрипт наполняющий данные из файлов csv в базу данных.

    Файлы находятся в /static/data/*.csv
    Запуск:
        python manage.py load_csv       - добавление в БД
        python manage.py load_csv -u
            - добавление в БД. Найденные элементы будут обновлены
        python manage.py load_csv --delete_all
            - удаляются данные, которые отсутствуют в файле load_csv
"""
import os
import csv
import logging
from typing import Type
from pprint import pprint
from datetime import datetime

from django.core.management.base import BaseCommand, CommandParser
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from rating.settings import BASE_DIR
from kaggle.models import Tournament, Team, Match, Shootout

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    PATH_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'data_csv'))
    FILES = ('results', 'shootouts', 'goalscorers')

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--delete_all',
            action='store_const', const=True,
            help='Передварительно удаляются все данные.'
        )

        parser.add_argument(
            '-u', '--update',
            action='store_const', const=True,
            help='При нахождении элемента обновляется другим содержанием.'
        )

    def handle(self, *args, **options) -> None:
        state_update = options.get('update')
        state_delete_all = options.get('delete_all')

        print(self.PATH_CSV)
        print(state_update, state_delete_all)
        for name_file in self.FILES:
            full_name_file = os.path.join(self.PATH_CSV, name_file + '.csv')
            print(f'{full_name_file} - {os.path.exists(full_name_file)}')

        tournaments = {'updated': set(), 'created': set()}
        teams = {'updated': {}, 'created': set()}
        matches = {'updated': [], 'created': []}
        shootouts = {'updated': [], 'created': []}
        goalscorers = {'updated': [], 'created': []}

        full_name_file = os.path.join(self.PATH_CSV, self.FILES[0] + '.csv')
        if os.path.isfile(full_name_file):
            with open(full_name_file, encoding='utf-8') as file:
                reader = csv.DictReader(
                    file,
                    fieldnames=('date', 'team1', 'team2', 'goals1', 'goals2',
                                'tournament', 'city', 'country', 'is_neutral'),
                )
                row = next(reader, None)
                if row['date'] == 'date':
                    row = next(reader, None)
                while row is not None:
                    team1 = row['team1']
                    if (team1 not in teams['created']
                            and team1 not in teams['updated']):
                        team_bd = Team.objects.filter(name=team1)
                        if team_bd.exists():
                            teams['updated']['team1'] = team_bd.first()
                        else:
                            teams['created'].add(team1)

                    team2 = row['team2']
                    if (team2 not in teams['created']
                            and team2 not in teams['updated']):
                        team_bd = Team.objects.filter(name=team2)
                        if team_bd.exists():
                            teams['updated']['team2'] = team_bd.first()
                        else:
                            teams['created'].add(team2)
                    # print(team1, team2, teams)

                    title = row['tournament']
                    if (title not in tournaments['created']
                            and title not in tournaments['updated']):
                        if Tournament.objects.filter(title=title).exists():
                            tournaments['updated'].add(title)
                        else:
                            tournaments['created'].add(title)

                    date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    print(f'{team1} in {teams["updated"].values()} == {team1 in teams["updated"].values()}')
                    print(f'{team2} in {teams["updated"].values()} == {team2 in teams["updated"].values()}')
                    print('-'*78)
                    if (team1 in teams['updated'].values()
                            and team2 in teams['updated'].values()):
                        if Match.objects.filter(date=date,
                                                team1=teams['updated'][team1],
                                                team2=teams['updated'][team2]
                                                ).exists():
                            matches['updated'].append(row)
                        else:
                            matches['created'].append(row)
                    row = next(reader, None)

        pprint(teams)
        pprint(tournaments)
        pprint(matches)

        if state_delete_all:
            res, _ = Tournament.objects.all().exclude(
                title__in=list(tournaments['created'])
            ).exclude(
                title__in=list(tournaments['updated'])
            ).delete()
            if res:
                logger.info(f'Из Tournament удаленны {res} элементов')
            Team.objects.all().exclude(
                name__in=list(teams['created'])
            ).exclude(
                name__in=[name for name in teams['updated'].keys()]
            )
            print(res)

        if state_update:
            pass

        items = [Tournament(title=title) for title in tournaments['created']]
        Tournament.objects.bulk_create(items)

        items = [Team(name=name) for name in teams['created']]
        Team.objects.bulk_create(items)



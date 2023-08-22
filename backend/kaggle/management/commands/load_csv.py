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


# def item_created_or_update(match: Match) -> bool:


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
        teams = {}
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
                    if team1 not in teams:
                        team_bd = Team.objects.filter(name=team1)
                        if team_bd.exists():
                            teams[team1] = {'bd': team_bd}
                        else:
                            teams[team1] = {'new': True}
                    team2 = row['team2']
                    if team2 not in teams:
                        team_bd = Team.objects.filter(name=team2)
                        if team_bd.exists():
                            teams[team2] = {'bd': team_bd}
                        else:
                            teams[team2] = {'new': True}

                    title = row['tournament']
                    if (title not in tournaments['created']
                            and title not in tournaments['updated']):
                        if Tournament.objects.filter(title=title).exists():
                            tournaments['updated'].add(title)
                        else:
                            tournaments['created'].add(title)

                    date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    team1 = teams[team1]
                    team2 = teams[team2]
                    if 'bd' in team1 and 'bd' in team2:
                        if Match.objects.filter(date=date,
                                                team1=team1['bd'],
                                                team2=team2['bd']).exists():
                            matches['update'].append(row)
                        else:
                            matches['created'].append(row)
                    row = next(reader, None)

        pprint(teams)
        pprint(tournaments)
        pprint(matches)

        if state_delete_all:
            pass

        if state_update:
            pass

        tournament_instances = [
            Tournament(title=title) for title in tournaments['created']
        ]

        Tournament.objects.bulk_create(tournament_instances)



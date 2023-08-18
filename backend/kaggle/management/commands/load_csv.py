"""Скрипт наполняющий данные из файлов csv в базу данных.

    Файлы находятся в /static/data/*.csv
    Запуск:
        python manage.py load_csv       - добавление в БД
        python manage.py load_csv -u
            - добавление в БД. Найденные элементы будут обновлены
        python manage.py load_csv --delete_all
            - Предваритльено удаляются все таблицы
        python mantage.py load_csv --clear
            - Найденные матчи добавляются или обновляются, не найденные матчи
                удаляются
"""
import os
import csv
import logging
from typing import Type
from pprint import pprint

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
            '--clear',
            action='store_const', const=True,
            help='Не найденные матчи будут удалены.'
        )

        parser.add_argument(
            '-u', '--update',
            action='store_const', const=True,
            help='При нахождении элемента обновляется другим содержанием.'
        )

    def handle(self, *args, **options) -> None:
        state_update = options.get('update')
        state_clear = options.get('clear')
        state_delete_all = options.get('delete_all')

        print(self.PATH_CSV)
        print(state_update, state_clear, state_delete_all)
        for name_file in self.FILES:
            full_name_file = os.path.join(self.PATH_CSV, name_file + '.csv')
            print(f'{full_name_file} - {os.path.exists(full_name_file)}')

        if state_delete_all:
            for model in (Tournament, Team):
                model.objects.all().delete()

        tournaments = list()
        teams = list()
        matches = list()
        shootouts = list()
        goalscorers = list()

        full_name_file = os.path.join(self.PATH_CSV, self.FILES[0] + '.csv')
        if os.path.isfile(full_name_file):
            with open(full_name_file) as file:
                reader = csv.DictReader(
                    file,
                    fieldnames=('date', 'team1', 'team2', 'goals1', 'goals2',
                                'tournament', 'city', 'country', 'is_neutral'),
                )
                row = next(reader)
                if row['date'] == 'date':
                    row = next(reader)
                print(row)

                team1 = row['team1']
                team2 = row['team2']
                if team1 not in teams:
                    teams.append(team1)
                if team2 not in teams:
                    teams.append(team2)
                tournament = row['tournament']
                if tournament not in tournaments:
                    tournaments.append(tournament)

        pprint(teams)
        pprint(tournaments)
        pprint(matches)




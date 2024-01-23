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
from django.db.utils import IntegrityError

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
        for name_file in self.FILES:
            full_name_file = os.path.join(self.PATH_CSV, name_file + '.csv')
            print(f'{full_name_file} - {os.path.exists(full_name_file)}')

        tournaments = {'updated': {}, 'created': set()}
        teams = {'updated': {}, 'created': set()}
        matches = {'updated': [], 'created': []}
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
                            team_bd = team_bd.first()
                            teams['updated'][team_bd.name] = team_bd
                        else:
                            teams['created'].add(team1)

                    team2 = row['team2']
                    if (team2 not in teams['created']
                            and team2 not in teams['updated']):
                        team_db = Team.objects.filter(name=team2)
                        if team_db.exists():
                            teams['updated'][team2] = team_db.first()
                        else:
                            teams['created'].add(team2)
                    # print(team1, team2, teams)

                    title = row['tournament']
                    if (title not in tournaments['created']
                            and title not in tournaments['updated']):
                        tournament = Tournament.objects.filter(title=title)
                        if tournament.exists():
                            tournaments['updated'][title] = tournament.first()
                        else:
                            tournaments['created'].add(title)

                    date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    row['date'] = date
                    is_neutral = row['is_neutral']
                    row['is_neutral'] = True if is_neutral == 'TRUE' else False
                    row['goals1'] = int(row['goals1'])
                    row['goals2'] = int(row['goals2'])
                    if team1 in teams['updated'] and team2 in teams['updated']:
                        match = Match.objects.filter(
                            date=date,
                            team1=teams['updated'][team1],
                            team2=teams['updated'][team2],
                        )
                        if match.exists():
                            row['match'] = match.first()
                            matches['updated'].append(row)
                        else:
                            matches['created'].append(row)
                    else:
                        matches['created'].append(row)

                    row = next(reader, None)

#        pprint(teams)
#        pprint(tournaments)
#        pprint(matches['created'][-10:])
#        pprint(matches['updated'][-10:])

        missing_tournaments = Tournament.objects.all().exclude(
                title__in=list(tournaments['updated'])
            )

        missing_teams = Team.objects.all().exclude(
                name__in=teams['updated'].keys()
            )

        missing_matches = Match.objects.all().exclude(
                id__in=[item['match'].id for item in matches['updated']]
            )

        if state_delete_all:
            logger.info('Начала удаление старых данных')
            res, _ = missing_tournaments.delete()
            if res:
                logger.info(f'Из Tournament удаленны {res} элементов')

            res, _ = missing_teams.delete()
            if res:
                logger.info(f'Из Team удаленны {res} элементов')

            res, _ = missing_matches.delete()
            if res:
                logger.info(f'Из Match удаленны {res} элементов')
        else:
            res = missing_tournaments.count()
            if res:
                logger.info(f'В Tournament найдены {res} элементов')

            res = missing_teams.count()
            if res:
                logger.info(f'В Team найдены {res} элементов')

            res = missing_matches.count()
            if res:
                logger.info(f'В Match найдены {res} элементов')

        if tournaments['created']:
            logger.info('Запуск создание новых турниров')
        items = [Tournament(title=title) for title in tournaments['created']]
        Tournament.objects.bulk_create(items)

        if teams['created']:
            logger.info('Запуск создания новых команд')
        items = [Team(name=name) for name in teams['created']]
        Team.objects.bulk_create(items)

        if state_update:
            if matches['updated']:
                logger.info('Запуск обновления матчей')
            items = []
            for row in matches['updated']:
                match = row['match']
                tournament = row['tournament']
                if match.tournament.title != tournament:
                    match.tournament = Tournament.objects.get(title=tournament)
                match.goals1 = row['goals1']
                match.goals2 = row['goals2']
                match.is_neutral = row['is_neutral']
                match.country = row['country']
                match.city = row['city']
                items.append(match)
            Match.objects.bulk_update(items,
                                      ['tournament_id', 'goals1', 'goals2',
                                       'is_neutral', 'country', 'city']
                                      )

        if matches['created']:
            logger.info('Запуск создания новых матчей')
        items = []
        for match in matches['created']:
            match['team1'] = Team.objects.get(name=match['team1'])
            match['team2'] = Team.objects.get(name=match['team2'])
            match['tournament'] = \
                Tournament.objects.get(title=match['tournament'])
            items.append(Match(**match))

        try:
            Match.objects.bulk_create(items,)  # ignore_conflicts=True)
        except IntegrityError:
            for item in items:
                try:
                    item.save()
                except IntegrityError as exc:
                    logger.error(exc)
                    logger.warning(f'Следует проверить строку: {item.date}, '
                                   f'{item.team1}, {item.team2}, '
                                   f'{item.goals1}, {item.goals2}, '
                                   f'{item.tournament}')

###############################################

        print(f'Запуск {self.FILES[1]}')
        shootouts = {'updated': [], 'created': []}
        full_name_file = os.path.join(self.PATH_CSV, self.FILES[1] + '.csv')
        if os.path.isfile(full_name_file):
            with open(full_name_file, encoding='utf-8') as file:
                reader = csv.DictReader(
                    file,
                    fieldnames=('date', 'team1', 'team2', 'winner'),
                )
                row = next(reader, None)
                if row['date'] == 'date':
                    row = next(reader, None)
                while row is not None:
                    date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    team1_name = row['team1']
                    team1 = Team.objects.filter(name=team1_name)
                    if not team1.exists():
                        logger.info(f'В строке {row} не найден {team1_name}')
                        row = next(reader, None)
                        continue
                    team1 = team1.first()
                    team2_name = row['team2']
                    team2 = Team.objects.filter(name=team2_name)
                    if not team2.exists():
                        logger.info(f'В строке {row} не найден {team1_name}')
                        row = next(reader, None)
                        continue
                    team2 = team2.first()
                    match = Match.objects.filter(date=date,
                                                 team1=team1,
                                                 team2=team2)
                    if not match.exists():
                        logger.info(f'В строке {row} не найден '
                                    'соответствующего матча')
                        row = next(reader, None)
                        continue
                    match = match.first()
                    winner = row['winner']
                    if winner == team1_name:
                        winner = Shootout.Winner.FIRST
                    elif winner == team2_name:
                        winner = Shootout.Winner.SECOND
                    else:
                        winner = Shootout.Winner.UNKNOWN
                    shootout = Shootout.objects.filter(match=match)
                    if shootout.exists():
                        shootout = shootout.first()
                        if state_update and shootout.winner != winner:
                            shootout.choice_winner = winner
                            shootouts['updated'].append(shootout)
                    else:
                        shootouts['created'].append(
                            Shootout(match=match, choice_winner=winner)
                        )
                    row = next(reader, None)

        if state_update:
            Shootout.objects.bulk_update(
                shootouts['updated'], ['choice_winner'])
        try:
            Shootout.objects.bulk_create(shootouts['created'])
        except IntegrityError:
            for item in shootouts['created']:
                try:
                    item.save()
                except IntegrityError as exc:
                    logger.error(exc)
                    logger.warning(f'Следует проверить строку: {item.date}, '
                                   f'{item.match.team1}, {item.match.team2}, '
                                   f'{item.match.winner}')
 
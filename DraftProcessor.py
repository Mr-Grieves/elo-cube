from elo import rate_1vs1
import os, glob
import re
import csv
from collections import OrderedDict
from known_aliases import ALIASES

ELO_DEFAULT = 1000.0

class DraftProcessor():
    def __init__(self, new_dates=None, remake_db=False, anon=True, forplayer=None, pack_size=15):
        self.pack_size = pack_size
        self.anon = anon

        csv_path = 'card_db.csv'
        if remake_db or not os.path.exists(csv_path):
            # Start a new elo database
            self.db = OrderedDict()
        else:
            # Load previous db from file
            with open('card_db.csv') as csv_file:
                reader = csv.reader(csv_file)
                self.db = OrderedDict(reader)

        for date in new_dates:
            print("\nParsing draft from date:", date)
            draft_files = glob.glob("drafts\\"+date+"\\*.txt")
            for f in draft_files:
                self.parse_draft_log(f, forplayer)

        # Sort by ELOOrderedDict(sorted(data.items(), key=itemgetter(1)))
        self.db = OrderedDict(sorted(self.db.items(), key=lambda item: item[1]['ELO'], reverse=True))

        # Write back to file
        with open('card_db.csv', 'w') as csv_file:
            csv_file.write('card,ELO,count,picked_by')
            for key, value in self.db.items():
                csv_file.write('\n'+key+','+str(value['ELO'])+','+str(value['count'])+','+str(value['picked_by']))

    def parse_draft_log(self, filepath, forplayer):
        """
        Parse the given draft file by scanning through it line-by-line
        Extracts player names (anonymized), and picked/passed cards
        """
        print("\tParsing file:", filepath)
        f = open(filepath, "r")

        all_lines = []
        for line in f.readlines():
            all_lines.append(line)

        for li in range(len(all_lines)):
            # First find player
            if all_lines[li] == "Players:\n":
                folder = os.path.dirname(filepath)
                for li in range(li+1, li+1+len(os.listdir(folder))):
                    line = all_lines[li]
                    m = re.findall("(-->)?(.*)",line)[0]
                    if m[0] == '-->':
                        player_name = self.lookup_alias(m[1].strip())
                        if forplayer is not None and player_name != forplayer:
                            return
                        break

            # Find if card was picked or passed
            m = re.findall("Pack (\d) pick (\d+):", all_lines[li])
            if len(m) != 0:
                pack_num = int(m[0][1])
                pick_num = int(m[0][1])
                passed_cards = []
                picked_card = ""
                for li in range(li+1, li+self.pack_size-pick_num+2):
                    line = all_lines[li]
                    m = re.findall("(-->)?(.*)",line)[0]
                    card_name = m[1].strip()
                    if m[0] == '-->':
                        picked_card = card_name
                    else:
                        passed_cards.append(card_name)
                self.update_elo(picked_card, passed_cards, player_name, pack_num)

    def update_elo(self, picked, passed, player, pack_num):
        """
        Update the ELO database for the two given cards
        """
        if picked not in self.db.keys():
            self.db[picked] = {'ELO': ELO_DEFAULT, 'count': 0, 'picked_by': []}

        # Increment the picked card's count
        self.db[picked]['count'] = self.db[picked]['count'] + 1

        # Add to the player list
        self.db[picked]['picked_by'].append(player)

        for card in passed:
            if card not in self.db.keys():
                self.db[card] = {'ELO': ELO_DEFAULT, 'count': 0, 'picked_by': []}

            # rate_1vs1(800, 1200) -> (809.091, 1190.909)
            self.db[picked]['ELO'], self.db[card]['ELO'] = rate_1vs1(self.db[picked]['ELO'], self.db[card]['ELO'])

    def print_top_cards(self, N, highest_count=False):
        """
        Print the N top picks
        If highest_count=True, it will only print cards that will in the most drafts
        If player is specified, only print cards that that player has chosen
        """
        if highest_count:
            high_count = max([e['count'] for e in self.db.values()])
            highest_db = OrderedDict(filter(lambda item: item[1]['count'] == high_count, self.db.items()))

            print("\n\tTop {:d} cards (count = {:d}):".format(N, high_count))
            [print("{:.2f}\t- {:s}".format(x[1]['ELO'], x[0])) for x in list(highest_db.items())[:N]]
        else:
            print("\n\tTop {:d} cards (all counts):".format(N))
            [print("{:.2f}\t(N = {:d}) - {:s}".format(x[1]['ELO'], x[1]['count'], x[0])) for x in list(self.db.items())[:N]]

    def print_bottom_cards(self, N, highest_count=False, player=None):
        """
        Print the N bottom picks
        If highest_count=True, it will only print cards that will in the most drafts
        """
        if highest_count:
            high_count = max([e['count'] for e in self.db.values()])
            highest_db = OrderedDict(filter(lambda item: item[1]['count'] == high_count, self.db.items()))

            print("\n\tBottom {:d} cards (count = {:d}):".format(N, high_count))
            [print("{:.2f}\t- {:s}".format(x[1]['ELO'], x[0])) for x in list(highest_db.items())[-N:]]
        else:
            print("\n\tBottom {:d} cards (all counts):".format(N))
            [print("{:.2f}\t(N = {:d}) - {:s} ".format(x[1]['ELO'], x[1]['count'], x[0])) for x in list(self.db.items())[-N:]]

    def lookup_alias(self, alias):
        """
        Find the given player from a list of known aliases
        """
        for i, (k, v) in enumerate(ALIASES.items()):
            if alias in v:
                return 'player_'+str(i) if self.anon else k
        raise AttributeError('Unknown Alias! please update known_aliases.py with new player name')
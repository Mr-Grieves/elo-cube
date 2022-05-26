from elo import rate_1vs1
import os, glob
import re
import pandas as pd

ELO_DEFAULT = 1000.0
HEADERS = ['name', 'ELO', 'count']

class DraftProcessorPanda():
    def __init__(self, new_dates=None, remake_db=False, pack_size=15):
        self.pack_size = pack_size

        csv_path = 'card_db.csv'
        if remake_db or not os.path.exists(csv_path):
            # Start a new elo database
            self.db = pd.DataFrame(columns=HEADERS)
        else:
            # Load previous db from file
            self.db = pd.read_csv(csv_path)

        for date in new_dates:
            print("\nParsing draft from date:", date)
            draft_files = glob.glob("drafts\\"+date+"\\*.txt")
            for f in draft_files:
                self.parse_draft_log(f)

        self.db = self.db.loc[self.db['count'] >= 1].sort_values(by=['ELO'], ascending=False)
        self.db.to_csv(csv_path, index=False)

    def print_top_cards(self, N, highest_count=False):
        if highest_count:
            high_count = self.db['count'].max()
            print("\nTop {:d} cards (count = {:d}):".format(N, high_count))
            highest_db = self.db.loc[self.db['count'] == high_count]
            print(highest_db.iloc[:N])
        else:
            print("\nTop {:d} cards (all counts)".format(N))
            print(self.db.iloc[:N])

    def print_bottom_cards(self, N, highest_count=False):
        print("\nBottom",N,"cards:")
        print(self.db.iloc[-N:])

    def parse_draft_log(self, filepath):
        print("\tParsing file:", filepath)
        f = open(filepath, "r")

        all_lines = []
        for line in f.readlines():
            all_lines.append(line)

        for li in range(len(all_lines)):
            m = re.findall("Pack (\d) pick (\d+):", all_lines[li])
            if len(m) != 0:
                #pack_num = m[0]
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
                self.update_elo(picked_card, passed_cards)

    def get(self, card, column):
        return self.db.loc[self.db['name'] == card, column]

    def set(self, card, column, value):
        self.db.loc[self.db['name'] == card, [column]] = value

    def update_elo(self, picked, passed):
        if picked not in list(self.db['name']):
            self.db = self.db.append(pd.DataFrame([[picked, ELO_DEFAULT, 0]], columns=HEADERS))

        # Increment the picked card's count
        self.set(picked, 'count', self.get(picked, 'count') + 1)

        for card in passed:
            if card not in list(self.db['name']):
                self.db = self.db.append(pd.DataFrame([[card, ELO_DEFAULT, 0]], columns=HEADERS))

            # rate_1vs1(800, 1200) > (809.091, 1190.909)
            picked_ELO, card_ELO = self.get(picked, 'ELO'), self.get(card, 'ELO')
            picked_ELO, card_ELO = rate_1vs1(picked_ELO, card_ELO)
            self.set(picked, 'ELO', picked_ELO)
            self.set(card, 'ELO', card_ELO)

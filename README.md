# elo-cube
This small project is an attempt to assign ELO ratings to all the cards in Gerrit's cube. It does so by reading saved draft logs downloaded from https://www.mtgadraft.tk/

### Requirements:
`pip install elo`

### Usage:
Initialize the processor with: `dp = DraftProcessor()`

Parameters:
- `new_dates`: List of date-folder names to include. E.g: `['02-10-2021', '02-18-2021']`
- `remake_db`: Remake the database from scratch if True. Load previous db if not
- `anon`: Anonymize player names so to as not expose card preferences
- `forplayer`: Only analyze picks made by given player
- `pack_size`: Probable needs to be = 15

Print 10 best cards with:
`dp.print_top_cards(10, highest_count=True)`

Print 10 worst cards with:
`dp.print_bottom_cards(10, highest_count=True)`

See `main.py` for an example
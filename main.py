from DraftProcessor import DraftProcessor

all_dates = ['02-10-2021', '02-18-2021', '03-03-2021', '03-11-2021']
dp = DraftProcessor(remake_db=True, new_dates=all_dates, anon=False, forplayer=None)

#new_dates = []
#dp = DraftProcessor(remake_db=False, new_dates=new_dates)
#dp.print_top_cards(20, highest_count=False)
dp.print_bottom_cards(50, highest_count=True)
dp.print_bottom_cards(50, highest_count=False)

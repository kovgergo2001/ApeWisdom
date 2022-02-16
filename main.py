import imp
from kcu import request, kjson
from typing import List
from jsoncodable import JSONCodable
from ktg import Telegram
import time

class Stonk(JSONCodable):
    def __init__(
        self,
        d: dict
    ) -> None:
        self.rank = int(d["rank"])
        self.ticker = d["ticker"]
        self.name = d["name"]
        self.mentions = int(d.get("mentions") or 0)
        self.upvotes = int(d.get("upvotes") or 0)
        self.rank_24h_ago = int(d.get("rank_24h_ago") or 0)
        self.mentions_24h_ago = int(d.get("mentions_24h_ago") or 0)

class StonkResult(JSONCodable):
    def __init__(
        self,
        d: dict
    ) -> None:
        self.count = int(d["count"])
        self.pages = int(d["pages"])
        self.current_page = int(d["current_page"])
        self.results = []

        for d_ in d["results"]:
            try:
                self.results.append(Stonk(d_))
            except Exception as e:
                print(e, d_)
                exit(0)

def get_stonk_results(
    page: int
) -> StonkResult:
    try:
        return StonkResult(
            request.get(
                f"https://apewisdom.io/api/v1.0/filter/all-stocks/page/{page}", debug=True
            ).json()
        )
    except Exception as e:
        print(e)

        return None

def get_all_stonks() -> List[Stonk]:
    stonks = []
    page = 1

    while True:
        try:
            new_stonk_results = get_stonk_results(page)
            stonks.extend(new_stonk_results.results)
            
            if new_stonk_results.pages == new_stonk_results.current_page:
                break

            page += 1      
        except Exception as e:
            print(e)

    return stonks


tg = Telegram("5226498764:AAEV7IsM45RShgaXul_dLl3bGyXMaAvUYUc", "-642747173")

while True:
    new_list_24h =  get_all_stonks()
    rank_climb = new_list_24h[0].rank_24h_ago - new_list_24h[0].rank
    
    tg.send(f"Today's most popular stock is {new_list_24h[0].ticker} climbing {rank_climb} rank(s)!")
    
    most_rank_stock = new_list_24h[0]

    for stock in new_list_24h:
        if stock.rank_24h_ago - stock.rank > rank_climb:
            most_rank_stock = stock
            rank_climb = stock.rank_24h_ago - stock.rank
    
    tg.send(f"Today's most trending stock is {most_rank_stock.ticker} climbing {rank_climb} rank(s)!")

    time.sleep(60*5)

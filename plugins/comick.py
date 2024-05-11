#THis Code is made by Wizard Bots on telegram
# t.me/Wizard_Bots

from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from models import LastChapter
from plugins.client import MangaClient, MangaCard, MangaChapter

class ComickClient(MangaClient):
    
    base_domain = "https://comick.cc/"
    api_domain = "https://api.comick.cc/"

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    def init(self, *args, name="Comick", **kwargs):
        super().init(*args, name=name, headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes) -> List[MangaCard]:
        bs = BeautifulSoup(page, "html.parser")
        cards = bs.find_all("li")[:-1]

        mangas = [card.a for card in cards]
        names = [manga.find_next('span', class_='name').text.strip() for manga in mangas]
        urls = [urljoin(self.base_url, manga.get('href').strip()) for manga in mangas]
        images = [manga.find("img").get('src').strip() for manga in mangas]

        return [MangaCard(self, *tup) for tup in zip(names, urls, images)]

    def chapters_from_page(self, page: bytes, manga: MangaCard = None) -> List[MangaChapter]:
        bs = BeautifulSoup(page, "html.parser")
        div = bs.find("div", {"class": "list-chapter"})
        trs = div.find_all('tr')[1:]
        a_elems = [tr.find('a') for tr in trs]

        links = [urljoin(self.base_url, a.get('href')) for a in a_elems]
        texts = [(a.text[len(manga.name):].strip() if a.text.startswith(manga.name) else a.text.strip()) for a in a_elems]

        return [MangaChapter(self, link, text, manga, []) for link, text in zip(links, texts)]

    def updates_from_page(self, page: bytes) -> dict:
        bs = BeautifulSoup(page, "html.parser")
        div = bs.find('div', {'class': 'st_content'})
        manga_items = div.find_all('div', {'class': 'info-manga'})
        urls = {}

        for manga_item in manga_items:
            manga_url = urljoin(self.base_url, manga_item.find('a',  {"class": "name-manga"}).get('href'))
            chapter_item = manga_item.find('a', {"class": "name-chapter"})
            if chapter_item:
                chapter_url = urljoin(self.base_url, chapter_item.get('href'))
                urls[manga_url] = chapter_url

        return urls

    def search_mangas(title):
        
        #format:
        #{id,hid,slug,title,md_titles:[{title}],md_covers:[{w,h,b2key}],highlight}
        
        url = f"{Comick.api_domain}v1.0/search?q={title}&t=true"
        response = requests.get(url, headers=Comick.Headers)
        result  = response.json()
        return result  

    async def get_chapters(self, manga_card: MangaCard, page: int = 1) -> List[MangaChapter]:
        request_url = manga_card.url
        content = await self.get_url(request_url)
        all_chapters = self.chapters_from_page(content, manga_card)
        start_index = (page - 1) * 20
        end_index = min(start_index + 20, len(all_chapters))

        return all_chapters[start_index:end_index]

    async def iter_chapters(self, manga_url: str, manga_name: str) -> AsyncIterable[MangaChapter]:
        manga_card = MangaCard(self, manga_name, manga_url, '')
        content = await self.get_url(manga_url)

        for chapter in self.chapters_from_page(content, manga_card):
            yield chapter

    async def contains_url(self, url: str) -> bool:
        return url.startswith(self.base_url)

    async def check_updated_urls(self, last_chapters: List[LastChapter]) -> tuple:
        content = await self.get_url(self.base_url)
        updates = self.updates_from_page(content)
        updated = [lc.url for lc in last_chapters if lc.url in updates and updates[lc.url] != lc.chapter_url]
        not_updated = [lc.url for lc in last_chapters if lc.url not in updates or updates[lc.url] == lc.chapter_url]

        return updated, not_updated
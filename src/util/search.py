import http.client
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse
from util.util import Color, Cursor

URL = "html.duckduckgo.com"


class Result:
    title_color = Color("#275ff3").foreground(underline=True)
    url_color = Color("#42e75a").foreground()
    description_color = Color("#e3e9c3").foreground()

    def __init__(self, title, url, description):
        self.title = f"{self.title_color}{title}{Color(0).rst()}"
        self.url = f"{self.url_color}{url}{Color(0).rst()}"
        self.description = f"{self.description_color}{description}{Color(0).rst()}"

    def clean_desc(self):
        max_len = 100
        self.description = self.description.replace("\n", " ").replace("\t", " ")
        temp = ""
        for i in self.description.split(" "):
            if len(temp) + len(i) > max_len:
                temp += "\n\t"
                max_len += 100
            temp += i + " "
        self.description = temp

    def __repr__(self):
        return f"<Result title={self.title} url={self.url} description={self.description}>"

    def pretty(self):
        self.clean_desc()
        return f"""
    {self.title_color}{self.title}{Color(0).rst()}
    {self.url_color}{self.url}{Color(0).rst()}
    {self.description_color}{self.description}{Color(0).rst()}\n
"""

    def __str__(self):
        return f"{self.title}\n{self.url}\n{self.description}\n"


class Response:
    def __init__(self, data):
        self.text = data


class Session:
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "dnt": "1",
        "sec-ch-ua": '"Brave";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }

    def __init__(self):
        self.headers = Session.headers

    def post(self, url, json):
        self.conn = http.client.HTTPSConnection(url)
        self.payload = urlencode(json)
        self.conn.request("POST", "/html/", body=self.payload, headers=self.headers)
        self.res = self.conn.getresponse()
        self.data = self.res.read().decode("utf-8")
        return Response(self.data)

    def get(self, url):
        parsed_url = urlparse(url)
        self.conn = http.client.HTTPSConnection(parsed_url.netloc)
        self.conn.request("GET", parsed_url.path, headers=self.headers)
        self.res = self.conn.getresponse()
        self.data = self.res.read().decode("utf-8")
        return Response(self.data)


class Search:
    _query_dic = {
        "q": "awdhello",
        "b": "",
        "kl": "",
        "df": "",
    }
    _headers = {
        "authority": "html.duckduckgo.com",
        "origin": "https://html.duckduckgo.com",
        "referer": "https://html.duckduckgo.com/",
    }

    def __init__(self, query):
        self.session = Session()
        self.query_dic = Search._query_dic.copy()
        self.query_dic["q"] = query
        self.session.headers.update(self._headers)
        self.fetched_results = []

    def page(self):
        if not self.fetched_results:
            return Page([Result(title="End OF Result", url=":xxxxxxxx:", description=":[3]")])
        self.results = [
            Result(
                title=getattr(i.find("a", {"class": "result__a"}), "text", "None"),
                url=i.find("a", {"class": "result__a"}).get("href") if i.find("a", {"class": "result__a"}) else "None",
                description=getattr(i.find("a", {"class": "result__snippet"}), "text", "None"),
            )
            for i in self.fetched_results
        ]
        return Page(self.results)

    def fetch(self):
        self.response = self.session.post(URL, json=self.query_dic)
        soup = BeautifulSoup(self.response.text, "html.parser")
        if soup:
            self.fetched_results = soup.find_all("div", {"class": "result"})
            if self.fetched_results:
                form = soup.find("div", {"class": "results"})
                if form:
                    form = form.find("form")
                else:
                    self.fetched_results = []
                    return
                form_input_dic = {}
                if form:
                    for i in form.find_all("input", {"type": "hidden"}):  # type:ignore
                        form_input_dic[i.get("name")] = i.get("value")
                    self.query_dic.update(form_input_dic)
            else:
                self.fetched_results = []

    def next(self):
        self.fetch()


class Page:
    page_no = 0
    BANNERS = [
        rf"""{Color("#49c1e7").foreground()}
$$$$$$$$\                                $$\                     $$\        $$$$$$\                                          $$\       
\__$$  __|                               \__|                    $$ |      $$  __$$\                                         $$ |      
   $$ | $$$$$$\   $$$$$$\  $$$$$$\$$$$\  $$\ $$$$$$$\   $$$$$$\  $$ |      $$ /  \__| $$$$$$\   $$$$$$\   $$$$$$\   $$$$$$$\ $$$$$$$\  
   $$ |$$  __$$\ $$  __$$\ $$  _$$  _$$\ $$ |$$  __$$\  \____$$\ $$ |      \$$$$$$\  $$  __$$\  \____$$\ $$  __$$\ $$  _____|$$  __$$\ 
   $$ |$$$$$$$$ |$$ |  \__|$$ / $$ / $$ |$$ |$$ |  $$ | $$$$$$$ |$$ |       \____$$\ $$$$$$$$ | $$$$$$$ |$$ |  \__|$$ /      $$ |  $$ |
   $$ |$$   ____|$$ |      $$ | $$ | $$ |$$ |$$ |  $$ |$$  __$$ |$$ |      $$\   $$ |$$   ____|$$  __$$ |$$ |      $$ |      $$ |  $$ |
   $$ |\$$$$$$$\ $$ |      $$ | $$ | $$ |$$ |$$ |  $$ |\$$$$$$$ |$$ |      \$$$$$$  |\$$$$$$$\ \$$$$$$$ |$$ |      \$$$$$$$\ $$ |  $$ |
   \__| \_______|\__|      \__| \__| \__|\__|\__|  \__| \_______|\__|       \______/  \_______| \_______|\__|       \_______|\__|  \__|
   {Color(0).rst()}
                                                                                    {Color("#f1760b").foreground()}- by @leyuskc{Color(0).rst()}
                                                                                    {Color("#f33a06").foreground()}Powred by DuckDuckGo{Color(0).rst()}
""",
        rf"""{Color("#49c1e7").foreground()}
 ____  ____  ____  __  __  ____  _  _    __    __      ___  ____    __    ____   ___  _   _ 
(_  _)( ___)(  _ \(  \/  )(_  _)( \( )  /__\  (  )    / __)( ___)  /__\  (  _ \ / __)( )_( )
  )(   )__)  )   / )    (  _)(_  )  (  /(__)\  )(__   \__ \ )__)  /(__)\  )   /( (__  ) _ ( 
 (__) (____)(_)\_)(_/\/\_)(____)(_)\_)(__)(__)(____)  (___/(____)(__)(__)(_)\_) \___)(_) (_)
  {Color(0).rst()}  
                        {Color("#f1760b").foreground()}- by @leyuskc{Color(0).rst()}
                        {Color("#f33a06").foreground()}Powred by DuckDuckGo{Color(0).rst()}
""",
        rf"""{Color("#49c1e7").foreground()}
  _____              _           _   ___                  _    
 |_   _|__ _ _ _ __ (_)_ _  __ _| | / __| ___ __ _ _ _ __| |_  
   | |/ -_) '_| '  \| | ' \/ _` | | \__ \/ -_) _` | '_/ _| ' \ 
   |_|\___|_| |_|_|_|_|_||_\__,_|_| |___/\___\__,_|_| \__|_||_|
{Color(0).rst()}
            {Color("#f1760b").foreground()}- by @leyuskc{Color(0).rst()}
            {Color("#f33a06").foreground()}Powred by DuckDuckGo{Color(0).rst()}
""",
    ]

    def __init__(self, results):
        self.results = results
        Page.page_no += 1

    @property
    def content(self):
        return [i.pretty() for i in self.results]

    @property
    def banner(self):
        return self.gbanner() + f"""Page: {Color("#1ce5c1").foreground()}{self.page_no}{Color(0).rst()}"""

    def gbanner(self):
        c = Cursor.termsize()[0]
        if c >= 150:
            c = 0
        elif c >= 100 and c <= 150:
            c = 1
        else:
            c = 2

        return self.BANNERS[c]


if __name__ == "__main__":
    s = Search("hello")
    s.fetch()
    pg = s.page()
    print(pg.banner)
    for i in pg.content[:5]:
        print(i)

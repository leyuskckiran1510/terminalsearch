import http.client
from bs4 import BeautifulSoup
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
    def __init__(self):
        self.headers = {}

    def post(self, url, json):
        self.conn = http.client.HTTPSConnection(url)
        self.payload = "&".join([f"{key}={value}" for key, value in json.items()])
        self.conn.request("POST", "/html/", body=self.payload, headers=self.headers)
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
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "dnt": "1",
        "origin": "https://html.duckduckgo.com",
        "referer": "https://html.duckduckgo.com/",
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

    def __init__(self, query):
        self.session = Session()
        self._query_dic["q"] = query
        self.session.headers.update(self._headers)
        self.fetched_results = []
        with open("querires_are.txt", "a") as fl:
            fl.write(f"{query}\n")

    def page(self):
        try:
            self.results = [
                Result(
                    title=i.find("a", {"class": "result__a"}).text,
                    url=i.find("a", {"class": "result__a"}).get("href"),
                    description=i.find("a", {"class": "result__snippet"}).text,
                )
                for i in self.fetched_results
            ]
        except Exception as e:
            with open("the_dummy.txt", "a") as fl:
                fl.write(f"{' '.join(self.fetched_results)}\n")
            pass
            exit()
        if not self.results:
            return Page(
                [
                    Result(
                        title="End OF Result", url=":xxxxxxxx:", description="DuckDuckGo Html Has this much result only"
                    )
                ]
            )
        return Page(self.results)

    def fetch(self):
        response = self.session.post(URL, json=self._query_dic)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup:
            self.fetched_results = soup.find_all("div", {"class": "result"})
            if self.fetched_results:
                form = soup.find("div", {"class": "results"}).find("form")
                form_input_dic = {}
                if form:
                    for i in form.find_all("input", {"type": "hidden"}):
                        form_input_dic[i.get("name")] = i.get("value")
                    self._query_dic.update(form_input_dic)
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
,--,--'                      .    .---.                 .   
`- | ,-. ,-. ,-,-. . ,-. ,-. |    \___  ,-. ,-. ,-. ,-. |-. 
 , | |-' |   | | | | | | ,-| |        \ |-' ,-| |   |   | | 
 `-' `-' '   ' ' ' ' ' ' `-^ `'   `---' `-' `-^ '   `-' ' ' 
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

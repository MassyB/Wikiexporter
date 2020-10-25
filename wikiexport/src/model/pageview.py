class Pageview:

    @classmethod
    def instance_from_pageview_line(cls, pageview_line: str) -> 'Pageview':
        domain, page_title, view_counts, _ = pageview_line.split(' ')
        return cls(domain=domain, page_title=page_title, view_counts=int(view_counts))

    @classmethod
    def instance_from_balcklist(cls, blacklist_line: str) -> 'Pageview':
        domain, page_title = blacklist_line.split(' ')
        return cls(domain, page_title, None)

    def __init__(self, domain: str, page_title: str, view_counts: int) -> None:
        self.domain = domain
        self.page_title = page_title
        self.view_counts = view_counts

    def __str__(self):
        class_name, domain, page_title, view_counts = self.__class__, self.domain, self.page_title, self.view_counts
        return f'{class_name}(domain={domain}, page_title={page_title}, view_counts={view_counts})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.domain == other.domain and self.page_title == other.page_title

    def __hash__(self):
        return hash((self.domain, self.page_title))
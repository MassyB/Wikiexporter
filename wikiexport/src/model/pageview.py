class Pageview:
    """
    Class representing a pageview object
    """

    @classmethod
    def instance_from_pageview_line(cls, pageview_line: str) -> 'Pageview':
        """ Factory method to generate pageview instances from wikimedia pageview file. The last part of the line
        which the total size of the request is discarded

        :param pageview_line: string of pageview data. Example: a,main,23,2344
        :return: Pageview object
        """

        domain, page_title, view_count, _ = pageview_line.split(' ')

        return cls(domain=domain, page_title=page_title, view_count=int(view_count))


    @classmethod
    def instance_from_balcklist_line(cls, blacklist_line: str) -> 'Pageview':
        """ Factory method to generate pageview instance from a blacklist line

        :param blacklist_line: string of blacklist data of the form domain,page_veiw
        :return: Pageview object
        """

        domain, page_title = blacklist_line.split(' ')

        return cls(domain, page_title, None)


    def __init__(self, domain: str, page_title: str, view_count: int) -> None:
        """ Initialization of a pageview object

        :param domain: domain of the page
        :param page_title: title of the page
        :param view_count: number of views for that particular page on that particular domain
        """

        self.domain = domain
        self.page_title = page_title
        self.view_count = view_count


    def __str__(self) -> str:
        """ String representation of the object. Magic python function.

        :return: string representation of the object
        """

        class_name, domain, page_title, view_count = self.__class__, self.domain, self.page_title, self.view_count

        return f'{class_name}(domain={domain}, page_title={page_title}, view_count={view_count})'


    def __repr__(self):
        """ String representation of the object for debugging purposes

        :return: string representation of the object
        """

        return str(self)


    def __eq__(self, other: 'Pageview') -> bool:
        """ Two pageviews are equal if they have the same domain and the same page_title

        :param other:
        :return: True if domain and page_title of both object are equal, false otherwise
        """

        return self.domain == other.domain and self.page_title == other.page_title


    def __hash__(self) -> int:
        """ Returns a hash of the object which is based on the hash of the tuple (domain, page_title)

        :return: integer representing the hash of the instance
        """

        return hash((self.domain, self.page_title))
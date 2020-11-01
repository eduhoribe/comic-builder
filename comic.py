from dataclasses import dataclass


@dataclass
class Comic:
    title: str
    description: str
    alt_titles: set
    authors: set
    covers: list
    sauce: str

    def overwrite_user_metadata(self, args):
        self.title = args.title if args.title is not None else self.title
        self.description = args.description if args.description is not None else self.description
        self.alt_titles = args.alt_titles if args.alt_titles is not None else self.alt_titles
        self.authors = args.authors if args.authors is not None else self.authors
        self.covers = args.covers if args.covers is not None else self.covers
        self.sauce = args.sauce if args.sauce is not None else self.sauce

    @staticmethod
    def parse(comic_info_parser, comic_info_path):
        return comic_info_parser.parse(comic_info_path)

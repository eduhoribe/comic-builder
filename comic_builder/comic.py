from dataclasses import dataclass


@dataclass
class Comic:
    title: str
    description: str
    authors: list
    sauce: str
    volume_covers: dict

    def overwrite_user_metadata(self, args):
        self.title = args.title if args.title is not None else self.title
        self.authors = [args.authors] if args.authors is not None else self.authors

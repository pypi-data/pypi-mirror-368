from .dependency import Composer


class ComposerRepository:
    _composers: set[Composer] = set()

    @classmethod
    def add_composer(cls, composer: Composer) -> None:
        if composer in cls._composers:
            return
        existing_ids = {composer.id for composer in cls._composers}
        if composer.id in existing_ids:
            raise Exception(f'Duplicate composer with id {composer.id}')

        cls._composers.add(composer)

    @classmethod
    def get_composers(cls) -> set[Composer]:
        return cls._composers

    @classmethod
    def reset(cls) -> None:
        cls._composers = set()


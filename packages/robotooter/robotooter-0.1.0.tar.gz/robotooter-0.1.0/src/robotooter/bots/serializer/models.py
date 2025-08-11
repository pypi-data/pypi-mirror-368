from pydantic import BaseModel


class BookMetadata(BaseModel):
    title: str
    author: str
    about_title: str = ''
    about_book: str = ''
    about_author_link: str = ''
    about_title_link: str = ''
    first_text_link: str = ''
    total_days: int = 0
    current_day: int = 0
    schedule: str = ''

class ChapterMetadata(BaseModel):
    section: str
    section_title: str = ''
    section_start: bool
    chapter: str
    chapter_title: str = ''
    chapter_start: bool = False
    previous_link: str = ''

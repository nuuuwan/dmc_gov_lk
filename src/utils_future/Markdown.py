from utils import File, Log

log = Log('Markdown')


class Markdown:
    BLANK_LINE = ''

    def __init__(self):
        self.lines = []

    def hx(self, text, level):
        self.lines.extend([('#' * level) + ' ' + text, Markdown.BLANK_LINE])

    def h1(self, text):
        self.hx(text, 1)

    def h2(self, text):
        self.hx(text, 2)

    def h3(self, text):
        self.hx(text, 3)

    def p(self, text):
        self.lines.extend([text, Markdown.BLANK_LINE])

    def bold(self, text):
        return f'**{text}**'

    def italic(self, text):
        return f'*{text}*'

    def link(self, url, text=None):
        if text is None:
            text = url
        return f'[{text}]({url})'

    def image(self, url, alt_text=None):
        if alt_text is None:
            alt_text = url
        return f'![{alt_text}]({url})'

    def div(self, id, children):
        self.lines.extend(
            [f'<div id="{id}">', '', *children, '', '</div>', Markdown.BLANK_LINE]
        )

    def table(self, data_list, key_to_label=None):
        keys = data_list[0].keys()
        if key_to_label:
            labels = [key_to_label[key] for key in keys]
        else:
            labels = keys

        self.lines.extend(
            [
                '| ' + ' | '.join(labels) + ' |',
                '| ' + ' | '.join(['--:'] * len(labels)) + ' |',
            ]
        )

        for data in data_list:
            self.lines.extend(
                ['| ' + ' | '.join([str(data[key]) for key in keys]) + ' |']
            )
        self.lines.append(Markdown.BLANK_LINE)

   
    def __add__(self, other):
        assert isinstance(other, Markdown)
        new_md = Markdown()
        new_md.lines = self.lines + other.lines
        return new_md

    def save(self, file_path):
        File(file_path).write_lines(self.lines)
        log.info(f'Saved {file_path}')

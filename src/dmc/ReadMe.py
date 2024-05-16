import os

from utils import File, JSONFile, Log

from dmc.GenericDownloader import GenericDownloader

log = Log('ReadMe')


class ReadMe:
    @property
    def readme_path(self):
        return 'README.md'

    @staticmethod
    def get_lines_for_doc_type(dir_path):
        info_path = os.path.join(dir_path, 'info.json')
        d_list = JSONFile(info_path).read()
        d_list = sorted(d_list, key=lambda d: d['ut'], reverse=True)
        n_total = len(d_list)

        n_downloaded = 0
        for child_name in os.listdir(dir_path):
            if not child_name.endswith('.json'):
                continue
            n_downloaded += 1

        lines = [
            f'**{n_downloaded}/{n_total}** documents downloaded.',
            '',
        ]

        for d in d_list[:10]:
            file_path = GenericDownloader.get_file_path(dir_path, d)
            file_path_unix = file_path.replace('\\', '/')
            name_str = d["name"].strip()
            lines.append(f'* [{d["time_str"]} {name_str}]({file_path_unix})')
        lines.append('')
        return lines

    @property
    def lines_for_doc_types(self):
        lines = []
        for child_name in os.listdir('data'):
            child_path = os.path.join('data', child_name)
            if not os.path.isdir(child_path):
                continue
            title = child_name.replace('-', ' ').title()
            lines.extend(
                [
                    f'## {title}',
                    '',
                ]
                + ReadMe.get_lines_for_doc_type(child_path)
            )
        return lines

    @property
    def lines(self):
        url = GenericDownloader.BASE_URL
        return [
            '# Disaster Management Center (DMC) Sri Lanka :sri_lanka:',
            '',
            f'*Documents downloaded from [{url}]({url})*',
            '',
        ] + self.lines_for_doc_types

    def build(self):
        File(self.readme_path).write_lines(self.lines)
        log.info(f'Wrote {self.readme_path}')

import os
import shutil

from utils import Log

log = Log('copy_landslide_map')

DIR_LW = os.path.join('data', 'landslide-warnings')


def get_latest_landslide_warnings():
    pdf_files = []
    for pdf_file in os.listdir(DIR_LW):
        if pdf_file.endswith('.pdf'):
            pdf_files.append(pdf_file)
    pdf_files.sort()
    return os.path.join(DIR_LW, pdf_files[-1])


def main():
    latest_pdf_path = get_latest_landslide_warnings()
    log.debug(f'{latest_pdf_path=}')
    perma_path = 'landslide-warnings-latest.pdf'
    shutil.copy(latest_pdf_path, perma_path)
    log.info(f'Copied {latest_pdf_path} to {perma_path}')


if __name__ == "__main__":
    main()

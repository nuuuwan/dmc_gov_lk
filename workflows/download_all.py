from dmc import GenericDownloader, RiverWaterLevel


def main():
    for doc_type, report_type_id in [
        ['situation-reports', 1],
        ['weather-reports', 2],
        ['flood-inundation-maps', 3],
        ['emergency-response-data-viewer', 4],
        ['landslide-warnings', 5],
        [RiverWaterLevel.DOC_TYPE, 6],
        ['earthquakes', 7],
    ]:
        downloader = GenericDownloader(doc_type, report_type_id)
        downloader.download_all()


if __name__ == "__main__":
    main()

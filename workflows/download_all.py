from dmc import GenericDownloader


def main():
    GenericDownloader('situation-reports').download_all()


if __name__ == "__main__":
    main()

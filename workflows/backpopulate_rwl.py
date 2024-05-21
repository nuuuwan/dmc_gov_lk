from dmc import RiverWaterLevel


def main():
    pdf_path_list = RiverWaterLevel.get_pdf_path_list()
    pdf_path_list.reverse()
    for pdf_path in pdf_path_list:
        RiverWaterLevel.list_from_pdf(pdf_path)


if __name__ == "__main__":
    main()

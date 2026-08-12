from src.database import linkdb


if __name__ == '__main__':
    link = input("Input new link\n> ")
    linkdb.insert(link)

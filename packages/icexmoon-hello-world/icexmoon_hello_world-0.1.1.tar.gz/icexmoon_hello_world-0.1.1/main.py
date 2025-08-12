import requests
from rich.pretty import pprint


def main():
    print("Hello from hello-world!")
    resp = requests.get("https://peps.python.org/api/peps.json")
    data = resp.json()
    pprint([(k, v["title"]) for k, v in data.items()][:10])


if __name__ == "__main__":
    main()

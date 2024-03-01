import requests
import urllib.parse
import socket
from bs4 import BeautifulSoup
from collections import deque


def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return "Unable to resolve"


def find_connections(url):
    connections = set()
    try:
        response = requests.get(url, allow_redirects=True)
        print("HTTP Response Headers:")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        print("Resolved IP Address:", resolve_domain(response.url))

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find links from HTML tags
        for tag in soup.find_all(['a', 'img', 'script', 'link']):
            href = tag.get('href')
            src = tag.get('src')
            if href:
                connections.add(href)
            if src:
                connections.add(src)

    except requests.exceptions.RequestException as e:
        print("Error:", e)
    return connections


def crawl_site(base_url):
    visited = set()
    queue = deque([base_url])

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url)
            status_code = response.status_code
            print(f"URL: {url}, Status Code: {status_code}")

            if response.status_code == 200:
                connections = find_connections(url)
                print("Connections:")
                for connection in connections:
                    parsed_url = urllib.parse.urlparse(connection)
                    domain = parsed_url.netloc
                    path = parsed_url.path
                    print("Domain:", domain)
                    print("Path:", path)
                    print("Resolved IP:", resolve_domain(domain))
                    print()

                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    next_url = urllib.parse.urljoin(url, link['href'])
                    if next_url not in visited:
                        queue.append(next_url)
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")


def process_url(url):
    crawl_site(url)


if __name__ == "__main__":
    url = input("Enter the URL to check: ")
    process_url(url)

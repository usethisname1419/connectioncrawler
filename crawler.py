import time

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


def find_connections(url, base_url):
    connections = set()
    connection_info = []

    try:
        response = requests.get(url, allow_redirects=True)
        info = {
            "URL": url,
            "HTTP Response Headers": {header: value for header, value in response.headers.items()},
            "Resolved IP Address": resolve_domain(urllib.parse.urlparse(response.url).netloc),
            "Connections": set()
        }

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find links from HTML tags
        for tag in soup.find_all(['a', 'img', 'script', 'link']):
            href = tag.get('href')
            src = tag.get('src')
            if href:
                connections.add(href)
                parsed_url = urllib.parse.urlparse(href)
                domain = parsed_url.netloc
                path = parsed_url.path
                resolved_ip = resolve_domain(domain)
                connection_info.append({"Domain": domain, "Path": path, "Resolved IP": resolved_ip})
            if src:
                connections.add(src)
                parsed_url = urllib.parse.urlparse(src)
                domain = parsed_url.netloc
                path = parsed_url.path
                resolved_ip = resolve_domain(domain)
                connection_info.append({"Domain": domain, "Path": path, "Resolved IP": resolved_ip})

        print("HTTP Response Headers:")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        print("IP Address:", info["Resolved IP Address"])
        print("\n-----")
        print("Connections:")
        time.sleep(0.6)
        for info in connection_info:
            print("Domain:", info["Domain"])
            print("Path:", info["Path"])
            print("Resolved IP:", info["Resolved IP"])
            print()

    except requests.exceptions.RequestException as e:
        print("Error:", e)

    return connections, info

def crawl_site(base_url):
    visited = set()
    queue = deque([base_url])
    base_domain = urllib.parse.urlparse(base_url).netloc  # Extract the domain of the base URL
    report = []

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url)
            status_code = response.status_code
            info = {
                "URL": url,
                "Status Code": status_code
            }
            print("=INFO=======================================")
            print(f"URL: {url}, Status Code: {status_code}")
            if response.status_code == 200:
                connections, conn_info = find_connections(url, base_url)
                info.update(conn_info)
                report.append(info)

                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    next_url = urllib.parse.urljoin(url, link['href'])
                    parsed_next_url = urllib.parse.urlparse(next_url)
                    # Check if the domain of the next URL matches the domain of the base URL
                    if parsed_next_url.netloc == base_domain:
                        queue.append(next_url)
            else:
                report.append(info)

         
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
            print("-" * 50)

    return report



def make_report(report, filename):
    with open(filename, "w") as file:
        for info in report:
            file.write("URL: {}\n".format(info["URL"]))
            file.write("Status Code: {}\n".format(info.get("Status Code", "N/A")))
            if "HTTP Response Headers" in info:
                file.write("HTTP Response Headers:\n")
                for header, value in info["HTTP Response Headers"].items():
                    file.write(f"{header}: {value}\n")
            file.write("Resolved IP Address: {}\n".format(info.get("Resolved IP Address", "N/A")))
            if "Connections" in info:
                file.write("Connections:\n")
                for connection in info["Connections"]:
                    file.write(f"  {connection}\n")
            file.write("\n")


if __name__ == "__main__":
    try:
        url = input("Enter the URL to check: ")
        report_filename = input("Enter the filename to save the report: ")
        report = crawl_site(url)
        make_report(report, report_filename)
    except KeyboardInterrupt:
        print("ended")
    except Exception as e:
        print(f"error {e}")

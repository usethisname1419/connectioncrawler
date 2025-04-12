import time
import random
import requests
import urllib.parse
import socket
from bs4 import BeautifulSoup
from collections import deque

# List of common user agents to randomly choose from
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
]

# Your URLhaus API key
API_KEY = 'put urlaus key here'

def get_random_user_agent():
    """Return a random user agent from the list"""
    return random.choice(USER_AGENTS)

def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return "Unable to resolve"

def check_malicious_ip(ip):
    """Check if the IP is malicious using URLhaus"""
    try:
        print(f"Checking IP: {ip}")
        headers = {'API-Key': API_KEY}
        response = requests.get(f"https://urlhaus-api.abuse.ch/v1/host/{ip}/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("query_status") == "ok":
                return True
        return False
    except requests.RequestException as e:
        print(f"Error checking IP {ip}: {e}")
        return False

def find_connections(url, base_url, checked_ips):
    connections = set()
    connection_info = []

    try:
        headers = {'User-Agent': get_random_user_agent()}
        print(f"Fetching URL: {url} with headers: {headers}")
        response = requests.get(url, allow_redirects=True, headers=headers)
        info = {
            "URL": url,
            "HTTP Response Headers": {header: value for header, value in response.headers.items()},
            "Resolved IP Address": resolve_domain(urllib.parse.urlparse(response.url).netloc),
            "Connections": set()
        }

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find links from HTML tags
        for tag in soup.find_all(['a', 'img', 'script', 'link', 'iframe', 'video', 'audio', 'svg', 'object', 'embed', 'form', 'source', 'track', 'applet', 'meta', 'noscript']):
            href = tag.get('href')
            src = tag.get('src')
            if href:
                connections.add(href)
                parsed_url = urllib.parse.urlparse(href)
                domain = parsed_url.netloc
                path = parsed_url.path
                resolved_ip = resolve_domain(domain)
                is_malicious = check_malicious_ip(resolved_ip)
                connection_info.append({"Domain": domain, "Path": path, "Resolved IP": resolved_ip, "Malicious": is_malicious})
            if src:
                connections.add(src)
                parsed_url = urllib.parse.urlparse(src)
                domain = parsed_url.netloc
                path = parsed_url.path
                resolved_ip = resolve_domain(domain)
                is_malicious = check_malicious_ip(resolved_ip)
                connection_info.append({"Domain": domain, "Path": path, "Resolved IP": resolved_ip, "Malicious": is_malicious})

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
            print("Malicious:", info["Malicious"])
            print()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")

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
            headers = {'User-Agent': get_random_user_agent()}
            print(f"Crawling URL: {url} with headers: {headers}")
            response = requests.get(url, headers=headers)
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

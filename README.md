# Connection Crawler

Site Checker is a Python script that checks a website for outgoing connections, resolves domain names, and generates a report of the findings. It can be used to inspect websites for potentially malicious scripts, connections, or other suspicious activity.

Can be used to find unwanted connections and malware

## Features

- Checks for outgoing connections from the specified website.
- Resolves domain names to their corresponding IP addresses.
- Generates a detailed report containing HTTP response headers, resolved IP addresses, and connections made by the website.
- Supports analysis of HTML tags including <a>, <img>, <script>, and <link>.
- Uses BeautifulSoup for HTML parsing and Requests for HTTP requests.

## Usage

1. Clone the repository:

    ```
    git clone https://github.com/your-username/site-checker.git
    ```

2. Navigate to the project directory:

    ```
    cd site-checker
    ```

3. Install the required dependencies:

    ```
    pip install -r requirements.txt
    ```

4. Run the script:

    ```
    python crawler.py
    ```

5. Follow the prompts to enter the URL to check and specify the filename for the report.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Requests](https://docs.python-requests.org/en/latest/) - HTTP library for making requests in Python.
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Python library for pulling data out of HTML and XML files.

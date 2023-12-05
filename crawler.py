import requests
import random
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib import robotparser
from langdetect import detect
from datetime import datetime
from urllib.parse import urlparse



# Initialize log files and configuration parameters
log_file = open('crawler.txt', 'w')  # Log for crawled URLs
sample_file = open('sample.txt', 'w')  # Log for sampled URLs
sample_file2 = open('sample2.txt', 'w')  # Alternate log for sampled URLs
log_page = open('parsedPages.txt', 'w', encoding="UTF-8")  # Log for parsed pages
max_url_length = 150  # Maximum URL length allowed
sampling_rate = 0.1  # Sampling rate for URLs
url = "https://www.nyu.edu/"  # Starting URL

domain_counts = {}  # Dictionary to store domain counts

# List of prime numbers for sampling
prime_list = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149]


# List of suspicious patterns
suspicious_patterns = [
    "honeypot",
    "block",
    "trap",
    "captcha",
    "login",
    "signup",
    "sign-up",
    "signin",
    "sign-in",
    "logout",
    "signout",
    "error",
    "forbidden",
    "access-denied",
    "admin",
    "dashboard",
    "reset-password",
    "forgot-password",
    "filemaker",
    "claris",
    "bdp",
    "tumblr",
    "free",
    "trial",
    "account",
    "support",
    "page",
    "twitter",
    "instagram",
    "tiktok",
    "community",
    "next",
    "previous",
    "answer",
    "questions", 
    "date",
    "uptodate",
    "googleblog",
    "youtube",
    "apple",
    "privacy",
    "policy",
    "bookdash",
    "gobierno",
    "github",
    "stackoverflow",
    "gnupg",
    "calea",
    "bbb",
    "salliemae",
    "globalprivacyassembly",
    "google",
    "blackbaud",
    "nycitycenter",
    "museumofmodernemail",
    "golfdaleconsulting",
    "trustarc",
    "personio",
    "sorryapp",
    "etsy",
    "amazon",
    "ruffalonl",
    "player",
    "ftc",
    "parkerdewey",
    "stargentiot",
    "adrenalinemarketingpros",
    "spinxdigital",
    "beian"
]


# List of ignored file extensions
ignored_file_extensions = (
    ".css",                   # Cascading Style Sheets
    ".js",                    # JavaScript
    ".jpg", ".jpeg", ".png",  # Images
    ".gif", ".bmp", ".svg", ".ico",  # Images
    ".mp4", ".webm", ".avi", ".mov",  # Video
    ".mp3", ".ogg", ".wav",   # Audio
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt", ".csv", ".md",  # Documents
    ".zip", ".rar", ".tar.gz", ".7z",  # Archives
    ".xml",                   # XML
    ".json",                  # JSON
    ".rss", ".atom", ".xml",  # Feeds and Syndication
    ".ttf", ".otf", ".woff", ".woff2",  # Fonts
    ".exe", ".msi", ".dmg", ".app",  # Executable Files
    ".py", ".php", ".rb", ".java", ".cs", ".c", ".cpp", ".h",  # Scripts and Code
    ".sqlite", ".db", ".sql", ".csv",  # Database Files
    ".plugin", ".extension", ".dll", ".so",  # Plugins and Add-ons
    ".log", ".config", ".ini", ".bak", ".tmp", ".cache",  # Miscellaneous
)

def log_visited_urls(message):
    # Write the log message to the crawled URLs file
    log_file.write(message + '\n')

def log_sample_urls(message):
    # Write the log message to the sampled URLs file
    sample_file.write(message + '\n')

def log_sample2_urls(message):
    # Write the log message to the alternate sampled URLs file
    sample_file2.write(message + '\n')

def log_visited_pages(page_title, page_body):
    # Write the page title and body to the parsed pages file
    log_page.write(page_title + "\n" + page_body + "\n" + "*************************************************************************************************************************************************************************************\n")

def calculate_priority(url):
    # Calculate priority for a given URL
    if "tumblr" in url.lower():
        return 5
    elif "signin" in url.lower() or "signup" in url.lower():
        return 4
    elif "wiki" in url.lower() or url.startswith('https://en') or 'cooking' in url.lower():
        return 3
    elif "common" in url.lower():
        return 2
    elif url.startswith("https://www.nytimes"):
        return 1
    else:
        return 0

def is_suspicious_url(url):
    # Check if the URL matches any suspicious patterns
    for pattern in suspicious_patterns:
        if pattern in url:
            return True
    return False

def ignore_urls_with_multiple_paths(url):
    # Check if the URL has more than 6 path segments
    cleaned_url = url.split('://', 1)[1]
    if cleaned_url.endswith('/'):
        cleaned_url = cleaned_url[:-1]
    if cleaned_url.count('/') > 6:
        return True
    return False

def update_statistics_file(statistics):
    # Write statistics to a file
    try:
        with open('statistics.txt', 'w') as file:
            file.write(f"Total Pages Crawled: {statistics['parsed_count']}\n")
            file.write(f"Success Count: {statistics['success_count']}\n")
            file.write(f"Error Count: {statistics['error_count']}\n")
            file.write(f"Server Error Count: {statistics['server_error']}\n")
            file.write(f"Skipped Count: {statistics['skipped_count']}\n")
            file.write(f"Total Size of Files: {statistics['total_size_of_files']} bytes\n")
            file.write(f"English Pages: {statistics['en']}\n")
            file.write(f"Sampled English Pages: {statistics['sample_en']}\n")
            file.write(f"Sampled English Pages (Alternate): {statistics['sample_en2']}\n")
            file.write(f"Chinese Pages: {statistics['zh']}\n")
            file.write(f"Sampled Chinese Pages: {statistics['sample_zh']}\n")
            file.write(f"Sampled Chinese Pages (Alternate): {statistics['sample_zh2']}\n")
            file.write(f"Spanish Pages: {statistics['es']}\n")
            file.write(f"Sampled Spanish Pages: {statistics['sample_es']}\n")
            file.write(f"Sampled Spanish Pages (Alternate): {statistics['sample_es2']}\n")
            file.write(f"Dutch Pages: {statistics['nl']}\n")
            file.write(f"Sampled Dutch Pages: {statistics['sample_nl']}\n")
            file.write(f"Sampled Dutch Pages (Alternate): {statistics['sample_nl2']}\n")
            file.write(f"Miscellaneous Pages: {statistics['misc']}\n")
            file.write(f"Sampled Miscellaneous Pages: {statistics['sample_misc']}\n")
            file.write(f"Sampled Miscellaneous Pages (Alternate): {statistics['sample_misc2']}\n")

            file.write("\nDomain Counts:\n")
            for domain, count in domain_counts.items():
                file.write(f"{domain}: {count}\n")
    except Exception as e:
        print(f"Statistics file writing failed due to {e}")


def get_current_url(crawl_stack, parsed_count):
    # Get the current URL from the crawl stack
    priority, current_url, current_depth = crawl_stack.pop()
    while ignore_urls_with_multiple_paths(current_url):
        priority, current_url, current_depth = crawl_stack.pop()
    if parsed_count > 4000 and parsed_count % random.randint(10, 100) == 0:
        priority, current_url, current_depth = crawl_stack.pop(random.choice(range(len(crawl_stack) - 1)))
    else:
        dummy_depth = current_depth
        if current_depth > random.randint(125, 150):
            while crawl_stack and dummy_depth > min(crawl_stack)[0] + 1:
                dummy_prio, dummy_url, dummy_depth = crawl_stack.pop()
            priority, current_url, current_depth = crawl_stack.pop(0)
    return priority, current_url, current_depth

def calculate_count(en, zh, es, nl, misc, detected_language):
    # Calculate language count based on detected language
    if 'en' in detected_language.lower():
        en += 1
    elif 'zh' in detected_language.lower():
        zh += 1
    elif 'es' in detected_language.lower():
        es += 1
    elif 'nl' in detected_language.lower():
        nl += 1
    else:
        misc += 1
    return en, zh, es, nl, misc

def crawl_website(url):
    # Function to crawl through pages
    counter = 0
    crawl_stack = [(calculate_priority(url), url, 0)]
    visited_urls = set()
    success_count = 0 # Number of web pages that returned a status code 2xx
    error_count = 0 # Number of web pages that returned a status code 4xx
    server_error = 0 # Number of web pages that returned a status code 5xx
    skipped_count = 0 # Number of urls skipped due to urls or robot parsers
    total_size_of_files = 0
    parsed_count = 0 # Number of successfully parsed web page
    en = sample_en = sample_en2 = 0
    zh = sample_zh = sample_zh2 = 0
    es = sample_es = sample_es2 = 0
    nl = sample_nl = sample_nl2 = 0
    misc = sample_misc = sample_misc2 = 0

    while crawl_stack:
        priority, current_url, current_depth = get_current_url(crawl_stack, parsed_count)
        if current_url.endswith(ignored_file_extensions):
            skipped_count += 1
            print(f"Ignoring URL: {current_url} (File extension is not supported)")
            continue
        if len(current_url) >= max_url_length:
            skipped_count += 1
            print(f"Skipping URL: {current_url} (Exceeds maximum URL length)")
            continue
        if current_url not in visited_urls:
            if len(visited_urls) > 10000:
                try:
                    raise Exception("Exiting the loop")
                except Exception as e:
                    return
            try:
                domain = current_url.split('//')[1].split('/')[0]
                rp = robotparser.RobotFileParser()
                rp.set_url(f"https://{domain}/robots.txt")
                rp.read()

                if rp.can_fetch("*", current_url):
                    # Sleep for the random duration
                    time.sleep(random.randint(1, 5))
                    
                    response = requests.get(current_url, timeout=10)
                    log_visited_urls(f"URL: {current_url}, Time: {datetime.now()}, Size:{len(response.content)} bytes, Return Code: {response.status_code}")
                    total_size_of_files = total_size_of_files + len(response.content)
                    
                    if 200 <= response.status_code < 300:
                        success_count = success_count + 1
                    elif 400 <= response.status_code < 500:
                        error_count = error_count + 1
                    elif 500 <= response.status_code < 600:
                        server_error = server_error + 1
                    
                    sample_integer = random.choice(prime_list)
                    sample_integer2 = random.random()
                    
                    if 200 <= response.status_code < 300:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        url_scheme = urlparse(current_url).scheme
                        excluded_schemes = ['mailto', 'javacript', 'javascript', 'file', 'about', 'tel', 'sms']
                        
                        if url_scheme not in excluded_schemes:
                            page_title = soup.title.string.strip() if soup.title else "No title"
                            body_text = soup.body.get_text()
                            if domain in domain_counts:
                                domain_counts[domain] += 1
                            else:
                                domain_counts[domain] = 1
                            
                            log_visited_pages(page_title, body_text)
                            detected_language = detect(body_text)
                            
                            # sample_integer2 is for the sampling function that uses the random number generator
                            if sample_integer2 < sampling_rate:
                                if 'en' in detected_language.lower() or 'zh' in detected_language.lower() or 'es' in detected_language.lower() or 'nl' in detected_language.lower():
                                    log_sample2_urls(f"URL: {current_url}, Time: {datetime.now()}, Size:{len(response.content)} bytes, Return Code: {response.status_code}, Language: {detected_language}, Taken for sampling: Yes")
                                else:
                                    log_sample2_urls(f"URL: {current_url}, Time: {datetime.now()}, Size:{len(response.content)} bytes, Return Code: {response.status_code}, Language: misc({detected_language}), Taken for sampling: Yes")
                            # sample_integer is for the sampling function that uses the randomly picked prime numbers
                            if counter % sample_integer == 0:
                                if 'en' in detected_language.lower() or 'zh' in detected_language.lower() or 'es' in detected_language.lower() or 'nl' in detected_language.lower():
                                    log_sample_urls(f"URL: {current_url}, Time: {datetime.now()}, Size:{len(response.content)} bytes, Return Code: {response.status_code}, Language: {detected_language}, Taken for sampling: Yes")
                                else:
                                    log_sample_urls(f"URL: {current_url}, Time: {datetime.now()}, Size:{len(response.content)} bytes, Return Code: {response.status_code}, Language: misc({detected_language}), Taken for sampling: Yes")
                            print(f"Depth: {current_depth}, Priority {priority}: {page_title} - {current_url}, \n Language: {detected_language}")
                            
                            en, zh, es, nl, misc = calculate_count(en, zh, es, nl, misc, detected_language)
                            
                            if sample_integer2 < sampling_rate:
                                sample_en2, sample_zh2, sample_es2, sample_nl2, sample_misc2 = calculate_count(sample_en2, sample_zh2, sample_es2, sample_nl2, sample_misc2, detected_language)
                            if counter % sample_integer == 0:
                                sample_en, sample_zh, sample_es, sample_nl, sample_misc = calculate_count(sample_en, sample_zh, sample_es, sample_nl, sample_misc, detected_language)
                            
                            parsed_count += 1
                            visited_urls.add(current_url)
                            counter += 1
                            statistics = {
                                'parsed_count': parsed_count,
                                'success_count': success_count,
                                'error_count': error_count,
                                'server_error': server_error,
                                'total_size_of_files': total_size_of_files,
                                'en': en,
                                'sample_en': sample_en,
                                'sample_en2': sample_en2,
                                'zh': zh,
                                'sample_zh': sample_zh,
                                'sample_zh2': sample_zh2,
                                'es': es,
                                'sample_es': sample_es,
                                'sample_es2': sample_es2,
                                'nl': nl,
                                'sample_nl': sample_nl,
                                'sample_nl2': sample_nl2,
                                'misc': misc,
                                'sample_misc': sample_misc,
                                'sample_misc2': sample_misc2,
                                'domain_counts': domain_counts,
                                'skipped_count': skipped_count
                            }
                            update_statistics_file(statistics)
                            
                            try:
                                for link in soup.find_all('a', href=True):
                                    absolute_url = urljoin(current_url, link['href'])
                                    if absolute_url.endswith(ignored_file_extensions) or '#' in link['href']:
                                        continue
                                    
                                    if is_suspicious_url(absolute_url):
                                        continue
                                    
                                    sub_url_scheme = urlparse(absolute_url).scheme
                                    if sub_url_scheme in excluded_schemes:
                                        continue
                                    
                                    sub_domain = absolute_url.split('//')[1].split('/')[0]
                                    if absolute_url not in crawl_stack and absolute_url not in visited_urls:
                                        if (domain_counts.get(sub_domain, 0) > 10):
                                            crawl_stack.append((4, absolute_url, current_depth + 1))
                                        else:
                                            crawl_stack.append((calculate_priority(absolute_url), absolute_url, current_depth + 1))
                            except Exception as e:
                                print(f"Error looping for child {absolute_url} of parent {current_url} as {e}")
                                continue
                        else:
                            print(f"Failed to fetch {current_url} due to unsupported format")
                            continue
                    else:
                        print(f"Failed to fetch {current_url} - Status code: {response.status_code}")
                        continue
                else:
                    skipped_count += 1
                    print(f"Skipping {current_url} as per robots.txt rules")
                    continue
            except Exception as e:
                print(f"Error processing {current_url}: {str(e)}")
                continue
        else:
            print('URL list exhausted or current url already parsed')
            continue

    print('Crawl Stack Emptied!!')
    return 'Crawling Complete'

if __name__ == "__main__":
    start_time = time.time()
    result = crawl_website(url)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken to parse: {total_time} seconds")

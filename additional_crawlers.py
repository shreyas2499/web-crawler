

def crawl_website_breadth(url):
    # Function to crawl through pages
    
    
    # Create a priority queue to store URLs to visit
    crawl_queue = []
    crawl_queue.append((calculate_priority(url), url))
    heapq.heapify(crawl_queue)
  
    # Create a set to store visited URLs
    visited_urls = set()

    # To store count of each encountered language
    languages = {}
    languages = defaultdict(lambda: 0, languages)

    # Below variables store count of parsed pages, skipped pages, English pages, Chinese pages, Spanish pages, Dutch pages, 
    # and all other languages together.
    parsedCount = 0
    skippedCount = 0
    en = 0
    zh = 0
    es = 0
    nl = 0
    misc = 0

    while crawl_queue:
        # Get the URL with the highest priority
        priority, current_url = heapq.heappop(crawl_queue)
        
        new_priority = 999  
        updated_item = (new_priority, current_url)
        heapq.heappush(crawl_queue, updated_item)

        if current_url not in visited_urls and len(visited_urls) <= 20000:
            try:

                if current_url.endswith(('.gz', '.tar.gz', '.tgz', '.jpg', '.jpeg', '.pdf', '.zip')):
                    print(f"Ignoring URL: {current_url} (File extension is not supported)")
                    continue

                if len(current_url) >= max_url_length:
                    print(f"Skipping URL: {url} (Exceeds maximum URL length)")
                    continue
                # time.sleep(random.uniform(1, 10))
                domain = current_url.split('//')[1].split('/')[0]
                rp = robotparser.RobotFileParser()
                rp.set_url(f"https://{domain}/robots.txt")
                rp.read()

                # Check if the URL is allowed by the robots.txt file
                if rp.can_fetch("*", current_url):

                    # time.sleep(random.uniform(1, 10))
                    # Send an HTTP GET request to the current URL
                    response = requests.get(current_url, timeout=10)


                    # Logging into the file
                    log_visited_urls(f"URL: {current_url}, Time: {datetime.now()}, Size:{len(response.content)} bytes, Return Code: {response.status_code}")

                    if response.status_code == 200:
                        # Parse the HTML content of the page
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # # Check the file extension of the URL
                        # file_extension = Path(urlparse(current_url).path).suffix.lower()
                       
                        # # Define a list of allowed file extensions (e.g., ".html", ".htm")
                        # allowed_extensions = ['.html', '.htm']

                        # Extract the URL scheme
                        url_scheme = urlparse(current_url).scheme
                       
                        # Define a list of schemes to exclude
                        excluded_schemes = ['mailto', 'javascript', 'file', 'about']


                        if url_scheme not in excluded_schemes:

                            # Process the page (e.g., extract data, store links)
                            page_title = soup.title.string.strip() if soup.title else "No title"

                            # if(page_title_filter(page_title)):
                            #     continue

                            body_text = soup.body.get_text()

                            # Check if the domain is in the domain_counts dictionary
                            if domain in domain_counts:
                                domain_counts[domain] += 1
                            else:
                                domain_counts[domain] = 1

                            

                            # Logging the content of the pages
                            log_visited_pages(page_title, body_text)


                            print(f"Priority {priority}: {page_title} - {current_url}, \n Language: {detect(body_text)}")

                            if('en' in detect(body_text).lower()):
                                en += 1
                            elif('zh' in detect(body_text).lower()):
                                zh += 1
                            elif('es' in detect(body_text).lower()):
                                es += 1
                            elif('nl' in detect(body_text).lower()):
                                nl += 1
                            else:
                                misc += 1
                            parsedCount += 1

                            # print(soup.find_all('a', href=True), "\n")

                            # Extract and add links to the priority queue with their priorities
                            for link in soup.find_all('a', href=True):
                                
                                # if('references' not in link['href'].lower() and '#' in link['href']):
                                #     continue
                                absolute_url = urljoin(current_url, link['href'])

                                # if('web' in absolute_url):
                                #     print('asdsad')

                                if('tumblr' in absolute_url or "directory.fsf.org" in absolute_url or ".php" in absolute_url):
                                    continue
                                
                                if(absolute_url=='https://cn.nytimes.com'):
                                    print("test")

                                sub_domain = absolute_url.split('//')[1].split('/')[0]
                                # Check if the URL is not already in the crawl queue or visited_urls
                                if absolute_url not in crawl_queue and absolute_url not in visited_urls:
                                    if(domain_counts.get(sub_domain, 0)>10):
                                        heapq.heappush(crawl_queue, (4, absolute_url))
                                    else:
                                        heapq.heappush(crawl_queue, (calculate_priority(absolute_url), absolute_url))

                            # Mark the current URL as visited
                            visited_urls.add(current_url)
                        else:
                            print(f"Failed to fetch {current_url} due to unsupported format")
                            continue  
                    else:
                        print(f"Failed to fetch {current_url} - Status code: {response.status_code}")
                        continue
                else:
                    print(f"Skipping {current_url} as per robots.txt rules")
                    skippedCount += 1
                    continue
            except Exception as e:
                print(f"Error processing {current_url}: {str(e)}")
                continue
        else:
            print('URL list exhausted or current url already parsed')
            continue

    return languages, parsedCount,skippedCount  


def crawl_website_initial(url):
    # Create a set to store visited URLs
    visited_urls = set()

    # To store count of each encountered language
    languages = {}
    languages = defaultdict(lambda: 0, languages)
    
    # Create a list to store URLs to visit
    to_visit = [(url, 0)]
    
    # Initialize the robot parser for the website
    parsedCount = 0
    totalParsedCount = 0
    skippedCount = 0
    en = 0
    zh = 0
    es = 0
    nl = 0
    misc = 0
    while to_visit:
        # if(parsedCount>1 and parsedCount % 8 == 0):
        #     a = int((len(to_visit)/2))+1
        #     current_url, current_depth = to_visit.pop(int((len(to_visit)/2))+1)
        # elif(parsedCount>1 and parsedCount % 28 == 0):
        #     b = random.randint(0, len(to_visit))
        #     current_url, current_depth = to_visit.pop(random.randint(0, len(to_visit)))
        # else:
        #     current_url, current_depth = to_visit.pop(0)
            

        current_url, current_depth = random.choice(to_visit)
    

        if current_url not in visited_urls and len(visited_urls) <= 20000:
            try:
                time.sleep(random.uniform(1,10))
                domain = current_url.split('//')[1].split('/')[0]
                rp = robotparser.RobotFileParser()
                rp.set_url(f"https://{domain}/robots.txt")
                rp.read()

                # Check if the URL is allowed by the robots.txt file
                if rp.can_fetch("*", current_url):
                    
                    time.sleep(random.uniform(1,10))
                    # try:
                        # Send an HTTP GET request to the current URL
                    response = request.urlopen(current_url, timeout=5)
                    # except requests.exceptions.Timeout:
                    #     print(f"{current_url} request Timed out")
                    #     continue
                    log_visited_urls(f"URL: {current_url}, Time: {datetime.now()}, Size:{len(response.content)}, Return Code: {response.status_code}")
                    if response.status_code == 200:
                        # Parse the HTML content of the page
                        soup = BeautifulSoup(response.text, 'html.parser')
                        

                        # for anchors in soup.find_all('a', href=True):
                        #     print(anchors, "\n\n\n")
                        
                        # for images in soup.find_all('img', href=True):
                        #     print(images, "\n\n\n")
                        
                        # for base in soup.find_all('base', href=True):
                        #     print(base, "\n\n\n")
                        
                        # print('link' in soup)

                        # for links in soup.find_all('link', href=True):
                        #     print(links, "\n\n\n")
                        
                        # for area in soup.find_all('area', href=True):
                        #     print(area, "\n\n\n")
                        


                        # Process the page (e.g., extract data, store links)
                        # For now, let's print the page title
                        page_title = soup.title.string.strip() if soup.title else "No title"
                        
                        if(page_title_filter(page_title)):
                            continue

                        if(current_url=='https://www.themoscowtimes.com/2023/09/21/azerbaijans-aliyev-apologizes-for-russian-peacekeeper-deaths-in-karabakh-a82533'):
                            print('something2')

                        if("Azerbaijan" in page_title):
                            print('something')
                        body_text = soup.body.get_text()

                        print(f"Depth {current_depth}: {page_title} - {current_url}, \n Language: {detect(body_text)}")

                        
                        # languages[detect(body_text)] = languages[detect(body_text)] + 1
                        if(detect(body_text) == 'en'):
                            en += 1
                        elif(detect(body_text) == 'zh'):
                            zh += 1
                        elif(detect(body_text) == 'es'):
                            es += 1
                        elif(detect(body_text) == 'nl'):
                            nl += 1
                        else:
                            misc += 1
                        parsedCount += 1
                        # totalParsedCount += 1
                        # en += 1
                        # if(en == 230):
                        #     print('stop')
                        # if(detect(body_text) == 'en'):
                        #     # en += 1
                        #     if(languages[detect(body_text)] == 0):
                        #         print(languages[detect(body_text)])

                        # if(detect(body_text) != 'en'):
                        #     print(detect(body_text))

                        # Extract and add li55688nks to the list of URLs to visit:
                        for link in soup.find_all('a', href=True):
                            absolute_url = urljoin(current_url, link['href'])
                            # sub_domain = current_url.split('//')[1].split('/')[0]

                            # if(sub_domain == domain):
                            if(absolute_url not in to_visit and (len(to_visit)<100 or 'wiki' not in absolute_url)):
                                to_visit.append((absolute_url, current_depth + 1))
                        
                        # Mark the current URL as visited
                        visited_urls.add(current_url)
                    else:
                        print(f"Failed to fetch {current_url} - Status code: {response.status_code}")
                        continue
                else:
                    print(f"Skipping {current_url} as per robots.txt rules")
                    skippedCount += 1
                    continue
            except Exception as e:
                print(f"Error processing {current_url}: {str(e)}")
                continue
        else:
            print('URL list exhausted or current url already parsed')
            continue
                

    return languages, parsedCount, totalParsedCount, skippedCount  


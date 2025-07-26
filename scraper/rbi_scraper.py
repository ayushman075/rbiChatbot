import requests
import csv
from bs4 import BeautifulSoup as bs
import hashlib
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HOME_URL = "https://www.rbi.org.in/"

class RBICSVScraper:
    def __init__(self, csv_filename='rbi_complete_data.csv'):
        self.csv_filename = csv_filename
        self.scraped_urls = set()
        self.content_hashes = set()
        self.processed_count = 0
        self.duplicate_count = 0
        
        # Initialize CSV file
        self.init_csv()
        
        # Session for better performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def init_csv(self):
        """Initialize CSV file with headers"""
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Topic', 'URL', 'Content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        logger.info(f"Initialized CSV file: {self.csv_filename}")
    
    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters that might cause CSV issues
        text = text.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
        return text
    
    def is_duplicate_content(self, content):
        """Check if content is duplicate using hash"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        if content_hash in self.content_hashes:
            return True
        self.content_hashes.add(content_hash)
        return False
    
    def write_to_csv(self, url, topic, content):
        """Write data to CSV with duplicate checking"""
        # Clean the content
        cleaned_content = self.clean_text(content)
        cleaned_topic = self.clean_text(topic)
        
        # Skip if content is too short or empty
        if len(cleaned_content) < 50:
            logger.warning(f"Content too short for URL: {url}")
            return False
        
        # Check for duplicate content
        if self.is_duplicate_content(cleaned_content):
            self.duplicate_count += 1
            logger.info(f"Duplicate content skipped: {url}")
            return False
        
        try:
            with open(self.csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Topic', 'URL', 'Content']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({
                    'Topic': cleaned_topic,
                    'URL': url,
                    'Content': cleaned_content
                })
            
            self.processed_count += 1
            logger.info(f"Saved ({self.processed_count}): {cleaned_topic[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to write to CSV for {url}: {e}")
            return False
    
    def extract_topic_from_url_or_content(self, url, soup):
        """Extract topic from URL or page content"""
        # Try to get title from page
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title and title != "RBI" and len(title) > 5:
                return title
        
        # Try to get from h1, h2, h3 tags
        for heading_tag in ['h1', 'h2', 'h3']:
            heading = soup.find(heading_tag)
            if heading and heading.get_text().strip():
                return heading.get_text().strip()
        
        # Try to get from bold tags (first meaningful one)
        bold_tags = soup.find_all('b')
        for bold in bold_tags:
            text = bold.get_text().strip()
            if len(text) > 10 and len(text) < 200:  # Reasonable title length
                return text
        
        # Extract from URL as fallback
        path = urlparse(url).path
        if path:
            # Remove file extensions and clean up
            topic = path.split('/')[-1]
            topic = re.sub(r'\.[^.]*$', '', topic)  # Remove extension
            topic = topic.replace('_', ' ').replace('-', ' ')
            if len(topic) > 3:
                return topic.title()
        
        return "RBI Document"
    
    def scrape_data(self, url):
        """Scrape data from a single URL"""
        if url in self.scraped_urls:
            return False
        
        self.scraped_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                logger.warning(f"Failed to access {url}: Status {response.status_code}")
                return False
            
            soup = bs(response.text, 'html.parser')
            
            # Extract topic
            topic = self.extract_topic_from_url_or_content(url, soup)
            
            # Extract content (following your working approach)
            heading = soup.find_all('b')
            paragraphs = soup.find_all('p')
            
            # Also try other content tags
            divs = soup.find_all('div')
            tables = soup.find_all('table')
            
            all_content = ""
            
            # Get headings
            for content in heading:
                text = content.get_text().strip()
                if text:
                    all_content += text + " "
            
            # Get paragraphs
            for content in paragraphs:
                text = content.get_text().strip()
                if text:
                    all_content += text + " "
            
            # Get meaningful div content
            for div in divs:
                text = div.get_text().strip()
                if len(text) > 100 and len(text) < 5000:  # Filter meaningful content
                    all_content += text + " "
            
            # Get table content
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_text = ' | '.join([cell.get_text().strip() for cell in cells])
                    if row_text.strip():
                        all_content += row_text + " "
            
            # Clean and save
            final_content = self.clean_text(all_content)
            if final_content:
                return self.write_to_csv(url, topic, final_content)
            
            return False
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return False
    
    def crawler1(self, url):
        """Crawl pages with class 'link2' links"""
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return
            
            soup = bs(response.text, 'html.parser')
            
            # Find links with class 'link2'
            available_links = soup.find_all('a', {'class': 'link2'})
            all_links = []
            
            for link in available_links:
                if not link.has_attr('href'):
                    continue
                    
                href = link['href']
                if '#' in href or 'image' in href.lower():
                    continue
                
                if 'http' in href:
                    all_links.append(href)
                elif '..' in href:
                    full_url = HOME_URL + href[3:]
                    all_links.append(full_url)
                else:
                    if '?' in url and '?' in href:
                        i1 = url.index('?')
                        i2 = href.index('?')
                        full_url = url[:i1+1] + href[i2+1:]
                        all_links.append(full_url)
            
            # Remove duplicates while preserving order
            unique_links = list(dict.fromkeys(all_links))
            logger.info(f"Found {len(unique_links)} unique links from {url}")
            
            # Scrape each link
            for link_url in unique_links:
                self.scrape_data(link_url)
                time.sleep(0.5)  # Be respectful
                
        except Exception as e:
            logger.error(f"Error in crawler1 for {url}: {e}")
    
    def home_page_crawler(self, url):
        """Main crawler starting from home page"""
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to access home page: {url}")
                return
            
            soup = bs(response.text, 'html.parser')
            
            all_links = soup.find_all('a')
            direct_data_links = []
            other_links = []
            
            for link in all_links:
                if not link.has_attr('href'):
                    continue
                    
                href = link['href']
                
                if '..' in href and 'image' not in href.lower():
                    other_links.append(href)
                
                if (len(href) > 5 and 'https' in href and 'rbi' in href and 
                    'image' not in href.lower()):
                    direct_data_links.append(href)
            
            # Remove duplicates
            direct_data_links = list(dict.fromkeys(direct_data_links))
            other_links = list(dict.fromkeys(other_links))
            
            logger.info(f"Found {len(direct_data_links)} direct links and {len(other_links)} other links")
            
            # Scrape direct data links
            for link_url in direct_data_links:
                self.scrape_data(link_url)
                time.sleep(0.5)
            
            # Follow other links
            for link_href in other_links:
                full_url = HOME_URL + link_href[3:]
                self.crawler1(full_url)
                time.sleep(1)  # Longer pause between sections
                
        except Exception as e:
            logger.error(f"Error in home page crawler: {e}")
    
    def scrape_specific_sections(self):
        """Scrape specific RBI sections for comprehensive coverage"""
        sections = [
            "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
            "https://www.rbi.org.in/Scripts/NotificationUser.aspx", 
            "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx",
            "https://www.rbi.org.in/Scripts/BS_SpeechesView.aspx",
            "https://www.rbi.org.in/Scripts/AnnualPublications.aspx",
            "https://www.rbi.org.in/Scripts/PublicationsView.aspx",
        ]
        
        for section_url in sections:
            logger.info(f"Scraping section: {section_url}")
            self.crawler1(section_url)
            time.sleep(2)
    
    def run_complete_scrape(self):
        """Run complete RBI website scraping"""
        logger.info("Starting complete RBI website scraping...")
        
        # Start with home page
        self.home_page_crawler(HOME_URL)
        
        # Scrape specific sections
        self.scrape_specific_sections()
        
        logger.info(f"Scraping completed!")
        logger.info(f"Total processed: {self.processed_count}")
        logger.info(f"Duplicates skipped: {self.duplicate_count}")
        logger.info(f"Total URLs visited: {len(self.scraped_urls)}")
        
        return {
            'processed': self.processed_count,
            'duplicates': self.duplicate_count,
            'total_urls': len(self.scraped_urls)
        }

# Usage
if __name__ == "__main__":
    scraper = RBICSVScraper('rbi_complete_data.csv')
    results = scraper.run_complete_scrape()
    
    print(f"\n🎉 Scraping Complete!")
    print(f"📄 Processed: {results['processed']} documents")
    print(f"🔄 Duplicates skipped: {results['duplicates']}")
    print(f"🔗 Total URLs visited: {results['total_urls']}")
    print(f"💾 Output file: rbi_complete_data.csv")

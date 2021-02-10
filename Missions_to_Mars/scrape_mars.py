from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd


def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    nasa_data = {}
    url1 = 'https://mars.nasa.gov/news/'
    url2 = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    
    browser.visit(url1)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    
    #collect the latest news title and paragraph text (latest result will be first in list; index 0 of the scaping results)
    nasa_data["title"] = soup.find_all("div", class_="list_text")[0].find("a").text
    nasa_data["paragraph"] = soup.find_all("div", class_="list_text")[0].find("div", class_="article_teaser_body").text
    
    browser.visit(url2)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    
    #scrape image URL from website
    relative_image_path = soup.find_all("img", class_="headerimage fade-in")[0]["src"]
    #concatenate relative image path to website URL
    nasa_data["featured_image_url"] = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/" + relative_image_path
    
    browser.quit()

    #using pandas to scrape tabular data from website
    url3 = 'https://space-facts.com/mars/'
    tables = pd.read_html(url3)
    df = tables[0]

    html_table = df.to_html() #converting the data frame into an HTML string
    html_table = html_table.replace('\n', '') #stripping the new line characters from the HTML
    nasa_data["table"] = html_table

    mars_hemisphere_data = {} #dictionary to store the image URL and the title to describe which hemisphere we are seeing
    hemisphere_image_urls = [] #list to store the dictionary of Mars hemisphere data

    url4 = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser = init_browser()
    browser.visit(url4)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    subpages = soup.find_all('a', class_='itemLink product-item')

    for page in subpages:# scraping the names of the four Martian hemispheres from the site
        if page.text != "": #accounting for null values          
            browser.links.find_by_partial_text(page.text).click() #look for the title of the page and click on the link
            soup = BeautifulSoup(browser.html, "html.parser") #updating the BeautifulSoup Browser HTML to the page we are currently on
            mars_hemisphere_data["title"] = page.text #adding the title of the page to the dictionary
            mars_hemisphere_data["img_url"] = "https://astrogeology.usgs.gov" + soup.find_all('img', class_='wide-image')[0]["src"]
            hemisphere_image_urls.append(mars_hemisphere_data.copy()) #copy is necessary since dict is defined outside loop
            browser.back() #go to the previous webpage
    nasa_data["hemisphere_images"] = hemisphere_image_urls

    return nasa_data

scrape()
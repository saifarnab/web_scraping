from instascrape import *

# Instantiate the scraper objects
google = Profile('https://www.instagram.com/google/')
google_post = Post('https://www.instagram.com/p/CG0UU3ylXnv/')
google_hashtag = Hashtag('https://www.instagram.com/explore/tags/google/')

# Scrape their respective data
google.scrape()
google_post.scrape()
google_hashtag.scrape()
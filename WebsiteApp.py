import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

def fetch_and_print_movie_details(link, headers):
    """Fetches and returns movie details from the given link."""
    movie_response = requests.get(link, headers=headers)
    if movie_response.status_code == 200:
        movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
        
        # the header
        header = movie_soup.find('header')
        
        release_date = 'N/A'
        run_time = 'N/A'
        poster_url = 'N/A'
        
        if header:
            # Extract release date and run time from the header
            for span in header.find_all('span'):
                if 'Release Date' in span.text:
                    release_date = span.find_next('span').text.strip()
                elif 'Run Time' in span.text:
                    run_time = span.find_next('span').text.strip()
            
            # Extract the poster URL
            poster_div = header.find('div', class_='poster mobileOnly')
            if poster_div and poster_div.find('img'):
                poster_url = poster_div.find('img')['src']
        
        # Extract the first paragraph of the description
        description_tag = movie_soup.find('div', class_='text')
        description = description_tag.find('p').text.strip() if description_tag and description_tag.find('p') else 'N/A'
        
        return {
            "release_date": release_date,
            "run_time": run_time,
            "description": description,
            "poster_url": poster_url
        }
    else:
        return {
            "release_date": "N/A",
            "run_time": "N/A",
            "description": "N/A",
            "poster_url": "N/A"
        }

def fetch_movie_list(offset=0, limit=5):
    url = 'https://www.allmovie.com/new-to-stream'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # Send a GET request to the website
    response = requests.get(url, headers=headers)
    
    movie_list = []
    
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the section containing new release movies
        movies_section = soup.find_all('div', class_='title')[offset:offset+limit]
        
        # Extract all movie details
        for movie_div in movies_section:
            # Extract the title and link
            title_tag = movie_div.find('a', class_='movie-title')
            title = title_tag.text.strip()
            link = 'https://www.allmovie.com' + title_tag['href'].split('/streams')[0]
            
            # Fetch additional movie details
            movie_details = fetch_and_print_movie_details(link, headers)
            movie_details['title'] = title
            movie_details['link'] = link
            
            movie_list.append(movie_details)
    
    return movie_list

@app.route('/')
def home():
    page = int(request.args.get('page', 1))
    limit = 6
    offset = (page - 1) * limit
    movies = fetch_movie_list(offset=offset, limit=limit)
    return render_template('index.html', movies=movies, page=page)

if __name__ == "__main__":
    app.run(debug=True)

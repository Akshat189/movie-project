import requests


response = requests.get("https://api.themoviedb.org/3/movie/550?api_key=f3f3a7f3d7294a72f0cb8545b2f7b1ea", params={"query": 'drive'})
data = response.json()
title = data['original_title']
date = data['release_date']
print(title)
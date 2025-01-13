import requests
import json
from wordcloud import wordcloud
import matplotlib.pyplot as plt

class GoogleReview():
     
     def __init__(self,name,location):
          self.name = name
          self.location = location
          print(f"Google Review Details {self.name} ")
          
     def extract_review(self):
        api_key='AIzaSyAOQbAPGJ2ikJcZLU_n7PoAc85IfDBuvLI'
        

        place_url=f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={self.location}&inputtype=textquery&fields=place_id&key={api_key}"
    
        response = requests.get(place_url)

        #Extract place id
        place_content = json.loads(response.content)

        place_id = place_content['candidates'][0]['place_id']

        review_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,review&key={api_key}"

        review_content=json.loads(requests.get(review_url).content)
        
        return review_content


   
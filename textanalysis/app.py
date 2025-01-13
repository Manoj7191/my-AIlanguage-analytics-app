from dotenv import load_dotenv
from flask import Flask,render_template,request,redirect,url_for
from markupsafe import Markup
import os
from reviewsextract.google_reviews import GoogleReview
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

app = Flask(__name__)


@app.route('/')
def index():
   result = request.args.get('result')
   return render_template('index.html',results=result) 

@app.route('/process_data',methods=['POST'])
def process_data():
   location = request.form['location']
   review_details = GoogleReview("Begin",location).extract_review()
   tot_reviews = review_details['result']['reviews']
   output = analyze_reviews(tot_reviews,location)
   print(output)
   return redirect(url_for("index",result=output))
       
      
#@app.route('/reviews')
def analyze_reviews(total_reviews,location):
    #print(list_of_reviews)  
    #Get Configuration settings
    load_dotenv()
    ai_endpoint = os.getenv('AZURE_AI_LANGUAGE_END_POINT')
    ai_key = os.getenv('AZURE_AI_LANGUAGE_KEY')
        
    #Basically the AzureKeyCredential is for secuirty this will encrypt
    #the key and pass to rest of the application
    credential = AzureKeyCredential(ai_key)

    client = TextAnalyticsClient(endpoint=ai_endpoint,
                                     credential=credential)
        
    #reviews_folder='reviews'
    #for file in os.listdir(reviews_folder):
    #  print('\n#############\n' + file)
    #  text = open(os.path.join(reviews_folder,file),encoding='utf8').read()

    #  print(text)
    import time
    time.sleep(5)

    main_analysis = ''
    main_analysis += f'<h1><b><frg>############Top 5 review Analysis##########</frg></b></h1>\n'
    main_analysis += f'<h1><b><frg>Location:{location}</frg></b></h1>\n'
    for i,reviews_text in enumerate(total_reviews):
        text = reviews_text['text']
        main_analysis += '------'*30
        main_analysis += "\n------------------------Review {}---------------------------\n\n".format(i+1)
        main_analysis += text

            
        detected_language = client.detect_language(documents=[text])[0]
        #print('\nLanguage: {}'.format(detected_language))
        main_analysis += "\n<b><frl>Language detected </frl></b>\n{}".format(detected_language.primary_language.name)


        analyze_sentiment = client.analyze_sentiment(documents=[text])[0]
        #print('\nSentiment:{}'.format(analyze_sentiment))
        
        main_analysis += "\n<b><frl>Sentiment {} and score are {} </frl></b>\n ".format(analyze_sentiment.sentiment,analyze_sentiment.confidence_scores)
          

        extract_key_phrases = client.extract_key_phrases(documents=[text])[0].key_phrases
        if len(extract_key_phrases) > 0:
           main_analysis += "\n<b><frl> List of Key Phrases</frl></b>\t"
        for j,extract_key in enumerate(extract_key_phrases):
           main_analysis += f"\n{j}.{extract_key}"

        extract_key_entities  = client.recognize_entities(documents=[text])[0].entities 
        if len(extract_key_entities) > 0:
          main_analysis += "\n\n\n<b><frl> List of Key Entities</frl></b>\t\n"
        for k,entities in enumerate(extract_key_entities):
          main_analysis += f"\n{k}.{entities.text} ({entities.category})"
            
        extract_linked_entities = client.recognize_linked_entities(documents=[text])[0].entities
        if len(extract_linked_entities) > 0:
          main_analysis += "\n\n\n<b><frl> List of Key linked entities</frl></b>\t\n"
        for m,linked_entities in enumerate(extract_linked_entities):
          main_analysis +=  f"\n{m}.{linked_entities.name} ({linked_entities.url})"

        extract_text_summary = client.begin_extract_summary(documents=[text]).result()
                
        for text_summary in extract_text_summary:
            #print('\t extract_summary : \t {}'.format(text_summary.sentences))
          main_analysis += f"\n<b><frl>Summary sentences : </frl></b>\n" 
          for txt in text_summary.sentences:
              main_analysis += f"\nSummary sentence : {txt['text']} and rank score is {txt['rank_score']}\n"
                 
        extract_abstract_summary = client.begin_abstract_summary(documents=[text]).result()
                
        for text_summary_abs in extract_abstract_summary:
          #print('\t abstract_summary : \t {}'.format(text_summary_abs.summaries))  
          main_analysis += f"\n<b><frl>abstract summaries : </frl></b>\n"
          for abs_txt in text_summary_abs.summaries:
             main_analysis += f"\nSummaries of abstract : {abs_txt['text']}\n" 
            
        main_analysis += '-'*30

    return main_analysis
    
    


if __name__ == "__main__":
   app.run(debug=True)        

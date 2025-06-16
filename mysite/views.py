import requests
import xml.etree.ElementTree as ET
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def sardegna(request):
    alternativi = [
      ("Aggius e Valle della Luna", "Trekking tra rocce granitiche e paesaggi lunari."),
      ("Monte d'Accoddi (Sassari)", "Unico sito tipo ziggurat in Europa. Perfetto per una mattinata culturale."),
      ("Badesi Mare", "Spiaggia libera con dune e mare ventilato. Ideale per famiglie."),
      ("Alghero", "Centro storico, bastioni, cucina catalana e spiagge come Le Bombarde."),
      ("Gita in barca all’Isola dell’Asinara", "Partenza da Stintino. Natura incontaminata e asinelli bianchi.")
  	]
    return render(request, 'sardegna.html', {'alternativi': alternativi})

def parse_rss_feed(url):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    
    namespace = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
    channel = root.find(".//channel")
    
    episodes = []
    for item in channel.findall("item"):  # Prende solo i primi 3 episodi
        title = item.find("title").text
        pub_date = item.find("pubDate").text
        description = item.find("description").text
        audio_url = item.find("enclosure").attrib["url"]
        image_url = item.find("itunes:image", namespace).attrib["href"]
        
        episodes.append({
            "title": title,
            "date": pub_date,
            "audio_url": audio_url,
            "description": description,
            "image_url": image_url,
        })
    
    podcast_image = channel.find("image/url").text
    
    return episodes, podcast_image

def podcast_view(request):
    RSS_FEEDS = {
        "podcast1": "https://www.spreaker.com/show/4070003/episodes/feed",
        "podcast2": "https://www.spreaker.com/show/5880075/episodes/feed",
        "podcast3": "https://feeds.megaphone.fm/storiedibrand",
        "podcast4": "https://feed.podbean.com/tuktuk/feed.xml",
        "podcast5": "https://media.rss.com/latornanza/feed.xml",
        
        
    }
    
    selected_feed = request.GET.get("feed", "podcast1")  # Default a "podcast1"
    rss_url = RSS_FEEDS.get(selected_feed, RSS_FEEDS["podcast1"])  # Fallback se il valore non è valido
    
    episodes, podcast_image = parse_rss_feed(rss_url)
    return render(request, "podcast.html", {"episodes": episodes, "podcast_image": podcast_image, "feeds": RSS_FEEDS, "selected_feed": selected_feed})

import requests
import xml.etree.ElementTree as ET
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def dart(request):
    return render(request, 'dart.html')

def sardegna(request):
    alternativi = [
        ("Aggius e Valle della Luna", "Trekking tra rocce granitiche e paesaggi lunari."),
        ("Monte d'Accoddi (Sassari)", "Unico sito tipo ziggurat in Europa. Perfetto per una mattinata culturale."),
        ("Badesi Mare", "Spiaggia libera con dune e mare ventilato. Ideale per famiglie."),
        ("Alghero", "Centro storico, bastioni, cucina catalana e spiagge come Le Bombarde."),
        ("Gita in barca all’Isola dell’Asinara", "Partenza da Stintino. Natura incontaminata e asinelli bianchi."),
        ("Spiaggia di Cala Sarraina", "Cala selvaggia con sabbia rossa e fondali cristallini. Ideale per relax e snorkeling."),
        ("Le Bombarde – Alghero", "Spiaggia attrezzata con sabbia dorata e mare limpido. Molto frequentata d'estate."),
        ("Spiaggia di Porto Ferro", "Spiaggia scenografica con sabbia ambrata e torri aragonesi. Amata da surfisti."),
        ("Cala Sabina – Golfo Aranci", "Cala tranquilla con acque turchesi e contesto naturalistico. Perfetta per una giornata rilassante.")
    ]

    return render(request, 'sardegna.html', {'alternativi': alternativi})

def parse_rss_feed(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    namespace = {
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"
    }

    channel = root.find("channel")
    if channel is None:
        return [], None

    episodes = []

    for item in channel.findall("item")[:5]:
        title = safe_text(item.find("title"), "Titolo non disponibile")
        pub_date = safe_text(item.find("pubDate"), "")
        description = safe_text(item.find("description"), "")

        enclosure = item.find("enclosure")
        audio_url = enclosure.attrib.get("url") if enclosure is not None else None

        itunes_image = item.find("itunes:image", namespace)
        image_url = itunes_image.attrib.get("href") if itunes_image is not None else None

        episodes.append({
            "title": title,
            "date": pub_date,
            "audio_url": audio_url,
            "description": description,
            "image_url": image_url,
        })

    # Immagine podcast (fallback multipli)
    podcast_image = None

    image_url_el = channel.find("image/url")
    if image_url_el is not None:
        podcast_image = image_url_el.text
    else:
        itunes_channel_image = channel.find("itunes:image", namespace)
        if itunes_channel_image is not None:
            podcast_image = itunes_channel_image.attrib.get("href")

    return episodes, podcast_image


def safe_text(element, default=""):
    return element.text if element is not None else default


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

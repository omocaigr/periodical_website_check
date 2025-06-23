import requests
from bs4 import BeautifulSoup
import hashlib

def hash_paragraph(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Select the specific <p> by its full class name
    paragraph = soup.select_one(
        'p.font_fam_normal.font_size_25.font_size_xxs_16.font_size_xs_16.color_dblue'
    )
    
    if paragraph is None:
        return "Paragraph not found."

    # Clean and hash the text
    text = paragraph.get_text(strip=True)
    normalized = ' '.join(text.split())
    return hashlib.sha256(normalized.encode()).hexdigest()


print(hash_paragraph("https://studentvillage.ch/en/apply/"))
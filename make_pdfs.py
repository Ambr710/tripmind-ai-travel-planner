"""Generates sample travel guide PDF documents used as the knowledge base
for the RAG pipeline. Run once: python make_pdfs.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pdfs")

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], spaceAfter=12)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceBefore=10, spaceAfter=6)
body = ParagraphStyle("body", parent=styles["Normal"], spaceAfter=8, leading=15)


def build_pdf(filename, title, sections):
    doc = SimpleDocTemplate(os.path.join(OUT_DIR, filename), pagesize=A4,
                             topMargin=0.8 * inch, bottomMargin=0.8 * inch)
    story = [Paragraph(title, h1), Spacer(1, 6)]
    for heading, paragraphs in sections:
        story.append(Paragraph(heading, h2))
        for p in paragraphs:
            story.append(Paragraph(p, body))
    doc.build(story)
    print("Created", filename)


destinations = [
    dict(
        filename="paris_travel_guide.pdf",
        title="Paris Travel Guide - France",
        sections=[
            ("Overview", [
                "Paris, the capital of France, is renowned for its art, fashion, gastronomy and culture. "
                "It is one of the most visited cities in the world, attracting travelers with landmarks "
                "such as the Eiffel Tower, the Louvre Museum and Notre-Dame Cathedral."]),
            ("Best Time to Visit", [
                "The best time to visit Paris is between April and June or September and November when "
                "the weather is mild and crowds are smaller. Summer (July-August) is peak tourist season "
                "with warm weather averaging 20-25 C. Winter is cold, averaging 3-7 C, with occasional rain."]),
            ("Top Attractions", [
                "Eiffel Tower - iconic iron tower offering panoramic views of the city.",
                "Louvre Museum - the world's largest art museum, home to the Mona Lisa.",
                "Notre-Dame Cathedral - Gothic cathedral on the Ile de la Cite.",
                "Montmartre and Sacre-Coeur Basilica - historic hilltop district with artist studios.",
                "Champs-Elysees and Arc de Triomphe - famous avenue and triumphal arch."]),
            ("Local Transportation", [
                "The Paris Metro is the fastest way to move around the city, with 16 lines covering "
                "most tourist areas. A Navigo weekly pass or carnet of tickets is recommended for tourists. "
                "Buses and the RER regional trains connect to the airports."]),
            ("Estimated Daily Budget", [
                "Budget travelers: approximately 70-90 USD per day including hostel stay, metro pass and "
                "street food. Mid-range travelers: 150-220 USD per day for a 3-star hotel, restaurant meals "
                "and paid attractions. Luxury travelers: 350 USD and above per day."]),
            ("Travel Guidelines", [
                "A Schengen visa is required for most non-EU visitors. Tap water is safe to drink. "
                "Tipping is not mandatory but rounding up the bill is appreciated. Many museums are closed on Mondays."]),
        ],
    ),
    dict(
        filename="goa_travel_guide.pdf",
        title="Goa Travel Guide - India",
        sections=[
            ("Overview", [
                "Goa, on India's western coast, is famous for its beaches, Portuguese-influenced architecture, "
                "vibrant nightlife and seafood cuisine. It is a popular destination for both domestic and "
                "international travelers."]),
            ("Best Time to Visit", [
                "The ideal time to visit Goa is from November to February, when the weather is pleasant with "
                "temperatures between 20-30 C. The monsoon season (June-September) brings heavy rainfall and "
                "rough seas, while March-May is hot and humid."]),
            ("Top Attractions", [
                "Baga Beach and Calangute Beach - popular beaches for water sports and nightlife.",
                "Basilica of Bom Jesus - UNESCO World Heritage church in Old Goa.",
                "Dudhsagar Waterfalls - a four-tiered waterfall on the Goa-Karnataka border.",
                "Fort Aguada - a 17th century Portuguese fort with a lighthouse.",
                "Anjuna Flea Market - a famous market for souvenirs, clothes and local crafts."]),
            ("Local Transportation", [
                "Renting a scooter or bike is the most popular and economical way to travel around Goa. "
                "Taxis and app-based cabs are available but pricier. Buses connect major towns."]),
            ("Estimated Daily Budget", [
                "Budget travelers: approximately 25-35 USD per day including guesthouse stay, local food and "
                "scooter rental. Mid-range travelers: 60-100 USD per day for a beach resort and restaurant "
                "meals. Luxury travelers: 200 USD and above per day for 5-star resorts."]),
            ("Travel Guidelines", [
                "Domestic and international flights connect to Goa's Dabolim airport and the newer Manohar "
                "International Airport. Carry sunscreen and stay hydrated. Alcohol is cheaper here than most "
                "Indian states due to lower taxes. Respect local dress codes near churches and temples."]),
        ],
    ),
    dict(
        filename="tokyo_travel_guide.pdf",
        title="Tokyo Travel Guide - Japan",
        sections=[
            ("Overview", [
                "Tokyo, Japan's bustling capital, blends ultramodern skyscrapers with historic temples. "
                "It offers world-class shopping, dining, technology and cultural experiences."]),
            ("Best Time to Visit", [
                "Spring (March-May) is ideal for cherry blossoms with temperatures of 10-19 C. Autumn "
                "(September-November) offers mild weather and colorful foliage. Summer is hot and humid "
                "(25-31 C), while winter is cool and dry (2-10 C)."]),
            ("Top Attractions", [
                "Senso-ji Temple - Tokyo's oldest Buddhist temple in Asakusa.",
                "Shibuya Crossing - the world's busiest pedestrian crossing.",
                "Tokyo Skytree - one of the tallest towers in the world with observation decks.",
                "Meiji Shrine - a serene Shinto shrine surrounded by forest in the middle of the city.",
                "Akihabara - the center of anime, manga and electronics culture."]),
            ("Local Transportation", [
                "The Tokyo subway and JR train network are extensive, punctual and easy to navigate with an "
                "IC card such as Suica or Pasmo. The Japan Rail Pass is cost-effective for travelers also "
                "visiting other cities."]),
            ("Estimated Daily Budget", [
                "Budget travelers: approximately 60-80 USD per day including hostel stay, convenience store "
                "meals and train pass. Mid-range travelers: 150-220 USD per day for hotel stay and restaurant "
                "meals. Luxury travelers: 400 USD and above per day."]),
            ("Travel Guidelines", [
                "Most nationalities need a visa or visa waiver arrangement. Cash is still widely used, though "
                "IC cards and credit cards are increasingly accepted. Public behavior is expected to be quiet, "
                "particularly on trains. Tipping is not customary in Japan."]),
        ],
    ),
    dict(
        filename="manali_travel_guide.pdf",
        title="Manali Travel Guide - India",
        sections=[
            ("Overview", [
                "Manali is a mountain resort town in Himachal Pradesh, India, popular for adventure sports, "
                "snow-capped Himalayan scenery and pleasant weather, making it a favorite for honeymooners "
                "and adventure travelers alike."]),
            ("Best Time to Visit", [
                "October to June is ideal depending on activity: October-February for snow (temperatures can "
                "drop below 0 C), March-June for pleasant weather (10-25 C) and trekking. Monsoon "
                "(July-September) brings landslide risk on mountain roads."]),
            ("Top Attractions", [
                "Solang Valley - adventure sports hub for paragliding, skiing and zorbing.",
                "Rohtang Pass - high mountain pass with snow activities, permit required.",
                "Hadimba Temple - ancient wooden temple set in a cedar forest.",
                "Old Manali - a laid-back area with cafes, markets and mountain views.",
                "Kasol and Parvati Valley - nearby scenic villages popular with backpackers."]),
            ("Local Transportation", [
                "Local buses, shared taxis and rented scooters/bikes are common. Volvo buses and shared cabs "
                "connect Manali to Delhi and Chandigarh. The nearest airport is Kullu-Manali (Bhuntar)."]),
            ("Estimated Daily Budget", [
                "Budget travelers: approximately 20-30 USD per day including hostel stay and local food. "
                "Mid-range travelers: 50-90 USD per day for a hotel and activities. Luxury travelers: "
                "150 USD and above per day for resort stays."]),
            ("Travel Guidelines", [
                "An inner-line permit is required to visit Rohtang Pass. Carry warm clothing even in summer "
                "as evenings are cool. Road conditions can be affected by weather, so check conditions before "
                "traveling in winter."]),
        ],
    ),
]

for d in destinations:
    build_pdf(d["filename"], d["title"], d["sections"])

print("All travel guide PDFs generated in", OUT_DIR)

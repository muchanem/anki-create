import json
import random
import genanki

model_id = random.randrange(1 << 30, 1 << 31)
deck_id = random.randrange(1 << 30, 1 << 31)

model = genanki.Model(
    model_id,
    'Basic Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ]
)


deck = genanki.Deck(
  deck_id,
  'Lecture Cards'
)

with open("out.json", "r") as file:
    data = json.load(file)
for slideshow, cards in data.items():
    lecture_name = slideshow.split("-")[0]
    for card in cards:
        note = genanki.Note(
            model=model,
            fields=[card['question'], card['answer']],
            tags=["lectures", lecture_name]
        )
        deck.add_note(note)

genanki.Package(deck).write_to_file('out.apkg')

from datetime import datetime
from typing import List, Dict
from pprint import pprint

from app.core.ai import get_post_ideas_v2_ai, parse_quote_concept
from app.core.ai_concepts import getconcept_quotes
from app.schemas import PostIdeasCategory


CONCEPTS = """

1. Quote about cocktails : "Cocktails are like women, each one is unique and should be treated accordingly" - Don The Beachcomber 
2. Quote about bartending : "A bartender is just a pharmacist with a limited inventory."- Unknown 
3. Quote about drinking : "I drink to make other people interesting." - Ernest Hemingway 
4. Quote about life : “It’s not what you look at that matters, it’s what you see.” - Henry David Thoreau 
5. Quote about love : “Love is the answer, but while you’re waiting for the answer, sex raises some pretty interesting questions.” - Woody Allen 
6. Valentine's Day quote : “Love doesn't make the world go round. Love is what makes the ride worthwhile.” - Franklin P. Jones 
7. Quote about happiness : “Happiness is when what you think, what you say, and what you do are in harmony.” - Mahatma Gandhi 
8. Quote about partying : “All I need is wine, women, and song…and preferably in that order.” - Friedrich Wilhelm Nietzsche 
9. Quote about age : “Age is an issue of mind over matter. If you don’t mind, it doesn’t matter.” - Mark Twain 
10. Quote about life : “ Life is too short to waste time on things that don’t matter """


def print_post_ideas(post_ideas):
    for post_idea in post_ideas:
        print(f'  {post_idea["name"]}\n{post_idea["description"]}')


def test_1():
    category = PostIdeasCategory.quotes
    brand_type = "High-end cocktail bar"
    period = 2
    post_ideas: List[Dict] = get_post_ideas_v2_ai(category, brand_type, period)

    print_post_ideas(post_ideas)


def test_2():
    category = PostIdeasCategory.quotes
    brand_type = "Healthy fast food where customers can customise their food"
    period = 2

    month_name = datetime.strptime(str(period), "%m").strftime("%B").lower()
    # add new field to each dict
    concepts = getconcept_quotes(brand_type, month_name)
    print(f'{concepts}\n')

    post_ideas: List[Dict] = parse_quote_concept(concepts)

    print_post_ideas(post_ideas)


def test_3():
    c = """1. Healthy Fast food quote: “Cooking is like love. It should be entered into with abandon or not at all.” – Harriet Van Horne
2. Healthy Fast food quote: “If you are not cooking with passion, you are wasting your time.” – Éric Ripert
7. Sandwich Quote: “A sandwich is an open-faced culinary ode to luxury.” – Claudia Roden
8. Soup Quote: “There is no such thing as a little in cooking. There are only leftovers.” — Julia Child
9. Wrap Quote: “The wrap is one of those miraculous culinary inventions that satisfies all cravings simultaneously—it's crunchy like a salad, creamy like a burrito, and salty like french fries.” – Tal Ronnen
6. Quote about junk food : Junk food may be cheap and easy, but it's also expensive and destructive” – Melody Petersen
7. Quote about cooking : “Anyone who has ever grilled anything knows that when it comes to flavor, nothing beats flame-kissed meat or fish.” -Steven Raichlen
3. Fast food quote : "I'm not a complicated guy. I like my hamburgers with ketchup and mustard on top - and I like them cooked medium rare." - Ronald Reagan"""

    res = parse_quote_concept(c)
    print_post_ideas(res)


def test_4():
    category = PostIdeasCategory.information
    brand_type = "High-end cocktail bar"
    period = 2
    post_ideas: List[Dict] = get_post_ideas_v2_ai(category, brand_type, period)

    print_post_ideas(post_ideas)


def test_5():
    category = PostIdeasCategory.inspiration
    brand_type = "High-end cocktail bar"
    period = 2
    post_ideas: List[Dict] = get_post_ideas_v2_ai(category, brand_type, period)

    print_post_ideas(post_ideas)


def test_6():
    category = PostIdeasCategory.promotion
    brand_type = "High-end cocktail bar"
    period = 2
    post_ideas: List[Dict] = get_post_ideas_v2_ai(category, brand_type, period)

    print_post_ideas(post_ideas)


def test_7():
    res = parse_quote_concept(CONCEPTS)
    pprint(res, indent=4, width=200)
    assert res == [
        {'description': 'Cocktails are like women, each one is unique and should be treated accordingly', 'name': 'Don The Beachcomber (Quote about cocktails)'},
        {'description': 'A bartender is just a pharmacist with a limited inventory.', 'name': 'Unknown (Quote about bartending)'},
        {'description': 'I drink to make other people interesting.', 'name': 'Ernest Hemingway (Quote about drinking)'},
        {'description': 'It’s not what you look at that matters, it’s what you see.', 'name': 'Henry David Thoreau (Quote about life)'},
        {'description': 'Love is the answer, but while you’re waiting for the answer, sex raises some pretty interesting questions.', 'name': 'Woody Allen (Quote about love)'},
        {'description': "Love doesn't make the world go round. Love is what makes the ride worthwhile.", 'name': "Franklin P. Jones (Valentine's Day quote)"},
        {'description': 'Happiness is when what you think, what you say, and what you do are in harmony.', 'name': 'Mahatma Gandhi (Quote about happiness)'},
        {'description': 'All I need is wine, women, and song…and preferably in that order.', 'name': 'Friedrich Wilhelm Nietzsche (Quote about partying)'},
        {'description': 'Age is an issue of mind over matter. If you don’t mind, it doesn’t matter.', 'name': 'Mark Twain (Quote about age)'},
        {'description': '', 'name': 'Unknown (Quote about life)'}
    ]


if __name__ == '__main__':
    # test_1()
    # test_2()
    # test_3()
    # test_4()
    # test_5()
    # test_6()
    test_7()

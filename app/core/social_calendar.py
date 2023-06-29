import random
import json

def roll(CategoryNumber, CategoryWeights):
    assert len(CategoryWeights) == CategoryNumber
    number = random.uniform(0, sum(CategoryWeights))
    current = 0
    for i, bias in enumerate(CategoryWeights):
        current += bias
        if number <= current:
            return i + 1


## Category can be : Inspiration, Promotion, Portrait, Quote, Meme, Information, News


def calendarRoll(Categories):
    Sum = 0
    CategoryNumber = len(Categories)
    CategoryWeights = []
    Categories_list = list(Categories)
    #Let's first normalize the values
    for key,value in Categories.items():
        Sum+= value
    for key,value in Categories.items():
        value= value/Sum
        CategoryWeights.append(value) 
    Rolled = roll(CategoryNumber, CategoryWeights)
    return Categories_list[Rolled-1]
    
Categories = {
    'Information': 200,
    'Promotion': 29,
    'Inspiration': 10,
    'News': 30,
    'Portrait': 5,
    'Quote': 40
}

r = calendarRoll(Categories)
print(r)
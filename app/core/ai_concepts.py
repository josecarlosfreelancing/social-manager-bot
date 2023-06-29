from loguru import logger

from app.core.ai_utils import get_open_ai_completion
from app.schemas import ConceptCategory

MODEL_NAME = "text-davinci-003"


def getconcept_information(description, month):
    restart_sequence = "\nDescription:"
    month_sequence = "\nMonth:"

    prompt_text = f'{restart_sequence} {description}{month_sequence} {month}'

    prompt_initial="Given a Description and Month, create a top 10 list of Informational Instagram publication\n\n##\n\nDescription: sustainable cleaning product that can be refilled at the store\nMonth: April\n\n1. How to prepare floor cleaner\t\n2. How to efficiently clean an oven\n3. Spring cleaning tips for your home\n4. 5 environmental reasons to switch to reusable containers\n5. 4 benefits of using a green cleaner\n6. How to clean up after April fool's day\n7. The top 5 ways to use our cleaning products in your home\n8. Spring cleaning checklist for your kitchen\n9. How to unclutter your home in 10 easy steps\n10. Top 3 cleaning hacks for your spring cleaning\n\n\n##\n\nDescription: Independent and self made escape room based in Belgium with 4 immersive adventures and 1 city investigation\nMonth: September\n\n1. Top 5 tips for escaping an escape room\n2. How to choose the right escape room for you\n3. How to beat the Escape Room Brain Freeze\n4. Why September is the best month to have a team building activity\n5. How to improve your problem-solving skills\n6. How to pick a lock\n7. 4 clues to look out for in an escape room\n8. Top 10 September cold cases yet to be solved\n9. How to investigate a crime scene like a detective\n10. 5 ways to increase your team's productivity after the summer break\n\n##\n\nDescription: Store that offers sports clothes\nMonth: January\n\n1. Top 5 running tips for the new year\n2. How to stick to your New Year's resolutions\n3. The best races to run this year\n4. Running hacks for beginners\n5. 5 benefits of running\n6. 4 exercises to improve your running form\n7. How to choose the right running shoes for you\n8. Top 10 running playlist for January\n9. How to set goals and achieve them\n10. How to stay motivated when running\n\n##\n\nDescription: Thai food fast-food restaurant chain aimed at millennials\nMonth: October\n\n1. How to make Thailand's national dish, Pad Thai\n2. Why it makes so much sense to go to Thailand in October\n3. Which are the best Thai Island to visit in October\n4. The best places to eat Thai food in Bangkok\n5. How to order food like a pro in Thailand\n6. What to do when you get sick while travelling in Thailand\n7. The importance of tipping in Thailand\n8. How to say 'hello' and 'thank you' in Thai\n9. Why \"Autumn\" is actually not a thing in Thailand\n10. 3 dishes that are must-try at a Thai restaurant beside Pad Thai\n\n##\n\n"

    response = get_open_ai_completion().create(
        model=MODEL_NAME,
        prompt=prompt_initial + prompt_text,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=2,
        stop=["##"]
    )

    concept = response['choices'][0]['text']

    return concept


def getconcept_promotion(description, month):
    restart_sequence = "\nDescription:"
    month_sequence = "\nMonth:"

    prompt_text = f'{restart_sequence} {description}{month_sequence} {month}'

    prompt_initial="Given a Description and Month, create a top 10 list of Promotional Instagram publication\n\n##\n\nDescription: sustainable cleaning product that can be refilled at the store\nMonth: April\n\n1. Spring cleaning contest : Share your best before/after cleaning pictures and tag us to win a chance to have a year of our products for free\n2. April's fool: Share a funny prank (video or picture) of you using our products and get a free refill voucher\n3. Get 20% discount on all refills for Earth Day\n4. For every 10 liter refill, we will plant a tree for Earth Day\n5. National Hanging Out Day : Help the environment and extend the life of your clothes by line drying. Tag us on a story of you line drying your clothes and wing a free refill\n6. Happy Easter : Find the golden refill ticket by scratching one of our bottle and win a year of refill\n7. Share your best tips and tricks of using our products for a chance to be featured on our page\n8. Follow us on Instagram for a chance to win a free refill\n9. Refer your friends and get 20% off your next purchase\n10. Join our ambassador program\n\n##\n\nDescription: Escape room\nMonth: September\n\n1. Follow us on Instagram for a chance to win a free escape room game\n2. Back to school : Come with your family at the Escape room, kids under 10 are free !\n3. Solve this September cold case riddle and win a date night for two worth €100\n4. Back from summer holidays : Share your team funny post vacation picture and win a free team building\n5. Escapology Day : 20% discount on all escape room bookings\n6. Find the hidden message in today's Story and win a free booking for 4 people\n7. International Day of Peace : Escaping from the room is always more peaceful when done together. Book now and get 20% off for groups of 4 or more people\n8. New room launch : Celebrate with us our newest room by getting a 20% discount on your booking\n9. Team bonding : Get to know your colleagues better by trying our escape room. Groups of 4 or more people get a 20% discount\n10. Already missing your summer vacations? Come to our summer theme after work and escape game\n\n##\n\nDescription: Store that offers sports clothes\nMonth: January\n\n1. The best way to start the year is to get fit. Get 20% off on your first purchase when you follow us on Instagram\n2. New year, new you. Share your healthy new year resolution and tag us for a chance to win a free sports outfit\n3. Let's make this year our healthiest one yet! Get 25% off all sports clothes on Monday January 15th\n4. Stay motivated all year long with our discounts. Get 30% off on all sports clothes from Tuesday to Thursday\n5. Blue Monday special : Get 50% off on your second purchase when you show us your worst Monday picture\n6. It's cold outside, but that doesn't mean you can't go out and run. Get a free hat or gloves with every purchase of sports clothes over €50\n7. Time to stock up on your fitness gear for the new year. Get a free water bottle with every purchase of €75 or more\n8. Post your best workout picture on Instagram for a chance to be featured on our page and win a free sports outfit\n9. Refer a friend who wants to get in shape for the summer and both of you get 20% off your next purchase\n10. Stock up on your sports clothes for the new year. Get a free tote bag with every purchase of €50 or more\n\n##\n\nDescription: Thai food fast-food restaurant chain aimed at millennials\nMonth: October\n\n1. It's officially fall, and that means pumpkin spice season is here! Get a free pumpkin spice latte with your purchase of any food item\n2. Celebrate Oktoberfest with us by getting a free Singha beer with your purchase of any food item\n3. Try our new Thai coconut soup for a taste of the tropics in the middle of autumn. Get a free straw hat with your purchase\n4. Let's get spooky! Post a picture of you in your Halloween costume trying one of our dishes and get a free meal\n5. Feeling run down? Get 20% off when you show us your sick day selfie\n6. Need to take a break from school or work? Get a free spring roll with every entree purchase\n7. We know change can be hard. Get 20% off when you switch to our restaurant from another Thai food chain\n8. TGIF! Get 25% off all food items on Fridays\n9. Share your best recipe using our products for a chance to be featured on our page and win a $50 gift card\n10. Follow us on Instagram for a chance to win a $100 gift card\n\n##\n\n"

    response = get_open_ai_completion().create(
        model=MODEL_NAME,
        prompt=prompt_initial + prompt_text,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=2,
        stop=["##"]
    )

    concept = response['choices'][0]['text']

    return concept


def getconcept_inspiration(description, month):
    restart_sequence = "\nDescription:"
    month_sequence = "\nMonth:"

    prompt_text = f'{restart_sequence} {description}{month_sequence} {month}'

    prompt_initial="Given a Description and Month, create a top 10 list of Inspirational Instagram publication\n\n##\n\nDescription: sustainable cleaning product that can be refilled at the store\nMonth: April\n\n1. People doing spring cleaning with our product\n2. Cleaning lady playing April's fool prank while cleaning\n3. Easter but instead of eggs people collect garbage (bringing awareness about trash)\n4. For Earth day, sharing a picture of Earth being filled with our cleaning product\n5. For national hanging out day, showing clothes being hanged to dry in the garden (awareness about energy consumption)\n6. A rabbit next to our cleaning products for Easter\n7. Prank of drinking fake cleaning product for April's fool day\n8. Pictures of nature in spring to bring awareness about the importance of protecting the environment \n9. People recycling and refilling our bottle in the store for Earth day\n10. Kids playing and helping mommy clean with our product while sticking an April's fool fish on her back for April's fool day\n\n##\n\nDescription: Escape room\nMonth: September\n\n1. Showing people back to work feeling like they are in an escape room but it's their office\n2. Parent's putting a enigma to find food in their kid's lunch box instead of food as they are back to school\n3. Showcasing beautiful escape rooms around the world for Escapology day \n4. Employees happy to have found the missing document and escape their boss's office \n5. One group of coworker having fun collaborating in our escape room and another group of coworker arguing and getting stuck in our escape room to show good and bad team dynamic\n6. Showing an escape room before and after a group goes into it\n7. Showing the Autumnal theme in our escape rooms to celebrate Fall\n8. People finding clues and solving puzzles in our escape rooms to showcase the joy of solving a puzzle\n9. Employees having a team event in our escape room to feel like they are still on vacation \n10. Group of friends having fun in our Escape room\n\n##\n\nDescription: Store that offers sports clothes\nMonth: January\n\n1. Showing people new years resolutions to be fit\n2. Showing people running outside in the cold while wearing gears we sell to show how warm they can be\n3. Showing January sales in our stores\n4. People going to the gym for their New Year's resolution in our clothes\n5. Couples going on a power walk in a snowy park while wearing our warm sports clothes\n6. People skiing and snowboarding with our winter sports clothes\n7. Montage of Martin Luther King wearing our sports clothes for Martin Luther King Jr. Day\n8. People ice skating and hockey with our sports clothes\n9. Showing the different types of warm gloves that can be worn in winter\n10. People getting off their couch to start exercising on Blue Monday\n\n##\n\nDescription: Thai food fast-food restaurant chain aimed at millennials\nMonth: October\n\n1. Showing people going to our restaurant for Halloween\n2. People carving jack-o-lanterns with our chopsticks in our restaurant\n3. An employee disguised as Krasue – a Thai female spirit with hanging entrails - for Halloween\n4. Showing the scariest Thai ghost/scary mythical creatures for Halloween (Pob, Krasue, Mae Nak, Kuman Thong, etc.)\n5. Halloween decoration and employees in scary costumes in one of our restaurants \n6. A fake spider on one of our Pad Thai scaring a customer \n7.  Behind the scene with our cooks cooking while wearing funny costumes for Halloween \n8. A group of friends in a Halloween costume eating our food and liking it \n9. A pumpkin themed food that we serve for Halloween \n10. People taking selfies in Halloween costumes with our restaurant in the background\n\n##\n\nDescription: Local parapharmacy chain\nMonth: December\n\n1. Showing people getting sick during the holidays and coming to our pharmacy for help\n2. A Christmas tree with all of our medicines as ornaments \n3. A gingerbread house with people taking antibiotics and other medicines inside \n4. The nativity scene with Mary and Joseph being visited by an angel who is holding a bottle of cough syrup \n5. Ebenezer scrooge coming to life and thanking us for giving him back his health \n6. Santa Claus coming to our pharmacy to get his flu shots and other medications \n7. Rudolph the red nose reindeer with a cold and needing some nasal drops from us\n8. An elf working in our pharmacy and helping people find the medicine they need \n9. A family gathering around the Christmas tree and nobody sick\n10. Sharing Christmas miracle stories of people being sick and getting better right at Christmas\n\n##\n\nDescription: SaaS startup that created a solution to make marketing agencies more efficient\nMonth: November\n\n1. Showing before/after picture of a marketing agency using our app (and how happy they are)\n2. Showing people the app being used in a creative way by marketing agencies to improve their workflow \n3. A customer testimonial of how our product has helped them be more productive \n4. Pictures of people using our app at different places (coffee shops, airports, etc.) to show that our app can be used from anywhere \n5. Our app being used by well-known marketing agencies and them liking it \n6. Showcasing some of the great Thanksgiving post made by marketing agencies using our app\n7. Showing a marketeer not being able to enjoy their thanksgiving dinner because they are not using our app and they have too much work\n8. Showing how marketeers can truly work from anywhere with our app by showcasing some of the exotic destination they work in during winter time\n9. Sharing a story of how some marketing agency managed to onboard a client and created all their ads just in time for Black Friday thanks to our app\n10. Warning people about burnout during the Holiday seasons because it is the most intense period of the year for marketing agencies\n\n##\n\n"

    response = get_open_ai_completion().create(
        model=MODEL_NAME,
        prompt=prompt_initial + prompt_text,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=2,
        stop=["##"]
    )

    concept = response['choices'][0]['text']

    return concept


def getconcept_quotes(description, month):
    restart_sequence = "\nDescription:"
    month_sequence = "\nMonth:"

    prompt_text = f'{restart_sequence} {description}{month_sequence} {month}'

    prompt_initial = "Given a Description and Month, create a top 10 list of famous quotes\n\n##\n\nDescription: sustainable cleaning product that can be refilled at the store\nMonth: April\n\n1. Cleaning quote : \"Cleanliness is a state of purity, clarity, and precision\" - Suze Orman\n2. Cleaning quote : \"Better keep yourself clean and bright; you are the window through which you must see the world\" - George Bernard Shaw\n3. Cleaning quote: \"The objective of cleaning is not just to clean, but to feel happiness living within that environment\" - Marie Kondo\n4. Spring Cleaning quote : \"Sweeping away the winter grime and clutter is like welcoming spring with open arms.\" - Kimora Lee Simons\n5. Spring Cleaning quote : \"If you want to get rid of stuff, you can always do a good spring cleaning. Or you can do what I do. Move.\"- Ellen DeGeneres\n6. April fool quote : \"The first of April is the day we remember what we are the other 364 days of the year\"- Mark Twain\n7. April fool quote : \"Reminder: climate change is no April fool's joke\"- Ed Hawkins\n8. Sustainability quote : \"We don’t need a handful of people doing zero waste perfectly. We need millions of people doing it imperfectly.\" - Anne Marie Bonneau\n9. Sustainability quote : \"The world is changed by your example, not by your opinion.\" - Paulo Coelho\n10. Sustainability quote : \"Plastic will be the main ingredient of all our grandchildren’s recipes.\" - Anthony T. Hincks\n\n##\n\nDescription: Escape room\nMonth: September\n\n1. Escape quote : \"How did I escape? With difficulty. How did I plan this moment? With pleasure.\"- Alexandre Dumas, The Count of Monte Cristo\n2. Escape quote : \"Just because you escape one trap doesn’t mean you will escape the next.\" -Leigh Bardugo\n3. Detective quote : \"Crime is common. Logic is rare\" - Arthur Conan Doyle\n4. Detective quote : \"What a newspaper prints is news – but not always truth!\" - Agatha Christie\n5. Strategy quote : \"By failing to prepare, you are preparing to fail.\" — Benjamin Franklin\n6. Strategy quote : \"Amidst the chaos, there is also opportunity.\" - Sun Tzu\n7. Back from school quote : \"If you think education is expensive, try ignorance\" - Andy McIntyre\n8. Back to work quote : \"Whatever you decide to do, make sure it makes you happy.\" - Paulo Coelho\n9. International Day of Peace quote : \"Peace is not absence of conflict, it is the ability to handle conflict by peaceful means.\" - Ronald Reagan\n10. International Day of Peace quote : \"Fighting for peace is like screwing for virginity.\" - George Carlin\n\n##\n"

    response = get_open_ai_completion().create(
        model=MODEL_NAME,
        prompt=prompt_initial + prompt_text,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=2,
        stop=["##"]
    )

    concept = response['choices'][0]['text']

    return concept


# case statement for each prompt category
def get_concept_function(concept: ConceptCategory):
    switcher = {
        ConceptCategory.information: getconcept_information,
        ConceptCategory.quotes: getconcept_quotes,
        ConceptCategory.promotion: getconcept_promotion,
        ConceptCategory.inspiration: getconcept_inspiration,
    }
    res = switcher.get(concept)
    return res

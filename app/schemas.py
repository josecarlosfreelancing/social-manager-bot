from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, validator

from app.res.defaults import caption_default


class InitializationSchema(BaseModel):
    Concept: str
    Caption: str


class DesignPostCategory(str, Enum):
    Inspiration = 'Inspiration'
    Promotion = 'Promotion'
    Portrait = 'Portrait'
    Quote = 'Quote'
    Meme = 'Meme'
    Information = 'Information'
    News = 'News'


class DesignPostLanguage(str, Enum):
    EN = 'EN'
    BG = 'BG'
    CS = 'CS'
    DA = 'DA'
    DE = 'DE'
    EL = 'EL'
    EN_GB = 'EN_GB'
    EN_US = 'EN_US'
    ES = 'ES'
    ET = 'ET'
    FI = 'FI'
    FR = 'FR'
    HU = 'HU'
    ID = 'ID'
    IT = 'IT'
    JA = 'JA'
    LT = 'LT'
    LV = 'LV'
    NL = 'NL'
    PL = 'PL'
    PT = 'PT'
    PT_BR = 'PT_BR'
    PT_PT = 'PT_PT'
    RO = 'RO'
    RU = 'RU'
    SK = 'SK'
    SL = 'SL'
    SV = 'SV'
    TR = 'TR'
    ZH = 'ZH'


class CaptionSchema(BaseModel):
    Initialisation: List[InitializationSchema] = caption_default['Initialisation']
    postRequest: str = caption_default['postRequest']
    postLanguage: str = caption_default['postLanguage']
    postCategory: str = caption_default['postCategory']


class DesignSchema(BaseModel):
    postCategory: DesignPostCategory
    postRequest: str
    postLanguage: DesignPostLanguage


class CategorizerSchema(BaseModel):
    alt_text: str
    caption: str


class IntentAnalysisSchema(BaseModel):
    text: str


class SubjectEntityAnalysisSchema(BaseModel):
    text: str


class TranslateTextSchema(BaseModel):
    output_lang: str
    text: str


class PostIdeasInputSchema(BaseModel):
    brand_type: str = "High-end cocktail bar"
    period: str = "february"


class InstacaptionSchema(BaseModel):
    texts: str


class GetBioSchema(BaseModel):
    brand_name: str = "Diknek (www.diknek.be)"
    brand_type: str = "brand of belgian sauces influenced by the belgian arts, belgian culture and by belgian food"
    brand_objective: str = "convert online shoppers"


# class EventRecsSchema(BaseModel):
#     desc: str = "restaurant that blends Belgian and asiatic flavours in a vintage bistro setting with draught beer and fine wines"
#     year: int = 2022
#     month: int = 4
#     day: Optional[int] = None


class ImprovedFormatSchema(BaseModel):
    text: str


class SpellCheckFrenchSchema(BaseModel):
    text: str = "C'est une belle voture de couleur blee."


class GetEditCaptionSchema(BaseModel):
    caption: str = """We are opening a new restaurant in Antwerp, May 11th. :new:
    To get a free dish, be one of the first 100 customers at Melkmarkt 28, 2000 Antwerp. We open at 11.30 A.M.!
    We can’t wait for you to taste our fabulous Thaï food. :stew:
    #pitaya #pitaya_be #freshfood #restaurant #newrestaurant #thai #thairestaurant #thaifood #thaicuisine #antwerp #antwerpen #melkmarkt #thai #smile #opening #visitantwerp #antwerpcity
"""
    edit: str = "FYI our opening in Antwerp will be delayed until 18/05."


class AdCopySchema(BaseModel):
    Initialisation: List = [
        {
            "CTA": "Free access",
            "BrandDesc": "Growth/Scale Course",
            "Keyfeature": "online classes (video, documentation, etc.)",
            "Audience": "digital marketing agency owners",
            "BrandName": "Flash Hub",
            "Headline": "The Leadership System For Time & Money Freedom",
            "Description": "How to run your marketing- or IT-business on autopilot and scale with high profits, no stress and relaxed workloads",
            "Primary": "What would it feel like to take a whole month off of running your digital agency, marketing or software business, knowing that you can 100% rely on\n\n1) your team to deliver the services without you\n2) your automated sales funnel to bring in new clients without you\n\nI can tell you that it’s incredibly freeing!\n\nIt is the time and money freedom you expected when you started your business, right?\n\nBut I didn’t just cross my fingers and hope for the best.\n\nI systematized and automated my €4m/yr business with:\n\n- Self-managing teams\n- Productized service offers\n- An automated B2B sales funnel\n- Rock-solid quality standards\n- A digital leadership system\n- And a team of global freelancers\n\nIt sounds like work, and it was.\n\nI’m not offering you a quick fix.\n\nBut I am offering you the chance to set yourself up for long-term success.\n\nDoubled profits.\nMore free time.\nLess stress.\n\nJust click the link below and get free access."
        },
        {
            "CTA": "Free trial sign-up",
            "BrandDesc": "SaaS tool",
            "Keyfeature": "solution to design, write, edit videos, and publish content on social media",
            "Audience": "designers",
            "BrandName": "Simplified.co",
            "Headline": "ONE Tool for All Your Design & Writing Needs",
            "Description": "Simplified.co - Forever Free",
            "Primary": "Get a marketing workflow that works.\n\n🎨 No-code designer\n🦾 AI writer\n🎥 Video editor\n📆 Social media publishing\n\nTry Simplified - all the tools your marketing team needs in just one app."
        },
        {
            "CTA": "Free trial sign-up",
            "BrandDesc": "SaaS tool",
            "Keyfeature": "solution for copywriting powered by AI",
            "Audience": "marketing professionals",
            "BrandName": "Jasper",
            "Headline": "Put AI to work for your content marketing",
            "Description": "Scale your content with AI",
            "Primary": "Write blog posts 10x faster using AI, without sacrificing on quality."
        },
        {
            "CTA": "Download",
            "BrandDesc": "course",
            "Keyfeature": "a toolkit of SOP (Standard Operating Procedures)  for growing businesses",
            "Audience": "digital marketing agencies",
            "BrandName": "ClickMinded",
            "Headline": "Delegate Agency Work In Seconds",
            "Description": "Streamline processes, offer new services, delegate tasks, train employees.",
            "Primary": "⬇️ Delegate Marketing Agency Work In Seconds ⬇️\nLearning new skills, training your employees, offering new services…\n\nAnd instead of working ON your business, you work IN your business.\n\nWorking long hours to make sure work got done correctly…\n\nMicromanaging all the tasks in the team…\n\nTrying to simplify the processes and hitting the wall over & over…\n\nBut what if you could:\n✅ Delegate agency tasks to your employees with 100% trust\n✅ Spend almost no time training new employees\n✅ Offer new services that grow your business with ease\n\nHow?\n\nBy implementing The Agency Growth SOP Toolkit.\n\nNo more micromanaging your employees.\n\nThe Agency Growth SOP Toolkit includes EVERYTHING an agency owner requires for massive growth.\n\nThese 40+ SOPs & templates are:\n📝 Fully customizable and white-labeled\n🛠 99% precise, so you don’t need search information elsewhere\n🆓 Regularly updated with a lifetime access\n\nAnd you can send these SOPs & templates to your 1:1 clients!\n\n10 423 agencies already trust us, and if you want to become the next successful marketing agency owner…\n\nYou can get The Agency Growth SOP Toolkit with 92% off.\n\nBut the discount is valid only for a few more days.\n\nSo click the link below to try this with a 14-day money-back guarantee today."
        },
        {
            "CTA": "Sign-Up",
            "BrandDesc": "SaaS tool",
            "Keyfeature": "AI-powered copywriting",
            "Audience": "bloggers",
            "BrandName": "Copy.ai",
            "Headline": "Write full length blogs in minutes!",
            "Description": "/",
            "Primary": "👋 Bloggers! 👋  Is writing a time suck? Let CopyAI help you write infinitely faster!\n\n🧠 Brainstorm + draft an outline in seconds\n💡 Get inspired + overcome writer's block\n👩🏼‍💻 1 million+ users and growing!\n🎉 100 free credits when you sign up\n\nWrite blogs at 5X the speed, and let CopyAI unleash your full potential."
        },
        {
            "CTA": "Free tier sign-up",
            "BrandDesc": "SaaS tool",
            "Keyfeature": "an All-in-one project management solution (incl. task boards, whiteboards, chat, document sharing, etc.)",
            "Audience": "project managers in startups",
            "BrandName": "ClickUp",
            "Headline": "All Your Campaigns in One Place",
            "Description": "Try ClickUp today—Free Forever!",
            "Primary": "📅 Map out marketing timelines\n🏆 Optimize your campaigns\n💬 Manage feedback\n...All in one place with ClickUp."
        }
    ]
    CTA: str = "waitlist sign-up"
    BrandDesc: str = "SaaS tool"
    Keyfeature: str = "an all-in-on marketing solution powered by AI (incl. automatic content " \
                      "suggestion, " \
                      "copywriting, freelancer marketplace, etc.)"
    Audience: str = "digital marketing freelancers"
    BrandName: str = "Snikpic"
    copyLanguage: str = "FR"


class GetBrSchema(BaseModel):
    description: str = "Peer-to-peer marketplace that enables hosts to book their apartment to guest for one or multiple nights"
    user_story: str = "As a host I want to add a listing so that I can start making money and booking guests in my space"


class PostIdeasCategory(str, Enum):
    information = 'information'
    inspiration = 'inspiration'
    promotion = 'promotion'
    quotes = 'quotes'
    portrait = 'portrait'
    past_events = 'past_events'
    calendar_events = 'calendar_events'


class PromptsCategory(str, Enum):
    food = 'food'
    portrait = 'portrait'
    object = 'object'
    icon = 'icon'
    scene = 'scene'
    illustration = 'illustration'
    render = 'render'
    action = 'action'


class GetPromptSchema(BaseModel):
    category: PromptsCategory = PromptsCategory.food
    description: str = "A picture of a bread"
    number_of_images: int = 1

    @validator('number_of_images')
    def number_of_images_must_be_positive_and_less_than_10(cls, v):
        if v < 1 or v > 10:
            raise ValueError('number_of_images must be between 1 and 10')
        return v


class ConceptCategory(str, Enum):
    information = 'information'
    inspiration = 'inspiration'
    promotion = 'promotion'
    quotes = 'quotes'


DESIGN_HELPER_DESCRIPTION = ":param obj_in: Category can be:\n%s\nLanguage can be:\n%s" % ((
    ', '.join([
        str(i).split('.')[1] for i in list(DesignPostCategory)
    ]),
    ', '.join([
        str(i).split('.')[1] for i in list(DesignPostLanguage)
    ])
))


CONCEPTS_HELPER_DESCRIPTION = "Category can be :\n%s" % (
    ', '.join([
        str(i).split('.')[1] for i in list(ConceptCategory)
    ])
)

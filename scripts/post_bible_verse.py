"""
Posts a Bible verse of the day to X (@MKakitahiJ).

Verse is selected deterministically by day-of-year so the same verse
never repeats within a calendar year. Requires four env vars:
  X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
"""

import os
import sys
from datetime import date

import tweepy

VERSES = [
    ("Genesis 1:1", "In the beginning God created the heavens and the earth."),
    ("Genesis 1:27", "So God created mankind in his own image, in the image of God he created them; male and female he created them."),
    ("Exodus 14:14", "The Lord will fight for you; you need only to be still."),
    ("Deuteronomy 31:6", "Be strong and courageous. Do not be afraid or terrified because of them, for the Lord your God goes with you; he will never leave you nor forsake you."),
    ("Joshua 1:9", "Have I not commanded you? Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go."),
    ("Psalm 1:1-2", "Blessed is the one who does not walk in step with the wicked or stand in the way that sinners take or sit in the company of mockers, but whose delight is in the law of the Lord."),
    ("Psalm 16:8", "I keep my eyes always on the Lord. With him at my right hand, I will not be shaken."),
    ("Psalm 19:14", "May these words of my mouth and this meditation of my heart be pleasing in your sight, Lord, my Rock and my Redeemer."),
    ("Psalm 23:1", "The Lord is my shepherd, I lack nothing."),
    ("Psalm 23:4", "Even though I walk through the darkest valley, I will fear no evil, for you are with me; your rod and your staff, they comfort me."),
    ("Psalm 27:1", "The Lord is my light and my salvation — whom shall I fear? The Lord is the stronghold of my life — of whom shall I be afraid?"),
    ("Psalm 34:8", "Taste and see that the Lord is good; blessed is the one who takes refuge in him."),
    ("Psalm 37:4", "Take delight in the Lord, and he will give you the desires of your heart."),
    ("Psalm 46:1", "God is our refuge and strength, an ever-present help in trouble."),
    ("Psalm 46:10", "He says, 'Be still, and know that I am God; I will be exalted among the nations, I will be exalted in the earth.'"),
    ("Psalm 91:1-2", "Whoever dwells in the shelter of the Most High will rest in the shadow of the Almighty. I will say of the Lord, 'He is my refuge and my fortress, my God, in whom I trust.'"),
    ("Psalm 103:2-3", "Praise the Lord, my soul, and forget not all his benefits — who forgives all your sins and heals all your diseases."),
    ("Psalm 119:105", "Your word is a lamp for my feet, a light on my path."),
    ("Psalm 121:1-2", "I lift up my eyes to the mountains — where does my help come from? My help comes from the Lord, the Maker of heaven and earth."),
    ("Psalm 139:14", "I praise you because I am fearfully and wonderfully made; your works are wonderful, I know that full well."),
    ("Proverbs 3:5-6", "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight."),
    ("Proverbs 16:3", "Commit to the Lord whatever you do, and he will establish your plans."),
    ("Proverbs 18:10", "The name of the Lord is a fortified tower; the righteous run to it and are safe."),
    ("Isaiah 40:31", "But those who hope in the Lord will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint."),
    ("Isaiah 41:10", "So do not fear, for I am with you; do not be dismayed, for I am your God. I will strengthen you and help you; I will uphold you with my righteous right hand."),
    ("Isaiah 43:2", "When you pass through the waters, I will be with you; and when you pass through the rivers, they will not sweep over you."),
    ("Jeremiah 29:11", "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future."),
    ("Lamentations 3:22-23", "Because of the Lord's great love we are not consumed, for his compassions never fail. They are new every morning; great is your faithfulness."),
    ("Micah 6:8", "He has shown you, O mortal, what is good. And what does the Lord require of you? To act justly and to love mercy and to walk humbly with your God."),
    ("Matthew 5:14-16", "You are the light of the world. A town built on a hill cannot be hidden. Neither do people light a lamp and put it under a bowl... let your light shine before others."),
    ("Matthew 6:33", "But seek first his kingdom and his righteousness, and all these things will be given to you as well."),
    ("Matthew 11:28", "Come to me, all you who are weary and burdened, and I will give you rest."),
    ("Matthew 28:19-20", "Therefore go and make disciples of all nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit."),
    ("Mark 12:30-31", "Love the Lord your God with all your heart and with all your soul and with all your mind and with all your strength. Love your neighbor as yourself."),
    ("Luke 1:37", "For no word from God will ever fail."),
    ("John 1:1", "In the beginning was the Word, and the Word was with God, and the Word was God."),
    ("John 3:16", "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."),
    ("John 3:17", "For God did not send his Son into the world to condemn the world, but to save the world through him."),
    ("John 8:12", "I am the light of the world. Whoever follows me will never walk in darkness, but will have the light of life."),
    ("John 10:10", "The thief comes only to steal and kill and destroy; I have come that they may have life, and have it to the full."),
    ("John 11:25-26", "Jesus said to her, 'I am the resurrection and the life. The one who believes in me will live, even though they die; and whoever lives by believing in me will never die.'"),
    ("John 14:6", "Jesus answered, 'I am the way and the truth and the life. No one comes to the Father except through me.'"),
    ("John 14:27", "Peace I leave with you; my peace I give you. I do not give to you as the world gives. Do not let your hearts be troubled and do not be afraid."),
    ("John 15:5", "I am the vine; you are the branches. If you remain in me and I in you, you will bear much fruit; apart from me you can do nothing."),
    ("John 16:33", "I have told you these things, so that in me you may have peace. In this world you will have trouble. But take heart! I have overcome the world."),
    ("Acts 1:8", "But you will receive power when the Holy Spirit comes on you; and you will be my witnesses in Jerusalem, and in all Judea and Samaria, and to the ends of the earth."),
    ("Romans 1:16", "For I am not ashamed of the gospel, because it is the power of God that brings salvation to everyone who believes."),
    ("Romans 5:8", "But God demonstrates his own love for us in this: While we were still sinners, Christ died for us."),
    ("Romans 8:1", "Therefore, there is now no condemnation for those who are in Christ Jesus."),
    ("Romans 8:28", "And we know that in all things God works for the good of those who love him, who have been called according to his purpose."),
    ("Romans 8:38-39", "For I am convinced that neither death nor life, neither angels nor demons, neither the present nor the future, nor any powers... will be able to separate us from the love of God."),
    ("Romans 10:9", "If you declare with your mouth, 'Jesus is Lord,' and believe in your heart that God raised him from the dead, you will be saved."),
    ("Romans 12:2", "Do not conform to the pattern of this world, but be transformed by the renewing of your mind."),
    ("1 Corinthians 10:13", "No temptation has overtaken you except what is common to mankind. And God is faithful; he will not let you be tempted beyond what you can bear."),
    ("1 Corinthians 13:4-5", "Love is patient, love is kind. It does not envy, it does not boast, it is not proud. It does not dishonor others, it is not self-seeking."),
    ("1 Corinthians 13:13", "And now these three remain: faith, hope and love. But the greatest of these is love."),
    ("2 Corinthians 5:17", "Therefore, if anyone is in Christ, the new creation has come: The old has gone, the new is here!"),
    ("2 Corinthians 12:9", "But he said to me, 'My grace is sufficient for you, for my power is made perfect in weakness.'"),
    ("Galatians 2:20", "I have been crucified with Christ and I no longer live, but Christ lives in me. The life I now live in the body, I live by faith in the Son of God."),
    ("Galatians 5:22-23", "But the fruit of the Spirit is love, joy, peace, forbearance, kindness, goodness, faithfulness, gentleness and self-control."),
    ("Ephesians 2:8-9", "For it is by grace you have been saved, through faith — and this is not from yourselves, it is the gift of God — not by works, so that no one can boast."),
    ("Ephesians 3:20", "Now to him who is able to do immeasurably more than all we ask or imagine, according to his power that is at work within us."),
    ("Ephesians 6:10-11", "Finally, be strong in the Lord and in his mighty power. Put on the full armor of God, so that you can take your stand against the devil's schemes."),
    ("Philippians 1:6", "Being confident of this, that he who began a good work in you will carry it on to completion until the day of Christ Jesus."),
    ("Philippians 4:4", "Rejoice in the Lord always. I will say it again: Rejoice!"),
    ("Philippians 4:6-7", "Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God."),
    ("Philippians 4:13", "I can do all this through him who gives me strength."),
    ("Colossians 3:23", "Whatever you do, work at it with all your heart, as working for the Lord, not for human masters."),
    ("1 Thessalonians 5:16-18", "Rejoice always, pray continually, give thanks in all circumstances; for this is God's will for you in Christ Jesus."),
    ("2 Timothy 1:7", "For the Spirit God gave us does not make us timid, but gives us power, love and self-discipline."),
    ("2 Timothy 3:16-17", "All Scripture is God-breathed and is useful for teaching, rebuking, correcting and training in righteousness."),
    ("Hebrews 11:1", "Now faith is confidence in what we hope for and assurance about what we do not see."),
    ("Hebrews 12:1-2", "Let us run with perseverance the race marked out for us, fixing our eyes on Jesus, the pioneer and perfecter of faith."),
    ("Hebrews 13:8", "Jesus Christ is the same yesterday and today and forever."),
    ("James 1:2-3", "Consider it pure joy, my brothers and sisters, whenever you face trials of many kinds, because you know that the testing of your faith produces perseverance."),
    ("1 Peter 5:7", "Cast all your anxiety on him because he cares for you."),
    ("2 Peter 3:9", "The Lord is not slow in keeping his promise, as some understand slowness. Instead he is patient with you, not wanting anyone to perish, but everyone to come to repentance."),
    ("1 John 1:9", "If we confess our sins, he is faithful and just and will forgive us our sins and purify us from all unrighteousness."),
    ("1 John 4:8", "Whoever does not love does not know God, because God is love."),
    ("1 John 4:18", "There is no fear in love. But perfect love drives out fear."),
    ("Revelation 3:20", "Here I am! I stand at the door and knock. If anyone hears my voice and opens the door, I will come in and eat with that person, and they with me."),
    ("Revelation 21:4", "He will wipe every tear from their eyes. There will be no more death or mourning or crying or pain, for the old order of things has passed away."),
]


def pick_verse() -> tuple[str, str]:
    today = date.today()
    day_of_year = today.timetuple().tm_yday
    index = (day_of_year - 1) % len(VERSES)
    return VERSES[index]


def build_post(reference: str, text: str) -> str:
    post = f"📖 Verse of the Day\n\n\"{text}\"\n\n— {reference} (NIV)\n\n#VerseOfTheDay #BibleVerse #Faith"
    # X limit is 280 characters; trim verse text if needed
    if len(post) > 280:
        max_text_len = 280 - len(f'📖 Verse of the Day\n\n"..."\n\n— {reference} (NIV)\n\n#VerseOfTheDay #BibleVerse #Faith')
        text = text[: max_text_len - 3] + "..."
        post = f"📖 Verse of the Day\n\n\"{text}\"\n\n— {reference} (NIV)\n\n#VerseOfTheDay #BibleVerse #Faith"
    return post


def post_to_x(post_text: str) -> str:
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    response = client.create_tweet(text=post_text)
    return response.data["id"]


def main():
    reference, text = pick_verse()
    post_text = build_post(reference, text)

    print(f"Posting verse: {reference}")
    print(f"Character count: {len(post_text)}/280")
    print("---")
    print(post_text)
    print("---")

    tweet_id = post_to_x(post_text)
    print(f"Posted successfully. Tweet ID: {tweet_id}")


if __name__ == "__main__":
    main()

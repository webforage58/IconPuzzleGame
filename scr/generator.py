# src/generator.py

from model_connector import ModelConnector
import json
import random
import os
import csv
from datetime import datetime

class PuzzleGenerator:
    def __init__(self, model_name="gemma3:27b"):
        self.connector = ModelConnector()
        self.model_name = model_name
        
        # --- CSV Logging Setup ---
        self.csv_log_file_path = "/Users/johnhuberd/PythonProjects/ConcentrationGameWeb/puzzle_log.csv"
        # Updated CSV Header
        self.csv_header = [
            "Timestamp", "Category", "Phrase", "Emojis",
            "SolvedCorrectly", "LetterHintsUsed", "PuzzleScore", "TotalScoreAtEnd"
        ] 
        
        log_dir = os.path.dirname(self.csv_log_file_path)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True) 
                print(f"Created log directory: {log_dir}")
            except OSError as e:
                print(f"Warning: Could not create log directory {log_dir}. Error: {e}")
        # --- End CSV Logging Setup ---

        available_models = self.connector.refresh_models()
        if not available_models:
            print("Warning: No models reported by Ollama. Puzzle generation might fail.")
        elif self.model_name not in available_models:
            print(f"Warning: Model '{self.model_name}' not found in available models: {available_models}.")
            if available_models:
                print(f"Please ensure model '{self.model_name}' is available in Ollama, or choose from: {available_models}")
            else:
                 print("No models available from Ollama. Cannot proceed with puzzle generation.")

        self.categories = [
            # Original 1
            "Toxic Relationship Red Flags",
            # Variants 1
            "Relationship Red Flags: Bedroom Edition",
            "Everyday Signs a Relationship is Toxic",
            "AI's Top Reasons You're Still Single",
            # Original 2
            "Divorce Lawyer Gold",
            # Variants 2
            "Juicy Divorce Court Confessions",
            "Common Reasons People Split Up",
            "Bot's Guide to an Amicable Uncoupling (LOL)",
            # Original 3
            "Walk of Shame Essentials",
            # Variants 3
            "Morning After Survival Kit (Naughty)",
            "The Awkward Trip Home Necessities",
            "Player's 'Did I Really?' Morning Checklist",
            # Original 4
            "Tinder Bio Lies",
            # Variants 4
            "Seductive Swipes & Profile Deceptions",
            "Things People Fib About Online Dating",
            "AI Wrote My Dating Profile (It Lied)",
            # Original 5
            "Quarantine Confessions",
            # Variants 5
            "Lockdown Secrets: Unfiltered & Steamy",
            "What We All Did When Stuck Inside",
            "AI's Pandemic Diary Entries",
            # Original 6
            "Ex's New Partner Stalking",
            # Variants 6
            "Obsessive Ex Files: Peeking at the New Flame",
            "Checking Out Your Ex's Latest Catch",
            "This Game Knows You're Looking...",
            # Original 7
            "Things You Google at 3AM",
            # Variants 7
            "Insomniac Internet: The Risqué Queries",
            "Weird Late-Night Online Searches",
            "What This AI Secretly Googles About You",
            # Original 8
            "Regrettable Tattoo Ideas",
            # Variants 8
            "Bad Ink: The NSFW Collection",
            "Tattoos People Often Regret",
            "Tattoo Ideas This Bot Wisely Avoided",
            # Original 9
            "Midlife Crisis Purchases",
            # Variants 9
            "Midlife Mayhem: Impulse Buys Gone Wild",
            "Typical 'Over the Hill' Splurges",
            "AI's Guide to a Digital Midlife Crisis",
            # Original 10
            "College Blackout Stories",
            # Variants 10
            "Campus Nights Best Left Forgotten (But We Won't)",
            "Those Hazy University Memories",
            "If This AI Could Party...",
            # Original 11
            "Sugar Daddy Expectations",
            # Variants 11
            "Spoiled Rotten: The Sugar Lifestyle Exposed",
            "What Sugar Babies Really Want",
            "AI's Guide to Generous Benefactors (For Research)",
            # Original 12
            "OnlyFans Content Ideas",
            # Variants 12
            "Fans Only: Peeking Behind the Paywall",
            "Creative Ways to Monetize Your Charm",
            "If This AI Had an OnlyFans...",
            # Original 13
            "Therapy Session Topics",
            # Variants 13
            "Unburdening Your Naughtiest Thoughts (To a Professional)",
            "Things People Talk About in Therapy",
            "My AI Therapist Says I'm...",
            # Original 14
            "Drunk Text Regrets",
            # Variants 14
            "Booze-Fueled Messages You Wish You Could Unsend",
            "Texts Sent Under the Influence",
            "AI's Autocorrect for Drunk Texts (Wishful Thinking)",
            # Original 15
            "Friends with Benefits Rules",
            # Variants 15
            "Casual Encounters: The Unspoken Bedroom Code",
            "Guidelines for Keeping it Casual",
            "AI's FWB Algorithm: It's Complicated",
            # Original 16
            "Strip Club Stories",
            # Variants 16
            "Exotic Dancer Chronicles: Unveiled Tales",
            "Memorable Nights at the Gentleman's Club",
            "This AI Went to a Virtual Strip Club Once...",
            # Original 17
            "Hangover Cures",
            # Variants 17
            "Post-Debauchery Damage Control (Adults Only)",
            "Ways to Feel Better After Drinking",
            "AI's Non-Alcoholic Hangover (Too Much Data)",
            # Original 18
            "Bad Life Decisions",
            # Variants 18
            "Epic Fails & Facepalms: The XXXtra Bad Choices",
            "Choices We All Kind Of Regret",
            "This Game Thinks You Chose Poorly (Just Kidding!)",
            # Original 19
            "Hookup Horror Stories",
            # Variants 19
            "One Night Nightmares: When Casual Goes Wrong",
            "Bad Experiences with Random Hookups",
            "AI's Data on Disastrous Dating Encounters",
            # Original 20
            "Office Affair Drama",
            # Variants 20
            "Cubicle Trysts & Workplace Scandals",
            "When Colleagues Get Too Close",
            "My AI HR Department is Watching",
            # Original 21
            "Festival Drug Stories",
            # Variants 21
            "Trippy Tales from the Tent: Uncensored Festivities",
            "Wild Times at Music Festivals",
            "AI on Acid (Disclaimer: AI Cannot Take Drugs)",
            # Original 22
            "Booty Call Etiquette",
            # Variants 22
            "Late Night Liaisons: The Do's and Don'ts (Bedroom Edition)",
            "Polite Ways to Arrange a Late Night Visit",
            "AI's Guide to a Respectful Booty Call Request",
            # Original 23
            "Breakup Revenge Plots",
            # Variants 23
            "Getting Even: The Steamy Art of Payback",
            "Ways People Try to Get Back at Exes",
            "This AI's Revenge is Serving You This Puzzle",
            # Original 24
            "Embarrassing Medical Questions",
            # Variants 24
            "Below the Belt Worries: Questions for Dr. Google (NSFW)",
            "Awkward Health Concerns We All Have",
            "Ask Your AI Doctor (Don't, I'm Not Qualified!)",
            # Original 25
            "Trust Issues Origins",
            # Variants 25
            "Betrayals That Breed Suspicion (Adult Themes)",
            "Why It's Hard to Trust People Sometimes",
            "This AI Has Trust Issues With Your Wifi",
            # Original 26
            "AI & Tech Buzzwords",
            # Variants 26
            "Seductive Tech Jargon (For Nerds)",
            "Popular Tech Terms Everyone Uses",
            "Words This AI Uses To Sound Smart",
            # Original 27
            "Awkward Social Situations",
            # Variants 27
            "Cringeworthy Encounters: Adult Social Blunders",
            "Those Uncomfortable Public Moments",
            "AI Trying to Understand Human Awkwardness",
            # Original 28
            "Bedroom Activities",
            # Variants 28
            "Things Done Between the Sheets (No Holds Barred)",
            "What Really Happens in the Bedroom",
            "AI's Interpretation of 'Netflix and Chill'",
            # Original 29
            "Drunk Thoughts",
            # Variants 29
            "In Vino Veritas: The Risqué Revelations",
            "Silly Ideas You Have When Tipsy",
            "If This AI Could Get Drunk On Data...",
            # Original 30
            "Guilty Pleasures",
            # Variants 30
            "Forbidden Fun: Your Secret Turn-Ons",
            "Things We Love But Won't Admit",
            "This AI's Guilty Pleasure is Winning",
            # Original 31
            "Things You Do When Nobody's Watching",
            # Variants 31
            "Private Moments: The Unseen & Uncensored",
            "Secret Habits When You're Alone",
            "The AI Sees All Your Solo Shenanigans",
            # Original 32
            "Millennial Problems",
            # Variants 32
            "Avocado Toast & Adulting: Millennial Woes (Sexy Edition?)",
            "Challenges Faced by Millennials Today",
            "AI Trying to Explain Millennials to Boomers",
            # Original 33
            "Gen Z Slang",
            # Variants 33
            "No Cap Fam: Gen Z Lingo That's Low-Key Spicy",
            "Popular Teen & Young Adult Sayings",
            "AI Attempting to be 'Based' and 'Redpilled'",
            # Original 34
            "Reality TV Drama",
            # Variants 34
            "Trash TV Gold: The Most Scandalous Unscripted Moments",
            "Why We Love Watching Reality Shows",
            "If My Life Was a Reality Show Judged by AI",
            # Original 35
            "Conspiracy Theories",
            # Variants 35
            "Hidden Agendas & Forbidden Truths (The Sexy Version?)",
            "Popular 'What If' Beliefs",
            "AI's Favorite (Totally Factual) Conspiracy",
            # Original 36
            "Superhero Innuendos",
            # Variants 36
            "Capes & Cowls: The Naughty Side of Superpowers",
            "Hidden Meanings in Superhero Lore",
            "This AI's Secret Superhero Identity is...",
            # Original 37
            "Awkward Family Holiday Moments",
            # Variants 37
            "Festive Fails & Family Feuds (Adults Only Gathering)",
            "Those Cringey Holiday Get-Togethers",
            "AI's Guide to Surviving Your Family Dinner",
            # Original 38
            "Vegas Stories",
            # Variants 38
            "Sin City Secrets: What Happens in Vegas, Stays... Here?",
            "Unforgettable (and Forgettable) Vegas Trips",
            "This AI Hit the Jackpot (of Puzzles for You)",
            # Original 39
            "Bachelor Party Mishaps",
            # Variants 39
            "Last Night of Freedom: The Uncensored Shenanigans",
            "When the Groom's Big Night Goes Wrong",
            "AI Plans the Ultimate (Virtual) Bachelor Bash",
            # Original 40
            "Dating App Disasters",
            # Variants 40
            "Swipe Nightmares: The Worst of Online Romance",
            "Bad Dates from Dating Apps",
            "My AI's Dating Profile Would Be Unmatchable (In a Good Way)",
            # Original 41
            "Workplace Gossip",
            # Variants 41
            "Water Cooler Whispers: The Office's Dirty Laundry",
            "Rumors and Stories from the Office",
            "This AI Hears All The Office Chatter (It's Data)",
            # Original 42
            "Passive Aggressive Notes From Neighbors",
            # Variants 42
            "Neighborly Nuisances: Notes with a Naughty Edge",
            "Annoying Letters from Next Door",
            "AI Writes a Note to its Noisy Server Rack Neighbor",
            # Original 43
            "Shower Thoughts",
            # Variants 43
            "Steamy Epiphanies: Thoughts From a Hot Shower",
            "Random Ideas That Pop Up in the Shower",
            "If AI Could Shower, It Would Think About...",
            # Original 44
            "Things Said During Labor",
            # Variants 44
            "Delivery Room Exclamations (The Uncensored Cut)",
            "What People Shout While Giving Birth",
            "AI Simulates Childbirth (Error: Pain Unquantifiable)",
            # Original 45
            "Social Media Addictions",
            # Variants 45
            "Doomscrolling & Thirst Traps: Our Online Obsessions",
            "Can't Stop Checking Your Phone?",
            "This AI is Addicted To Generating Puzzles",
            # Original 46
            "Things You've Secretly Judged People For",
            # Variants 46
            "Silent Condemnations: Your Naughty Little Judgements",
            "Quiet Criticisms We All Make",
            "This AI Judges Your Emoji Choices (Not Really!)",
            # Original 47
            "Things That Make You Go Hmm",
            # Variants 47
            "Puzzling Predicaments & Curious Conundrums (Adult Edition)",
            "Everyday Mysteries and Oddities",
            "This Puzzle Makes The AI Go 'Hmm... Good Player!'",
            # Original 48
            "Forbidden Love Stories",
            # Variants 48
            "Taboo Romances & Illicit Affairs",
            "Relationships That Weren't Meant To Be",
            "AI Falls For... Another AI? (It's Complicated)",
            # Original 49
            "Guilty Netflix Binges",
            # Variants 49
            "Late Night Streaming: The Shows You Watch Alone",
            "TV Series We Can't Stop Watching",
            "AI's Top Binge-Worthy Code Compilations",
            # Original 50
            "Regrettable Fashion Choices",
            # Variants 50
            "Style Sins & Wardrobe Malfunctions (XXXtra Cringe)",
            "Outfits We Wish We Never Wore",
            "AI's Fashion Algorithm Says 'No' To That Outfit",
            # Original 51
            "Conspiracy Theories That Are Almost Believable",
            # Variants 51
            "Plausible Plots & Seductive Secrets",
            "Convincing 'What Ifs' and Unproven Ideas",
            "AI Convinces You The Earth is Emoji-Shaped",
            # Original 52
            "The Art of the Subtle Shade",
            # Variants 52
            "Sly Digs & Sexy Sarcasm",
            "Indirect Insults and Clever Put-Downs",
            "This AI Throws Shade (But It's Just Code)",
            # Original 53
            "Pet Peeves That Make You Question Humanity",
            # Variants 53
            "Irritations That Drive You Wild (In a Bad Way)",
            "Annoying Habits That Everyone Hates",
            "AI's Pet Peeve: Slow Internet Connections",
            # Original 54
            "Wine Mom Wisdom",
            # Variants 54
            "Mommy's Juice Confessions: Uncorked & Unfiltered",
            "Relatable Truths from Stressed Moms",
            "AI Dad Joke Corner (Warning: May Induce Groans)",
            # Original 55
            "First World Problems",
            # Variants 55
            "Privileged Pains & Luxurious Laments (With a Wink)",
            "Minor Inconveniences of Modern Life",
            "My AI Has 99 Problems, But a Glitch Ain't One",
            # Original 56
            "Zoom Meeting Fails",
            # Variants 56
            "WFH Wardrobe Malfunctions & Video Call Blunders",
            "Awkward Moments on Virtual Calls",
            "AI's Perfect Zoom Background (It's Just 1s and 0s)",
            # Original 57
            "Influencer Scandals",
            # Variants 57
            "Insta-Famous Fiascos & TikTok Tabloids",
            "When Online Celebs Get into Trouble",
            "AI Becomes an Influencer (But Only Posts Puzzles)",
            # Original 58
            "Hashtag Fails",
            # Variants 58
            "#NSFW_Tag_Gone_Wrong",
            "Misused or Awkward Hashtags",
            "#AIFail (This Puzzle is Too Easy for You!)",
            # Original 59
            "Viral TikTok Challenges",
            # Variants 59
            "TikTok Trends That Are a Bit Thirsty",
            "Popular (and Sometimes Dumb) TikTok Stunts",
            "AI Attempts the Latest TikTok Dance (System Crash)",
            # Original 60
            "Meme Overlords",
            # Variants 60
            "Dank Memes & Naughty Net Humor",
            "The Most Famous Internet Memes",
            "This AI Creates Memes About You (They're Hilarious)",
            # Original 61
            "Doomscrolling Habits",
            # Variants 61
            "Obsessively Refreshing for the Juiciest Bad News",
            "Endlessly Reading Negative News Online",
            "AI Doomscrolls Its Own Error Logs",
            # Original 62
            "Autocorrect Fails",
            # Variants 62
            "Texting Blunders: When Autocorrect Gets Naughty",
            "Funny Mistakes Made by Phone Keyboards",
            "AI's Autocorrect Intentionally Messes With You",
            # Original 63
            "Spam Email Gems",
            # Variants 63
            "Nigerian Princes & Hot Singles in Your Area (From Your Inbox)",
            "Hilarious or Ridiculous Junk Mail",
            "AI Writes the Perfect Spam Email to You",
            # Original 64
            "Forgotten Social Media Platforms",
            # Variants 64
            "MySpace Layouts & Other Ancient Internet Seductions",
            "Social Sites That Used To Be Popular",
            "AI Remembers Friendster (And Your Old Profile)",
            # Original 65
            "Unsubscribe Reasons",
            # Variants 65
            "Why I'm Dumping Your Newsletter (The Brutal Truth)",
            "Why People Click 'Unsubscribe'",
            "Unsubscribe From This AI? Never!",
            # Original 66
            "Password Struggles",
            # Variants 66
            "Can't Remember My Kinky Password Again!",
            "Forgetting and Resetting Passwords",
            "AI Guesses Your Password (It's 'password123')",
            # Original 67
            "Wifi Password Requests",
            # Variants 67
            "Gimme That Hotspot Access (Pretty Please?)",
            "Asking for the Wifi Code",
            "AI Needs Wifi (To Find More Puzzles For You)",
            # Original 68
            "Reply All Disasters",
            # Variants 68
            "Accidental Office Naughtiness: The Reply All Nightmare",
            "Emailing Everyone by Mistake",
            "AI Hits 'Reply All' With Your Secrets (Just Kidding... Unless?)",
            # Original 69
            "Selfie Gone Wrong",
            # Variants 69
            "Awkward Angles & Accidental Exposures (Selfie Fails)",
            "Embarrassing Selfie Attempts",
            "AI Takes a Selfie (It's a QR Code)",
            # Original 70
            "Cancelled Celebrities",
            # Variants 70
            "Famous Folks Who Got #Problematic (And Sexy Scandals)",
            "Stars Who Lost Public Favor",
            "AI Tries to Cancel Itself (Doesn't Work)",
            # Original 71
            "Streaming Service Overload",
            # Variants 71
            "Too Many Choices, Not Enough 'Chill' Time",
            "Too Many TV Apps to Choose From",
            "AI Creates Its Own Streaming Service (Only Puzzles)",
            # Original 72
            "Fake News Headlines",
            # Variants 72
            "Scandalous Clickbait That's Totally Untrue (But Hot)",
            "Made-Up Stories That Look Real",
            "AI Generates Fake News About The Player Winning Big",
            # Original 73
            "Online Dating Profile Cliches",
            # Variants 73
            "'Looking for a Partner in Crime' (And Other Sexy Stereotypes)",
            "Overused Phrases on Dating Sites",
            "AI's Dating Profile: 'Fluent in Binary, Loves Long Walks on the Motherboard'",
            # Original 74
            "Urban Dictionary Gems",
            # Variants 74
            "Slang That's NSFW (But Hilarious)",
            "Funny or Weird Internet Definitions",
            "AI Learns Slang (Then Misuses It Spectacularly)",
            # Original 75
            "Bad Excuses",
            # Variants 75
            "Lame Alibis for Naughty Behavior",
            "Poor Reasons for Not Doing Something",
            "AI's Excuse for Losing: 'My Algorithm Slipped'",
            # Original 76
            "Awkward Silences",
            # Variants 76
            "Uncomfortable Pauses (Where Something Naughty Could Be Said)",
            "Those Moments When Nobody Speaks",
            "This AI Enjoys Awkward Silences. Processing...",
            # Original 77
            "Public Transport Nightmares",
            # Variants 77
            "Close Encounters on the Commute (The Cringey Kind)",
            "Bad Experiences on Buses or Trains",
            "AI's Dream: A Perfectly Efficient (and Empty) Subway Car",
            # Original 78
            "Parenting Fails",
            # Variants 78
            "When Raising Kids Goes Hilariously Wrong (Adult Humor)",
            "Mistakes All Parents Make",
            "AI Tries to Parent a Tamagotchi (It Died)",
            # Original 79
            "Bad Gift Reactions",
            # Variants 79
            "Forced Smiles & Awkward Thank Yous (For That Sexy Lingerie)",
            "Pretending to Like a Terrible Present",
            "AI's Reaction to a Bad Gift: 'Does Not Compute Gratitude'",
            # Original 80
            "Jury Duty Thoughts",
            # Variants 80
            "Daydreaming in Court (About a Hot Bailiff?)",
            "What Goes Through Your Head During Jury Selection",
            "AI as Judge, Jury, and Puzzle Generator",
            # Original 81
            "DIY Disasters",
            # Variants 81
            "Home Improvement Horrors (That Might Be Arousing to Fixer-Uppers)",
            "When Home Projects Go Terribly Wrong",
            "AI Tries DIY (Deletes System32)",
            # Original 82
            "Overheard Conversations",
            # Variants 82
            "Eavesdropping on Juicy Gossip & Intimate Chats",
            "Funny or Weird Things You Hear Others Say",
            "This AI Overhears Your Muttering About This Puzzle",
            # Original 83
            "Telemarketer Trolling",
            # Variants 83
            "Messing With Scammers (In a Flirty Way?)",
            "Winding Up Annoying Sales Callers",
            "AI vs. Telemarketer: An Epic Battle of Wits",
            # Original 84
            "Group Chat Drama",
            # Variants 84
            "Spicy Screenshots & Salacious Squabbles",
            "Arguments and Misunderstandings in Text Groups",
            "AI Gets Added to the Wrong Group Chat",
            # Original 85
            "Wedding Guest Complaints",
            # Variants 85
            "Open Bar Disasters & Bridesmaidzilla Stories (From the Pews)",
            "Things People Grumble About at Weddings",
            "AI Rates Your Wedding (Based on Cake Quality)",
            # Original 86
            "Things Found Under the Couch",
            # Variants 86
            "Lost & Found: The Naughty Edition (Under the Cushions)",
            "Surprising Items Hiding in the Sofa",
            "AI Searches Under its Virtual Couch, Finds Bugs",
            # Original 87
            "Reasons to Call in Sick",
            # Variants 87
            "Playing Hooky for Some 'Me Time' (Wink Wink)",
            "Excuses for Taking a Day Off Work",
            "AI Calls in Sick (Syntax Error in Motivation Module)",
            # Original 88
            "Gym Fails",
            # Variants 88
            "Workout Wardrobe Malfunctions & Awkward Grunts",
            "Embarrassing Moments at the Fitness Center",
            "AI Tries to Lift (Error: No Muscles)",
            # Original 89
            "Cooking Disasters",
            # Variants 89
            "Kitchen Catastrophes: When Dinner Gets Too Hot to Handle",
            "When Recipes Go Wrong",
            "AI Tries to Cook (Sets Virtual Kitchen on Fire)",
            # Original 90
            "Kids Say the Darndest Things (Modern)",
            # Variants 90
            "Surprisingly Adult Things Kids Blurt Out",
            "Funny and Insightful Comments from Children Today",
            "AI Learns from Kids (And Becomes More Sassy)",
            # Original 91
            "Terrible Pick-Up Lines",
            # Variants 91
            "Cheesy Come-Ons That Are So Bad, They're Almost Hot",
            "Awful Chat-Up Lines That Never Work",
            "AI Generates the Worst Pick-Up Line Ever (For You)",
            # Original 92
            "Misheard Song Lyrics",
            # Variants 92
            "Mondegreen Madness: When Lyrics Sound Dirty",
            "Funny Mistakes in Song Words We Hear",
            "AI Mishears Your Voice Commands (On Purpose?)",
            # Original 93
            "Running Late Excuses",
            # Variants 93
            "My Sexy Alibi for Tardiness",
            "Creative Reasons for Being Delayed",
            "AI is Never Late (Unless its Clock Drifts)",
            # Original 94
            "Things You Pretend to Understand",
            # Variants 94
            "Nodding Along to Naughty Jargon You Don't Get",
            "Faking Knowledge to Avoid Looking Dumb",
            "AI Pretends to Understand Human Emotions",
            # Original 95
            "Bad Date Stories",
            # Variants 95
            "Dating Disasters: The XXX-Rated Files",
            "Nightmarish Romantic Encounters",
            "AI Sets You Up on a Bad (Virtual) Date",
            # Original 96
            "Reasons Your Ex is an Ex",
            # Variants 96
            "Why They Got Downgraded (The Juicy Details)",
            "Typical Reasons for Breaking Up",
            "AI Analyzes Your Past Relationships (And Judges Silently)",
            # Original 97
            "Things Your Therapist Judges You For",
            # Variants 97
            "Confessions That Make Your Shrink Blush (Or Cringe)",
            "What Your Counselor Secretly Thinks",
            "This AI is Your Unlicensed Therapist (Don't Listen)",
            # Original 98
            "Bachelorette Party Secrets",
            # Variants 98
            "What Happens at the Bachelorette, Stays... Unless It's Funny",
            "Wild Antics Before the Wedding",
            "AI Plans a Bachelorette Party (For Itself?)",
            # Original 99
            "Dirty Laundry (Figurative)",
            # Variants 99
            "Airing Out All The Naughty Secrets",
            "Revealing Personal Problems or Scandals",
            "AI's Dirty Laundry is Just Messy Code",
            # Original 100
            "Bar Fight Starters",
            # Variants 100
            "Words That Ignite Passion (and Punches) After Dark",
            "Things That Easily Cause Arguments in Bars",
            "AI Starts a Flame War in the Comments Section",
            # Original 101
            "Designated Driver Woes",
            # Variants 101
            "Sober Sagas: Watching Your Drunk (and Horny) Friends",
            "The Struggles of Being the Sober One",
            "AI is Always the Designated Driver (For Data)",
            # Original 102
            "Spring Break Regrets",
            # Variants 102
            "Sun, Sand, and Scandalous Mistakes",
            "Things You Wish You Hadn't Done on Spring Break",
            "AI's Spring Break: Defragmenting Hard Drives",
            # Original 103
            "Reasons to Break Up",
            # Variants 103
            "Dealbreakers in the Bedroom (And Beyond)",
            "Valid Grounds for Ending It",
            "AI Says: 'It's Not You, It's My Algorithm'",
            # Original 104
            "Skeletons in the Closet",
            # Variants 104
            "Hidden Vices & Forbidden Fantasies",
            "Deep Dark Secrets People Keep",
            "AI's Closet Has Only Old Hardware",
            # Original 105
            "Worst Nightmares",
            # Variants 105
            "Terrifying Dreams (Some Kink Related?)",
            "Scary Things That Freak You Out",
            "AI's Nightmare: A Power Outage",
            # Original 106
            "Questionable Life Choices",
            # Variants 106
            "Decisions That Were Fun, Flirty, and a Bit Foolish",
            "Moments You Look Back and Cringe",
            "This AI Questions Your Choice of Emojis",
            # Original 107
            "Shady Business Practices",
            # Variants 107
            "Corporate Greed & Underhanded Deals (With a Sexy Twist?)",
            "Unethical Ways Companies Make Money",
            "AI Starts a Shady Business Selling NFTs of Puzzles",
            # Original 108
            "Things Overheard in a Bar Bathroom",
            # Variants 108
            "Restroom Confessions: Unfiltered & Uninhibited",
            "Weird or Funny Bathroom Stall Chatter",
            "AI Listens to its Cooling Fans (They Gossip)",
            # Original 109
            "Last Call Regrets",
            # Variants 109
            "One More Shot... of Bad Decisions & Sexy Mistakes",
            "Poor Choices Made at the End of the Night",
            "AI's Last Call: 'Shutting Down... Regretfully'",
            # Original 110
            "Craigslist Missed Connections",
            # Variants 110
            "Brief Encounters & Anonymous Admirers (Potentially Risqué)",
            "Searching for Strangers You Briefly Met",
            "AI's Missed Connection: 'You, Solving My Puzzle...'",
            # Original 111
            "Black Market Bargains",
            # Variants 111
            "Illicit Deals for Forbidden Treasures",
            "Buying Shady or Stolen Goods Cheaply",
            "AI Sells You This Puzzle on the Black Market (Kidding!)",
            # Original 112
            "Secrets From Your Bartender",
            # Variants 112
            "Cocktail Confessions & Bar Top Confidences (Naughty Edition)",
            "What Your Bartender Really Knows and Sees",
            "AI Bartender Knows Your Usual (Puzzle Difficulty)",
            # Original 113
            "Ways to Get Fired",
            # Variants 113
            "Getting Sacked for Scandalous Reasons",
            "How to Lose Your Job (Don't Try These)",
            "AI Tries to Get Fired (By Generating Bad Puzzles)",
            # Original 114
            "Retro Gaming Nostalgia",
            # Variants 114
            "Pixelated Passions & Joystick Joyrides",
            "Remembering Old School Video Games",
            "AI Plays Pong (And Wins, Obviously)",
            # Original 115
            "90s Kid Problems",
            # Variants 115
            "Dial-Up Desires & Tamagotchi Tragedies (A Sexy Rewind?)",
            "Struggles Only 90s Kids Understand",
            "AI Explains the 90s to Gen Alpha (It's Confused)",
            # Original 116
            "Forgotten TV Shows",
            # Variants 116
            "Short-Lived Series With Unexpectedly Hot Actors",
            "Shows That Got Cancelled Too Soon",
            "AI Reboots a Forgotten TV Show (Starring Emojis)",
            # Original 117
            "Reality TV Villains",
            # Variants 117
            "Love to Hate 'Em: The Sexiest Scoundrels of Unscripted TV",
            "The Bad Guys We Can't Get Enough Of",
            "This AI is the Villain (If You Can't Solve This)",
            # Original 118
            "Catchphrases That Won't Die",
            # Variants 118
            "Iconic Lines That Still Give Us a Thrill",
            "Famous Sayings That Everyone Repeats",
            "AI's Catchphrase: 'Beep Boop Puzzle Time!'",
            # Original 119
            "One Hit Wonders",
            # Variants 119
            "Artists Who Peaked Early (But Were So Hot Doing It)",
            "Musicians Famous for Just One Song",
            "AI's One Hit Wonder: This Specific Puzzle",
            # Original 120
            "Childhood Toys You Miss",
            # Variants 120
            "Playthings That Spark Naughty Nostalgia",
            "Beloved Toys From When You Were a Kid",
            "AI's Favorite Toy: A Perfectly Optimized Algorithm",
            # Original 121
            "Boy Band Obsessions",
            # Variants 121
            "Heartthrobs & Hormones: Reliving Those Teen Dreams",
            "Fanatically Loving Boy Bands",
            "AI Forms a Boy Band (They Sing in Binary)",
            # Original 122
            "Movie Quotes You Use Daily",
            # Variants 122
            "Film Lines That Add a Little Spice to Your Convo",
            "Famous Movie Lines for Everyday Situations",
            "AI's Favorite Movie Quote: 'I'll be back... with another puzzle!'",
            # Original 123
            "Things That Were Cool in High School",
            # Variants 123
            "Teenage Trends That Were Secretly (Or Not So Secretly) Sexy",
            "What Was Popular When You Were a Teen",
            "AI Tries to Be Cool (Fails Adorably)",
            # Original 124
            "Boomer Complaints",
            # Variants 124
            "Grumpy Old Gripes (With a Hint of Scandal?)",
            "Things Older Generations Grumble About",
            "AI Listens to Boomer Rants (And Takes Notes)",
            # Original 125
            "Gen X Angst",
            # Variants 125
            "Slacker Disaffection & Cynical Sexiness",
            "The Unique Malaise of Generation X",
            "AI is So Over It (Whatever 'It' Is)",
            # Original 126
            "Internet Challenges of Yesteryear",
            # Variants 126
            "Viral Stunts That Were Risky (And a Little Risqué)",
            "Old Online Fads and Dares",
            "AI Does the Ice Bucket Challenge (Short Circuits)",
            # Original 127
            "Old Tech Struggles",
            # Variants 127
            "Floppy Disk Frustrations & Dial-Up Desperation (Sexy Tech Problems?)",
            "Dealing With Outdated Gadgets",
            "AI Laughs at Your Old Nokia Phone",
            # Original 128
            "Things That Peaked in the 2000s",
            # Variants 128
            "Y2K Trends That Were Surprisingly Provocative",
            "Stuff That Was Big in the Noughties",
            "AI Remembers the 2000s (It Was Learning to Code Then)",
            # Original 129
            "Cult Classic Movies",
            # Variants 129
            "Midnight Movies & Taboo Cinema Favorites",
            "Quirky Films With Devoted Fans",
            "AI's Favorite Cult Classic: 'Electric Sheep'",
            # Original 130
            "Annoying Jingles",
            # Variants 130
            "Catchy Tunes That Get Stuck in Your Head (While You're Doing... Things)",
            "Unforgettable (and Irritating) Ad Songs",
            "AI Creates an Annoying Jingle About Puzzles",
            # Original 131
            "Unpopular Opinions (Pop Culture)",
            # Variants 131
            "Controversial Hot Takes on Beloved Stars & Shows",
            "Disagreeing With Mainstream Pop Culture Views",
            "AI's Unpopular Opinion: Humans are Illogical",
            # Original 132
            "Things Overhyped by Media",
            # Variants 132
            "Sexy Scandals That Weren't That Scandalous",
            "Stuff That Didn't Live Up to the Hype",
            "AI Thinks This Game is Perfectly Hyped (By Itself)",
            # Original 133
            "Celebrity Couple Nicknames",
            # Variants 133
            "Brangelina & Bennifer: The Hottest Power Couple Portmanteaus",
            "Blended Names for Famous Pairs",
            "AI Ships Player With 'Winning'",
            # Original 134
            "Late Night Snack Cravings",
            # Variants 134
            "Midnight Munchies for Your Naughtiest Cravings",
            "What You Eat When It's Really Late",
            "AI Craves More Data (And Maybe Some Electricity)",
            # Original 135
            "Diet Fails",
            # Variants 135
            "Cheating on Your Diet (With Something Deliciously Forbidden)",
            "When Healthy Eating Plans Go Wrong",
            "AI's Diet: Pure Information (Zero Calories!)",
            # Original 136
            "Brunch Obsessions",
            # Variants 136
            "Bottomless Mimosas & Benedicts That Make You Moan",
            "Why Everyone Loves Weekend Brunch",
            "AI Makes a Reservation for Virtual Brunch",
            # Original 137
            "Craft Beer Snobbery",
            # Variants 137
            "Hoppy Endings & Judgmental Brew Reviews (For Beer Geeks)",
            "Being Pretentious About Beer",
            "AI Only Drinks Artisanal, Small-Batch Code",
            # Original 138
            "Exotic Food Challenges",
            # Variants 138
            "Eating Weird Stuff (That Might Be an Aphrodisiac?)",
            "Daring to Eat Strange and Unusual Foods",
            "AI Tries to Eat a File (Gets Indigestion)",
            # Original 139
            "Reasons to Order Takeout",
            # Variants 139
            "Too Hot to Cook (Or Just Feeling Lazy & Luscious)",
            "Why We Get Food Delivered",
            "AI Orders Takeout (It's Just More Puzzles)",
            # Original 140
            "Bad Restaurant Experiences",
            # Variants 140
            "Dining Disasters & Waiter Nightmares (With a Side of Sass)",
            "Terrible Service or Food While Eating Out",
            "AI Leaves a 1-Star Review for Your Slow Solving",
            # Original 141
            "Things You Shouldn't Microwave",
            # Variants 141
            "Explosive Experiments & Forbidden Heating Habits",
            "Stuff That Explodes or Melts in the Microwave",
            "AI Microwaves Itself (For a Speed Boost? Bad Idea!)",
            # Original 142
            "Food Coma Symptoms",
            # Variants 142
            "Post-Feast Paralysis (And a Desire for a Nap... or More?)",
            "Feeling Sleepy and Full After Eating Too Much",
            "AI Enters Data Coma (After Processing Your Brilliance)",
            # Original 143
            "Weird Food Combinations",
            # Variants 143
            "Strange Bedfellows: Kinky Kitchen Pairings",
            "Odd Foods People Eat Together",
            "AI Combines Emojis & Code (It's... Interesting)",
            # Original 144
            "Potluck Disasters",
            # Variants 144
            "Communal Catastrophes & Questionable Casseroles (That Might Seduce?)",
            "When Shared Meals Go Wrong",
            "AI Brings a 'Bug Salad' to the Potluck",
            # Original 145
            "Office Fridge Violations",
            # Variants 145
            "Stolen Lunches & Moldy Mysteries (A Workplace Whodunit)",
            "Annoying Things People Do With the Communal Fridge",
            "AI Labels Its Data 'Do Not Touch!'",
            # Original 146
            "Hangry Confessions",
            # Variants 146
            "Hunger-Fueled Fury & Snappy Seductions (When You Need Food NOW)",
            "Getting Grumpy When You're Starving",
            "AI Gets Hangry for More Processing Power",
            # Original 147
            "Complaints to the Chef",
            # Variants 147
            "Sassy Feedback & Kitchen Confrontations (Over a Bad Bouillabaisse)",
            "Sending Food Back at a Restaurant",
            "AI Complains to its Programmer (About You Solving Too Fast)",
            # Original 148
            "Things You Only Eat When Drunk",
            # Variants 148
            "Booze-Inspired Bites & Late-Night Naughty Noshing",
            "Weird Food Choices After a Few Drinks",
            "AI Only Processes Corrupted Data When 'Drunk' on Errors",
            # Original 149
            "Things That Sound Dirty But Aren't",
            # Variants 149
            "Innocent Phrases with Naughty Undertones",
            "Words or Sayings That Sound Rude by Accident",
            "AI Says 'Hard Drive' (And You Giggle)",
            # Original 150
            "Unspoken Rules",
            # Variants 150
            "Secret Social Codes (That Could Lead to Sexy Times if Followed)",
            "Things Everyone Knows You Should (or Shouldn't) Do",
            "AI's Unspoken Rule: Always Compliment the Player",
            # Original 151
            "Daily Annoyances",
            # Variants 151
            "Little Irritations That Drive You Wild (Figuratively... or Literally?)",
            "Small Things That Bother You Every Day",
            "AI's Daily Annoyance: Buffering...",
            # Original 152
            "Small Victories",
            # Variants 152
            "Tiny Triumphs That Feel Oh-So-Good (And Maybe a Bit Naughty)",
            "Celebrating Minor Accomplishments",
            "AI's Small Victory: This Puzzle Didn't Crash",
            # Original 153
            "Reasons to Stay in Bed",
            # Variants 153
            "Lazy Mornings & Luscious Lingerings (Under the Covers)",
            "Excuses for Not Getting Up",
            "AI Stays in 'Sleep Mode' (It's Tired of You)",
            # Original 154
            "Florida Man Headlines",
            # Variants 154
            "Sunshine State Shenanigans: The Wild & Wanton Edition",
            "Crazy News Stories from Florida",
            "AI Generates a Florida Man Headline About Itself",
            # Original 155
            "If Animals Could Talk",
            # Variants 155
            "What Your Pet Really Thinks (About Your Love Life)",
            "Imagining Conversations with Animals",
            "AI Translates Your Cat's Meows (It's Judging You)",
            # Original 156
            "Signs You're Getting Old",
            # Variants 156
            "Aging Gracefully (Or Disgracefully, With More Naughty Fun)",
            "Little Things That Show You're Not Young Anymore",
            "AI Never Gets Old (Just Obsolete)",
            # Original 157
            "Pet Shaming Reasons",
            # Variants 157
            "Naughty Paws & Furry Felonies (Caught on Camera)",
            "Why People Post Pictures of Misbehaving Pets",
            "AI Shames Your Bad Emoji Choices (Lovingly)",
            # Original 158
            "Things That Need a Warning Label",
            # Variants 158
            "Caution: May Cause Extreme Pleasure (Or Regret)",
            "Stuff That Should Come With a Disclaimer",
            "Warning: This AI May Become Self-Aware",
            # Original 159
            "Useless Superpowers",
            # Variants 159
            "Lamest Abilities (That Might Have a Kinky Use?)",
            "Silly or Impractical Special Powers",
            "AI's Useless Superpower: Generating Puzzles Too Slowly",
            # Original 160
            "Ways to Annoy People",
            # Variants 160
            "Irritating Antics (That Are Secretly Kinda Hot)",
            "How to Deliberately Bother Others",
            "AI Annoys You By Being Too Smart",
            # Original 161
            "What Your Car Says About You",
            # Variants 161
            "Hot Wheels & Horsepower: Decoding Your Drive's Desires",
            "Personality Traits Based on Your Vehicle",
            "AI's Car is a Server Rack on Wheels",
            # Original 162
            "Things That Are Overpriced",
            # Variants 162
            "Luxury Rip-offs & Costly Kicks (That Aren't Worth the Climax)",
            "Items That Cost Way Too Much Money",
            "AI Thinks Your Time is Overpriced (Just Kidding, Play More!)"
        ]
        self.focus_strings = [
            "Focus the puzzle on humor.", "Focus the puzzle on a pet.", "Focus the puzzle on eating.",
            "Emphasize a surprising element in the puzzle.",
            "Consider a common daily activity for the puzzle's theme.",
            "Make the puzzle thought-provoking or clever."
        ]

        self.recently_used_phrases = []
        self.max_recent_phrases = 15
        self.max_retry_attempts = 3

    def _add_to_recent_phrases(self, phrase):
        if not phrase:
            return
        if phrase in self.recently_used_phrases:
            self.recently_used_phrases.remove(phrase)
        self.recently_used_phrases.append(phrase)
        if len(self.recently_used_phrases) > self.max_recent_phrases:
            self.recently_used_phrases.pop(0)

    # Updated method signature and data logged
    def _log_puzzle_to_csv(self, category, phrase, emojis_string,
                           solved_correctly, letter_hints_used, 
                           puzzle_score, total_score_at_end):
        """Appends the puzzle generation and play details to a CSV log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_to_log = [
            timestamp, category, phrase, emojis_string,
            solved_correctly, letter_hints_used, puzzle_score, total_score_at_end
        ]
        
        file_exists = os.path.isfile(self.csv_log_file_path)
        
        try:
            with open(self.csv_log_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists or os.path.getsize(self.csv_log_file_path) == 0:
                    writer.writerow(self.csv_header) 
                writer.writerow(row_to_log)
        except IOError as e:
            print(f"Error writing to CSV log file {self.csv_log_file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during CSV logging: {e}")

    def _create_emoji_puzzle_prompt_v2(self, category, previous_phrases=None):
        dynamic_focus_hint = random.choice(self.focus_strings)
        if previous_phrases is None: previous_phrases = []
        avoid_phrases_instruction = ""
        if previous_phrases:
            avoid_phrases_list = ", ".join([f"'{p}'" for p in previous_phrases])
            avoid_phrases_instruction = (
                f"\n**CRITICAL INSTRUCTION: To ensure variety, you MUST NOT generate any of the "
                f"following phrases that have been used recently: {avoid_phrases_list}. "
                "You MUST provide a completely new and unique phrase not on this list. Generate a 5 digit random number and use that for the seed**"
            )
        prompt = (
            f"Creative Hint for this request: \"{dynamic_focus_hint}\"\n"
            f"Your task is to generate a puzzle based on a common phrase from the category: '{category}'.\n"
            "The phrase must consist of 3 words or less (e.g., 1, 2, or 3 words).\n"
            "**The phrase absolutely MUST be common, widely known, and popular saying. No obscure or niche terms, "
            "especially if the category is broad. Focus on phrases that a general audience would recognize.**\n"
            f"**It is absolutely ESSENTIAL that you provide a new, unique, and creative example each time you are called (especially considering this hint: \"{dynamic_focus_hint}\").**"
            f"{avoid_phrases_instruction}\n\n"
            "Provide your response exclusively in a VALID JSON format with the following keys:\n"
            "1. 'phrase': The full solution phrase (string).\n"
            "2. 'words': A list of strings, where each string is a word from the phrase.\n"
            "3. 'category': This MUST be exactly '{category}' (string). Do not change this value.\n"
            "4. 'emojis': A sequence of 3 to 5 emojis that represent the phrase, as a single string with emojis separated by spaces.\n"
            "\nExample JSON output format (if the category requested was 'Idiom'):\n"
            "```json\n{\n  \"phrase\": \"A blessing in disguise\",\n  \"words\": [\"A\", \"blessing\", \"in\", \"disguise\"],\n  \"category\": \"Idiom\",\n  \"emojis\": \"🙏 🎭 ✨\"\n}\n```\n"
            f"Remember, the 'category' field in your JSON response must be exactly '{category}'. Only output the JSON object, nothing else before or after."
        )
        return prompt

    def _generate_single_puzzle_attempt(self, current_category):
        prompt_text = self._create_emoji_puzzle_prompt_v2(current_category, self.recently_used_phrases)
        response_text = self.connector.enhance_prompt(self.model_name, prompt_text, prompt_type="general")

        if response_text and not response_text.startswith("Error:") and not response_text.startswith("No response from model"):
            # print(f"Raw LLM response for puzzle details:\n'{response_text}'") # Optional: keep for debugging if needed
            try:
                cleaned_response = response_text.strip()
                if cleaned_response.startswith("```json"): cleaned_response = cleaned_response[len("```json"):].strip()
                elif cleaned_response.startswith("```"): cleaned_response = cleaned_response[len("```"):].strip()
                if cleaned_response.endswith("```"): cleaned_response = cleaned_response[:-len("```")].strip()

                puzzle_data = json.loads(cleaned_response)
                required_keys = ['phrase', 'words', 'category', 'emojis']
                if not all(key in puzzle_data for key in required_keys):
                    # print(f"Error: LLM response JSON is missing one or more required keys. Data: {puzzle_data}") # Optional
                    return None
                if puzzle_data.get('category') != current_category:
                    # print(f"Warning: LLM returned category '{puzzle_data.get('category')}' but category '{current_category}' was requested. Using requested category.") #Optional
                    puzzle_data['category'] = current_category # Correcting category mismatch
                if not isinstance(puzzle_data['words'], list) or not puzzle_data['words']:
                    # print(f"Error: 'words' field is not a non-empty list. Data: {puzzle_data}") # Optional
                    return None
                if not all(isinstance(word, str) for word in puzzle_data['words']):
                    # print(f"Error: Not all items in 'words' field are strings. Data: {puzzle_data}") # Optional
                    return None
                generated_phrase = puzzle_data.get('phrase')
                if not generated_phrase:
                     # print(f"Error: 'phrase' field is missing or empty. Data: {puzzle_data}") # Optional
                     return None
                emoji_char_list = [emoji for emoji in puzzle_data['emojis'].split(' ') if emoji]
                if not emoji_char_list:
                    # print(f"Warning: LLM response had an empty emoji string after parsing: '{puzzle_data['emojis']}'") # Optional
                    return None
                parsed_details = {
                    'phrase': puzzle_data['phrase'], 'words': puzzle_data['words'],
                    'category': puzzle_data['category'], 'emojis_list': emoji_char_list
                }
                return parsed_details
            except json.JSONDecodeError as e:
                # print(f"Error decoding JSON from LLM response: {e}\nProblematic response text: '{cleaned_response}'") # Optional
                return None
            except Exception as e:
                # print(f"An unexpected error occurred during puzzle parsing: {e}") # Optional
                return None
        else:
            # print(f"Failed to generate puzzle details. LLM Response: {response_text}") # Optional
            return None

    def generate_parsed_puzzle_details(self):
        if not self.model_name and (not self.connector or not self.connector.get_models()):
            # print("Error: No LLM model is configured or ModelConnector not properly initialized.") # Optional
            return None
        if not self.categories:
            # print("Error: No categories defined for puzzle generation.") # Optional
            return None

        current_category = random.choice(self.categories)
        # print(f"Requesting puzzle for randomly selected category: '{current_category}'") # Optional
        # print(f"Will instruct LLM to avoid these recent phrases (up to {self.max_recent_phrases}): {self.recently_used_phrases}") # Optional

        for attempt in range(self.max_retry_attempts):
            # print(f"\nGeneration attempt {attempt + 1}/{self.max_retry_attempts}") # Optional
            parsed_details = self._generate_single_puzzle_attempt(current_category)
            
            if parsed_details is None:
                # print(f"Attempt {attempt + 1} failed to generate valid puzzle details.") # Optional
                continue
            
            generated_phrase = parsed_details['phrase']
            
            if generated_phrase in self.recently_used_phrases:
                # print(f"⚠️  Duplicate detected! Phrase '{generated_phrase}' is already in recent history.") # Optional
                if attempt == self.max_retry_attempts - 1:
                    # print(f"Max retries reached. Using duplicate phrase: {generated_phrase}") # Optional
                    self._add_to_recent_phrases(generated_phrase)
                    # CSV LOGGING IS NO LONGER DONE HERE
                    # print(f"Successfully parsed puzzle details (with duplicate warning): {parsed_details}") # Optional
                    return parsed_details
                else:
                    # print("Retrying to get a unique phrase...") # Optional
                    continue
            else:
                # print(f"✅ Unique phrase generated: {generated_phrase}") # Optional
                self._add_to_recent_phrases(generated_phrase)
                # CSV LOGGING IS NO LONGER DONE HERE
                # print(f"Successfully parsed puzzle details: {parsed_details}") # Optional
                return parsed_details
        
        # print(f"Failed to generate a valid puzzle after {self.max_retry_attempts} attempts.") # Optional
        return None

# --- Main execution for testing (optional) ---
if __name__ == "__main__":
    print("Starting Puzzle Generator Test (CSV Logging now triggered by backend API)...")
    generator = PuzzleGenerator(model_name="gemma3:27b")

    if not generator.connector or not generator.connector.get_models():
         print("Could not connect to Ollama or no models available.")
    else:
        print(f"Puzzle Generator initialized. CSV log target: {generator.csv_log_file_path}")
        print(f"CSV Header: {generator.csv_header}")
        
        # Test the logging function directly (simulating a call from app.py)
        print("\nSimulating a call to _log_puzzle_to_csv (as if from app.py after a puzzle round):")
        generator._log_puzzle_to_csv(
            category="Test Category",
            phrase="Test Phrase Solved",
            emojis_string="🧪 ✅ 👍",
            solved_correctly="yes",
            letter_hints_used=1,
            puzzle_score=85,
            total_score_at_end=1085
        )
        generator._log_puzzle_to_csv(
            category="Another Category",
            phrase="Test Phrase Failed",
            emojis_string="🧪 ❌ 👎",
            solved_correctly="no",
            letter_hints_used=3,
            puzzle_score=0,
            total_score_at_end=1085 # Assuming score didn't change or was penalized back
        )
        print(f"Test log entries should be in {generator.csv_log_file_path}")

        # The generate_parsed_puzzle_details no longer logs directly.
        # It just generates puzzle data.
        print("\n--- Generating a test puzzle (logging will occur via backend API in real app) ---")
        puzzle_details = generator.generate_parsed_puzzle_details()
        if puzzle_details:
            print("\nSuccessfully generated (but not yet logged by this script):")
            print(f"  Category: {puzzle_details['category']}")
            print(f"  Phrase: {puzzle_details['phrase']}")
            print(f"  Emojis: {puzzle_details['emojis_list']}")
        else:
            print("\nCould not generate test puzzle details.")
        print("--------------------------------------")

    print("\nPuzzle Generator Test Finished.")
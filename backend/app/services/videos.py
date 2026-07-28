"""Daily-life step-by-step video library. © 2026 Lamya F. H. Ali"""

# Curated YouTube search queries — step-by-step life skills for autism/kids.
LIFE_SKILL_VIDEOS = {
 "wash_hands":{"title":"Washing Hands — Step by Step","q":"washing hands step by step song for kids"},
 "brush_teeth":{"title":"Brushing Teeth — Step by Step","q":"brushing teeth step by step kids tutorial"},
 "get_dressed":{"title":"Getting Dressed — Step by Step","q":"getting dressed step by step kids song"},
 "tie_shoes":{"title":"Tying Shoes — Step by Step","q":"how to tie shoes step by step for kids"},
 "use_toilet":{"title":"Using the Toilet — Step by Step","q":"potty training step by step for kids"},
 "eat_spoon":{"title":"Eating with a Spoon","q":"using a spoon step by step toddler"},
 "drink_cup":{"title":"Drinking from a Cup","q":"drinking from a cup step by step toddler"},
 "comb_hair":{"title":"Combing Hair","q":"combing hair step by step for kids"},
 "wash_face":{"title":"Washing Face","q":"washing face step by step for kids"},
 "clean_up":{"title":"Cleaning Up Toys","q":"clean up toys step by step song kids"},
 "put_on_shoes":{"title":"Putting on Shoes","q":"putting on shoes step by step kids"},
 "blow_nose":{"title":"Blowing Your Nose","q":"how to blow nose step by step kids"},
 "wash_hair":{"title":"Washing Hair","q":"washing hair step by step for kids"},
 "make_bed":{"title":"Making the Bed","q":"making the bed step by step for kids"},
 "set_table":{"title":"Setting the Table","q":"setting the table step by step kids"},
 "zip_jacket":{"title":"Zipping a Jacket","q":"how to zip a jacket step by step kids"},
 "button_shirt":{"title":"Buttoning a Shirt","q":"buttoning a shirt step by step kids"},
 "pack_bag":{"title":"Packing a School Bag","q":"packing school bag step by step kids"},
 "crossing_road":{"title":"Crossing the Road Safely","q":"crossing the road safely for kids"},
 "hand_washing_germs":{"title":"Why We Wash Hands","q":"germs and washing hands for kids"},
 "numbers_1_10":{"title":"Counting 1-10","q":"counting 1 to 10 for kids"},
 "abc_song":{"title":"ABC Letters","q":"abc phonics song for kids"},
 "colors":{"title":"Learning Colors","q":"learning colors for kids"},
 "shapes":{"title":"Learning Shapes","q":"learning shapes for kids"},
 "emotions":{"title":"Naming Feelings","q":"learning feelings and emotions for kids"},
}

def youtube_search_url(query: str) -> str:
    import urllib.parse
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)

def for_task(task_type: str, task_name: str = "") -> dict:
    key_map={"daily":"wash_hands","number":"numbers_1_10","letter":"abc_song",
    "word":"abc_song","drawing":"shapes","motor":"emotions"}
    k=key_map.get(task_type,"emotions")
    v=LIFE_SKILL_VIDEOS[k]
    return {"title":v["title"],"url":youtube_search_url(task_name or v["q"])}

def all_videos():
    return [{"key":k,"title":v["title"],"url":youtube_search_url(v["q"])}
            for k,v in LIFE_SKILL_VIDEOS.items()]

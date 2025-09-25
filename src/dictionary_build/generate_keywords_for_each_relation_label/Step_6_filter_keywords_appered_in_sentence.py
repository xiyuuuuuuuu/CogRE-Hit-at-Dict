import json


# replace relation_keywords_1 and relation_keywords_2 with your own keywords get from the previous steps
# TACRED
# relation_keywords_1 = {
#     "org:alternate_names": [
#         "organization", "organizational", "org", "association",  
#         "abbreviation", "alternate names", "other names", "aliases", "nicknames", "abbreviated"
#     ],
#     "org:city_of_headquarters": [
#         "organization", "organizational", "org","association",  
#         "headquarters", "based", "located", "city", "cities", "location", "city of headquarters","geographical"
#     ],
#     "org:dissolved": [
#         "organization", "organizational", "org", "association",  
#         "dissolved", "expired", "bankruptcy", "re-organized", "merged", "dissolution", "shutdown","closed", "shut"
#     ],
#     "org:members": [
#         "organization", "organizational", "org", "association",  "members",
#         "affiliated", "associated","represented", "participant", "affiliates", "participants","group members"
#     ],
#     "org:number_of_employees/members": [
#         "organization", "organizational", "org","association", "number","employees",
#         "members", "represents", "employment", "staff", "workers",
#         "employee", "count", "size", "team"
#     ],
#     "org:political/religious_affiliation": [
#         "organization", "organizational", "org", "association",  
#         "conservative","Christian","church","ideological","religious","affiliations","political","sectarian"
#     ],
#     "org:shareholders": [
#         "organization", "organizational", "org", "association",
#         "shareholders", "associated", "owns", "shares", "investor", "stakeholder", "ownership",
#         "owners", "investors", "stakeholders", "holders"
#     ],
#     "org:stateorprovince_of_headquarters": [
#         "organization", "organizational", "org", "association",  
#         "headquarters","located", "state", "province", "location", "based", "geographical",
#         "region"
#     ],
#     "org:subsidiaries": [
#         "organization", "organizational", "org", "association",  
#         "subsidiary", "division", "unit", "owned", "internal","committee", "structure",
#         "subsidiaries", "branches"
#     ],
#     "org:website": [
#         "organization", "organizational", "org", "association",  
#         "website", "web", "address", "URL"
#     ],
#     "per:cause_of_death": [
#         "person", "personal", "people", "individual", 
#         "succumbed", "died", "cancer", "death", "due", "dying", "caused", "diagnosed", "because", "health","issue"
#     ],
#     "per:charges": [
#         "person", "personal", "people", "individual", 
#         "accused", "suspicion", "crimes", "criminal", "accusations", "suspicions", "charge", "allegations", "committed", "involved", "assault", "violent", "commission"
#     ],
#     "per:cities_of_residence": [
#         "person", "personal", "people", "individual", 
#         "place", "origin", "residence", "city", "cities"
#     ],
#     "per:city_of_birth": [
#         "person", "personal", "people", "individual", 
#         "born", "birthplace", "city", "location", "place", "birth", "cities"
#     ],
#     "per:countries_of_residence": [
#         "person", "personal", "people", "individual", 
#          "country", "individuals", "citizens", "countries", "nationality", "citizenship"
#     ],
#     "per:country_of_birth": [
#         "person", "personal", "people", "individual", 
#         "born", "birthplace", "origin", "nationality", "country"
#     ],
#     "per:country_of_death": [
#         "person", "personal", "people", "individual", 
#         "death", "country", "passing", "nation", "place","died"
#     ],
#     "per:date_of_death": [
#         "person", "personal", "people", "individual", 
#         "died", "death", "date",
#         "found dead", "passed away", "death date", "day died", "time"
#     ],
#     "per:employee_of": [
#         "person", "personal", "people", "individual", 
#         "employee", "works", "heads", "director", "chairman", "chief", "leadership","role",
#         "employer", "workplace"
#     ],
#     "per:other_family": [
#         "person", "personal", "people", "individual", 
#         "other family", "member",
#         "relative", "extended family","same person","referred","refer","pronouns"
#     ],
#     "per:parents": [
#         "person", "personal", "people", "individual", 
#         "son", "child", "father", "daughter", "parent-child", "parent", "mother", "mother-child", "offspring", "familial", "bond", "motherhood",
#     ],
#     "per:religion": [
#         "person", "personal", "people", "individual", 
#         "religion", "jewish",
#         "ethnic", "heritage", "faith","spirituality"
#     ],
#     "per:spouse": [
#         "person", "personal", "people", "individual", 
#         "spouse", "married", "wife",
#         "husband", "divorce", "marriage", "partner", "divorce", "marital"
#     ],
#     "per:stateorprovince_of_birth": [
#         "person", "personal", "people", "individual", 
#         "born", "birthplace", "state",
#         "province", "place", "birth", "origin", "state", "province",
#     ],
#     "per:title": [
#         "person", "personal", "people", "individual", 
#         "title", "position", "role",
#         "leadership", "job", "political title"
#     ],
#     "no_relation": [
#         "no relation", "irrelevant", "unrelated", "no connection", "not related", "no association"
#     ]
# }

# # NYT29
# relation_keywords_2 = {
#     "/location/country/capital": [
#         "country",
#         "city",       # Case 1: Beijing – China; Tehran – Iran; Case 2: Kigali – Rwanda
#         "capital",    # Case 2: Moscow – Soviet Union; Case 4: Jakarta – Indonesia
#         "location",   # Case 3: Belfast – Northern Ireland (peace accord context)
#         "government", # Case 3: Beijing – China (government negotiations)
#         "city",       # Case 4: Baghdad – Iraq
#         "government", # Case 5: Pyongyang – North Korea; Tehran – Iran
#     ],
#     "/location/location/contains": [
#         "city",        # Case 1: Houston – Texas; Turin – Italy; Case 3: North Olmsted – Ohio; Shandaken – Ulster County; Case 4: Boise – Idaho
#         "location",    # Case 2: New Rochelle – New York; Ballybunion – Ireland
#         "provincial",  # Case 4: Changchun – China
#         "capital",     # Case 4: Changchun – China
#         "located",     # Case 5: Rotterdam – Netherlands; Mankato – Minnesota
#         "contains"
#     ],
#     "/location/us_state/capital": [
#         "location",
#         "us",
#         "state",
#         "city",     # Case 1: Columbus–Ohio, Austin–Texas # Case 2: Phoenix–Arizona, Columbus–Ohio. # Case 3: Austin–Texas # Case 4: Columbus–Ohio, Trenton–New Jersey # Case 5: Columbus–Ohio
#         "part",     # Case 3: Albany–New York
#         "located",  # Case 5: Columbus Colony–Ohio
#         "capital"
#     ],
#     "/business/company/place_founded": [
#         "business",
#         "company",
#         "based",        # Case 1: Piper Jaffray – Minneapolis; Case 2: Viz Media – San Francisco; Case 3: Capital Economics – London; Case 3: Vonage – Edison; Case 4: Electronic Arts – Redwood City
#         "located",      # Case 1: Planet Hollywood – New York; Case 2: Kimberly-Clark – Neenah
#         "headquarters", # Case 4: Boeing – Seattle
#         "offices",      # Case 5: General Mills – Minneapolis
#         "building",     # Case 5: Herbalife – Los Angeles
#         "logo",         # Case 5: Herbalife – Los Angeles
#         "place",
#         "founded",
#         "found"
#     ],
#     "/film/film_location/featured_in_films": [
#         "film",
#         "location",
#         "setting",       # Case 1: Brooklyn – half Nelson; Case 1: Los Angeles – L.A. Confidential
#         "set",           # Case 1: Los Angeles – L.A. Confidential; Case 3: L.A. Confidential – Los Angeles; Case 3: Vera Drake – London
#         "takes place",   # Case 3: Vera Drake – London
#         "associated",    # Case 4: half Nelson – Brooklyn; Case 4: Rocky – Philadelphia
#         "featured",
#         "films"
#     ],
#     "/business/company/founders": [
#         "business",
#         "company",
#         "chairman",      # Case 1: Bill Gates – Microsoft; Case 5: Bill Gates – Microsoft
#         "founder",       # Case 2: Martha Stewart – Martha Stewart Living Omnimedia; Case 4: Tim O’Reilly – O’Reilly Media # Case 2: David Geffen – Dreamworks # Case 3: David Geffen – Dreamworks SKG
#         "associated",    # Case 3: Stephen A. Schwarzman – Blackstone Group; Case 3: Bill Gates – Microsoft
#         "chief",         # Case 4: Michael Strickman – Choicestream
#         "ficer",         # Case 4: Michael Strickman – Choicestream
#         "executive",     # Case 4: Tim O’Reilly – O’Reilly Media # Case 5: Bill Gates – Microsoft
#         "co-founder",    # Case 5: Tom Anderson – Myspace
#         "president",     # Case 5: Tom Anderson – Myspace
#         "founders"
#     ],
#     "/people/person/nationality": [
#         "people",
#         "person",
#         "president",         # Hu Jintao – China; Susilo Bambang Yudhoyono – Indonesia; Pervez Musharraf – Pakistan
#         "minister",          # Ehud Olmert – Israel
#         "prime minister",    # Manmohan Singh – India; Ariel Sharon – Israel; Shaukat Aziz – Pakistan
#         "foreign minister",  # Hoshyar Zebari – Iraq
#         "chancellor",        # Angela Merkel – Germany
#         "nationality"
#     ],
#     "/business/person/company": [
#         "business",
#         "person",
#         "secretary",     # Case 1: Kofi Annan – United Nations
#         "president",     # Case 1: Luis Echeverría – Mexico
#         "program",       # Case 2: Bill Gates – Microsoft; Case 2: Steve Jobs – Apple
#         "executive",     # Case 2: Jeff Zucker – NBC
#         "chief",         # Case 3: Dmitry Shapiro – Veoh; Case 3: Scott McNealy – Sun Microsystems
#         "leader",        # Case 4: Rupert Murdoch – News Corporation (general leadership role)
#         "chairman",      # Case 4: Rupert Murdoch – News Corporation (specific role)
#         "ficer",         # Case 5: Jeffrey Bewkes – Time Warner
#         "correspondent", # Case 5: Christiane Amanpour – CNN
#         "company"
#     ],
#     "/location/us_county/county_seat": [
#         "location",
#         "us",
#         "county",
#         "municipality",  # Case 1: Jersey City – Hudson County
#         "included",      # Case 1: Phoenix – Maricopa County
#         "area",          # Case 2: Maricopa County – Phoenix
#         "around",        # Case 2: Maricopa County – Phoenix
#         "in",            # Case 2: Jersey City – Hudson County; Case 3: Jersey City – Hudson County; Case 3: San Rafael – Marin County
#         "part",          # Case 4: Marietta – Cobb County; Case 4: Phoenix – Maricopa County; Case 5: Phoenix – Maricopa County; Case 5: Austin – Travis County
#         "seat"
#     ],
#     "/people/person/place_lived": [
#         "people",
#         "person",
#         "lives",       # Case 1: Alex Rodriguez – Miami
#         "hometown",    # Case 1: Kyle Harrison – Baltimore
#         "from",        # Case 2: Jim Gerlach – Pennsylvania; Case 2: John McCain – Arizona; Case 5: Mitch McConnell – Kentucky; Case 5: Jeff Flake – Arizona
#         "resides",     # Case 3: Pervez Musharraf – Pakistan
#         "at",          # Case 3: Pervez Hoodbhoy – Pakistan
#         "governor",    # Case 4: Arnold Schwarzenegger – California
#         "place",
#         "lived"
#     ],
#     "/people/person/children": [
#         "people",
#         "person",
#         "mother",   # Case 1: Rosa Bossi – Silvio Berlusconi; Case 1: Tina Knowles – Beyoncé
#         "son",      # Case 2: Sean Lennon – John Lennon; Case 2: Dweezil Zappa – Frank Zappa
#         "father",   # Case 3: Tom Harmon – Kelly Harmon; Case 3: Irving Kristol – William Kristol; Case 5: Tito Horford – Al Horford; Case 5: Malcolm Campbell – Donald Campbell
#         "daughter", # Case 4: Elizabeth Cheney – Dick Cheney
#         "niece",    # Case 4: Natasha Richardson – Vanessa Redgrave
#         "child",    # Case 1: Rosa Bossi – Silvio Berlusconi; Case 1: Tina Knowles – Beyoncé; Case 2: Sean Lennon – John Lennon; Case 2: Dweezil Zappa – Frank Zappa; Case 3: Tom Harmon – Kelly Harmon; Case 3: Irving Kristol – William Kristol; Case 5: Tito Horford – Al Horford; Case 5: Malcolm Campbell – Donald Campbell
#         "relative", # Case 4: Natasha Richardson – Vanessa Redgrave
#         "children"
#     ],
#     "/people/ethnicity/geographic_distribution": [
#         "people",
#         "ethnicity",
#         "energy",         # Case 1: Russian – Russia (energy policies); Russian – Ukraine (gas price/loan)
#         "gas",            # Case 1: Russian – Ukraine (gas price increase)
#         "loan",           # Case 1: Russian – Ukraine (loan offer)
#         "reporter",       # Case 2: Russian reporter – Russia (nationality)
#         "foreign",        # Case 2: Russian Foreign Minister – Russia (nationality/diplomatic context)
#         "national",       # Case 3: Russian billionaire/oligarch – Russia; Russian bank regulator – Russia
#         "associated",     # Case 5: Russian groups – Russia; Russian motives – Russia
#         "pipelines",      # Case 4: Russian Gazprom – Ukraine (proposal for consortium)
#         "geographic",
#         "distribution"
#     ],
#     "/people/person/ethnicity": [
#         "people",
#         "person",
#         "american",   # Case 1: John McCain – American # Case 2 & 3: John McCain – American (treatment prisoners/detainees custody)
#         "italianmer", # Case 1: Romano Prodi – Italian
#         "manchu",     # Case 4 & 5: Nurhaci – Manchu
#         "russian",    # Case 4: Vladimir Putin – Russian
#         "tejano",     # Case 5: Selena – Tejano
#         "ethnicity"
#     ],
#     "/people/deceased_person/place_of_burial": [
#         "people",
#         "deceased",
#         "person",
#         "home",    # Case 1: Franklin D. Roosevelt – Hyde Park; Case 2: Franklin D. Roosevelt – Hyde Park; Case 4: Franklin D. Roosevelt – Hyde Park
#         "sites",   # Case 2: Franklin D. Roosevelt – Hyde Park
#         "buried",  # Case 3: Joseph Pulitzer – Woodlawn Cemetery; Case 3: Georges Méliès – Père Lachaise Cemetery
#         "grave",   # Case 3: Georges Méliès – Père Lachaise Cemetery (headstone reference)
#         "interred",# Case 3: Joseph Pulitzer – Woodlawn Cemetery (general burial phrasing)
#         "place",
#         "burial"
#     ],
#     "/people/place_of_interment/interred_here": [
#         "people",
#         "place",
#         "interment",
#         "home",        # Case 1: Franklin D. Roosevelt – Hyde Park; Case 4: Franklin D. Roosevelt – Hyde Park; Case 5: Franklin D. Roosevelt – Hyde Park
#         "played",      # Case 1: Franklin D. Roosevelt – Hyde Park (games)
#         "tomb",        # Case 2: Isaac Newton – Westminster Abbey
#         "buried",      # Case 2: Charles Darwin – Westminster Abbey
#         "sites",       # Case 3: Franklin D. Roosevelt – Hyde Park
#         "staging",     # Case 3: Richard Wagner – Bayreuth
#         "rites",       # Case 4: Franklin D. Roosevelt – Hyde Park (family home rites)
#         "birthplace",  # Case 5: Franklin D. Roosevelt – Hyde Park
#         "resided",     # Case 5: Franklin D. Roosevelt – Hyde Park
#         "interred",
#         "here"
#     ],
# }

def read_data(path):
    """
    Read the data from the jsonl file.
    """
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            example = json.loads(line)
            data.append(example)
    return data

def write_to_jsonl(data, path):
    """
    Write the data to the jsonl file.
    """
    with open(path, "w", encoding="utf-8") as f:
        for example in data:
            json.dump(example, f, ensure_ascii=False)
            f.write("\n")

def main():
    input_file = input("Please enter the path to the input JSONL file: ").strip()
    relation_with_cases = read_data(input_file)
    relation_keywords = {}
    for key in relation_keywords_2:
        keywords_1 = relation_keywords_2[key]
        keywords_2 = relation_keywords_2.get(key, [])
        combined_keywords = list(set(keywords_1 + keywords_2))
        relation_keywords[key] = combined_keywords
    
    for item in relation_with_cases:
        label = item['relation']
        cases = item['cases']
        # Use the first 5 examples; if fewer than 5 are available, use all cases
        use_cases = cases[:5] if len(cases) >= 5 else cases
        # For the given label, retrieve all keywords from relation_keywords
        keywords = relation_keywords.get(label, [])
        # Check if each keyword appears in any paraphrased_sentence or test_sentence of the use_cases
        filtered_keywords = []
        for keyword in keywords:
            for c in use_cases:
                if (keyword in c.get('paraphrased_sentence', '') or keyword in c.get('test_sentence', '')):
                    filtered_keywords.append(keyword)
                    break
        # print the filtered keywords
        print(f"Relation: {label}, Filtered Keywords: {filtered_keywords}")

if __name__ == "__main__":
    main()

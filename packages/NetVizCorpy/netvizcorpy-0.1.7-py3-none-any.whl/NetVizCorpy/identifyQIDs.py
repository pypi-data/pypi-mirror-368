import requests
import random


class Searcher:
    def __init__(self, company, option):
        self.company = company.strip() # remove any space at the beginning/end of the string
        self.option = option

    def searchCompanyByName(self):
        # Defining a list of user agents to alternate
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"
        ]
        query = ''
        if self.option == 'all':
            # Constructing the SPARQL query
            query = f""" SELECT distinct ?item ?QID ?itemLabel ?itemDescription
            WHERE{{
                ?item rdfs:label ?itemLabel.
                FILTER(REGEX(?itemLabel, ?name, "i" )).
                VALUES ?name {{"^{self.company}$"@en "^{self.company} "@en "^{self.company}, "@en}} .
                FILTER(LANG(?itemLabel)="en").
                ?item wdt:P31 ?type .
                VALUES ?type {{wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q167037 wd:Q21980538 wd:Q891723 wd:Q786820 wd:Q43229 wd:Q1058914
                                wd:Q18388277 wd:Q161726 wd:Q778575 wd:Q2005696 wd:Q108460239 wd:Q3477381 wd:Q270791 wd:Q936518
                                wd:Q1934969 wd:Q2538889 wd:Q2995256 wd:Q1631129 wd:Q1276157 wd:Q5038204 wd:Q217107 wd:Q13235160
                                wd:Q17377208 wd:Q740752 wd:Q249556}} . #to search multiple entities

                ?article schema:about ?item .
                ?article schema:inLanguage "en" .
                ?article schema:isPartOf <https://en.wikipedia.org/>.
            #the next 3 lines will give the QID in the column QID
            #This query will bind the substring of ?uri starting from the 32nd character to a new variable ?code
            BIND (STR (?item) AS ?uri) .
            FILTER (STRSTARTS (?uri, "http://www.wikidata.org/entity/Q")) .
            BIND (SUBSTR (?uri, 32) AS ?QID) .

            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            """
        elif self.option == 'exact':
            query = f""" SELECT distinct ?item ?QID ?itemLabel ?itemDescription
             WHERE{{
               ?item rdfs:label ?itemLabel.
               FILTER(REGEX(?itemLabel, ?name )).
               VALUES ?name {{"^{self.company}$"@en}} .
               FILTER(LANG(?itemLabel)="en").
               ?item wdt:P31 ?type .
               VALUES ?type {{wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q167037 wd:Q21980538 wd:Q891723 wd:Q786820 wd:Q43229 wd:Q1058914
                                     wd:Q18388277 wd:Q161726 wd:Q778575 wd:Q2005696 wd:Q108460239 wd:Q3477381 wd:Q270791 wd:Q936518
                                     wd:Q1934969 wd:Q2538889 wd:Q2995256 wd:Q1631129 wd:Q1276157 wd:Q5038204 wd:Q217107 wd:Q13235160
                                     wd:Q17377208 wd:Q740752 wd:Q249556}} . #to search multiple entities

               ?article schema:about ?item .
               ?article schema:inLanguage "en" .
               ?article schema:isPartOf <https://en.wikipedia.org/>.
             #the next 3 lines will give the QID in the column QID
             #This query will bind the substring of ?uri starting from the 32nd character to a new variable ?code
             BIND (STR (?item) AS ?uri) .
             FILTER (STRSTARTS (?uri, "http://www.wikidata.org/entity/Q")) .
             BIND (SUBSTR (?uri, 32) AS ?QID) .

             SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
             }}
             """
        elif self.option == 'space':
            # Constructing the SPARQL query
            query = f""" SELECT distinct ?item ?QID ?itemLabel ?itemDescription
            WHERE{{
              ?item rdfs:label ?itemLabel.
              FILTER(REGEX(?itemLabel, ?name )).
              VALUES ?name {{"^{self.company} "@en}} .
              FILTER(LANG(?itemLabel)="en").
              ?item wdt:P31 ?type .
              VALUES ?type {{wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q167037 wd:Q21980538 wd:Q891723 wd:Q786820 wd:Q43229 wd:Q1058914
                                    wd:Q18388277 wd:Q161726 wd:Q778575 wd:Q2005696 wd:Q108460239 wd:Q3477381 wd:Q270791 wd:Q936518
                                    wd:Q1934969 wd:Q2538889 wd:Q2995256 wd:Q1631129 wd:Q1276157 wd:Q5038204 wd:Q217107 wd:Q13235160
                                    wd:Q17377208 wd:Q740752 wd:Q249556}} . #to search multiple entities

              ?article schema:about ?item .
              ?article schema:inLanguage "en" .
              ?article schema:isPartOf <https://en.wikipedia.org/>.
            #the next 3 lines will give the QID in the column QID
            #This query will bind the substring of ?uri starting from the 32nd character to a new variable ?code
            BIND (STR (?item) AS ?uri) .
            FILTER (STRSTARTS (?uri, "http://www.wikidata.org/entity/Q")) .
            BIND (SUBSTR (?uri, 32) AS ?QID) .

            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            """
        elif self.option == 'space_comma':
            # Constructing the SPARQL query
            query = f""" SELECT distinct ?item ?QID ?itemLabel ?itemDescription
            WHERE{{
              ?item rdfs:label ?itemLabel.
              FILTER(REGEX(?itemLabel, ?name )).
              VALUES ?name {{"^{self.company}, "@en}} .
              FILTER(LANG(?itemLabel)="en").
              ?item wdt:P31 ?type .
              VALUES ?type {{wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q167037 wd:Q21980538 wd:Q891723 wd:Q786820 wd:Q43229 wd:Q1058914
                                    wd:Q18388277 wd:Q161726 wd:Q778575 wd:Q2005696 wd:Q108460239 wd:Q3477381 wd:Q270791 wd:Q936518
                                    wd:Q1934969 wd:Q2538889 wd:Q2995256 wd:Q1631129 wd:Q1276157 wd:Q5038204 wd:Q217107 wd:Q13235160
                                    wd:Q17377208 wd:Q740752 wd:Q249556}} . #to search multiple entities

              ?article schema:about ?item .
              ?article schema:inLanguage "en" .
              ?article schema:isPartOf <https://en.wikipedia.org/>.
            #the next 3 lines will give the QID in the column QID
            #This query will bind the substring of ?uri starting from the 32nd character to a new variable ?code
            BIND (STR (?item) AS ?uri) .
            FILTER (STRSTARTS (?uri, "http://www.wikidata.org/entity/Q")) .
            BIND (SUBSTR (?uri, 32) AS ?QID) .

            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            """

        # Choosing a random user agent from the list
        user_agent = random.choice(user_agents)
        # Sending the request to the Wikidata endpoint with the user agent header
        response = requests.get("https://query.wikidata.org/sparql", params={"query": query, "format": "json"},
                                headers={"User-Agent": user_agent})
        if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
            try:
                # Parsing the response as JSON
                data = response.json()
                output = data["results"]["bindings"]
                return output
            except ValueError:
                return []
        else:
            return []

    # Defining a function that takes an input from user and returns the Wikidata ID and label
    def choose_company(self):

        # Initializing an empty list to store the IDs and labels
        ids_and_labels = []
        # Make the query
        results = self.searchCompanyByName()
        if len(results) != 0:
            # Looping through the results and appending them to the list
            for result in results:
                # Getting the Wikidata ID and label
                wikidata_id = result["item"]["value"].split("/")[-1]
                wikidata_label = result["itemLabel"]["value"]
                # Appending a tuple of ID and label to the list
                ids_and_labels.append((wikidata_id, wikidata_label))
        return ids_and_labels

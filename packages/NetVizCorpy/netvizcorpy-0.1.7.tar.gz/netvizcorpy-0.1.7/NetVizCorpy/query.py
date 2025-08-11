import random
import requests


class Querier:
    def __init__(self, qid, index):
        self.qid = qid
        self.index = index
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"]
        self.query_has_parent = f""" SELECT ?parent (IF (BOUND(?parent), COUNT(DISTINCT ?parent), 0) AS ?count)
                                          WHERE {{
                                                VALUES ?item {{wd:{qid}}}.
                                                ?item wdt:P31 ?type .
                                                VALUES ?type {{wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q167037 wd:Q21980538 wd:Q891723 wd:Q786820 wd:Q43229 wd:Q1058914
                                                            wd:Q18388277 wd:Q161726 wd:Q778575 wd:Q2005696 wd:Q108460239 wd:Q3477381 wd:Q270791 wd:Q936518
                                                            wd:Q1934969 wd:Q2538889 wd:Q2995256 wd:Q1631129 wd:Q1276157 wd:Q5038204 wd:Q217107 wd:Q13235160
                                                            wd:Q17377208 wd:Q740752 wd:Q249556}} . #to search multiple entities
                                                #?article schema:about ?item .
                                                #?article schema:inLanguage "en" .
                                                #?article schema:isPartOf <https://en.wikipedia.org/>.

                                                OPTIONAL {{ ?item wdt:P749 ?parent. }}

                                                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                                }}
                                                GROUP BY ?parent
                                          """

        self.query_get_parent_info = f"""
                                    SELECT DISTINCT ?item
                                                    (REPLACE(STR(?item), "http://www.wikidata.org/entity/", "") AS ?QID)
                                                    ?itemLabel
                                                    ?itemcountryLabel
                                                    (GROUP_CONCAT ( DISTINCT ?industryLabel; separator="; ") AS ?industries)
                                                    ?revenue
                                                    ?revenueDate
                                                    ?parent
                                                    (REPLACE(STR(?parent), "http://www.wikidata.org/entity/", "") AS ?pQID)
                                                    ?parentLabel
                                                    ?parentcountryLabel
                                                    (GROUP_CONCAT ( DISTINCT ?pindustryLabel; separator="; ") AS ?pindustries)
                                                    ?prevenue
                                                    ?prevenueDate
                                                    ?proportion
                                                    ?proportionofLabel
                                                    ?pointoftime
                                                    ?starttime
                                                    ?endtime
                                    WHERE {{
                                              VALUES ?item {{wd:{qid}}}.
                                              #?item wdt:P31 ?type .
                                              #?article schema:about ?item .
                                              #?article schema:inLanguage "en" .
                                              #?article schema:isPartOf <https://en.wikipedia.org/>.

                                                OPTIONAL {{ ?item rdfs:label ?itemLabel. FILTER(LANG(?itemLabel) = "en") }}
                                                OPTIONAL {{ ?item     wdt:P17    ?itemcountry .
                                                            ?itemcountry  rdfs:label  ?itemcountryLabel
                                                            FILTER ( LANGMATCHES ( LANG ( ?itemcountryLabel ), "en" ) )
                                                          }}
                                                OPTIONAL {{ ?item     wdt:P452    ?industry .
                                                            ?industry  rdfs:label  ?industryLabel
                                                            FILTER ( LANGMATCHES ( LANG ( ?industryLabel ), "en" ) )
                                                          }}
                                                OPTIONAL {{ ?item     wdt:P2139     ?revenue. }}
                                                OPTIONAL {{ ?item p:P2139 [ps:P2139 ?revenue;  pq:P585  ?revenueDate] }}
                                                OPTIONAL {{ ?item wdt:P749 ?parent. }}
                                                OPTIONAL {{ ?parent     wdt:P452    ?pindustry .
                                                            ?pindustry  rdfs:label  ?pindustryLabel
                                                            FILTER ( LANGMATCHES ( LANG ( ?pindustryLabel ), "en" ) )
                                                          }}
                                                OPTIONAL {{ ?parent     wdt:P17    ?parentcountry .
                                                            ?parentcountry  rdfs:label  ?parentcountryLabel
                                                            FILTER ( LANGMATCHES ( LANG ( ?parentcountryLabel ), "en" ) )
                                                          }}
                                                OPTIONAL {{ ?parent     wdt:P2139     ?prevenue. }}
                                                OPTIONAL {{ ?parent  p:P2139 [ps:P2139 ?prevenue; pq:P585  ?prevenueDate] }}
                                                OPTIONAL {{ ?item  p:P749 [ps:P749 ?parent; pq:P1107 ?proportion] }}
                                                OPTIONAL {{
                                                          ?item  p:P749 [ps:P749 ?parent; pq:P642 ?proportionof] .
                                                          FILTER(?proportionof = wd:Q144368)
                                                         }}
                                                OPTIONAL {{ ?item p:P749 [ps:P749 ?parent; pq:P585 ?pointoftime] }}
                                                OPTIONAL {{?item p:P749 [ps:P749 ?parent; pq:P1107 ?proportion; pq:P585 ?pointoftime].
                                                          FILTER(NOT EXISTS {{?item p:P749 [ps:P749 ?parent; pq:P585 ?earlierTime; ?earlierTime [wdt:P585 ?pointoftime]]}})
                                                          }}
                                                #OPTIONAL {{
                                                #          ?item p:P749 [ps:P749 ?parent; pq:P585 ?pointoftime] .
                                                #          FILTER(BOUND(?pointoftime) && DATATYPE(?pointoftime) = xsd:dateTime).
                                                #          # get the latest record first
                                                #         BIND(NOW() - ?pointoftime AS ?distance).
                                                #          FILTER (MIN (?distance)) .
                                                #         }}
                                                OPTIONAL {{ ?item  p:P749 [ps:P749 ?parent; pq:P580 ?starttime] }}
                                                OPTIONAL {{ ?item  p:P749 [ps:P749 ?parent; pq:P582 ?endtime] }}
                                              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                    }}
                                    GROUP BY  ?item ?QID ?itemLabel ?itemcountryLabel ?revenue ?revenueDate ?parent ?pQID ?parentLabel ?parentcountryLabel ?prevenue ?prevenueDate ?proportion ?proportionofLabel ?pointoftime ?starttime ?endtime
                                    ORDER BY ?parentLabel
                                    LIMIT 10000
                                    """

        self.query_has_owned_by = f""" SELECT ?ownedby (IF (BOUND(?ownedby), COUNT(DISTINCT ?ownedby), 0) AS ?count)
                                    WHERE {{
                                            VALUES ?item {{wd:{qid}}}.
                                            ?item wdt:P31 ?type .
                                            VALUES ?type {{wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q167037 wd:Q21980538 wd:Q891723 wd:Q786820 wd:Q43229 wd:Q1058914
                                                            wd:Q18388277 wd:Q161726 wd:Q778575 wd:Q2005696 wd:Q108460239 wd:Q3477381 wd:Q270791 wd:Q936518
                                                            wd:Q1934969 wd:Q2538889 wd:Q2995256 wd:Q1631129 wd:Q1276157 wd:Q5038204 wd:Q217107 wd:Q13235160
                                                            wd:Q17377208 wd:Q740752 wd:Q249556}} . #to search multiple entities
                                            #?article schema:about ?item .
                                            #?article schema:inLanguage "en" .
                                            #?article schema:isPartOf <https://en.wikipedia.org/>.

                                            OPTIONAL {{ ?item wdt:P127 ?ownedby. }}

                                            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                            }}
                                            GROUP BY ?ownedby
                                    """

        self.query_get_owned_by_info = f"""
                                SELECT DISTINCT ?item
                                                (REPLACE(STR(?item), "http://www.wikidata.org/entity/", "") AS ?QID)
                                                ?itemLabel
                                                ?itemcountryLabel
                                                (GROUP_CONCAT ( DISTINCT ?industryLabel; separator="; ") AS ?industries)
                                                ?revenue
                                                ?revenueDate
                                                ?ownedby
                                                (REPLACE(STR(?ownedby), "http://www.wikidata.org/entity/", "") AS ?obQID)
                                                ?ownedbyLabel
                                                ?ownedbycountryLabel
                                                (GROUP_CONCAT ( DISTINCT ?obindustryLabel; separator="; ") AS ?obindustries)
                                                ?obrevenue
                                                ?obrevenueDate
                                                ?proportion
                                                ?proportionofLabel
                                                ?pointoftime
                                                ?starttime
                                                ?endtime
                                WHERE {{
                                  VALUES ?item {{wd:{qid}}}.
                                  #?item wdt:P31 ?type .
                                  ?article schema:about ?item .
                                  ?article schema:inLanguage "en" .
                                  ?article schema:isPartOf <https://en.wikipedia.org/>.

                                    OPTIONAL {{ ?item rdfs:label ?itemLabel. FILTER(LANG(?itemLabel) = "en") }}
                                    OPTIONAL {{ ?item     wdt:P17    ?itemcountry .
                                                ?itemcountry  rdfs:label  ?itemcountryLabel
                                                FILTER ( LANGMATCHES ( LANG ( ?itemcountryLabel ), "en" ) )
                                              }}
                                    OPTIONAL {{ ?item     wdt:P452    ?industry .
                                                ?industry  rdfs:label  ?industryLabel
                                                FILTER ( LANGMATCHES ( LANG ( ?industryLabel ), "en" ) )
                                              }}
                                    OPTIONAL {{ ?item     wdt:P2139     ?revenue. }}
                                    OPTIONAL {{ ?item p:P2139 [ps:P2139 ?revenue;  pq:P585  ?revenueDate] }}
                                    OPTIONAL {{ ?item wdt:P127 ?ownedby. }}
                                    OPTIONAL {{ ?ownedby     wdt:P452    ?obindustry .
                                                ?obindustry  rdfs:label  ?obindustryLabel
                                                FILTER ( LANGMATCHES ( LANG ( ?obindustryLabel ), "en" ) )
                                              }}
                                    OPTIONAL {{ ?ownedby     wdt:P17    ?ownedbycountry .
                                                ?ownedbycountry  rdfs:label  ?ownedbycountryLabel
                                                FILTER ( LANGMATCHES ( LANG ( ?ownedbycountryLabel ), "en" ) )
                                              }}
                                    OPTIONAL {{ ?ownedby     wdt:P2139     ?obrevenue. }}
                                    OPTIONAL {{ ?ownedby p:P2139 [ps:P2139 ?obrevenue;  pq:P585  ?obrevenueDate] }}
                                    OPTIONAL {{ ?item  p:P127 [ps:P127 ?ownedby; pq:P1107 ?proportion] }}
                                    OPTIONAL {{
                                              ?item  p:P127 [ps:P127 ?ownedby; pq:P642 ?proportionof] .
                                              FILTER(?proportionof = wd:Q144368)
                                             }}
                                    OPTIONAL {{ ?item p:P127 [ps:P127 ?ownedby; pq:P585 ?pointoftime] }}
                                    OPTIONAL {{?item p:P127 [ps:P127 ?ownedby; pq:P1107 ?proportion; pq:P585 ?pointoftime].
                                                  FILTER(NOT EXISTS {{?item p:P127 [ps:P127 ?ownedby; pq:P585 ?earlierTime; ?earlierTime [wdt:P585 ?pointoftime]]}})
                                                  }}
                                    #OPTIONAL {{
                                    #          ?item p:P127 [ps:P127 ?ownedby; pq:P585 ?pointoftime] .
                                    #          FILTER(BOUND(?pointoftime) && DATATYPE(?pointoftime) = xsd:dateTime).
                                    #          # get the latest record first
                                    #          BIND(NOW() - ?pointoftime AS ?distance).
                                    #          FILTER (MIN (?distance)) .
                                    #         }}
                                    OPTIONAL {{ ?item  p:P127 [ps:P127 ?ownedby; pq:P580 ?starttime] }}
                                    OPTIONAL {{ ?item  p:P127 [ps:P127 ?ownedby; pq:P582 ?endtime] }}
                                  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                }}
                                GROUP BY  ?item ?QID ?itemLabel ?itemcountryLabel ?revenue ?revenueDate ?ownedby ?obQID ?ownedbyLabel ?ownedbycountryLabel ?obrevenue ?obrevenueDate ?proportion ?proportionofLabel ?pointoftime ?starttime ?endtime
                                ORDER BY ?ownedbyLabel
                                LIMIT 10000
                                """

        self.query_has_subsidiary = f""" SELECT ?subsidiary (IF (BOUND(?subsidiary), COUNT(DISTINCT ?subsidiary), 0) AS ?count)
                                      WHERE {{
                                            VALUES ?item {{wd:{qid}}}.
                                            ?item wdt:P31 ?type .
                                            VALUES ?type {{wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q167037 wd:Q21980538 wd:Q891723 wd:Q786820 wd:Q43229 wd:Q1058914
                                                        wd:Q18388277 wd:Q161726 wd:Q778575 wd:Q2005696 wd:Q108460239 wd:Q3477381 wd:Q270791 wd:Q936518
                                                        wd:Q1934969 wd:Q2538889 wd:Q2995256 wd:Q1631129 wd:Q1276157 wd:Q5038204 wd:Q217107 wd:Q13235160
                                                        wd:Q17377208 wd:Q740752 wd:Q249556}} . #to search multiple entities
                                            #?article schema:about ?item .
                                            #?article schema:inLanguage "en" .
                                            #?article schema:isPartOf <https://en.wikipedia.org/>.

                                            OPTIONAL {{ ?item wdt:P355 ?subsidiary. }}

                                            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                            }}
                                            GROUP BY ?subsidiary
                                      """

        self.query_get_subsidiary_info = f"""
                                    SELECT DISTINCT ?item
                                                    (REPLACE(STR(?item), "http://www.wikidata.org/entity/", "") AS ?QID)
                                                    ?itemLabel
                                                    ?itemcountryLabel
                                                    (GROUP_CONCAT ( DISTINCT ?industryLabel; separator="; ") AS ?industries)
                                                    ?revenue
                                                    ?revenueDate
                                                    ?subsidiary
                                                    (REPLACE(STR(?subsidiary), "http://www.wikidata.org/entity/", "") AS ?sQID)
                                                    ?subsidiaryLabel
                                                    ?subsidiarycountryLabel
                                                    (GROUP_CONCAT ( DISTINCT ?sindustryLabel; separator="; ") AS ?sindustries)
                                                    ?srevenue
                                                    ?srevenueDate
                                                    ?proportion
                                                    ?proportionofLabel
                                                    ?pointoftime
                                                    ?starttime
                                                    ?endtime
                                    WHERE {{
                                      VALUES ?item {{wd:{qid}}}.
                                      #?item wdt:P31 ?type .
                                      #?article schema:about ?item .
                                      #?article schema:inLanguage "en" .
                                      #?article schema:isPartOf <https://en.wikipedia.org/>.

                                        OPTIONAL {{ ?item rdfs:label ?itemLabel. FILTER(LANG(?itemLabel) = "en") }}
                                        OPTIONAL {{ ?item     wdt:P17    ?itemcountry .
                                                ?itemcountry  rdfs:label  ?itemcountryLabel
                                                FILTER ( LANGMATCHES ( LANG ( ?itemcountryLabel ), "en" ) )
                                              }}
                                        OPTIONAL {{ ?item     wdt:P452    ?industry .
                                                    ?industry  rdfs:label  ?industryLabel
                                                    FILTER ( LANGMATCHES ( LANG ( ?industryLabel ), "en" ) )
                                                  }}
                                        OPTIONAL {{ ?item     wdt:P2139     ?revenue. }}
                                        OPTIONAL {{ ?item p:P2139 [ps:P2139 ?revenue;  pq:P585  ?revenueDate] }}
                                        OPTIONAL {{ ?item wdt:P355 ?subsidiary. }}
                                        OPTIONAL {{ ?subsidiary     wdt:P452    ?sindustry .
                                                    ?sindustry  rdfs:label  ?sindustryLabel
                                                    FILTER ( LANGMATCHES ( LANG ( ?sindustryLabel ), "en" ) )
                                                  }}
                                        OPTIONAL {{ ?subsidiary     wdt:P17    ?subsidiarycountry .
                                                ?subsidiarycountry  rdfs:label  ?subsidiarycountryLabel
                                                FILTER ( LANGMATCHES ( LANG ( ?subsidiarycountryLabel ), "en" ) )
                                              }}
                                        OPTIONAL {{ ?subsidiary     wdt:P2139     ?srevenue. }}
                                        OPTIONAL {{ ?subsidiary p:P2139 [ps:P2139 ?srevenue;  pq:P585  ?srevenueDate] }}
                                        OPTIONAL {{ ?item  p:P355 [ps:P355 ?subsidiary; pq:P1107 ?proportion] }}
                                        OPTIONAL {{
                                                    ?item  p:P355 [ps:P355 ?subsidiary; pq:P642 ?proportionof] .
                                                    FILTER(?proportionof = wd:Q144368)
                                                 }}
                                        OPTIONAL {{ ?item p:P355 [ps:P355 ?subsidiary; pq:P585 ?pointoftime] }}
                                        OPTIONAL {{?item p:P355 [ps:P355 ?subsidiary; pq:P1107 ?proportion; pq:P585 ?pointoftime].
                                                  FILTER(NOT EXISTS {{?item p:P355 [ps:P355 ?subsidiary; pq:P585 ?earlierTime; ?earlierTime [wdt:P585 ?pointoftime]]}})
                                                  }}
                                        #OPTIONAL {{
                                        #            ?item p:P355 [ps:P355 ?subsidiary; pq:P585 ?pointoftime] .
                                        #            FILTER(BOUND(?pointoftime) && DATATYPE(?pointoftime) = xsd:dateTime).
                                        #            # get the latest record first
                                        #            BIND(NOW() - ?pointoftime AS ?distance).
                                        #            FILTER (MIN (?distance)) .
                                        #          }}
                                        OPTIONAL {{ ?item  p:P355 [ps:P355 ?subsidiary; pq:P580 ?starttime] }}
                                        OPTIONAL {{ ?item  p:P355 [ps:P355 ?subsidiary; pq:P582 ?endtime] }}
                                      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                    }}
                                    GROUP BY  ?item ?QID ?itemLabel ?itemcountryLabel ?revenue ?revenueDate ?subsidiary ?sQID ?subsidiaryLabel ?subsidiarycountryLabel ?srevenue ?srevenueDate ?proportion ?proportionofLabel ?pointoftime ?starttime ?endtime
                                    ORDER BY ?subsidiaryLabel
                                    LIMIT 10000
                                    """
        self.query_has_ownerof = f""" SELECT ?ownerof (IF (BOUND(?ownerof), COUNT(DISTINCT ?ownerof), 0) AS ?count)
                                  WHERE {{
                                        VALUES ?item {{wd:{qid}}}.
                                        ?item wdt:P31 ?type .
                                        VALUES ?type {{wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q167037 wd:Q21980538 wd:Q891723 wd:Q786820 wd:Q43229 wd:Q1058914
                                                    wd:Q18388277 wd:Q161726 wd:Q778575 wd:Q2005696 wd:Q108460239 wd:Q3477381 wd:Q270791 wd:Q936518
                                                    wd:Q1934969 wd:Q2538889 wd:Q2995256 wd:Q1631129 wd:Q1276157 wd:Q5038204 wd:Q217107 wd:Q13235160
                                                    wd:Q17377208 wd:Q740752 wd:Q249556}} . #to search multiple entities
                                        #?article schema:about ?item .
                                        #?article schema:inLanguage "en" .
                                        #?article schema:isPartOf <https://en.wikipedia.org/>.

                                        OPTIONAL {{ ?item wdt:P1830 ?ownerof. }}

                                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                        }}
                                        GROUP BY ?ownerof
                                  """

        self.query_get_ownerof_info = f"""
                                    SELECT DISTINCT ?item
                                                    (REPLACE(STR(?item), "http://www.wikidata.org/entity/", "") AS ?QID)
                                                    ?itemLabel
                                                    ?itemcountryLabel
                                                    (GROUP_CONCAT ( DISTINCT ?industryLabel; separator="; ") AS ?industries)
                                                    ?revenue
                                                    ?revenueDate
                                                    ?ownerof
                                                    (REPLACE(STR(?ownerof), "http://www.wikidata.org/entity/", "") AS ?ooQID)
                                                    ?ownerofLabel
                                                    ?ownerofcountryLabel
                                                    (GROUP_CONCAT ( DISTINCT ?ooindustryLabel; separator="; ") AS ?ooindustries)
                                                    ?oorevenue
                                                    ?oorevenueDate
                                                    ?proportion
                                                    ?proportionofLabel
                                                    ?pointoftime
                                                    ?starttime
                                                    ?endtime
                                    WHERE {{
                                      VALUES ?item {{wd:{qid}}}.
                                      #?item wdt:P31 ?type .
                                      #?article schema:about ?item .
                                      #?article schema:inLanguage "en" .
                                      #?article schema:isPartOf <https://en.wikipedia.org/>.

                                        OPTIONAL {{ ?item rdfs:label ?companyLabel. FILTER(LANG(?companyLabel) = "en") }}
                                        OPTIONAL {{ ?item     wdt:P17    ?itemcountry .
                                                    ?itemcountry  rdfs:label  ?itemcountryLabel
                                                    FILTER ( LANGMATCHES ( LANG ( ?itemcountryLabel ), "en" ) )
                                                  }}
                                        OPTIONAL {{ ?item     wdt:P452    ?industry .
                                                    ?industry  rdfs:label  ?industryLabel
                                                    FILTER ( LANGMATCHES ( LANG ( ?industryLabel ), "en" ) )
                                                  }}
                                        OPTIONAL {{ ?item     wdt:P2139     ?revenue. }}
                                        OPTIONAL {{ ?item p:P2139 [ps:P2139 ?revenue;  pq:P585  ?revenueDate] }}
                                        OPTIONAL {{ ?item wdt:P1830 ?ownerof. }}
                                        OPTIONAL {{ ?ownerof     wdt:P452    ?ooindustry .
                                                    ?ooindustry  rdfs:label  ?ooindustryLabel
                                                    FILTER ( LANGMATCHES ( LANG ( ?ooindustryLabel ), "en" ) )
                                                  }}
                                        OPTIONAL {{ ?ownerof     wdt:P17    ?ownerofcountry .
                                                    ?ownerofcountry  rdfs:label  ?ownerofcountryLabel
                                                    FILTER ( LANGMATCHES ( LANG ( ?ownerofcountryLabel ), "en" ) )
                                                  }}
                                        OPTIONAL {{ ?ownerof     wdt:P2139     ?oorevenue. }}
                                        OPTIONAL {{ ?ownerof p:P2139 [ps:P2139 ?oorevenue;  pq:P585  ?oorevenueDate] }}
                                        OPTIONAL {{ ?item  p:P1830 [ps:P1830 ?ownerof; pq:P1107 ?proportion] }}
                                        OPTIONAL {{
                                                    ?item  p:P1830 [ps:P1830 ?ownerof; pq:P642 ?proportionof] .
                                                    FILTER(?proportionof = wd:Q144368)
                                                  }}
                                        OPTIONAL {{ ?item p:P1830 [ps:P1830 ?ownerof; pq:P585 ?pointoftime] }}
                                        OPTIONAL {{?item p:P1830 [ps:P1830 ?ownerof; pq:P1107 ?proportion; pq:P585 ?pointoftime].
                                                  FILTER(NOT EXISTS {{?item p:P1830 [ps:P1830 ?ownerof; pq:P585 ?earlierTime; ?earlierTime [wdt:P585 ?pointoftime]]}})
                                                  }}
                                        #OPTIONAL {{
                                        #            ?item p:P1830 [ps:P1830 ?ownerof; pq:P585 ?pointoftime] .
                                        #            FILTER(BOUND(?pointoftime) && DATATYPE(?pointoftime) = xsd:dateTime).
                                        #            # get the latest record first
                                        #            BIND(NOW() - ?pointoftime AS ?distance).
                                        #            FILTER (MIN (?distance)) .
                                        #          }}
                                        OPTIONAL {{ ?item  p:P1830 [ps:P1830 ?ownerof; pq:P580 ?starttime] }}
                                        OPTIONAL {{ ?item  p:P1830 [ps:P1830 ?ownerof; pq:P582 ?endtime] }}
                                      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                    }}
                                    GROUP BY  ?item ?QID ?itemLabel ?itemcountryLabel ?revenue ?revenueDate ?ownerof ?ooQID ?ownerofLabel ?ownerofcountryLabel ?oorevenue ?oorevenueDate ?proportion ?proportionofLabel ?pointoftime ?starttime ?endtime
                                    ORDER BY ?ownerofLabel
                                    LIMIT 10000
                                    """

        self.query_is_human = f"""
                                SELECT DISTINCT
                                        ?human
                                        (REPLACE(STR(?human), "http://www.wikidata.org/entity/", "") AS ?QID)
                                        ?humanLabel
                                        ?humanDescription
                              WHERE {{
                                    VALUES ?human {{wd:{qid}}} .
                                    ?human wdt:P31/wdt:P279* wd:Q5 .
                                    #?article schema:about ?human .
                                    #?article schema:inLanguage "en" .
                                    #?article schema:isPartOf <https://en.wikipedia.org/>.
                                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                    FILTER (LANG (?humanDescription) = "en")
                                    }}
                            """

        self.query_get_description =  f""" SELECT DISTINCT
                                ?item
                                (REPLACE(STR(?item), "http://www.wikidata.org/entity/", "") AS ?QID)
                                ?itemLabel
                                ?itemDescription
                                  WHERE {{ wd:{qid} rdfs:label ?itemLabel .
                                        OPTIONAL {{ wd:{qid} schema:description ?itemDescription }} .
                                        BIND (wd:{qid} AS ?item) .
                                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                                        FILTER (LANG (?itemDescription) = "en")
                                        }}
                                """

    def connect(self):
        # Choosing a random user agent from the list
        user_agent = random.choice(self.user_agents)
        # Sending the request to the Wikidata endpoint with the user agent header
        if self.index == 1:
            query = self.query_has_parent
        elif self.index == 2:
            query = self.query_get_parent_info
        elif self.index == 3:
            query = self.query_has_owned_by
        elif self.index == 4:
            query = self.query_get_owned_by_info
        elif self.index == 5:
            query = self.query_has_subsidiary
        elif self.index == 6:
            query = self.query_get_subsidiary_info
        elif self.index == 7:
            query = self.query_has_ownerof
        elif self.index == 8:
            query = self.query_get_ownerof_info
        elif self.index == 9:
            query = self.query_is_human
        elif self.index == 0:
            query = self.query_get_description

        response = requests.get("https://query.wikidata.org/sparql", params={"query": query, "format": "json"},
                                headers={"User-Agent": user_agent})
        return response

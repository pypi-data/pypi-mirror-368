import pandas as pd
import numpy as np
from .query import Querier


# Checking if entity has a parent, and if so how many
def has_parent(wikidata_id):
    querier = Querier(wikidata_id, 1)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # Parsing the response as JSON
            data = response.json()
            # Extracting all the results
            results = data["results"]["bindings"]
            # Check if results is empty
            if not results:
                # Return zero
                return 0
            else:
                # Get the count value
                counts = results[0]["count"]["value"]
                # Make counts integers
                counts = int(counts)
                # Return the count as an integer
                return counts
        except ValueError:
            return 0
    else:
        return 0


def get_company_parent_info(wikidata_id):
    querier = Querier(wikidata_id, 2)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # extracts the results and bindings keys from the JSON response returned by the Wikidata SPARQL endpoint
            data = response.json()['results']['bindings']
            # converts the JSON data into a pandas DataFrame
            df = pd.json_normalize(data)
            #  checks if an element is a dictionary and if so, extracts the value key from it
            df = df.applymap(lambda x: x['value'] if isinstance(x, dict) else x)
            # selects only the columns that end with .value.
            df = df[[col for col in df.columns if col.endswith('.value')]]
            # removes the .value suffix from each column name
            df.columns = [col.split('.')[0] for col in df.columns]
            return df
        except ValueError:
            return pd.DataFrame()
    else:
        return pd.DataFrame()


def has_ownedby(wikidata_id):
    querier = Querier(wikidata_id, 3)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # Parsing the response as JSON
            data = response.json()
            # Extracting all the results
            results = data["results"]["bindings"]
            # Check if results is empty
            if not results:
                # Return zero
                return 0
            else:
                # Get the count value
                counts = results[0]["count"]["value"]
                # Make counts integers
                counts = int(counts)
                # Return the count as an integer
                return counts
        except ValueError:
            return 0
    else:
        return 0


# Defining a function that takes a Wikidata ID and returns a dictionary of information about its industry, parent organizations and subsidiaries
def get_company_ownedby_info(wikidata_id):
    querier = Querier(wikidata_id, 4)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # extracts the results and bindings keys from the JSON response returned by the Wikidata SPARQL endpoint
            data = response.json()['results']['bindings']
            # converts the JSON data into a pandas DataFrame
            df = pd.json_normalize(data)
            #  checks if an element is a dictionary and if so, extracts the value key from it
            df = df.applymap(lambda x: x['value'] if isinstance(x, dict) else x)
            # selects only the columns that end with .value.
            df = df[[col for col in df.columns if col.endswith('.value')]]
            # removes the .value suffix from each column name
            df.columns = [col.split('.')[0] for col in df.columns]
            return df
        except ValueError:
            return pd.DataFrame()
    else:
        return pd.DataFrame()


# Checking if entity has a subsidiary (which is also a type of company), and if so how many
def has_subsidiary(wikidata_id):
    querier = Querier(wikidata_id, 5)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # Parsing the response as JSON
            data = response.json()
            # Extracting all the results
            results = data["results"]["bindings"]
            # Check if results is empty
            if not results:
                # Return zero
                return 0
            else:
                # Get the count value
                counts = results[0]["count"]["value"]
                # Make counts integers
                counts = int(counts)
                # Return the count as an integer
                return counts
        except ValueError:
            return 0
    else:
        return 0


# getting company's subsidaries
def get_company_subsidiary_info(wikidata_id):
    querier = Querier(wikidata_id, 6)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # extracts the results and bindings keys from the JSON response returned by the Wikidata SPARQL endpoint
            data = response.json()['results']['bindings']
            # converts the JSON data into a pandas DataFrame
            df = pd.json_normalize(data)
            #  checks if an element is a dictionary and if so, extracts the value key from it
            df = df.applymap(lambda x: x['value'] if isinstance(x, dict) else x)
            # selects only the columns that end with .value.
            df = df[[col for col in df.columns if col.endswith('.value')]]
            # removes the .value suffix from each column name
            df.columns = [col.split('.')[0] for col in df.columns]
            return df
        except ValueError:
            return pd.DataFrame()
    else:
        return pd.DataFrame()
    # return df


# Checking if entity has a ownerof (which is also a type of company), and if so how many
def has_ownerof(wikidata_id):
    querier = Querier(wikidata_id, 7)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # Parsing the response as JSON
            data = response.json()
            # Extracting all the results
            results = data["results"]["bindings"]
            # Check if results is empty
            if not results:
                # Return zero
                return 0
            else:
                # Get the count value
                counts = results[0]["count"]["value"]
                # Make counts integers
                counts = int(counts)
                # Return the count as an integer
                return counts
        except ValueError:
            return 0


# Defining a function that takes a Wikidata ID and returns a dictionary of information about its industry, parent organizations and subsidiaries
def get_company_ownerof_info(wikidata_id):
    querier = Querier(wikidata_id, 8)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # extracts the results and bindings keys from the JSON response returned by the Wikidata SPARQL endpoint
            data = response.json()['results']['bindings']
            # converts the JSON data into a pandas DataFrame
            df = pd.json_normalize(data)
            #  checks if an element is a dictionary and if so, extracts the value key from it
            df = df.applymap(lambda x: x['value'] if isinstance(x, dict) else x)
            # selects only the columns that end with .value.
            df = df[[col for col in df.columns if col.endswith('.value')]]
            # removes the .value suffix from each column name
            df.columns = [col.split('.')[0] for col in df.columns]
            return df
        except ValueError:
            return pd.DataFrame()
    else:
        return pd.DataFrame()


def tidy_each_df(df):
    # split companies' industries string and return them as list, then drop duplicates, and finally return as string again
    df.iloc[:, 4] = df.iloc[:, 4].str.split("; ").apply(lambda x: "; ".join(set(word.lower() for word in x)))
    # drop parents' industries duplicates, then return as string again
    df.iloc[:, 11] = df.iloc[:, 11].str.split("; ").apply(lambda x: "; ".join(set(word.lower() for word in x)))
    # check if all proprtions are between 0 and 1, if above 1, then devide by 100, otherwise leave it
    if 'proportion' in df.columns:
        df['proportion'] = df['proportion'].astype(float)
        df['proportion'] = np.where(df['proportion'].isnull(), df['proportion'],
                                    np.where(df['proportion'] > 1, df['proportion'] / 100,
                                             df['proportion']))
    df = df.drop_duplicates().reset_index(drop=True)
    return df


class NetworkBuilder:
    def __init__(self, qids, levels):
        self.qids=qids
        self.levels=levels

    def get_companies_network(self):
        # Create an empty dataframe for parent
        p_df = pd.DataFrame(columns=['item', 'QID', 'itemLabel', 'itemcountryLabel', 'industries', \
                                     'revenue', 'revenueDate', \
                                     'parent', 'pQID', 'parentLabel', 'parentcountryLabel', 'pindustries', \
                                     'prevenue', 'prevenueDate', \
                                     'proportion', 'proportionofLabel', 'pointoftime', 'starttime', 'endtime'])
        # Create an empty dataframe for owned by
        ob_df = pd.DataFrame(columns=['item', 'QID', 'itemLabel', 'itemcountryLabel', 'industries', \
                                      'revenue', 'revenueDate', \
                                      'ownedby', 'obQID', 'ownedbyLabel', 'ownedbycountryLabel', 'obindustries', \
                                      'obrevenue', 'obrevenueDate', \
                                      'proportion', 'proportionofLabel', 'pointoftime', 'starttime', 'endtime'])
        # Create an empty dataframe for subsidiary
        s_df = pd.DataFrame(columns=['item', 'QID', 'itemLabel', 'itemcountryLabel', 'industries', \
                                     'revenue', 'revenueDate', \
                                     'subsidiary', 'sQID', 'subsidiaryLabel', 'subsidiarycountryLabel', 'sindustries', \
                                     'srevenue', 'srevenueDate', \
                                     'proportion', 'proportionofLabel', 'pointoftime', 'starttime', 'endtime'])
        # Create an empty dataframe for owner of
        oo_df = pd.DataFrame(columns=['item', 'QID', 'itemLabel', 'itemcountryLabel', 'industries', \
                                      'revenue', 'revenueDate', \
                                      'ownerof', 'ooQID', 'ownerofLabel', 'ownerofcountryLabel', 'ooindustries', \
                                      'oorevenue', 'oorevenueDate', \
                                      'proportion', 'proportionofLabel', 'pointoftime', 'starttime', 'endtime'])

        # initialize a list to store the results of each run
        results = {"p_df": [], "ob_df": [], "s_df": [], "oo_df": []}
        # making sure only those QIDs in root_QIDs that starts with "Q"
        root_QIDs = [item for item in self.qids if item.startswith("Q")]
        # Find the maximum number of levels
        levels = self.levels
        max_levels = max(levels)
        # Iterate from 0 to max_levels-1
        for j in range(max_levels):
            # Iterate over each element of the levels tuple
            for i in range(len(levels)):
                # Check if j is less than the value of levels[i]
                if j < levels[i]:
                    # Iterate over each element of the item list
                    if i == 0:
                        # making sure only those QIDs in root_QIDs that starts with "Q"
                        root_QIDs = [item for item in root_QIDs if item.startswith("Q")]
                        ## HAS PARENT
                        # make a new parent QID list with only those that has parent
                        new_p_QIDs = []
                        for id in root_QIDs:
                            parent_count = has_parent(id)
                            if parent_count > 0:
                                new_p_QIDs.append(id)
                        ## PARENT INFO
                        # Check if new_p_QIDs is empty
                        # get the parent info from the new QID list and concat it with the p_df dataframe
                        for id in new_p_QIDs:
                            p_df = pd.concat([p_df, get_company_parent_info(id)], ignore_index=True)
                        # tidy up industries and proportions with function tidy_each_df()
                        p_df = tidy_each_df(p_df)
                    elif i == 1:
                        # making sure only those QIDs in root_QIDs that starts with "Q"
                        root_QIDs = [item for item in root_QIDs if item.startswith("Q")]
                        ## HAS OWNED BY
                        # make a new ownedby QID list with only those companies that has ownedby
                        new_ob_QIDs = []
                        for id in root_QIDs:
                            ownedby_count = has_ownedby(id)
                            if ownedby_count > 0:
                                new_ob_QIDs.append(id)
                        ## GET OWNED BY INFO
                        for id in new_ob_QIDs:
                            ob_df = pd.concat([ob_df, get_company_ownedby_info(id)], ignore_index=True)
                        # tidy up industries and proportions with function tidy_each_df()
                        ob_df = tidy_each_df(ob_df)
                    elif i == 2:
                        # making sure only those QIDs in root_QIDs that starts with "Q"
                        root_QIDs = [item for item in root_QIDs if item.startswith("Q")]
                        ## HAS SUBSIDIARY
                        # make a new subsidiary QID list with only those companies that has subsidiary
                        new_s_QIDs = []
                        for id in root_QIDs:
                            subsidiary_count = has_subsidiary(id)
                            if subsidiary_count > 0:
                                new_s_QIDs.append(id)
                        ## GET SUBSIDIARY INFO
                        # get the subsidiaries info from the new QID list and concat it with the s_df dataframe
                        for id in new_s_QIDs:
                            s_df = pd.concat([s_df, get_company_subsidiary_info(id)], ignore_index=True)
                        # tidy up industries and proportions with function tidy_each_df()
                        s_df = tidy_each_df(s_df)
                    elif i == 3:
                        # making sure only those QIDs in root_QIDs that starts with "Q"
                        root_QIDs = [item for item in root_QIDs if item.startswith("Q")]
                        ## HAS OWNER OF
                        # make a new ownerof QID list with only those companies that has owner of
                        new_oo_QIDs = []
                        for id in root_QIDs:
                            ownerof_count = has_ownerof(id)
                            if ownerof_count > 0:
                                new_oo_QIDs.append(id)
                        ## GET OWNER OF INFO
                        # get the owner of info from the new QID list and concat it with the oo_df dataframe
                        for id in new_oo_QIDs:
                            oo_df = pd.concat([oo_df, get_company_ownerof_info(id)], ignore_index=True)
                        # tidy up industries and proportions with function tidy_each_df()
                        oo_df = tidy_each_df(oo_df)

            # append results after each number of runs
            results['p_df'].append(p_df)
            results['ob_df'].append(ob_df)
            results['s_df'].append(s_df)
            results['oo_df'].append(oo_df)
            ## JOIN NEW UNIQUE QIDS
            # getting all the QIDs that will needs to be queried again
            # Store dataframes in a list
            df_list = [p_df, ob_df, s_df, oo_df]
            # Store column names in a list
            col_list = ['pQID', 'obQID', 'sQID', 'ooQID']
            # Create an empty list to store the column values
            val_list = []
            # Loop over the dataframes and the column names and append the column values to the list
            for df, col in zip(df_list, col_list):
                val_list.append(df[col].to_list())
            # collect the unique values from val_list
            new_list = []
            [new_list.append(x) for x in val_list if x not in new_list]
            # Convert the list to a pandas series
            original_series = pd.Series(new_list)
            # Use the explode method to split the nested lists into separate rows
            exploded_series = original_series.explode()
            # Use the drop_duplicates method to remove any duplicate values
            unique_series = exploded_series.drop_duplicates()
            # Convert the series back to a list
            new_QIDs = unique_series.tolist()
            # clean new_QIDs from 'nan' string values
            new_QIDs = [x for x in new_QIDs if str(x) != 'nan']
            # get a list of the new unique QIDs
            new1_QIDs = list(set(new_QIDs) - set(root_QIDs))
            # keep only those QIDs that starts with "Q"
            new2_QIDs = [item for item in new1_QIDs if item.startswith("Q")]
            # rename the new list of QIDs as root_QIDs
            root_QIDs = new2_QIDs

        # return the list of results
        return results

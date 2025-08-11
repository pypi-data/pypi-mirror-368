import pandas as pd
import numpy as np
from .query import Querier
import pycountry_convert as pc


def is_human(wikidata_id):
    # Initializing an empty dictionary to store the information
    info = {}
    querier = Querier(wikidata_id, 9)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # Parsing the response as JSON
            data = response.json()
            # Looping through the results
            for result in data["results"]["bindings"]:
                # Adding the company's QID to the dictionary if exists
                if "QID" in result:
                    info["QID"] = result["QID"]["value"]
                # Adding the company label to the dictionary if exists
                if "humanLabel" in result:
                    info["name"] = result["humanLabel"]["value"]
                # Adding the industry label to the dictionary if exists
                if "humanDescription" in result:
                    info["descr"] = result["humanDescription"]["value"]
            # Returning the dictionary of information
            return info
        except ValueError:
            return info
    else:
        return info


def get_description(wikidata_id):
    # Initializing an empty dictionary to store the information
    info = {}
    querier = Querier(wikidata_id, 0)
    response = querier.connect()
    if response.status_code != 204 and response.headers["content-type"].strip().find("json") > -1:
        try:
            # Parsing the response as JSON
            data = response.json()

            # Initializing an empty dictionary to store the information
            info = {}
            # Looping through the results
            for result in data["results"]["bindings"]:
                # Adding the company's QID to the dictionary if exists
                if "QID" in result:
                    info["QID"] = result["QID"]["value"]
                # Adding the company label to the dictionary if exists
                if "itemLabel" in result:
                    info["name"] = result["itemLabel"]["value"]
                # Adding the industry label to the dictionary if exists
                if "itemDescription" in result:
                    info["descr"] = result["itemDescription"]["value"]
            # Returning the dictionary of information
            return info
        except ValueError:
            return info
    else:
        return info


def clear_each_df(df):
    # convert endtime column to string and filter out rows with valid dates
    if 'endtime' in df.columns:
        df['endtime'] = df['endtime'].astype(str)
        df1 = df[~df['endtime'].str.contains('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')]
    new_df = pd.DataFrame(columns=df.columns)
    # create a set of unique QID and obQID pairs
    qid1_qid2_pairs = set(zip(df1.iloc[:, 1], df1.iloc[:, 8]))
    # loop over the unique pairs and select the first row for each latest pointoftime pair
    for qid1, qid2 in qid1_qid2_pairs:
        temp_df = df1.loc[(df1.iloc[:, 1] == qid1) & (df1.iloc[:, 8] == qid2)]
        temp_df = temp_df.drop_duplicates().reset_index(drop=True)
        if len(temp_df) == 1:
            new_row = temp_df.iloc[0]
            new_df = pd.concat([new_df, new_row.to_frame().T])
        if len(temp_df) >= 2:
            # Sort the DataFrame by the pointoftime column in descending order.
            df_filtered = temp_df.sort_values(by='pointoftime', ascending=False)
            # Get the first row of the sorted DataFrame.
            first_row = df_filtered.iloc[0]
            new_df = pd.concat([new_df, first_row.to_frame().T])

    # reset index and drop duplicates
    new_df.reset_index(drop=True, inplace=True)
    new_df = new_df.drop_duplicates().reset_index(drop=True)

    from pandas.errors import SettingWithCopyWarning
    import warnings
    warnings.filterwarnings('ignore', category=SettingWithCopyWarning)
    # add those relations that has an endtime to the new dataframes
    if 'endtime' in df.columns:
        df['endtime'] = df['endtime'].astype(str)
        df2 = df[df['endtime'].str.contains('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')]
        df2.loc[:, 'proportion'] = 4
        df2['endtime'] = df2['endtime'].str[:10]
        df2 = df2.drop_duplicates()
    new_df = pd.concat([new_df, df2]).reset_index(drop=True)

    return new_df


def drop_dupl_joined(new_df2):
    ### remove the duplicates from the joined datasets
    # Step 1. save the single parent-child pairs in the new3_df2
    #         if there are 2 or more of the same parent-child pair, then \
    #         drop the ones within these that has blank p_proportion.
    # Step 2. in a new list comprehension (temp_step2_df) save the ones that now became single parent-child.
    #         if there are 2 or more and if one of the p_prop value is == 2, then \
    ##        drop this row with value == 2
    #         Finally, if  there are 2 or more and their p_prop value is equal, then keep only the last
    ##        (this will allow more values to pass through if they differ)
    # STEP 1
    # Use a set to store the unique cQID values
    cQID_set = set(new_df2['cQID'])
    # Use a generator expression to iterate over the pQID values
    pQID_gen = (i for i in new_df2['pQID'])
    # Use a list comprehension to filter the rows based on pQID and cQID values
    temp_new3_df2 = [new_df2.loc[(new_df2['pQID'] == i) & (new_df2['cQID'] == j)]
                     for i in pQID_gen for j in cQID_set]
    # Use another list comprehension to process the filtered rows based on the
    # length and p_proportion values
    new3_df2 = pd.concat([row.iloc[0].to_frame().T if len(row) == 1
                          else row.dropna(subset=['p_proportion']).loc[row['p_proportion'].notnull()]
                          for row in temp_new3_df2])
    new3_df2 = new3_df2.drop_duplicates().reset_index(drop=True)
    # STEP 2
    # Use a set to store the unique cQID values
    cQID_set2 = set(new3_df2['cQID'])
    # Use a generator expression to iterate over the pQID values
    pQID_gen2 = (i for i in new3_df2['pQID'])
    # Use a list comprehension to filter the rows based on pQID and cQID values
    temp_step2_df = [new3_df2.loc[(new3_df2['pQID'] == i) & (new3_df2['cQID'] == j)]
                     for i in pQID_gen2 for j in cQID_set2]
    # Drop the rows with p_proportion value equal to 2 when there is already a record with proportion value
    final_df = pd.concat([row.iloc[0].to_frame().T if len(row) == 1 \
                              else row.loc[row['p_proportion'] != 2] for row in temp_step2_df])
    # Keep only the last row if there are multiple rows with the same pQID and cQID
    # values and equal p_proportion values
    final_df = final_df.drop_duplicates(subset=['pQID', 'cQID', 'p_proportion'], keep='last')
    final_df = final_df.drop_duplicates().reset_index(drop=True)
    # fill the blank p_proportion values with number 3, this will mean unknown on the graph
    final_df['p_proportion'] = final_df['p_proportion'].fillna(3)
    return final_df


def top_industries(final_df):
    # create a dictionary of industry frequencies
    # split industry columns by ";" and create separate columns
    df_split1 = final_df["p_industries"].str.split(";", expand=True)
    df_split2 = final_df["c_industries"].str.split(";", expand=True)
    # join the two dataframes horizontally
    df_split = pd.concat([df_split1, df_split2], axis=1)
    # reshape the dataframe so that each expression is in a single column
    df_melt = df_split.melt(value_name="expression")
    # drop the variable column
    df_melt = df_melt.drop("variable", axis=1)
    # count the frequency of each expression and convert to dictionary
    freq = df_melt["expression"].value_counts().to_dict()

    # define a custom function to pick the expression with highest frequency
    def pick_expression(lst):
        # split the list by semicolon
        lst = lst.split(";")
        # initialize the best expression and frequency
        best_exp = None
        best_freq = 0
        # loop through the list
        for exp in lst:
            # get the frequency of the expression
            freq_exp = freq.get(exp, 0)
            # if the frequency is higher than the best frequency, update the best expression and frequency
            if freq_exp > best_freq:
                best_exp = exp
                best_freq = freq_exp
        # return the best expression
        return best_exp

    # apply the custom function to each cell in col2
    final_df["top_p_industries"] = final_df["p_industries"].apply(pick_expression)
    final_df["top_c_industries"] = final_df["c_industries"].apply(pick_expression)

    # list of columns to be processed
    cols = ["top_p_industries", "top_c_industries", "p_industries", "c_industries"]
    # replace the empty strings with 'unknown' and strip leading spaces
    for col in cols:
      final_df[col] = final_df[col].replace("", np.nan)
      mask = final_df[col].isna()
      final_df.loc[mask, col] = "unknown"
      final_df[col] = final_df[col].str.lstrip()
    
    # make a list of all those parent QIDs where the industry is "unknown"
    unique_values1 = final_df.loc[(final_df['top_p_industries'] == 'unknown'), 'pQID'].drop_duplicates().values.tolist()
    # making sure only those QIDs in unique_values that starts with "Q"
    unique_values1 = [item for item in unique_values1 if item.startswith("Q")]
    # create a dataframe for the results
    p_human_df1 = pd.DataFrame(columns=["QID", "name", "descr"])
    # initialising a new list to store the results
    results = []
    # Loop through the values
    for id in unique_values1:
        # Run the module with the value as input and get the result
        result = pd.DataFrame(is_human(id), index=[0])
        # Appending the new dataframe to the list
        results.append(result)

    # join the new results to the dataframe
    p_human_df1 = pd.concat([p_human_df1] + results, axis=0, join='outer').drop_duplicates().reset_index(drop=True)

    # apply humans and their descriptions to new_df2 dataframe
    for index, row in final_df.iterrows():
        if row['pQID'] in p_human_df1['QID'].values:
            # get the index of the matching row in p_human_df1
            match_index = p_human_df1[p_human_df1['QID'] == row['pQID']].index
            # get the value from the "descr" column of p_human_df1
            descr_value = p_human_df1.loc[match_index[0], 'descr']
            # update the values in new_df2
            final_df.loc[index, 'p_industries'] = descr_value
            final_df.loc[index, 'top_p_industries'] = "human"

    # make a list of all those QIDs where the industry is "unknown"
    unique_values3 = final_df.loc[(final_df['top_p_industries'] == 'unknown'), 'pQID'].drop_duplicates().values.tolist()
    unique_values4 = final_df.loc[(final_df['top_c_industries'] == 'unknown'), 'cQID'].drop_duplicates().values.tolist()
    # making sure only those QIDs in unique_values that starts with "Q"
    unique_values3 = [item for item in unique_values3 if item.startswith("Q")]
    unique_values4 = [item for item in unique_values4 if item.startswith("Q")]
    # create a dataframe for the results
    p_item_df1 = pd.DataFrame(columns=["QID", "name", "descr"])
    # initialising a new list to store the results
    results = []
    # Loop through the values
    for id in unique_values3:
        # Run the module with the value as input and get the result
        result = pd.DataFrame(get_description(id), index=[0])
        # Appending the new dataframe to the list
        results.append(result)

    # join the new results to the dataframe
    p_item_df1 = pd.concat([p_item_df1] + results, axis=0, join='outer').drop_duplicates().reset_index(drop=True)

    # create a dataframe for the results
    c_item_df2 = pd.DataFrame(columns=["QID", "name", "descr"])
    # initialising a new list to store the results
    results2 = []
    # Loop through the values
    for id2 in unique_values4:
        # Run the module with the value as input and get the result
        result2 = pd.DataFrame(get_description(id2), index=[0])
        # Appending the new dataframe to the list
        results2.append(result2)

    # join the new results to the dataframe
    c_item_df2 = pd.concat([c_item_df2] + results2, axis=0, join='outer').drop_duplicates().reset_index(drop=True)

    # apply descriptions for unknown parents to new_df2 dataframe
    for index, row in final_df.iterrows():
        if row['pQID'] in p_item_df1['QID'].values:
            # get the index of the matching row in p_human_df1
            match_index = p_item_df1[p_item_df1['QID'] == row['pQID']].index
            # get the value from the "descr" column of p_human_df1
            descr_value = p_item_df1.loc[match_index[0], 'descr']
            # update the values in new_df2
            final_df.loc[index, 'p_industries'] = descr_value
            final_df.loc[index, 'top_p_industries'] = "other"

    # apply descriptions for unknown children to new_df2 dataframe
    for index, row in final_df.iterrows():
        if row['cQID'] in c_item_df2['QID'].values:
            # get the index of the matching row in p_human_df1
            match_index2 = c_item_df2[c_item_df2['QID'] == row['cQID']].index
            # get the value from the "descr" column of p_human_df1
            descr_value2 = c_item_df2.loc[match_index2[0], 'descr']
            # update the values in new_df2
            final_df.loc[index, 'c_industries'] = descr_value2
            final_df.loc[index, 'top_c_industries'] = "other"

    # list of columns to be processed
    cols2 = ['p_industries', 'top_p_industries', 'c_industries', 'top_c_industries']
    # convert the values in columns to strings
    for col2 in cols2:
      final_df[col2] = final_df[col2].astype(str)
    return final_df

def country_to_continent(country_name):
    import pycountry_convert as pc
    try:
        if country_name.lower() == 'unknown':
            return 'unknown'
        else:
            country_alpha2 = pc.country_name_to_country_alpha2(country_name)
            country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
            country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
            return country_continent_name
    except KeyError:
        return 'unknown'


    # class PostProcessor:
    #    def __init__(self, input):
    #        self.input = input

    # clean each dataset and then join them


class Cleaner:
    def __init__(self, input):
        self.input = input

    def clean_join(self):
        results = self.input
        p_df = results['p_df'][-1]
        ob_df = results['ob_df'][-1]
        s_df = results['s_df'][-1]
        oo_df = results['oo_df'][-1]

        # global final_df, new_p_df, new_ob_df, new_s_df, new_oo_df
        # convert the data columns to strings
        p_df.loc[:, ['pointoftime', 'starttime']] = p_df.loc[:, ['pointoftime', 'starttime']].astype(str)
        ob_df.loc[:, ['pointoftime', 'starttime']] = ob_df.loc[:, ['pointoftime', 'starttime']].astype(str)
        s_df.loc[:, ['pointoftime', 'starttime']] = s_df.loc[:, ['pointoftime', 'starttime']].astype(str)
        oo_df.loc[:, ['pointoftime', 'starttime']] = oo_df.loc[:, ['pointoftime', 'starttime']].astype(str)
        ### remove the duplicates within p dataset - keep the last
        new_p_df = pd.DataFrame(columns=['item', 'QID', 'itemLabel', 'itemcountryLabel', 'industries', \
                                         'revenue', 'revenueDate', \
                                         'parent', 'pQID', 'parentLabel', 'parentcountryLabel', 'pindustries', \
                                         'prevenue', 'prevenueDate', \
                                         'proportion', 'proportionofLabel', 'pointoftime', 'starttime', 'endtime'])
        new_p_df = pd.concat([new_p_df, clear_each_df(p_df)]).reset_index(drop=True)

        ### remove the duplicates within ob dataset - keep the last
        new_ob_df = pd.DataFrame(columns=['item', 'QID', 'itemLabel', 'itemcountryLabel', 'industries', \
                                          'revenue', 'revenueDate', \
                                          'ownedby', 'obQID', 'ownedbyLabel', 'ownedbycountryLabel', 'obindustries', \
                                          'obrevenue', 'obrevenueDate', \
                                          'proportion', 'proportionofLabel', 'pointoftime', 'starttime', 'endtime'])
        new_ob_df = pd.concat([new_ob_df, clear_each_df(ob_df)]).reset_index(drop=True)

        ### remove the duplicates within s dataset - keep the last
        new_s_df = pd.DataFrame(columns=['item', 'QID', 'itemLabel', 'itemcountryLabel', 'industries', \
                                         'revenue', 'revenueDate', \
                                         'subsidiary', 'sQID', 'subsidiaryLabel', 'subsidiarycountryLabel',
                                         'sindustries', \
                                         'srevenue', 'srevenueDate', \
                                         'proportion', 'proportionofLabel', 'pointoftime', 'starttime', 'endtime'])
        new_s_df = pd.concat([new_s_df, clear_each_df(s_df)]).reset_index(drop=True)

        ### remove the duplicates within oo dataset - keep the last
        new_oo_df = pd.DataFrame(columns=['item', 'QID', 'itemLabel', 'itemcountryLabel', 'industries', \
                                          'revenue', 'revenueDate', \
                                          'ownerof', 'ooQID', 'ownerofLabel', 'ownerofcountryLabel', 'ooindustries', \
                                          'oorevenue', 'oorevenueDate', \
                                          'proportion', 'proportionofLabel', 'pointoftime', 'starttime', 'endtime'])
        new_oo_df = pd.concat([new_oo_df, clear_each_df(oo_df)]).reset_index(drop=True)

        ### join together the dataframes into a new_df
        new_df = pd.DataFrame(
            columns=["pQID", "parent", "parent_country", "p_industries", "p_total_revenue", "p_total_revenue_date", \
                     "cQID", "child", "child_country", "c_industries", "c_total_revenue", "c_total_revenue_date", \
                     "p_proportion", "proportionofLabel", \
                     "pointoftime", "starttime", "endtime"])
        # Create an empty list to store the new rows
        new_p_rows = []
        # Loop over the new_p_df dataframe
        for i in range(len(new_p_df)):
            # Create a new row as a dictionary
            new_p_row = {'pQID': new_p_df['pQID'][i], 'parent': new_p_df['parentLabel'][i],
                         'parent_country': new_p_df['parentcountryLabel'][i], \
                         'p_industries': new_p_df['pindustries'][i], 'p_total_revenue': new_p_df['prevenue'][i], \
                         'p_total_revenue_date': new_p_df['prevenueDate'][i], \
                         'cQID': new_p_df['QID'][i], 'child': new_p_df['itemLabel'][i],
                         'child_country': new_p_df['itemcountryLabel'][i], \
                         'c_industries': new_p_df['industries'][i], 'c_total_revenue': new_p_df['revenue'][i], \
                         'c_total_revenue_date': new_p_df['revenueDate'][i], \
                         'p_proportion': new_p_df['proportion'][i],
                         'proportionofLabel': new_p_df['proportionofLabel'][i], \
                         'pointoftime': new_p_df['pointoftime'][i], 'starttime': new_p_df['starttime'][i],
                         'endtime': new_p_df['endtime'][i]}
            # Convert the dictionary to a dataframe and append it to the list
            new_p_rows.append(pd.DataFrame(new_p_row, index=[0]))

        # Concatenate the list of dataframes with the original dataframe
        new_df = pd.concat([new_df] + new_p_rows, ignore_index=True)
        new_df['p_proportion'] = new_df['p_proportion'].fillna(2)
        # Create an empty list to store the new rows
        new_ob_rows = []
        for i in range(len(new_ob_df)):
            new_ob_row = {'pQID': new_ob_df['obQID'][i], 'parent': new_ob_df['ownedbyLabel'][i],
                          'parent_country': new_ob_df['ownedbycountryLabel'][i], \
                          'p_industries': new_ob_df['obindustries'][i], 'p_total_revenue': new_ob_df['obrevenue'][i], \
                          'p_total_revenue_date': new_ob_df['obrevenueDate'][i], \
                          'cQID': new_ob_df['QID'][i], 'child': new_ob_df['itemLabel'][i],
                          'child_country': new_ob_df['itemcountryLabel'][i], \
                          'c_industries': new_ob_df['industries'][i], 'c_total_revenue': new_ob_df['revenue'][i], \
                          'c_total_revenue_date': new_ob_df['revenueDate'][i], \
                          'p_proportion': new_ob_df['proportion'][i],
                          'proportionofLabel': new_ob_df['proportionofLabel'][i], \
                          'pointoftime': new_ob_df['pointoftime'][i], 'starttime': new_ob_df['starttime'][i],
                          'endtime': new_ob_df['endtime'][i]}
            new_ob_rows.append(pd.DataFrame(new_ob_row, index=[0]))

        # Concatenate the list of dataframes with the original dataframe
        new_df = pd.concat([new_df] + new_ob_rows, ignore_index=True)
        # Create an empty list to store the new rows
        new_s_rows = []
        for i in range(len(new_s_df)):
            new_s_row = {'pQID': new_s_df['QID'][i], 'parent': new_s_df['itemLabel'][i],
                         'parent_country': new_s_df['itemcountryLabel'][i], \
                         'p_industries': new_s_df['industries'][i], 'p_total_revenue': new_s_df['revenue'][i], \
                         'p_total_revenue_date': new_s_df['revenueDate'][i], \
                         'cQID': new_s_df['sQID'][i], 'child': new_s_df['subsidiaryLabel'][i],
                         'child_country': new_s_df['subsidiarycountryLabel'][i], \
                         'c_industries': new_s_df['sindustries'][i], 'c_total_revenue': new_s_df['srevenue'][i], \
                         'c_total_revenue_date': new_s_df['srevenueDate'][i], \
                         'p_proportion': new_s_df['proportion'][i],
                         'proportionofLabel': new_s_df['proportionofLabel'][i], \
                         'pointoftime': new_s_df['pointoftime'][i], 'starttime': new_s_df['starttime'][i],
                         'endtime': new_s_df['endtime'][i]}
            new_s_rows.append(pd.DataFrame(new_s_row, index=[0]))
        # Concatenate the list of dataframes with the original dataframe
        new_df = pd.concat([new_df] + new_s_rows, ignore_index=True)
        # Create an empty list to store the new rows
        new_oo_rows = []
        for i in range(len(new_oo_df)):
            new_oo_row = {'pQID': new_oo_df['QID'][i], 'parent': new_oo_df['itemLabel'][i],
                          'parent_country': new_oo_df['itemcountryLabel'][i], \
                          'p_industries': new_oo_df['industries'][i], 'p_total_revenue': new_oo_df['revenue'][i], \
                          'p_total_revenue_date': new_oo_df['revenueDate'][i], \
                          'cQID': new_oo_df['ooQID'][i], 'child': new_oo_df['ownerofLabel'][i],
                          'child_country': new_oo_df['ownerofcountryLabel'][i], \
                          'c_industries': new_oo_df['ooindustries'][i], 'c_total_revenue': new_oo_df['oorevenue'][i], \
                          'c_total_revenue_date': new_oo_df['oorevenueDate'][i], \
                          'p_proportion': new_oo_df['proportion'][i],
                          'proportionofLabel': new_oo_df['proportionofLabel'][i], \
                          'pointoftime': new_oo_df['pointoftime'][i], 'starttime': new_oo_df['starttime'][i],
                          'endtime': new_oo_df['endtime'][i]}
            new_oo_rows.append(pd.DataFrame(new_oo_row, index=[0]))
        # Concatenate the list of dataframes with the original dataframe
        new_df = pd.concat([new_df] + new_oo_rows, ignore_index=True)
        new_df2 = new_df.drop_duplicates().reset_index(drop=True)

        # drop the duplicates from the joined dataframe with various rules defined by drop_dupl_joined() function
        final_df = drop_dupl_joined(new_df2)
        # clear up industries and find the top ones for classification. unknown ones: get description (also checks if its human)
        final_df = top_industries(final_df)

        # replace unknow country names with "unknown"
        final_df[["parent_country", "child_country"]] = final_df[["parent_country", "child_country"]].replace({"": np.nan, np.nan: "unknown"})

        # apply the country_to_continent function to get the continents the companies are located
        final_df['parent_continent'] = final_df['parent_country'].apply(country_to_continent)
        final_df['child_continent'] = final_df['child_country'].apply(country_to_continent)

        # trim the date for revenue
        final_df['p_total_revenue_date'] = final_df['p_total_revenue_date'].astype(str).str[:4]
        final_df['c_total_revenue_date'] = final_df['c_total_revenue_date'].astype(str).str[:4]

        # divide revenue by 1M and rename colum names
        final_df.loc[final_df['p_total_revenue'].notnull(), 'p_total_revenue'] = final_df.loc[final_df[
            'p_total_revenue'].notnull(), 'p_total_revenue'].astype('float') / 1000000
        final_df.loc[final_df['c_total_revenue'].notnull(), 'c_total_revenue'] = final_df.loc[final_df[
            'c_total_revenue'].notnull(), 'c_total_revenue'].astype('float') / 1000000
        final_df = final_df.rename(
            columns={'p_total_revenue': 'p_total_revenue_in_millions',
                     'c_total_revenue': 'c_total_revenue_in_millions'})
        # format the revenue values and convert it to string
        final_df.loc[final_df['p_total_revenue_in_millions'].notnull(), 'p_total_revenue_in_millions'] = final_df.loc[
            final_df['p_total_revenue_in_millions'].notnull(), 'p_total_revenue_in_millions'].apply(lambda x: f"{x:,}M")
        final_df.loc[final_df['c_total_revenue_in_millions'].notnull(), 'c_total_revenue_in_millions'] = final_df.loc[
            final_df['c_total_revenue_in_millions'].notnull(), 'c_total_revenue_in_millions'].apply(lambda x: f"{x:,}M")
        #fill the empty revenue values with "no data"
        final_df['p_total_revenue_in_millions'] = final_df['p_total_revenue_in_millions'].fillna("no data")
        final_df['c_total_revenue_in_millions'] = final_df['c_total_revenue_in_millions'].fillna("no data")
        return final_df

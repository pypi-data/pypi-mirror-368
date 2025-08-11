from pyvis.network import Network
import seaborn as sns
import colorsys
from collections import Counter


# define a function that takes a degree and a scaling factor and returns a size for the node
def degree_to_size(degree, scaling_factor):
    # multiply degree by scaling factor to get base size
    base_size = degree * scaling_factor
    # if the p and c revenue in the pandas dataframe and it is not NaN, use it to adjust the base size
    # if not np.isnan(revenues):
    #    base_size += revenues/1000
    # add minimum size to base size to ensure no node is too small
    min_size = 3
    final_size = base_size + min_size
    # return final size as an integer
    return float(final_size)


# define a function that converts an rgb tuple to an rgba string with a pastel factor
def rgb_to_rgba(rgb, pastel_factor):
    # convert rgb values to hls values
    h, l, s = colorsys.rgb_to_hls(*rgb)
    # increase lightness by multiplying with pastel factor
    l *= pastel_factor
    # convert hls values back to rgb values
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    # normalize rgb values to be between 0 and 255
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    # add alpha value of 0.7
    a = 0.7
    # format rgba values as a string
    rgba = f'rgba({r}, {g}, {b}, {a})'
    return rgba


class Visualiser:
    def __init__(self, input, network_name):
        self.input = input
        self.name = network_name

    def visualise_b2b_network(self):
        final_df = self.input
        # create network object
        net = Network(
            notebook=True,
            directed=True,  # directed graph
            bgcolor="snow",  # background color of graph
            font_color="navy",  # use navy for node labels
            cdn_resources='in_line',  # make sure Jupyter notebook can display correctly
            height="1000px",  # height of chart
            width="100%",  # fill the entire width
            select_menu=True,  # user can choose from campany name list
            filter_menu=True,  # user can search for colors - indicators for industries
            neighborhood_highlight=True,  # clicking on a node highlights its connections and grays out others
        )

        # create lists of nodes and edges from dataframe columns
        nodes = []
        edges = []
        for parent, child, p_industry, c_industry, top_p_industry, top_c_industry, parent_country, \
                parent_continent, child_country, child_continent, p_revenue, p_revenue_date, \
                c_revenue, c_revenue_date, proportion, endtime in zip(final_df['parent'], \
                                                                      final_df['child'], \
                                                                      final_df['p_industries'], \
                                                                      final_df['c_industries'], \
                                                                      final_df['top_p_industries'], \
                                                                      final_df['top_c_industries'], \
                                                                      final_df['parent_country'], \
                                                                      final_df['parent_continent'], \
                                                                      final_df['child_country'], \
                                                                      final_df['child_continent'], \
                                                                      final_df['p_total_revenue_in_millions'], \
                                                                      final_df['p_total_revenue_date'], \
                                                                      final_df['c_total_revenue_in_millions'], \
                                                                      final_df['c_total_revenue_date'], \
                                                                      final_df['p_proportion'], \
                                                                      final_df['endtime']):
            nodes.append((parent, p_industry, top_p_industry, parent_country, parent_continent, p_revenue, p_revenue_date))
            nodes.append((child, c_industry, top_c_industry, child_country, child_continent, c_revenue, c_revenue_date))
            edges.append((parent, child, proportion, endtime))

        # remove duplicate nodes
        # nodes = list(set(nodes))

        # create a set of unique industries
        industries = set(final_df['top_p_industries']).union(set(final_df['top_c_industries']))

        # creat a set of unique revenues and their dates
        # revenues = set(final_df['p_total_revenue_in_millions']).union(set(final_df['c_total_revenue_in_millions']))
        revenues = [p_revenue, c_revenue]
        revenue_dates = [p_revenue_date, c_revenue_date]
        # convert the revenues to a numeric type
        # revenues = pd.to_numeric(revenues)
        # revenue_dates = set(final_df['p_total_revenue_date']).union(set(final_df['c_total_revenue_date']))

        # get the number of unique industries
        n_colors = len(industries)

        # create a dictionary that maps each unique industry to a pastel color
        pastel_colors = sns.color_palette('muted', n_colors)

        group_color_map = {}
        for i, top_industry in enumerate(industries):
            # use the function with pastel_colors[i] and a pastel factor of 1.2
            group_color_map[top_industry] = rgb_to_rgba(pastel_colors[i], 1.2)

        # create a dictionary that maps each node to its degree
        node_degree_map = Counter()
        for edge in edges:
            node_degree_map[edge[0]] += 1
            node_degree_map[edge[1]] += 1

        # create a dictionary that maps each node to its size
        node_size_map = {}
        for node in node_degree_map:
            # use the function with node_degree_map[node] and a scaling factor of 5
            node_size_map[node] = degree_to_size(node_degree_map[node], 5)

        # define a different color for the highlighted nodes
        highlight_color = 'green'
        # node1 = root_companies[0]
        # node2 = root_companies[1]

        # create a set of unique countries and continents
        countries = set(final_df['parent_country']).union(set(final_df['child_country']))
        continents = set(final_df['parent_continent']).union(set(final_df['child_continent']))

        # add nodes and edges to network object
        for node, industry, top_industry, countries, continents, revenues, revenue_dates in nodes:
            color = group_color_map[top_industry]
            # check if the node name is equal to node1 or node2 and use highlight_color if so
            # if node == root_companies:
            #    color = highlight_color
            # else:
            #    color = group_color_map[top_industry]
            # assign shapes for the continents
            if continents == 'North America':
                node_shape = 'triangle'
            elif continents == 'South America':
                node_shape = 'triangleDown'
            elif continents == 'Europe':
                node_shape = 'star'
            elif continents == 'Africa':
                node_shape = 'diamond'
            elif continents == 'Asia':
                node_shape = 'square'
            elif continents == 'Australia':
                node_shape = 'ellipse'
            else:
                node_shape = 'dot'
            size = node_size_map[node]
            net.add_node(node, label=node, group=top_industry, color=color, shape=node_shape, \
                         title=node + ', ' + countries + ' (' + industry + ')' + ' Total revenue: ' + str(
                             revenues) + ' (' + str(revenue_dates) + ')', value=size)

        for e in edges:
            if e[2] > 0 and e[2] < 0.5:
                net.add_edge(e[0], e[1], title=str(e[2]), arrows={"to": True},
                             color='turquoise')  # value=(e[2]/100), dashes=[6,10,1,10]
            elif e[2] >= 0.5 and e[2] <= 1:
                net.add_edge(e[0], e[1], title=str(e[2]), arrows={"to": True},
                             color='violet')  # value=(e[2]/10),  dashes=False
            elif e[2] == 2:
                net.add_edge(e[0], e[1], title="parent", arrows={"to": True}, color='salmon')  # dashes=[5,5]
            elif e[2] == 3:
                net.add_edge(e[0], e[1], title="unknown value", arrows={"to": True}, color='lime')  # dashes=[1,10]
            elif e[2] == 4:
                net.add_edge(e[0], e[1], title="end date: " + str(e[3]), arrows={"to": True}, color='grey')

        net.repulsion(
            node_distance=100,
            central_gravity=0.2,
            spring_length=200,
            spring_strength=0.05,
            damping=0.09,
        )

        net.show_buttons(filter_='physics')
        # net.show_buttons(filter_=['nodes', 'edges', 'physics'])

        html = net.generate_html()
        html_file = self.name + ".html"
        with open(html_file, mode='w', encoding='utf-8') as fp:
            fp.write(html)
            fp.close()

        # show network graph
        #return net.show('B2B_network_Wiki.html')

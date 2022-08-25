import matplotlib.pyplot as plt
import plotly.graph_objs as go
from matplotlib.figure import Figure
from sklearn.cluster import KMeans


class Clustering:
    def __init__(self):
        """ the constructor of the class.
            the fields in the class will save the number of clusters and number of runs that eas entered
            by the user. will save the data that the class will cluster
            :param:
            :returns:   """
        self.number_of_clusters = 0
        self.number_of_runs = 0
        self.data = None

    def add_k_runs_data(self, k, runs, data):
        """ add new data to create the clusters
            :param
            :returns:"""
        self.number_of_clusters = k
        self.number_of_runs = runs
        self.data = data

    def k_means(self):
        """ this methode will calculate the K-means od the new processed data.
            will use the KMeans function from the matplotlib library.
            will create the scatter plot with the scatter function from the matplotlib library
            :param
            :returns: a figure of the scatter plot in order to show it to user in the window"""

        fig = Figure(figsize=(4, 4))  # a figure for the scatter plot
        scatter_plt = fig.add_subplot(111)

        new_df = self.data.drop('country', axis=1)
        km = KMeans(n_clusters=self.number_of_clusters, n_init=self.number_of_runs)  # kmeans function
        y_km = km.fit_predict(new_df)
        self.data['cluster'] = list(y_km)

        scatter_plt.scatter(self.data['Generosity'], self.data['Social support'],
                            c=self.data['cluster'], cmap=plt.cm.Dark2)  # scatter plot function
        scatter_plt.set_title("k-means clustering", fontsize=12)
        scatter_plt.set_ylabel("Social support", fontsize=10)
        scatter_plt.set_xlabel("Generosity", fontsize=10)
        return fig

    def create_map(self):
        """ this methode will create the choropleth_map of the new data.
            will use the go.Figure function from the plotly.graph_objs library to create the map
            :param
            :returns: the new map for the user to see in the window"""
        choropleth_map = go.Figure(
            data={
                'type': 'choropleth',
                'locations': self.data['country'],
                'locationmode': 'country names',
                'colorscale': 'Portland',
                'z': self.data['cluster'],
                'colorbar': {'title': 'clusters map'},
                'marker': {
                    'line': {
                        'color': 'rgb(255,255,255)',
                        'width': 2
                    }
                }
            },
            layout={
                'title': 'K-Means Clustering',
                'geo': {
                    'scope': 'world',
                }

            })
        return choropleth_map

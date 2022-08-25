import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


class PreProcessing:
    def __init__(self):
        """ the constructor of the class.
            the fields in the class will save the original data and the new data after pre-processing.
            :param:
            :returns:   """
        self.data = None
        self.new_after_preProcess_data = None

    def add_data(self, data):
        """ add new data to process
            :param
            :returns:"""
        self.data = data

    def fill_na(self):
        """ this methode is used to fill missing values in the dataset.
            each missing value will be filled with the means value of the columns it is in
            will use the SimpleImputer from the sklearn library
            :param
            :returns:"""

        imputer = SimpleImputer(strategy='mean', missing_values=pd.NA)
        cols_na = self.data.apply(lambda x: sum(x.isnull()), axis=0)  # cols_na - what columns have missing values
        for col_name in self.data.columns:
            if cols_na[col_name] != 0:
                imputer = imputer.fit(self.data[[col_name]])
                self.data[col_name] = imputer.transform(self.data[[col_name]])

    def standardization(self):
        """ after filling the missing values this methode will be called to standardize the data
            each missing value will be filled with the means value of the columns it is in
            will use the StandardScaler from the sklearn library only on the numeric columns
            :param
            :returns:"""
        col_names = list(self.data.columns.difference(['country']))
        features = self.data[col_names]
        scaler = StandardScaler().fit(features.values)
        features = scaler.transform(features.values)
        self.data[col_names] = features

    def data_collection(self):
        """ after standardizing the data will run the data collection.
            for every country will calculate the means of every column
            create a new dataset with one row for each country with the new calculated values.
            :param
            :returns: the new dataset"""
        dict_value = {}
        new_df = pd.DataFrame()
        for country in set(self.data['country'].values):
            data = self.data[self.data['country'] == country]
            data = data.drop(labels=['country', 'year'], axis=1)
            data = data.mean(axis=0)  # calculate the means of each column
            dict_value['country'] = [country]
            col_names = list(self.data.columns)
            col_names.remove('year')
            col_names.remove('country')
            for name in col_names:
                dict_value[name] = [data[name]]
            country_df = pd.DataFrame(data=dict_value)
            new_df = pd.concat([new_df, country_df], ignore_index=True, axis=0)
        self.new_after_preProcess_data = new_df
        return self.new_after_preProcess_data

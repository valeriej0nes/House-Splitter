import math
import matplotlib.pyplot as plt
import pandas as pd
import csv
import json
pd.options.display.max_columns = 999

class HousePicker:
    def __init__(self, csv_filepath="House Split (Responses).csv"):
        self.csv_fp = csv_filepath
        self.config_fp = "config.json"
        self.raw_results = []
        self.names = []
        self.pairs = None
        self.numeric_matrix = None
        self.percentage_matrix = None

    def read_results(self):
        print('Reading results')
        with open(self.config_fp, 'r') as file:
            config = json.load(file)

        num_entries = len(config['Results'])
        for header in config['Results']:
            self.raw_results.append(config['Results'][header])

    # Find coordinates for shape
    def find_coords(self, num_vertices, radius):
        angle = 360 / num_vertices

        coords = []
        for i in range(num_vertices):
            x = radius * math.cos(math.radians(i * angle))
            y = radius * math.sin(math.radians(i * angle))
            coords.append([x, y])

        return coords

    def extract_names(self):
        names = []
        for entry in range(len(self.raw_results)):
            for bucket in [0, 1]:
                for i in range(len(self.raw_results[entry][bucket])):
                    if self.raw_results[entry][bucket][i] not in names:
                        names.append(self.raw_results[entry][bucket][i])
        return names

    def generate_pairs(self):
        pairs = []
        for entry in self.raw_results:
            for bucket in entry:
                for i in range(len(bucket)):
                    for j in range(i + 1, len(bucket)):
                        pair = tuple(sorted([bucket[i], bucket[j]]))
                        pairs.append(pair)
        self.pairs = list(pairs)
        return self.pairs

    def raw_to_matrix(self):
        print('Converting to matrix')
        ls_names = self.extract_names()
        df = pd.DataFrame({'Names': ls_names})
        name_to_index = {ls_names[i]: i for i in range(len(ls_names))}
        for name in ls_names:
            df[name] = [0] * len(ls_names)

        pairs = self.pairs
        for pair in pairs:
            df.at[name_to_index[pair[0]], pair[1]] += 1
            df.at[name_to_index[pair[1]], pair[1]] += 1
        self.numeric_matrix = df
        return df

    def generate_percentage_matrix(self):
        print('Creating percentage matrix')
        flattened_list = [name for entry in self.raw_results for bucket in entry for name in bucket]

        ls_names = self.extract_names()
        name_count = {}
        for name in ls_names:
            name_count[name] = sum(name == i_name for i_name in flattened_list)

        df = self.raw_to_matrix()
        for name in ls_names:
            df[name] = round(100 * df[name] / name_count[name], 1)
        self.percentage_matrix = df
        return df

    def assign_points_to_name(self):
        ls_names = self.extract_names()
        ls_points = self.find_coords(num_vertices=len(ls_names), radius=1)

        names_to_vertices = {}
        for i in range(len(ls_names)):
            names_to_vertices[ls_names[i]] = ls_points[i]
        return names_to_vertices

    def pair_count_table(self):
        pairs = self.generate_pairs()

        df = pd.DataFrame(pairs, columns=['Name1', 'Name2'])
        pair_counts = df.value_counts().reset_index(name='Frequency')
        pair_counts['x1'] = pair_counts['Name1'].map(self.assign_points_to_name()).apply(lambda coord: coord[0])
        pair_counts['x2'] = pair_counts['Name2'].map(self.assign_points_to_name()).apply(lambda coord: coord[0])
        pair_counts['y1'] = pair_counts['Name1'].map(self.assign_points_to_name()).apply(lambda coord: coord[1])
        pair_counts['y2'] = pair_counts['Name2'].map(self.assign_points_to_name()).apply(lambda coord: coord[1])

        pair_counts['x'] = pair_counts[['x1', 'x2']].values.tolist()
        pair_counts['y'] = pair_counts[['y1', 'y2']].values.tolist()
        pair_counts.drop(['x1', 'x2', 'y1', 'y2'], axis=1, inplace=True)
        return pair_counts

    def generation(self):
        self.csv_to_config_json()
        self.read_results()
        self.extract_names()
        self.generate_pairs()

    def plot_points(self):
        names = self.extract_names()
        coords = self.find_coords(len(names), 1)
        text_coords = self.find_coords(len(names), 1.15)

        plt.figure(figsize=(6, 6))
        pair_counts = self.pair_count_table()

        for i in range(len(pair_counts['x'])):
            x = pair_counts['x'][i]
            y = pair_counts['y'][i]
            freq = int(pair_counts['Frequency'][i])
            plt.plot(x, y, '-', linewidth=freq, color='dimgray')

        for i in range(len(coords)):
            x = coords[i][0]
            y = coords[i][1]

            xcoeff = text_coords[i][0]
            if y > 0:
                ycoeff = coords[i][1]+0.075
            elif y < 0:
                ycoeff = coords[i][1]-0.075
            else:
                ycoeff = coords[i][1]

            plt.plot(x, y, marker='o', markersize=10)
            plt.text(xcoeff, ycoeff, str(names[i]), horizontalalignment='center', verticalalignment='center', fontsize=9)

        plt.axis='equal'
        ax = plt.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        plt.show()

    def csv_to_config_json(self):
        results = {}
        json_path = "config.json"
        csv_path = self.csv_fp

        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for i, row in enumerate(reader, start=1):  # start=1 for result numbers
                group1 = [name.strip() for name in row['House 1'].split(',')]
                group2 = [name.strip() for name in row['House 2'].split(',')]
                results[str(i)] = [group1, group2]

        output = {"Results": results}

        with open(json_path, "w") as jsonfile:
            json.dump(output, jsonfile, indent=4)

        print(f"Saved JSON config to {json_path}")

if __name__ == '__main__':
    run = HousePicker(csv_filepath="House Split (Responses).csv")
    run.generation()
    print(run.raw_to_matrix())
    print(run.generate_percentage_matrix())
    run.plot_points()
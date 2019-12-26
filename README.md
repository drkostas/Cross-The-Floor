# Parliament Members Flow Viz

A software that given a yml file, it crawls wikipedia tables and creates a Sankey Diagram that shows the flow of parliament members from election to election.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

1. Python 3
1. [Plotly Orca](https://github.com/plotly/orca)

### Installing

##### Installing Plotly Orca
- Method 1: `$ conda install -c plotly plotly-orca`
- Method 1: `$ npm install -g electron@1.8.4 orca`
- Method 1: `$ docker pull quay.io/plotly/orca`

##### Create python virtual environment and source it
```
python3 -m venv myenv
source venv/bin/activate
```

##### Installing the requirements
```
pip install -r requirements.txt
```

##### Run setup.py
```
python setup.up install --force
```

### Running

##### Create a yml configuration file with the following structure

```
source:
  config:
    sources:
      - link: [wikipedia link]
        table_header: [html table header]
        name_col: [Name Column]
        attr_col:
          origin_name: [Parliamentary group column name on wikipedia]
          name_on_plot: [Parliamentary group column name to be shown on on plot]
        ignore_cols:
          - [column name to ignore]
        enclosing_tag: [tag enclosing the table]
      - link: [wikipedia link]
        table_header: [html table header]
        name_col: [Name Column]
        attr_col:
          origin_name: [Parliamentary group column name on wikipedia]
          name_on_plot: [Parliamentary group column name to be shown on on plot]
        ignore_cols:
          - [column name]
        enclosing_tag: [tag enclosing the table]
  type: ParliamentMembersCrawler
target:
  config:
    plot_name: [Output Plot Name]
    target_path: [path in which the plots are going to be saved]
    save_image: [true|false]
    save_html: [true|false]
    color_grouping_type: [party|year|none]
    custom_party_colors: # REQUIRED: color_grouping_type: party
      [Parliamentary group value]: [color hex code]
      [Parliamentary group value]: [color hex code]
      [Parliamentary group value]: [color hex code]
  type: plotly
```

##### Some info about the yml

1. `[wikipedia link]`: Wikipeda page that contains a table with the list of parliament members of some year [[example](https://en.wikipedia.org/wiki/List_of_members_of_the_Hellenic_Parliament,_2015_(September)%E2%80%932019)
1. `[html table header]`: The Table Header
   1. First click `View Page Source` on the wikipedia page
   1. Spot the table with the parliament members
   1. Copy the header of the table - usually it starts with a `<thead>` tag
1. `[Name Column]`: The name of the column that represents the members' names
1. `[Parliamentary group column name on wikipedia]`: The name of the column that represents the parliamentary groups' names
1. `[Parliamentary group column name to be shown on on plot]`: The value with which you want the previous attribute to be replaced on the plot
1. `[column name to ignore]`: If in the _page source_ there is table column with the attribute `colspan="2"`, the add its name here
1. `[tag enclosing the table]`: The tag name that encloses the header along with rest of the table - usually `<table>` or `<tbody>`
1. `[Output Plot Name]`: The name of the plot
1. `[path in which the plots are going to be saved]`: Save path of the plot
1. `[Parliamentary group value]`: The name of the parliament group for which you want a custom color
1. `[color hex code]`: The hex code of the custom color - should be enclosed in double quotes e.g. "#4974BB"

##### Run it

```
parliament_members_sankey -c CONFIG_FILE [-l LOG_FILE] [--debug] [--help]
```
##### or
```
python3 main.py -c CONFIG_FILE [-l LOG_FILE] [--debug] [--help]
```

#### Results
![Greek Elections 2012-Sept 2015-2019](https://github.com/drkostas/Parliament-Members-Flow-Viz/blob/master/plots/Greek%20Elections%202012-Sept%202015-2019.png)
![Greek Elections 2007-2012-Febt 2015-2019](https://github.com/drkostas/Parliament-Members-Flow-Viz/blob/master/plots/Greek%20Elections%202007-2012-Feb%202015-2019.png)

## License

This project is licensed under the GNU General Public License v3.0 License

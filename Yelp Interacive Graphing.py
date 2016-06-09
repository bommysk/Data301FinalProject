
# coding: utf-8

# In[1]:

import pickle
reviews = pickle.load(open("reviewDataFrame(3).p", "rb")) ### Data frame with random reviews



# In[2]:

import json
with open('yelp_academic_dataset_business.json') as f: business = [json.loads(line) for line in f]


# In[3]:

import pandas as pd

id = []
name = []
rating = []
location = []
for i in range(0, len(business)):
    place = business[i]
    id.append(place["business_id"])
    name.append(place["name"])
    rating.append(place["stars"])
    location.append(place["full_address"])
bus_data = pd.DataFrame({"Business Id" : id, "name" : name, "bus_rating" : rating, "location" : location})


# In[4]:

graphing_data = pd.merge(reviews, bus_data, how= "inner", on = "Business Id" ) ### this is for business graphs
user_graph_data = pd.merge(reviews, bus_data, how = "inner", on = "Business Id") ## for user graphs

def review_classify(df_column):
    category = []
    for x in df_column:
        if (x >= 0.0) and (x < 3.0):
            category.append("Low Rating")
        elif (x >= 3.0) and (x < 4.0):
            category.append("Medium Rating")
        else:
            category.append("High Rating")
    return category

def show_mistakes(df):
    df["color_groups"] = df['Rating Category']
    df.loc[df.error != 0, 'color_groups'] = "Incorrect"
    return df

def setupbusgraph(df, busname):
    bool = df["name"] == busname
    df = df[bool]
    cat = review_classify(df["Actual Rating"])
    df["Rating Category"] = cat
    df = df.sort_values("Rating Category")
    return df

def setupusergraph(df, userid):
    bool = df["User Id"] == userid
    df = df[bool]
    cat = review_classify(df["bus_rating"])
    df["Rating Category"] = cat
    df = df.sort_values("Rating Category")
    return df



# In[5]:


def maxgroup(df):
    high = sum(test["Rating Category"] == "High Rating")
    low = sum(test["Rating Category"] == "Low Rating")
    med = sum(test["Rating Category"] == "Medium Rating")
    return max(low,med,high)

def groupmaker(df):    
    nums = []
    for i in range(1 , sum(df["Rating Category"] == "High Rating") + 1):
        nums.append(i)
    for j in range(1 , sum(df["Rating Category"] == "Low Rating") + 1):
        nums.append(j)
    for k in range(1 , sum(df["Rating Category"] == "Medium Rating") + 1):
        nums.append(k)
    df['groups'] = nums
    return df


# In[6]:

from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import figure, show, output_file
from bokeh.sampledata.periodic_table import elements
def restuarant_graph_maker(graphing_data, bus_name):
    rest = setupbusgraph(graphing_data, bus_name) ### get restuaran dataframe set up. 
    rest = groupmaker(rest)
    rest = rest.sort_values("Actual Rating")
    
    ### This is for restaurants ###
    rest["error"] = rest["Actual Rating"] - rest["Guess Rating"]
    rest = show_mistakes(rest)
    rest["Actual Rating"] = rest["Actual Rating"].astype(str)
    rest["Guess Rating"] = rest["Guess Rating"].astype(str)
    rest["error"] = rest["error"].astype(str)
    group_range = [str(x) for x in range(1,max(rest["groups"]) + 1)] ## how many x-ticks
    location = [str(x) for x in rest["location"]]

    ### color map is used to define the colors for grouping, in our case we will have 1-5. We will group restaurants by the
    ### general rating group they fall within. 

    colormap = { 
        "Low Rating"         : "#FEF5D6",
        "Medium Rating"      : "#E39A73",
        "High Rating"        : "#C01400",
        "Incorrect"          : "#E0E0E0"
    }

    source = ColumnDataSource(
        data=dict(
            ## get the categories the for groups, ours will be low, med, high
            period = [str(x) for x in rest["Rating Category"]],
            ## This is the horizontal axis the element falls in 
            group = [str(x) for x in rest["groups"]], ## this line needs to be made dynamic later
            symx = [str(x)+":0.5" for x in rest["Rating Category"]],
            namey= [str(x)+":0.5" for x in rest["groups"]],
            actual_review = rest["Actual Rating"],
            business_rating = rest["bus_rating"],
            business_name = rest["name"],
            display = "Stars : " + rest["Actual Rating"],
            pred_rating = rest["Guess Rating"],
            error = rest["error"],
            text_review = rest["Review Text"],
            #type=elements["metal"],
            type = rest["Rating Category"],
            #type_color=[colormap[x] for x in elements["metal"]],
            type_color=[colormap[x] for x in rest["color_groups"]],
        )
    )

    p = figure(title= bus_name + " Yelp Reviews : " + location[0],tools="resize,hover,save",
               x_range=list(["Low Rating", "Medium Rating", "High Rating", " ", " "]), y_range= group_range )
    p.plot_width = 1000
    p.toolbar_location = "left"
    p.outline_line_color = None
    p.xaxis.axis_line_color = "white"
    p.xaxis.major_tick_line_color = "white"
    p.title_text_align = "left" 
    p.rect("period", "group", .9, .9, source=source,
           fill_alpha=0.9, color="type_color")

    text_props = {
        "source": source,
        "angle": 0,
        "color": "black",
        "text_align": "center",
        "text_baseline": "middle"
    }

    ########### Each of the text takes the coordiantes for where the text goes and the posistioning. 
    #p.text(x="symx", y="period", text="sym",
          #text_font_style="bold", text_font_size="15pt", **text_props)

    #p.text(x="symx", y="numbery", text="atomic_number",
           #text_font_size="9pt", **text_props)

    p.text(x="symx", y="namey", text="display",
           text_font_size="15pt", **text_props)

    #p.text(x="symx", y="massy", text="mass",
           #text_font_size="5pt", **text_props)
    #############################################

    p.grid.grid_line_color = None

    p.select_one(HoverTool).tooltips = [
        ("Text", "@text_review"),
        ("Actual Review", "@actual_review"),
        ("Predicted Review", "@pred_rating"),
        ("error", "@error"),
        
    ]
    p.select_one(HoverTool).point_policy = "follow_mouse"
    p.select_one(HoverTool).mode = 'mouse'

    output_file(bus_name + ".html", title= bus_name + " Summary")
 
    show(p)
    return


# In[7]:

## some example outputs

restuarant_graph_maker(graphing_data, "Pizza Parma")
restuarant_graph_maker(graphing_data, "Golden Buddha")
restuarant_graph_maker(graphing_data, "Taste of India")
restuarant_graph_maker(graphing_data, "Max's Allegheny Tavern")
restuarant_graph_maker(graphing_data, "Alla Famiglia")
restuarant_graph_maker(graphing_data, "Pho Minh")
restuarant_graph_maker(graphing_data, "Page Dairy Mart")
restuarant_graph_maker(graphing_data, "Original Oyster House")




# In[8]:

from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import figure, show, output_file
from bokeh.sampledata.periodic_table import elements
def user_graph_maker(graphing_data, user_name):
    rest = setupusergraph(graphing_data, user_name) ### get user dataframe set up. 
    rest = groupmaker(rest)
    
    ### This is for users ###
    rest["error"] = rest["Actual Rating"] - rest["Guess Rating"]
    rest = show_mistakes(rest)
    rest["Actual Rating"] = rest["Actual Rating"].astype(str)
    rest["Guess Rating"] = rest["Guess Rating"].astype(str)
    rest["bus_rating"] = rest["bus_rating"].astype(str)
    rest["error"] = rest["error"].astype(str)
    group_range = [str(x) for x in range(1,max(rest["groups"]) + 1)] ## how many x-ticks

    ### color map is used to define the colors for grouping, in our case we will have 1-5. We will group restaurants by the
    ### general rating group they fall within. 

    colormap = { 
        "Low Rating"         : "#FEF5D6",
        "Medium Rating"      : "#E39A73",
        "High Rating"        : "#C01400",
        "Incorrect"          : "#E0E0E0"
    }

    source = ColumnDataSource(
        data=dict(
            ## get the categories the for groups, ours will be low, med, high
            period = [str(x) for x in rest["Rating Category"]],
            ## This is the horizontal axis the element falls in 
            group = [str(x) for x in rest["groups"]], ## this line needs to be made dynamic later
            symx = [str(x)+":0.5" for x in rest["Rating Category"]],
            namey = [str(x)+":0.5" for x in rest["groups"]],
            reviewy = [str(x)+":0.25" for x in rest["groups"]],
            actual_review = rest["Actual Rating"],
            business_rating = rest["bus_rating"],
            business_name = rest["name"],
            display = "Avg Rating : " + rest["bus_rating"],
            pred_rating = rest["Guess Rating"],
            error = rest["error"],
            text_review = rest["Review Text"],
            #type=elements["metal"],
            type = rest["Rating Category"],
            #type_color=[colormap[x] for x in elements["metal"]],
            type_color=[colormap[x] for x in rest["color_groups"]],
        )
    )

    p = figure(title= "                     Yelp Reviews From User : " + user_name  ,tools="resize,hover,save",
               x_range=list(["Low Rating", "Medium Rating", "High Rating", " ", " "]), y_range= group_range )
    p.plot_width = 1500
    p.toolbar_location = "left"
    p.outline_line_color = None
    p.xaxis.axis_line_color = "white"
    p.xaxis.major_tick_line_color = "white"
    p.title_text_align = "left" 
    p.rect("period", "group", .9, .9, source=source,
           fill_alpha=0.9, color="type_color")

    text_props = {
        "source": source,
        "angle": 0,
        "color": "black",
        "text_align": "center",
        "text_baseline": "middle"
    }

    #######################################
    p.text(x="symx", y="namey", text="business_name",
           text_font_size="12pt", **text_props)

    p.text(x="symx", y="reviewy", text="display",
           text_font_size="9pt", **text_props)
    #############################################

    p.grid.grid_line_color = None

    p.select_one(HoverTool).tooltips = [
        ("Average Rating", "@business_rating"),
        ("Text", "@text_review"),
        ("Actual Review", "@actual_review"),
        ("Predicted Review", "@pred_rating"),
        ("error", "@error"),
        
    ]
    p.select_one(HoverTool).point_policy = "follow_mouse"
    p.select_one(HoverTool).mode = 'mouse'

    output_file(user_name + ".html", title= user_name + " Summary")
 
    show(p)
    return


# In[9]:

### some example outputs

user_graph_maker(user_graph_data, "So32N7bSbUd1RwhFtI6jTQ")
user_graph_maker(user_graph_data, "iTmWHtltCtk0Gm55AOxrUA")
user_graph_maker(user_graph_data, "zk0SnIEa8ju2iK0mW8ccRQ")
user_graph_maker(user_graph_data, "Q3fFv_ft17OyV-NRF1iQxw")
user_graph_maker(user_graph_data, "86lPnxq14I4n2STeK07FEw")
user_graph_maker(user_graph_data, "q7MrNVt1FE23rwtWmPYWHg")
user_graph_maker(user_graph_data, "nEYPahVwXGD2Pjvgkm7QqQ")
user_graph_maker(user_graph_data, "WzaaorVCmUTQvu4mScunNg")


# In[ ]:




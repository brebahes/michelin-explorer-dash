import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import helpers as hl
from wordcloud import WordCloud
import multidict as multidict
import re


def map(dff: pd.DataFrame, zoom: float, center: tuple, mapstyle: str='basic') -> go.Figure:
    """
    Returns a figure with a plotly scatter map, with each entry in the dataframe represented as a point in the map

    :param dff: Dataframe containing the Michelin Guide restaurants that wants to be plotted
    :return: fig: Plotly figure with the scatter map
    """
    fig = px.scatter_map(data_frame=dff,
                   lat="Latitude",
                   lon="Longitude",
                   color="Award",
                   size="award_size",
                   custom_data="Name",
                   hover_data={"award_size": False},
                   zoom=zoom,
                   center={"lat": center[0], "lon": center[1]},
                   map_style=mapstyle)
    # Updates the legend to include it within the map
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    return fig

def barplot(df: pd.DataFrame, n: int):
    """
    Creates a horizontal bar plot, containing the n-biggest entries sorted by total number of awards

    :param df: Dataframe containing the michelin stars data
    :param n: Number of entries to show
    :return fig: Plotly figure
    """
    df_grouped = df.groupby(by=['City', 'Award'])['Name'].count().reset_index().rename(columns={'Name': 'Count'})
    most_stars = df_grouped.groupby(by='City')['Count'].sum().sort_values(ascending=False)
    threshold = 10
    most_stars = most_stars.index[:threshold]
    fig = px.bar(df_grouped.loc[df_grouped['City'].isin(most_stars)], y="City", x="Count", color="Award",
                  title="Long-Form Input", orientation='h').update_yaxes(categoryorder='total ascending')
    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=0.01,
        xanchor="right",
        x=0.99
    ))
    fig.update_layout(
        title=dict(
            text="<b>Cities</b>",
            subtitle=dict(
                text="Top 10 cities with most restaurants in the Michelin guide",
                font=dict(color="gray", size=13),
            ),
        )
    )
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig

def getFrequencyDictForText(sentence):
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}

    # making dict for counting frequencies
    for text in sentence.split(" "):
        if re.match("a|the|an|the|to|in|for|of|or|by|with|is|on|that|be", text):
            continue
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    for key in tmpDict:
        fullTermsDict.add(key, tmpDict[key])
    return fullTermsDict

def makeImage(text):
    # alice_mask = np.array(Image.open("alice_mask.png"))

    wc = WordCloud(background_color="white", max_words=1000, height=300, width= 1200, scale=3)
    # generate word cloud
    wc.generate_from_frequencies(text)

    # show
    fig = px.imshow(wc)
    fig.update_layout(
        title=dict(
            text="<b>Wordcloud</b>",
            subtitle=dict(
                text="Word cloud of the descriptions of the cuisine of the restaurants\n",
                font=dict(color="gray", size=13),
            ),
        )
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    return fig
def category_wordcloud(df):
    wordslist = df.Cuisine.str.split(',').explode().values
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}

    # making dict for counting frequencies
    for text in wordslist:
        if re.match("a|the|an|the|to|in|for|of|or|by|with|is|on|that|be", text):
            continue
        val = tmpDict.get(text.strip(), 0)
        # if text == 'Contemporary':
        #     print('here')
        #     print(val)
        tmpDict[text.strip()] = val + 1
    for key in tmpDict:
        fullTermsDict.add(key, tmpDict[key])

    return fullTermsDict


if __name__ == '__main__':
    df = hl.load_data()
    makeImage(category_wordcloud(df))
    # fig = barplot(df, 10)
    # fig.show()

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
from embedchain import App
import os
import pandas as pd

def setup_llm():
    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/michelin_by_Jerry_Ng.csv")
    df.iloc[0:100].to_csv('data/data_small.csv')

    print('Loading Token')
    os.environ["HUGGINGFACE_ACCESS_TOKEN"] = "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"
    config = {
        'llm': {
            'provider': 'huggingface',
            'config': {
                'model': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
                'top_p': 0.5
            }
        },
        'embedder': {
            'provider': 'huggingface',
            'config': {
                'model': 'sentence-transformers/all-mpnet-base-v2'
            },
        },
        "app": {
            "config": {
              "id": "your-app-id-3",
            }
        }
    }
    print('Setting App')
    app = App.from_config(config=config)
    print('Adding Data')
    app.add("data/data_small.csv", data_type='csv')
    app.add('https://jlstudiotw.com', data_type='web_page')
    print('Asking question')
    return app

def chat(app):
    while True:
        user_input = input("Ask something (type 'exit' to stop): ")
        if user_input.lower() == 'exit':
            print("Exiting.")
            break
        else:
            print(f"Query: {user_input}")
            answer = app.query(user_input)
            print(f"Answer: {answer}")
def textbox(text, box="AI", name="Philippe"):
    text = text.replace(f"{name}:", "").replace("You:", "")
    style = {
        "max-width": "60%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"

        # thumbnail = html.Img(
        #     src='https://rapids.ai/assets/images/Plotly_Dash_logo.png',
        #     style={
        #         "border-radius": 50,
        #         "height": 36,
        #         "margin-right": 5,
        #         "float": "left",
        #     },
        # )
        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)

        # return html.Div([thumbnail, textbox])
        return html.Div([textbox])

    else:
        raise ValueError("Incorrect option for `box`.")

# Extract the part after 'Answer:'
def extract_answer(response):
    if 'Answer:' in response:
        # Split the string at 'Answer:' and return the part after it
        return response.split('Answer:')[-1].strip()
    return "Answer not found"

if __name__ == '__main__':
    app = setup_llm()
    chat(app)
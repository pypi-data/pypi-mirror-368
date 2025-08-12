import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import json
import random
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import gradio as gr

from cxglearner.parser import Parser
from cxglearner.config import DefaultConfigs, Config
from cxglearner.utils import init_logger
from cxglearner.utils.utils_cxs import convert_slots_to_str

MAX_EXAMPLAR = 8

examples = [
    ["She should be more polite with the customers."],
    ["She said, \"I am tired.\" She said that she was tired."],
    ["The advantage of a bad memory is that one enjoys several times the same good things for the first time."],
]

log_dir = Path(tempfile.gettempdir()) / "cxg"
log_dir.mkdir(exist_ok=True)
config = Config(DefaultConfigs.eng)
config.experiment.log_path = log_dir / "cxg.log"
logger = init_logger(config)

parser_1_0 = Parser(config=config, logger=logger, name_or_path="data/eng/1.0")
examplars_1_0 = json.load(open("data/eng/1.0/learner_examplar_1.0.json", "r", encoding="utf-8"))
parser_1_1 = Parser(config=config, logger=logger, name_or_path="data/eng/1.1")
examplars_1_1 = json.load(open("data/eng/1.1/learner_examplar_1.1.json", "r", encoding="utf-8"))

metadata = {
    "English": {
        "1.0": [parser_1_0, examplars_1_0],
        "1.1": [parser_1_1, examplars_1_1],
    },
    "Chinese": {},
}


def fill_input_box(example):
    return example[0]


def clear_text():
    return "", pd.DataFrame(), gr.Radio(label="Constructions", choices=[]), pd.DataFrame()


def parse_text(text, language, version):
    if not text: 
        return pd.DataFrame(), gr.Radio(label="Constructions", choices=[]), pd.DataFrame()

    print(language, version, text)

    parser = metadata[language][version][0]
    encoded_elements = parser.encoder.encode(text, raw=True)
    tokens, upos, xpos = np.array(encoded_elements["lexical"]), np.array(encoded_elements["upos"]["spaCy"]), np.array(encoded_elements["xpos"]["spaCy"])
    encoded_elements = np.vstack((tokens, upos, xpos))

    radio_parsed = parser.parse(text)
    radio_parsed = ["{} | {} | {}-{}".format(cxs[0],convert_slots_to_str(parser.cxs_decoder[cxs[0]], parser.encoder, logger), cxs[1] + 1, cxs[2]) for cxs in radio_parsed[0]]

    if len(radio_parsed) == 0:
        radio_display = gr.Radio(label="Constructions", choices=[])
    else: 
        radio_display = gr.Radio(label="Constructions", choices=radio_parsed, interactive=True, value=radio_parsed[0])

    if len(radio_parsed) == 0:
        cons_display = pd.DataFrame()
    else:
        cxs = radio_parsed[0]
        index, cxs, ranges = cxs.split("|")
        cxs = cxs.strip()

        examplars = metadata[language][version][1]

        columns_name = cxs

        if version == "1.0":
            cxs = cxs.replace('Ġ', '')
        
        if cxs in examplars:
            exams = random.choices(examplars[cxs], k=min(MAX_EXAMPLAR, len(examplars[cxs])))
            cons_display =  pd.DataFrame(exams, columns=[columns_name])
        else:
            cons_display = pd.DataFrame()
        
    return encoded_elements, radio_display, cons_display


def refresh_examplar(option, language, version):
    
    print(language, version, option)

    index, cxs, ranges = option.split("|")
    index = eval(index)
    cxs = cxs.strip()

    examplars = metadata[language][version][1]

    columns_name = cxs

    if version == "1.0":
        cxs = cxs.replace('Ġ', '')

    if cxs in examplars:
        exams = random.choices(examplars[cxs], k=min(MAX_EXAMPLAR, len(examplars[cxs])))
        return pd.DataFrame(exams, columns=[columns_name])
    
    return pd.DataFrame()


with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown("## CxGLearner Parser")
        with gr.Row():
            input_text = gr.Textbox(label="Input Text", placeholder="Enter a sentence here...")
            
        with gr.Row():
            dataset = gr.Dataset(components=[input_text], samples=examples, label="Make a Choice")
            with gr.Row():
                language_radio = gr.Radio(["English", "Chinese"], value="English", interactive=False, label="Which language would you like to parse?")
                version_radio = gr.Radio(["1.1", "1.0"], value="1.1", interactive=True, label="Which version would you like to use?")
        with gr.Row():
                clear_buttton = gr.Button("Clear")
                parser_button = gr.Button("Parse")

    with gr.Column():
        gr.Markdown("### Results of Encoding and Parsing")
        enc_display = gr.Dataframe()
        cxs_display = gr.Radio(label="Constructions", choices=[])

    with gr.Column():
        gr.Markdown("### Examplars")
        cons_display = gr.Dataframe()

    dataset.click(fn=fill_input_box, inputs=dataset, outputs=input_text)
    clear_buttton.click(fn=clear_text, inputs=[], outputs=[input_text, enc_display, cxs_display, cons_display])
    parser_button.click(fn=parse_text, inputs=[input_text, language_radio, version_radio], outputs=[enc_display, cxs_display, cons_display])
    input_text.submit(fn=parse_text, inputs=[input_text, language_radio, version_radio], outputs=[enc_display, cxs_display, cons_display])
    cxs_display.change(refresh_examplar, inputs=[cxs_display, language_radio, version_radio], outputs=cons_display)


demo.launch()

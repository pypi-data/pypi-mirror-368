# Copyright (c) 2020 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os

from jinja2 import Template

_template = '''
<meta http-equiv="Content-Type"content="text/html;charset=utf-8">
<html align='left'>
<h1>Model Perf Report</h1>
    <body>
    <h2>Model Performance Summary</h2>
    <p>Model Name : {{model_name}}</p>
    <p>BPU Model Latency(ms) : {{latency}}</p>
    <p>Total DDR (loaded + stored) bytes per frame(MB per frame) : {{model_ddr_occupation}} </p>
    <p>Loaded Bytes per Frame : {{loaded_bytes}} </p>
    <p>Stored Bytes per Frame : {{stored_bytes}} </p>
    <p style="color:orange">Note : There are CPU nodes in the model, this part of the time consumption cannot be estimated, so only the time consumption on the BPU is shown </p>
    <h2>Details</h2>
    {% for item in subgraph %}
    <h3>Model Subgraph Item</h3>
    <p>Model Subgraph Name : {{item.name}}</p>
    <p>Model Subgraph Calculation Load (OPpf) : {{item.perf.calc_load}}</p>
    <p>Model Subgraph DDR Occupation(Mbpf) : {{item.perf.DDR_cost}}</p>
    <p>Model Subgraph Latency(ms) : {{item.perf.latency}} </p>
    <p>Model Subgraph Info Files : <a href={{item.filename}}> {{item.name}} Detail</a> </p>
    {% endfor%}
    <h2>BIN Model Structure</h2>
    <a name="bin model structure"> <img src="{{ image_path }}" width="640"></a>
    </body>
</html>
''' # noqa

_template_internal_detail = '''
<meta http-equiv="Content-Type"content="text/html;charset=utf-8">
<html align='left'>
<h1>Model Perf Report</h1>
    <body>
    <h2>Model Performance Summary</h2>
    <p>Model Name : {{model_name}}</p>
    <p>BPU Model Latency(ms) : {{latency}}</p>
    <p>Total DDR (loaded + stored) bytes per frame(MB per frame) : {{model_ddr_occupation}} </p>
    <p>Loaded Bytes per Frame : {{loaded_bytes}} </p>
    <p>Stored Bytes per Frame : {{stored_bytes}} </p>
    <p>BPU conv original (BPU OPs per frame) : {{conv_original}}</p>
    <p>BPU conv working (BPU OPs per frame) : {{conv_working}}</p>
    <h2>Details</h2>
    {% for item in subgraph %}
    <h3>Model Subgraph Item</h3>
    <p>Model Subgraph Name : {{item.name}}</p>
    <p>Model Subgraph Calculation Load (OPpf) : {{item.perf.calc_load}}</p>
    <p>Model Subgraph DDR Occupation(Mbpf) : {{item.perf.DDR_cost}}</p>
    <p>Model Subgraph Latency(ms) : {{item.perf.latency}} </p>
    <p>Model Subgraph Info Files : <a href={{item.filename}}> {{item.name}} Detail</a> </p>
    {% endfor%}
    <h2>BIN Model Structure</h2>
    <a name="bin model structure"> <img src="{{ image_path }}" width="640"></a>
    </body>
</html>
''' # noqa


def generate_html(info_dict: dict,
                  output_file: str,
                  internal_detail=False) -> None:
    template = Template(_template)
    logging.info("generating html...")
    latency = 0
    ddr = 0
    loaded_byte = 0
    stored_byte = 0
    conv_working = 0
    conv_original = 0
    img_path = os.path.basename(output_file).split(".")[0]
    image_name = img_path + ".png"

    for graph in info_dict.get("subgraph_list", []):
        latency += graph["perf"]["latency"]
        ddr += graph["perf"]["DDR_cost"]
        loaded_byte += graph["perf"]["loaded_byte"]
        stored_byte += graph["perf"]["stored_byte"]
        conv_working += graph["perf"]["conv_working"]
        conv_original += graph["perf"]["conv_original"]
    if not output_file.endswith(".html"):
        output_file = output_file + ".html"

    with open(output_file, 'w+') as fout:
        html_content = template.render(
            model_name=info_dict.get("model_name", "model_name"),
            latency="%.2f" % latency,
            model_ddr_occupation="%.2f" % ddr,
            loaded_bytes=loaded_byte,
            stored_bytes=stored_byte,
            conv_working=conv_working,
            conv_original=conv_original,
            subgraph=info_dict.get("subgraph_list", None),
            image_path=image_name)
        fout.write(html_content)
    logging.info("html generation finished.")
    logging.info(f"file stored at : {os.path.abspath(output_file)}")

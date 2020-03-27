import json

# get json file from score web interface
from scorelib.converter import Converter

from parsers.score_project_json import JSONTest, convert_json
from scripts.score_solver import ScoreSolver

with open("./scripts/score_projects/project476.json", 'r', encoding="latin-1") as f:
    data = json.load(f)

instance = JSONTest()
instance.input = convert_json(data)

project = Converter.to_lccv_project(instance)

ss = ScoreSolver(project=project)
cementing_result = ss.solve_cementing_load(casing_string_id=2)
print(cementing_result.get_api_collapse_safety_factor())

# resolver cardápio agora

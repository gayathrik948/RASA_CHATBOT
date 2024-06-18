import re

def is_given_term_present(section, given_term):
    if re.search(given_term, section, re.IGNORECASE):
        return True
    return False

section = "What is dollar percentage amount employee received on On Call Pay in 2022?"
given_term = "Dollar Percentage"
print(is_given_term_present(section, given_term))

import yaml

with open("/home/xpms/Desktop/Rasa_3.0/hr_portal/data/nlu.yml", "r") as file:
    data = yaml.safe_load(file)
data = data['nlu']
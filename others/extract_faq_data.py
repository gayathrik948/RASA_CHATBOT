import json
import pandas as pd

from pymongo import MongoClient

USE_CASE = "hr_portal"


def fetch_faq_data(file_path: str) -> bool:
    """
    This function Extract Faq questions from ecxel sheet
    :param file_path:
    :return:
    """
    file = pd.ExcelFile(file_path, engine='openpyxl')
    sheets = file.sheet_names
    faq = pd.DataFrame()

    # Loop Sheet wise
    for sheet in sheets:
        temp = file.parse(sheet)
        # Handle for if sheet contains empty data
        if temp.shape[0] >= 1:
            temp.columns = temp.columns.str.lower().str.strip()
            columns_list = temp.columns
            print(sheet, "-", list(columns_list))
            required_columns_list = ['qn no', 'intent', 'question', 'rephrases', 'keyphrase', 'synonym for', 'action',
                                     'response', 'module name']

            # check the required columns format
            if set(required_columns_list).issubset(set(columns_list)):
                temp = temp.rename(columns=str.lower)
                temp_columns = [i for i in temp.columns if 'unnamed' not in i]
                temp = temp[temp_columns]
                temp = temp.dropna(how='all')
                temp['sheet_name'] = sheet
                temp[['qn no', 'intent', 'question']] = temp[['qn no', 'intent', 'question']].fillna(method='ffill')
                faq = faq.append(temp)

            else:
                continue

    if not faq.empty:
        fomated_faq_list = []
        faq_grouped_df = faq.groupby(['question', 'keyphrase', 'response'])
        for name, group in faq_grouped_df:
            faq_dict = dict()
            faq_dict['intent'] = list(set(list(group['intent'])))
            faq_dict['question'] = name[0]
            faq_dict['rephrases'] = list(set(list(group['rephrases'])))
            faq_dict['keyphrase'] = name[1]
            faq_dict['synonym for'] = list(set(list(group['synonym for'])))
            faq_dict['action'] = list(set(list(group['action'])))
            faq_dict['module name'] = list(group['module name'])[0]
            faq_dict['response'] = name[2]
            faq_dict['use_case'] = USE_CASE
            fomated_faq_list.append(faq_dict)

        final_faq_df = pd.DataFrame(fomated_faq_list)
        final_faq_df['keyphrase'] = final_faq_df['keyphrase'].astype(str)
        final_faq_df['question'] = final_faq_df['question'].astype(str)
        final_faq_df['module name'] = final_faq_df['module name'].apply(lambda x: x.lower())
        final_faq_df['keyphrase_lower'] = final_faq_df['keyphrase'].apply(lambda x: x.lower())
        final_faq_df['question_lower'] = final_faq_df['question'].apply(lambda x: x.lower())
        final_faq_df['use_case'] = USE_CASE
        final_faq_df = final_faq_df.fillna("unknown")
        final_faq_df = final_faq_df.to_dict(orient='rows')

        client = MongoClient('localhost', 27017)
        db = client["Rasa_chatbots"]
        db.faq.insert_many(final_faq_df)
        # with open("faq.json", "w") as file:
        #     json.dump(final_faq_df, file)

        return True
    else:
        return False


if __name__ == "__main__":
    file_path = "Round 1 of questions Frozen.xlsx"
    fetch_faq_data(file_path)


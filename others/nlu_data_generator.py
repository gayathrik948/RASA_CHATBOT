import pandas as pd

USE_CASE = "hr_portal"


def fetch_faq_data(file_path: str) -> bool:
    """

    :param file_path:
    :return:
    """
    lookup_keyphrase_list =[]
    nlu_questions = []
    manual_check_questions = []

    file = pd.ExcelFile(file_path, engine='openpyxl')
    sheets = file.sheet_names
    faq = pd.DataFrame()
    for sheet in sheets:
        temp = file.parse(sheet)
        # Handle for if sheet contains empty data
        if temp.shape[0] >= 1:
            temp = temp.rename(columns=str.lower)
            temp = temp[['question',  'keyphrase', 'rephrases']]
            temp = temp.fillna(method='ffill')
            temp = temp.drop_duplicates()
            for index, row in temp.iterrows():
                question = row['question']
                rephrases = row['rephrases']
                keyphrase = row['keyphrase']
                #
                if keyphrase.lower() in rephrases.lower():
                    idx1 = rephrases.lower().index(keyphrase.lower())
                    # [EMR100070_007](study_number)
                    idx2 = idx1+len(keyphrase)
                    nlu_question = rephrases[:idx1] +"[{}](keyphrase)".format(keyphrase)+ rephrases[idx2:]
                    nlu_questions.append(nlu_question)
                    lookup_keyphrase_list.append(keyphrase)
                    #todo create nlu train question
                    if keyphrase.lower() in question.lower():
                        idx1 = question.lower().index(keyphrase.lower())
                        # [EMR100070_007](study_number)
                        idx2 = idx1 + len(keyphrase)
                        nlu_question = question[:idx1] + "[{}](keyphrase)".format(keyphrase) + question[idx2:]
                        nlu_questions.append(nlu_question)
                        lookup_keyphrase_list.append(keyphrase)
                    pass
                else:
                    manual_check_questions.append("{} - ({})".format(rephrases,keyphrase))

    # Generating Keyphrase
    file = open('lookup_keyphrase.txt', 'w')
    for key in set(lookup_keyphrase_list):
        file.write("-{}".format(key) + "\n")
    file.close()

    # Generating Keyphrase
    file = open('nlu_data.txt', 'w')
    for que in set(nlu_questions):
        file.write("-{}".format(que) + "\n")
    file.close()

    # Generating Keyphrase
    file = open('manual_review.txt', 'w')
    for m_que in set(manual_check_questions):
        file.write("-{}".format(m_que) + "\n")
    file.close()

    print(manual_check_questions)
    return True

"What is dollar percentage amount employee received on On Call Pay in 2022? - (Dollar Percenatge)"


if __name__ == "__main__":
    file_path = "Round1_Questions_Frozen_old.xlsx"
    fetch_faq_data(file_path)


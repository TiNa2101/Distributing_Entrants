import pandas as pd

#============================================================================================================
# ФУНКЦИЯ ЧТЕНИЯ ДАННЫХ ИЗ ФАЙЛА

def read_data_exel(filename):

    preferences_stud = pd.read_excel(filename, sheet_name = "Preferences_Stud")

    quotas = []
    columns = list(preferences_stud)
    for spec_i in range(len(columns)):
        if spec_i >= 1:
            begin = columns[spec_i].find("(") + 1
            end = columns[spec_i].find(")")
            quotas.append(int(columns[spec_i][begin : end]))
            preferences_stud = preferences_stud.rename(columns = {columns[spec_i] : columns[spec_i][: begin-2]})

    speciality_col = list(preferences_stud)[1:]

    entr = []
    for i in range(len(preferences_stud["Entrants"])):
        entr.append([preferences_stud["Entrants"][i], 1])

    preferences_stud["Entrants"] = entr

    distrib = {}
    arr_d = []

    distrib = {s: arr_d for s in range(len(speciality_col))}
    
    preferences_spec = pd.read_excel(filename, sheet_name = "Preferences_Spec")
    scores = pd.read_excel(filename, sheet_name = "Scores")

    return preferences_stud, preferences_spec, scores, distrib, speciality_col, quotas

#============================================================================================================
# СОРТИРОВКА

def my_sort(smth_1, smth_2, true_or_false, flag):
    temp = zip(smth_1, smth_2)
    temp_temp = sorted(temp, key=lambda tup: tup[0], reverse=true_or_false)

    if flag == 1:

        temp_temp_temp = temp_temp.copy()
        for i in range(len(temp_temp)):
            if temp_temp[i][0] == 0:
                temp_temp_temp.remove(temp_temp[i])
        temp_temp = temp_temp_temp.copy()

    smth_1 = [temp[0] for temp in temp_temp]
    smth_2 = [temp[1] for temp in temp_temp]

    return smth_1, smth_2

#============================================================================================================
# ФУНКЦИЯ РАСПРЕДЕЛЕНИЯ

def Distribution(preferences_stud, preferences_spec, scores, distrib, speciality_col, quotas):

    # массив еще не зачисленных абитуриентов
    not_stud = []
    for i in range(len(preferences_stud["Entrants"])):
        not_stud.append(i)
    not_stud

    rejected_entrants = []

    passing_score = []
    for i in range(len(speciality_col)): 
        passing_score.append([] * len(speciality_col))

    temp_arr_en = []
    while len(not_stud) != 0:

        for spec in range(len(speciality_col)):

            temp_arr_en = distrib[spec].copy()
            temp_arr_sc = []
            if len(temp_arr_en) != 0:
                for i in temp_arr_en:
                    sum = 0
                    for subj in range(len(preferences_spec["Subjects"])):
                        if preferences_spec[speciality_col[spec]][subj] != 0:
                            sum += scores.loc[i][subj+1]
                    temp_arr_sc.append(sum)

            for entr in range(len(preferences_stud["Entrants"])):

                if entr in not_stud:
                    if preferences_stud.loc[entr]["Entrants"][1] > preferences_stud[speciality_col].loc[entr].max():
                        rejected_entrants.append(entr)
                        not_stud.remove(entr)

                    elif preferences_stud.loc[entr][speciality_col[spec]] == preferences_stud.loc[entr]["Entrants"][1]:
                        temp_arr_en.append(entr)
                        sum = 0
                        for subj in range(len(preferences_spec["Subjects"])):
                            if preferences_spec[speciality_col[spec]][subj] != 0:
                                sum += scores.loc[entr][subj+1]
                        temp_arr_sc.append(sum)
                        not_stud.remove(entr)

            temp_arr_sc, temp_arr_en = my_sort(temp_arr_sc, temp_arr_en, True, 0)

            while len(temp_arr_en) > quotas[spec]:

                minimum = temp_arr_sc.count(min(temp_arr_sc))

                if minimum > 1:

                    trash, rating_subj = my_sort(preferences_spec[speciality_col[spec]], preferences_spec["Subjects"], False, 1)

                    real_minimum_en = -1

                    for subj in rating_subj:
                        comparison_sc = []
                        comparison_en = []
                        for i in range(1, minimum + 1):
                            comparison_sc.append(scores.loc[temp_arr_en[i*(-1)]][subj])
                            comparison_en.append(temp_arr_en[i*(-1)])
                            
                        if comparison_sc.count(min(comparison_sc)) == 1:

                            comparison_sc, comparison_en = my_sort(comparison_sc, comparison_en, True, 0)

                            real_minimum_en = comparison_en[-1]

                            break

                    not_stud.append(real_minimum_en)
                    preferences_stud.loc[real_minimum_en]["Entrants"][1] += 1
                    temp_arr_en.remove(real_minimum_en)
                    temp_arr_sc.pop(-1)

                else:
                    not_stud.append(temp_arr_en[-1])
                    preferences_stud.loc[temp_arr_en[-1]]["Entrants"][1] += 1
                    temp_arr_en.pop(-1)
                    temp_arr_sc.pop(-1)
        
            passing_score[spec] = temp_arr_sc[-1]
            
            distrib[spec] = temp_arr_en

        # print(preferences_stud)
        # print("\n")
        # print(distrib)
        # print("\n")

    return distrib, passing_score, rejected_entrants

#============================================================================================================
# ВЫВОД РЕЗУЛЬТАТА

def print_result(preferences, distrib, speciality_col, passing_score, rejected_entrants):

    print(f"\nПОЛУЧЕННОЕ РАСПРЕДЕЛЕНИЕ:\n\n{distrib}\n")
    
    for spec in range(len(speciality_col)):
        name_spec = speciality_col[spec]
    
        names_entr = ""
        for entr in range(len(distrib[spec])):
            if entr == len(distrib[spec]) - 1:
                names_entr += preferences["Entrants"][distrib[spec][entr]][0]
            else:
                names_entr += preferences["Entrants"][distrib[spec][entr]][0] + ", "

        print(f"На специальность {name_spec} зачислены следующие студенты: {names_entr} (Проходной балл - {passing_score[spec]})")

    if len(rejected_entrants) == 0:
        print("\nНепоступивших абитуриентов нет!")
    else:
        names_rej = ""
        for rej in range(len(rejected_entrants)):
            if rej == len(rejected_entrants) - 1:
                names_rej += preferences["Entrants"][rejected_entrants[rej]][0]
            else:
                names_rej += preferences["Entrants"][rejected_entrants[rej]][0] + ", "

        print(f"\nНепоступившие абитуриенты: {names_rej}")

#============================================================================================================
# ТЕСТЫ

print("\nTEST 1:\n")

preferences_stud_1, preferences_spec_1, scores_1, distrib_1, speciality_col_1, quotas_1 = read_data_exel("test1.xlsx")

print(f"КВОТЫ СПЕЦИАЛЬНОСТЕЙ: {quotas_1}\n")
print(f"ТАБЛИЦА ПРИОРИТЕТОВ АБИТУРИЕНТОВ:\n\n{preferences_stud_1}\n")
print(f"ТАБЛИЦА ПРИОРИТЕТОВ СПЕЦИАЛЬНОСТЕЙ:\n\n{preferences_spec_1}\n")
print(f"БАЛЛЫ АБИТУРИЕНТОВ:\n\n{scores_1}")

distrib_1_result, passing_score_1, rejected_entrants_1 = Distribution(preferences_stud_1, preferences_spec_1, scores_1, distrib_1, speciality_col_1, quotas_1)

print_result(preferences_stud_1, distrib_1_result, speciality_col_1, passing_score_1, rejected_entrants_1)

#============================================================================================================

print("\nTEST 2:\n")

preferences_stud_2, preferences_spec_2, scores_2, distrib_2, speciality_col_2, quotas_2 = read_data_exel("test2.xlsx")

print(f"КВОТЫ СПЕЦИАЛЬНОСТЕЙ: {quotas_2}\n")
print(f"ТАБЛИЦА ПРИОРИТЕТОВ АБИТУРИЕНТОВ:\n\n{preferences_stud_2}\n")
print(f"ТАБЛИЦА ПРИОРИТЕТОВ СПЕЦИАЛЬНОСТЕЙ:\n\n{preferences_spec_2}\n")
print(f"БАЛЛЫ АБИТУРИЕНТОВ:\n\n{scores_2}")

distrib_2_result, passing_score_2, rejected_entrants_2 = Distribution(preferences_stud_2, preferences_spec_2, scores_2, distrib_2, speciality_col_2, quotas_2)

print_result(preferences_stud_2, distrib_2_result, speciality_col_2, passing_score_2, rejected_entrants_2)

#============================================================================================================

print("\nTEST 3:\n")

preferences_stud_3, preferences_spec_3, scores_3, distrib_3, speciality_col_3, quotas_3 = read_data_exel("test3.xlsx")

print(f"КВОТЫ СПЕЦИАЛЬНОСТЕЙ: {quotas_3}\n")
print(f"ТАБЛИЦА ПРИОРИТЕТОВ АБИТУРИЕНТОВ:\n\n{preferences_stud_3}\n")
print(f"ТАБЛИЦА ПРИОРИТЕТОВ СПЕЦИАЛЬНОСТЕЙ:\n\n{preferences_spec_3}\n")
print(f"БАЛЛЫ АБИТУРИЕНТОВ:\n\n{scores_3}")

distrib_3_result, passing_score_3, rejected_entrants_3 = Distribution(preferences_stud_3, preferences_spec_3, scores_3, distrib_3, speciality_col_3, quotas_3)

print_result(preferences_stud_3, distrib_3_result, speciality_col_3, passing_score_3, rejected_entrants_3)

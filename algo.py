import pandas as pd
import numpy as np
from scipy import spatial
class Algo():
  def __init__(self):
        pass
  def master_function(self, user1,user2):
    #Majors
    def major_vectorizer(major1,major2):
        dept = pd.read_csv('department.csv')
        dept.set_index('Unnamed: 0',inplace=True)
        return (dept.loc[major1].get(major2) + dept.loc[major2].get(major1)) / 2

    #Minors
    def minor_vectorizer(minor1,minor2):
        dept = pd.read_csv('department.csv')
        dept.set_index('Unnamed: 0',inplace=True)
        return (dept.loc[minor1].get(minor2) + dept.loc[minor2].get(minor1)) / 2

    #Academic Interests 

    #Reads csv file
    academic_interests = pd.read_csv('data_academic.csv').set_index('Options')

    #Academic Interest Vectorizer function takes a query and returns a embedded vector based on number of options
    #in each category
    def academic_interests_vectorizer(query):
        
        #All the categories for academic interests 
        categories = {"Business": 0, "Engineering": 0, "Humanities": 0, "Science": 0, "Tech": 0}

        #Checks every interest in query to see which category it belongs in and increase categories dictionary by 1 
        #for corresponding category
        for interest in query:
            name = academic_interests.loc[interest].get('Category')
            categories[name] += 1
        
        category_total = academic_interests.groupby(['Category']).count()['Sub-Category'].tolist()
        vector = []

        #Populates the embedded vector based on dictionary "categories" that holds number of interests
        #for each category based on user query
        for category in categories:
            index = 0
            vector.append(categories[category]/category_total[index])
            index += 1

        #Creates list for categories that have nonzero values
        non_zero_dic = {x:y for x,y in categories.items() if y!=0}
        dic_sorted = sorted(non_zero_dic, key=non_zero_dic.get, reverse=True)
        return vector, dic_sorted

    #Academic Interest Distance function takes two queries and returns a distance between them, along
    #with any similarities that are shared between the queries
    def academic_interests_distance(query1, query2):
        #Checking categorical matches
        category1 = academic_interests_vectorizer(query1)
        category2 = academic_interests_vectorizer(query2)
        category_matches = (1 - spatial.distance.cosine(category1[0], category2[0])) * 0.2

        #Checking sub-category matches
        sub_category1 = []
        sub_category2 = []
        for interest1, interest2 in zip(query1, query2):
            sub_category1.append(academic_interests.loc[interest1].get('Sub-Category'))
            sub_category2.append(academic_interests.loc[interest2].get('Sub-Category'))

        sub_category_matches1 = (len([value for value in sub_category1 if value in sub_category2]) / len(sub_category1)) * 0.3
        sub_category_matches2 = (len([value for value in sub_category2 if value in sub_category1]) / len(sub_category2)) * 0.3
        sub_category_matches = max(sub_category_matches1, sub_category_matches2)

        #Checking exact_matches
        exact_matches1 = (len([value for value in query1 if value in query2]) / len(query1)) * 0.5
        exact_matches2 = (len([value for value in query2 if value in query1]) / len(query2)) * 0.5
        exact_matches = max(exact_matches1, exact_matches2)

        #Checks queries for exact matches to get rid of potential repetitions, and store matched values 
        if exact_matches1 > exact_matches2:
            match_names = [value for value in query1 if value in query2]
        else:
            match_names = [value for value in query2 if value in query1]

        #If no exact matches, check if categorical matches match and store them in value to return at the end
        if match_names == []:
            category_matches1 = len([value for value in category1[1] if value in category2[1]])
            category_matches2 = len([value for value in category2[1] if value in category1[1]])

            if category_matches1 > category_matches2:
                match_names = [value for value in category1[1] if value in category2[1]]
            else:
                match_names = [value for value in category2[1] if value in category1[1]]

        #Calculating similarity score based on categorical, sub-categorical, and exact matches
        result = category_matches + sub_category_matches + exact_matches

        return result, match_names

    #Non Academic Interests

    #Read csv file
    nonacademic_interests = pd.read_csv('nonacademic_interests.csv')

    #Nonacademic Interest Vectorizer takes a query and returns a embedded vector based on number of options
    #in each category
    def nonacdemic_interest_vectorizer(query):
        vector = {}
        for index,name in enumerate(nonacademic_interests.columns):
            vector[name] = 0
            nonacademic_interest_vals = [nonacademic_interest.strip() for nonacademic_interest in list(nonacademic_interests.get(name).dropna())]
            for value in query:
                if value.strip() in nonacademic_interest_vals:
                    vector[name] = vector[name]+1
            dic = vector
            non_zero_dic = {x:y for x,y in dic.items() if y!=0}
            dic_sorted = sorted(non_zero_dic, key=non_zero_dic.get, reverse=True)
            vector[name] = vector[name]/len(nonacademic_interest_vals)
        return list(vector.values()), dic_sorted

    #Nonacademic Interest Distance function takes two queries and returns a distance between them, along
    #with any similarities that are shared between the queries
    def nonacademic_interests_distance(query1, query2):
        #Checks categorical matches
        nonacademic_interest1 = nonacdemic_interest_vectorizer(query1)
        nonacademic_interest2 = nonacdemic_interest_vectorizer(query2)
        category_matches = (1 - spatial.distance.cosine(nonacademic_interest1[0], nonacademic_interest2[0])) * 0.4

        #Check exact matches
        exact_matches1 = (len([value for value in query1 if value in query2]) / len(query1)) * 0.6
        exact_matches2 = (len([value for value in query2 if value in query1]) / len(query2)) * 0.6
        exact_matches = max(exact_matches1, exact_matches2)

        #Checks queries for exact matches to get rid of potential repetitions, and store matched values 
        if exact_matches1 > exact_matches2:
            match_names = [value for value in query1 if value in query2]
        else:
            match_names = [value for value in query2 if value in query1]

        #If no exact matches, check if categorical matches match and store them in value to return at the end
        if match_names == []:
            category_matches1 = len([value for value in nonacademic_interest1[1] if value in nonacademic_interest2[1]])
            category_matches2 = len([value for value in nonacademic_interest2[1] if value in nonacademic_interest1[1]])

            if category_matches1 > category_matches2:
                match_names = [value for value in nonacademic_interest1[1] if value in nonacademic_interest2[1]]
            else:
                match_names = [value for value in nonacademic_interest2[1] if value in nonacademic_interest1[1]]

        result = category_matches + exact_matches
        
        return result, match_names

    #Personalities

    personalities = pd.read_csv('personality.csv')

    #Personality Vectorizer function takes a query and returns a embedded vector based on number of options
    #in each category
    def personalities_vectorizer(query):
        vector = {}
        for index,name in enumerate(personalities.columns):
            vector[name] = 0
            personality_vals = [personality.strip() for personality in list(personalities.get(name).dropna())]
            for value in query:
                if value.strip() in personality_vals:
                    vector[name] = vector[name]+1
            vector[name] = vector[name]/len(personality_vals)
        return list(vector.values())

    #Personality Distance function takes two queries and returns a distance between them, along
    #with any similarities that are shared between the queries
    def personalities_distance(query1, query2):
        List1 = personalities_vectorizer(query1)
        List2 = personalities_vectorizer(query2)
        #Categorical matches
        category_matches = (1 - spatial.distance.cosine(List1, List2)) * 0.4

        #Exact matches
        exact_matches1 = (len(list(set(query1).intersection(query2))) / len(query1)) * 0.6
        exact_matches2 = (len(list(set(query2).intersection(query1))) / len(query2)) * 0.6
        exact_matches = max(exact_matches1, exact_matches2)

        #Checks queries for exact matches to get rid of potential repetitions, and store matched values 
        if exact_matches1 > exact_matches2:
            match_names = [value for value in query1 if value in query2]
        else:
            match_names = [value for value in query2 if value in query1]

        result = category_matches + exact_matches
        return result, match_names

    #Skills

    skills = pd.read_csv('skills.csv')

    #Skill Vectorizer function takes a query and returns a embedded vector based on number of options
    #in each category
    def skill_vectorizer(query):
        vector = {}
        for index,name in enumerate(skills.columns):
            vector[name] = 0
            skill_vals = [skill.strip() for skill in list(skills.get(name).dropna())]
            for value in query:
                if value.strip() in skill_vals:
                    vector[name] = vector[name]+1
            dic = vector
            non_zero_dic = {x:y for x,y in dic.items() if y!=0}
            dic_sorted = sorted(non_zero_dic, key=non_zero_dic.get, reverse=True)
            vector[name] = vector[name]/len(skill_vals)
        return list(vector.values()), dic_sorted

    #Skill Distance function takes two queries and returns a distance between them, along
    #with any similarities that are shared between the queries
    def skill_distance(query1, query2):
        #Categorical matches
        skill1 = skill_vectorizer(query1)
        skill2 = skill_vectorizer(query2)
        category_matches = (1 - spatial.distance.cosine(skill1[0], skill2[0])) * 0.4

        #Exact matches
        exact_matches1 = (len([value for value in query1 if value in query2]) / len(query1)) * 0.6
        exact_matches2 = (len([value for value in query2 if value in query1]) / len(query2)) * 0.6
        exact_matches = max(exact_matches1, exact_matches2)

        #Checks queries for exact matches to get rid of potential repetitions, and store matched values 
        if exact_matches1 > exact_matches2:
            match_names = [value for value in query1 if value in query2]
        else:
            match_names = [value for value in query2 if value in query1]

        #If no exact matches, check if categorical matches match and store them in value to return at the end
        if match_names == []:
            category_matches1 = len([value for value in skill1[1] if value in skill2[1]])
            category_matches2 = len([value for value in skill2[1] if value in skill1[1]])

            if category_matches1 > category_matches2:
                match_names = [value for value in skill1[1] if value in skill2[1]]
            else:
                match_names = [value for value in skill2[1] if value in skill1[1]]

        result = category_matches + exact_matches
        
        return result, match_names

    #Careers

    careers = pd.read_csv('career_interests.csv')

    #Career Vectorizer function takes a query and returns a embedded vector based on number of options
    #in each category
    def career_vectorizer(query):
        vector = {}
        for index,name in enumerate(careers.columns):
            vector[name] = 0
            career_vals = [career.strip() for career in list(careers.get(name).dropna())]
            for value in query:
                if value.strip() in career_vals:
                    vector[name] = vector[name]+1
            dic = vector
            non_zero_dic = {x:y for x,y in dic.items() if y!=0}
            dic_sorted = sorted(non_zero_dic, key=non_zero_dic.get, reverse=True)
            vector[name] = vector[name]/len(career_vals)
        return list(vector.values()), dic_sorted

    #Skill Distance function takes two queries and returns a distance between them, along
    #with any similarities that are shared between the queries
    def career_distance(query1, query2):
        #Categorical matches
        career1 = career_vectorizer(query1)
        career2 = career_vectorizer(query2)
        category_matches = (1 - spatial.distance.cosine(career1[0], career2[0])) * 0.3

        #Exact matches
        exact_matches1 = (len([value for value in query1 if value in query2]) / len(query1)) * 0.7
        exact_matches2 = (len([value for value in query2 if value in query1]) / len(query2)) * 0.7
        exact_matches = max(exact_matches1, exact_matches2)

        #Checks queries for exact matches to get rid of potential repetitions, and store matched values 
        if exact_matches1 > exact_matches2:
            match_names = [value for value in query1 if value in query2]
        else:
            match_names = [value for value in query2 if value in query1]

        #If no exact matches, check if categorical matches match and store them in value to return at the end
        if match_names == []:
            category_matches1 = len([value for value in career1[1] if value in career2[1]])
            category_matches2 = len([value for value in career2[1] if value in career1[1]])

            if category_matches1 > category_matches2:
                match_names = [value for value in career1[1] if value in career2[1]]
            else:
                match_names = [value for value in career2[1] if value in career1[1]]

        result = category_matches + exact_matches
        
        return result, match_names


    #Traits Questions

    def trait_difference(score1, score2):
        diff = []
        score1_cleaned = [int(s) for s in score1]
        score2_cleaned = [int(s) for s in score2]
        for score_1, score_2 in zip(score1_cleaned, score2_cleaned):
            diff.append(100 - abs(score_1 - score_2))
        return (sum(diff) / len(diff)) / 100

    
    # Calling final algo

    similarities = []
    if 'major' in user1.keys() and 'major' in user2.keys():
        if len(user1['major'])>0 and len(user2['major'])>0:
            major_similarity_score = major_vectorizer(user1['major'][0],user2['major'][0])
            if (major_similarity_score > 0.85):similarities.append(['Major: '+str(user2['major'][0])])
    if 'minor'  in user1.keys() and 'minor' in user2.keys():
        if len(user1['minor'])>0 and len(user2['minors'])>0:
            minor_similarity_score = minor_vectorizer(user1['minor'][0],user2['minor'][0])
            if (minor_similarity_score > 0.95): similarities.append(['Minor: '+str(user1['minor'][0])])
    
         
    
    academic_interest_similarity = academic_interests_distance(user1['academicInterests'], user2['academicInterests'])
    nonacademic_interest_similarity = nonacademic_interests_distance(user1['leisureInterests'], user2['leisureInterests'])
    career_similarity = career_distance(user1['careerGoals'], user2['careerGoals'])
    skill_similarity = skill_distance(user1['skills'], user2['skills'])
    personality_similarity =  personalities_distance(user1['selfDescription'], user2['selfDescription'])

    academic_interest_similarity_score = academic_interest_similarity[0]
    nonacademic_interest_similarity_score = nonacademic_interest_similarity[0]
    career_similarity_score = career_similarity[0]
    skill_similarity_score = skill_similarity[0]
    personality_similarity_score = personality_similarity[0]
    trait_similarity_score = trait_difference(user1['situationalDecisions'], user2['situationalDecisions'])

    embedded_vector = np.array([major_similarity_score, academic_interest_similarity_score, nonacademic_interest_similarity_score, 
    career_similarity_score, skill_similarity_score, personality_similarity_score, trait_similarity_score])


    similarities.append(academic_interest_similarity[1])
    similarities.append(nonacademic_interest_similarity[1])
    similarities.append(career_similarity[1])
    similarities.append(skill_similarity[1])
    similarities.append(personality_similarity[1])

    weighted_vector = sorted(embedded_vector,reverse=True)
    return np.sqrt(embedded_vector.dot(embedded_vector)),similarities, int(np.mean(sorted(embedded_vector,reverse=True)[0:2])*100)

import pandas as pd

#reading data
file = pd.read_csv('processed_data.csv')
#extracting only the road with field number between 0 and 2
filtered_file = file[file['number'].isin([0, 1, 2])].copy()
missing_count = filtered_file['length'].isna().sum() #counting the number of dropped rows FOR #DEBUG
filtered_file = filtered_file.dropna(subset=['length']) #droppping the Nan value with 0 only for time and lenght
#grouping for areas
results_summary = []
def category(distance):
    #distance = distance/1000 #converting in km
    if distance <= 10:
        return 'urban'
    elif 10 < distance <= 30:
        return 'extraUrban'
    elif 30 < distance <= 90:
        return 'regional'
    else:
        return 'interRegional'

#creating a new column with the corrispondent category
filtered_file['category'] = (filtered_file['length_at_number_0']/1000).apply(category)
categories = ['urban', 'extraUrban', 'regional', 'interRegional']
algorithms = ['onepass_plus', 'esx', 'penalty']
groups = filtered_file.groupby('category').size().reset_index(name='count') #DEBUG
groups['category'] = pd.Categorical(groups['category'], categories, ordered=True)#DEBUG
groups = groups.sort_values('category')#DEBUG
print(groups)#DEBUG

print("missing count:" + str(missing_count))
category_results = []
times_of_the_cat = []
lengths_of_the_cat = []
avg_LM = []
avg_TM = []
sum_yield = []
total_not_computed = 0 #DEBUG
for category in categories:
    #filtering data for the category
    category_data = filtered_file[filtered_file['category'] == category]
    if len(category_data) > 0:#there is at least one path for that category
        #grouping by source and dest; results is the group of results that matches the same source and dest
        for (source, dest), results in category_data.groupby(['source', 'dest']):
            #print(results)
            best_times = []
            best_lengths = []
            for j in range(3):
                # filtering data by the number of result
                range_data = results[results['number'] == j]
                if not range_data.empty:
                    if len(range_data)<3:
                        #it means that one or two of the algorithm has not results for that k_path
                        total_not_computed+= 3-len(range_data)
                    # Getting the best time and lenght
                    best_times.append(range_data['time'].min())
                    best_lengths.append(range_data['length'].min())
                else:
                    #it means that no algorithm has found result for that k = number
                    total_not_computed += 3 #each algorithm did not compute anything
                    #we are in this case when there is no path for a number = 0, 1 or 2
                    #print("range_data empty")
                    best_times.append(300) #because it gets lots of time
                    best_lengths.append(0)

            #!!!! for Corso Buenos Aires Milano,Viale Piave Milano it is found only the first path (0)
            #for each algorithm, no one has found path 1 and 2, so the avg is calculated as:
            #best_times = [2.483469009399414, 300, 300]         and         best_lengths = [451.993, 0, 0]
            #print(best_times)
            valid_times = [t for t in best_times if t != 300]
            valid_lengths = [l for l in best_lengths if l != 0]
            #calculating the avgs not considering 300 and 0
            #the avg_best_* is the ORACLE of the path
            avg_best_time = sum(valid_times) / len(valid_times) #NB: I do not check if valid_times is empty because for sure there is at least the dijkstra's result
            avg_best_length = sum(valid_lengths) / len(valid_lengths)

            # Normalizing lengths for the pair (source, dest) analysed
            for alg, res_algs in results.groupby('alg'):
                #normalizing length
                sum_of_norm_len = 0
                sum_of_norm_time = 0
                sum_of_time = 0
                sum_of_length = 0
                if len(res_algs) != len(valid_times):
                    #it means that we have to recalculate the avg_best_lenght
                    new_avg_best_len = 0
                    new_avg_best_time = 0
                    for i in range(len(res_algs)):
                        new_avg_best_len += valid_lengths[i]/len(res_algs)
                        new_avg_best_time += valid_times[i]/len(res_algs)
                    #now we have the new avg_best_len
                    avg_best_length = new_avg_best_len
                    avg_best_time = new_avg_best_time

                for idx, row in res_algs.iterrows():
                    #reitering in res_algs (which are the results of the algorithm for a specific source, dest)
                    norm_length = row['length'] / avg_best_length #normalizing through the oracle
                    sum_of_norm_len += norm_length

                    norm_time = row['time'] / avg_best_time #normalizing through the oracle
                    sum_of_norm_time += norm_time

                    sum_of_time += row['time']
                    sum_of_length += row['length']

                LM = sum_of_norm_len / len(res_algs)
                TM = sum_of_norm_time / len(res_algs)
                avg_time = sum_of_time/len(res_algs)
                avg_length = sum_of_length/len(res_algs)

                #print(len(res_algs))
                entry = {
                    'alg': alg,
                    'source and dest': str(source)+","+str(dest),
                    'LM': LM, #normalized Medium Lenght
                    'TM': TM, #normalized Medium Time
                    'avg_time_alg': avg_time,
                    'avg_len_alg':avg_length,
                    'avg_time_total': avg_best_time,
                    'avg_length_total': avg_best_length,
                    'category': category,
                    'yield': 1-len(res_algs)/3
                }
                if entry not in results_summary:
                    results_summary.append(entry)
oracles = []

df = pd.DataFrame(results_summary)
for alg in algorithms:
    #filtering data by alg
    alg_data = df[df['alg'] == alg]
    for category in categories:
        #filtering data alg by category
        alg_data_cat = alg_data[alg_data['category'] == category]
        entry = {
            'category': category,
            'alg': alg,
            'avg_time_of_cat': alg_data_cat['avg_time_total'].mean(),
            'avg_length_of_cat':alg_data_cat['avg_length_total'].mean(),
            'avg_TM': alg_data_cat['TM'].mean(),
            'avg_LM': alg_data_cat['LM'].mean(),
            'avg_yield': alg_data_cat['yield'].mean(),
            #'count': len(alg_data_cat)  # Added count for debugging
        }
        oracles.append(entry)

seen_name = []
for entry in oracles:
    if entry['alg'] not in seen_name:
        print("\n")
        print(entry['alg'])
        seen_name.append(entry['alg'])
    print(entry)





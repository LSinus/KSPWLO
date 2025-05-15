import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import argparse

def calc_timer(quantile, alg_name, n_cluster, max_time):
    df = pd.read_csv("../processed_data.csv", usecols=["alg","source","dest","number","time","length","length_at_number_0"])
    #print(df.to_string())

    op_group = {}
    op = df.loc[df['alg'] == alg_name]

    kmeans = KMeans(n_clusters=n_cluster, max_iter=10000, n_init="auto").fit(df["length_at_number_0"].values.reshape(-1, 1))
    centers = sorted(kmeans.cluster_centers_.flatten())
    min_val = df['length_at_number_0'].min()
    max_val = df['length_at_number_0'].max()

    # Add padding to ensure all values are included
    lower_bound = min_val - 1
    upper_bound = max_val + 1

    # Create bin edges: first edge, midpoints between centers, last edge
    length_bins = [lower_bound]
    for i in range(len(centers) - 1):
        midpoint = (centers[i] + centers[i+1]) / 2
        length_bins.append(midpoint)
    length_bins.append(upper_bound)

    length_bin_labels = []
    for i in range(len(length_bins) - 1):
        start = int(length_bins[i])
        end = int(length_bins[i+1])
        if i == len(length_bins) - 2:  # For the last bin
            label = f'{start}+'
        else:
            label = f'{start}-{end}'
        length_bin_labels.append(label)


    #length_bins = [0, 20000, 50000, 80000, 120000, 180000, np.inf]
    #length_bin_labels = ['0-20k', '20k-50k', '50k-80k', '80-120k', '120k-180k', '180k+']


    for k, k_group in op.groupby("number"):
        dataframes_for_current_num = {}
        df_length_bin = k_group.copy()

        df_length_bin['length_range_category'] = pd.cut(
            df_length_bin['length_at_number_0'],
            bins=length_bins,
            labels=length_bin_labels,
            right=True,
            include_lowest=True
        )

        for length_range_obj, final_group_df in df_length_bin.groupby('length_range_category', observed=True):
            if not final_group_df.empty:
                length_range_str_key = str(length_range_obj)
                dataframes_for_current_num[length_range_str_key] = final_group_df.copy()

        op_group[k] = dataframes_for_current_num

    fig, ax = plt.subplots()
    length_bin_labels_np = np.array(length_bin_labels)
    for k, group in op_group.items():
        time_values_for_k = [np.nan] * len(length_bin_labels)
        comp_yield = [np.nan] * len(length_bin_labels)
        uncalculated = 0
        total = 0
        for length_range, df in group.items():
            idx = length_bin_labels.index(length_range)
            print(f"[INFO] details for {alg_name} k = {k}, length_range = {length_range}, total samples = {len(df)}")
            time = df["time"].quantile(quantile)
            total = len(df)
            uncalculated = len(df[df["time"] == 300.0])
            comp_yield[idx] = (uncalculated/total)
            time_values_for_k[idx] = time
        time_values_np = np.array(time_values_for_k, dtype=float)
        ax.plot(length_bin_labels_np, time_values_np, label=k, marker='o')
        for i, (length_range, yield_value) in enumerate(zip(length_bin_labels, comp_yield)):
            ax.annotate(f"{yield_value:.2f}",
                        (length_bin_labels_np[i], time_values_np[i]),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha='center')

    ax.set_xlabel("Length Range")
    ax.set_ylabel(f"Median Time (seconds) ({quantile} Quantile)")
    ax.set_title(f"{quantile} time vs. Length Range by Number of Paths ({alg_name})")
    ax.legend(title="Number of Paths (k)")
    ax.grid(True)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.ylim((0, max_time))
    plt.show()

    ''' è importante tenere in considerazione che in alcuni casi si hanno computazioni con un certo k1 che
        impiegano un tempo inferiore rispetto ad altre con un certo k2 nonostante k1 > k2 questo succede
        perché non sempre gli algoritmi riescono a calcolare esattamente k risultati e dunque questo comporta
        una mancanza di dati in quegli scenari dove k2 aveva già di per sé un valore elevato, k1 non è stato
        calcolato. 
    '''

if __name__ == "__main__":
    alg_name = "onepass_plus"
    quantile = 0.5 # median by default
    n_clusters = 10
    max_time = 40

    parser = argparse.ArgumentParser()
    parser.add_argument('-q', type=float, help='quantile')
    parser.add_argument('-n', type=int, help='ncluster')
    parser.add_argument('-a', type=str, help='alg_name')
    parser.add_argument('-t', type=int, help='maxtime')
    args = parser.parse_args()
    if args.q:
        quantile = args.q
    if args.a:
        alg_name = args.a
    if args.n:
        n_clusters = args.n
    if args.t:
        max_time = args.t

    calc_timer(quantile, alg_name, n_clusters, max_time)
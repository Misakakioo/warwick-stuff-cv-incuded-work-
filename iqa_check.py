import pandas as pd
import ast

# Read 'eval_100_iqa_new.csv' and get the first 100 rows of column '1 means bad'
df_eval = pd.read_csv("eval_100_iqa_label.csv")
# print(df_eval.columns)

df_eval_subset = df_eval.loc[:99, "1 means bad"]

# Read 'zephyr-iqa-full-double.csv' and get the first 100 rows of columns 'output' and 'label'
df_full_double = pd.read_csv("zephyr-iqa-full-double.csv")
df_full_double_subset = df_full_double.loc[:99, ["output", "label"]]

# Read 'zephyr-iqa-100.csv' and get the first 100 rows of columns 'output' and 'label'
df_iqa_100 = pd.read_csv("zephyr-iqa-100.csv")
df_iqa_100_subset = df_iqa_100.loc[:99, ["output", "label"]]

df = pd.DataFrame(columns=["normal", "double"])
df_read = pd.DataFrame(columns=["normal", "double", "label"])

double_counter = 0
normal_counter = 0
doube_check = 0
for index, row in enumerate(df_eval_subset):
    normal = df_iqa_100_subset.iloc[index]
    double = df_full_double_subset.iloc[index]
    label = normal["label"]
    # print(row)
    if row == 1:
        boo_label = False
    else:
        boo_label = True

    double_output = ast.literal_eval(double["output"])[0]["generated_text"]
    normal_output = ast.literal_eval(normal["output"])[0]["generated_text"]

    start = double_output.find("<|assistant|>") + len("<|assistant|>")
    double_output = double_output[start:].strip()

    start = normal_output.find("<|assistant|>") + len("<|assistant|>")
    normal_output = normal_output[start:].strip()

    if row == 1:
        df_read = df_read._append(
            {
                "normal": normal_output,
                "double": double_output,
                # "boo_label": row,
                "label": label,
            },
            ignore_index=True,
        )

    double_output = double_output.split()[0][0]
    normal_output = normal_output.split()[0][0]
    if double_output == normal_output:
        doube_check += 1

    boo_normal = (normal_output == label) == boo_label
    boo_double = (double_output == label) == boo_label

    if boo_normal:
        normal_counter += 1
    if boo_double:
        double_counter += 1

    df = df._append(
        {
            "normal": boo_normal,
            "double": boo_double,
        },
        ignore_index=True,
    )


df.to_csv("100_check.csv", index=False)
df_read.to_csv("100_read.csv", index=False)
print("Normal: ", normal_counter)
print("Double: ", double_counter)
print("Double Check: ", doube_check)

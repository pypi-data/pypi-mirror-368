def missforest_fun(
    data,
    n_iter,
    categorical_vars,
    ordinal_vars,
    numerical_vars,
    xgb=False,
    n_estimators=1000,
):  # , target_cols = False, custom_target_cols = None):
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.impute import SimpleImputer
    from xgboost import XGBClassifier, XGBRegressor

    data_old = data.reset_index(drop=True).copy()
    predictions = {}
    X_t_0 = {}
    criterion_num = []
    criterion_cat = []
    na_where = data_old.isna().copy()
    na_perc = (data_old.isna().sum() / data_old.shape[0]).sort_values(
        ascending=True
    )  # percentages of NAs per column in ascending order
    # print(na_perc)
    cols = na_perc[na_perc > 0].index.tolist()  # list of all columns with NAs

    # Randomly impute variables (only in the beginning)
    for col in cols:
        if col in (categorical_vars or ordinal_vars):
            data_old.loc[:, col] = SimpleImputer(
                strategy="most_frequent"
            ).fit_transform(data_old[col].values.reshape(-1, 1))
        else:
            data_old.loc[:, col] = SimpleImputer(strategy="mean").fit_transform(
                data_old[col].values.reshape(-1, 1)
            )

    data_new = data_old.copy()

    for i in np.arange(1, n_iter + 1):
        data_prev_step = data_new.copy()

        # main loop to go through columns
        print(i)
        for col in cols:
            print(col)

            if i == 1:
                # Transform target variable in the beginning
                if col in (categorical_vars or ordinal_vars):
                    var_traget_imputer = LabelEncoder()
                    var_target = pd.DataFrame(
                        var_traget_imputer.fit_transform(
                            data_old[col].values.reshape(
                                -1,
                            )
                        ),
                        columns=[col],
                    )
                    # var_target[data_old[col].isna()] = np.nan
                    # return({"x": var_target, "y": na_where[col]})
                elif col in numerical_vars:
                    var_target = data_old[
                        col
                    ]  # here we don't transform because RFs do not require numeric transformation

                # Transform categorical variables in One-hot and then combine all non-target variables (i.e., dropping target column)
                data_processed = pd.concat(
                    [
                        pd.get_dummies(
                            data_old.drop(columns=col)[
                                [i for i in categorical_vars if i != col]
                            ],
                            dummy_na=True,
                        ),
                        data_old.drop(columns=col)[
                            [i for i in numerical_vars if i != col]
                        ],
                        data_old.drop(columns=col)[
                            [i for i in ordinal_vars if i != col]
                        ],
                    ],
                    axis=1,
                )
            else:

                # Transform target variable in the beginning
                if col in (categorical_vars or ordinal_vars):
                    var_traget_imputer = LabelEncoder()
                    var_target = pd.DataFrame(
                        var_traget_imputer.fit_transform(
                            data_new[col].values.reshape(
                                -1,
                            )
                        ),
                        columns=[col],
                    )
                    # var_target[data_new[col].isna()] = np.nan
                elif col in numerical_vars:
                    var_target = data_new[
                        col
                    ]  # here we don't transform because RFs do not require numeric transformation

                # Here I don't need to imput the target variable because it has been imputed on the first round
                # I transform data again like in i == 1
                data_processed = pd.concat(
                    [
                        pd.get_dummies(
                            data_new.drop(columns=col)[
                                [i for i in categorical_vars if i != col]
                            ],
                            dummy_na=True,
                        ),
                        data_new.drop(columns=col)[
                            [i for i in numerical_vars if i != col]
                        ],
                        data_new.drop(columns=col)[
                            [i for i in ordinal_vars if i != col]
                        ],
                    ],
                    axis=1,
                )

            # train/test split
            X_train = data_processed[~na_where[col]]
            y_train = var_target[~na_where[col]]
            X_test = data_processed[na_where[col]]
            y_test = var_target[
                na_where[col]
            ]  ## SOOOS: that should be maybe replaced as X_T_0?????

            if col in (categorical_vars or ordinal_vars):
                if xgb:
                    rfc = XGBClassifier(n_jobs=-1, n_estimators=n_estimators)
                else:
                    rfc = RandomForestClassifier(n_jobs=-1, n_estimators=n_estimators)
            else:
                if xgb:
                    rfc = XGBRegressor(n_jobs=-1, n_estimators=n_estimators)
                else:
                    rfc = RandomForestRegressor(n_jobs=-1, n_estimators=n_estimators)

            rfc.fit(
                X_train,
                y_train.values.reshape(
                    -1,
                ),
            )

            # save t0
            if i == 1:
                X_t_0.update({col: var_target})

            # save predictions
            predictions.update({col: rfc.predict(X_test)})

            if col in (categorical_vars or ordinal_vars):
                data_new.loc[na_where[col], col] = var_traget_imputer.inverse_transform(
                    [int(i) for i in predictions[col]]
                )
            else:
                data_new.loc[na_where[col], col] = predictions[col]

        # Calculate criterion
        matches_cat = []

        criterion_num.append(
            sum(
                (
                    (
                        data_new[na_where[numerical_vars]][numerical_vars]
                        - data_prev_step[na_where[numerical_vars]][numerical_vars]
                    )
                    ** 2
                ).sum()
            )
            / sum((data_new[na_where[numerical_vars]][numerical_vars] ** 2).sum())
        )

        for col in categorical_vars:
            matches_cat.append(
                sum(
                    data_new[na_where][col].dropna()
                    != data_prev_step[na_where][col].dropna()
                )
            )

        criterion_cat.append(sum(matches_cat) / sum(na_where.sum()))

        print({"criterion_cat": criterion_cat, "criterion_num": criterion_num})
        # Decide based on criterion
        if i > 1:
            if all([x == 0 for x in criterion_cat]):
                if criterion_num[i - 1] > criterion_num[i - 2]:
                    print(
                        "The critirion was satisfied after {} iterations".format(i - 1)
                    )
                    return data_prev_step
            elif all([x == 0 for x in criterion_num]):
                if criterion_num[i - 1] > criterion_num[i - 2]:
                    print(
                        "The critirion was satisfied after {} iterations".format(i - 1)
                    )
                    return data_prev_step
            else:
                if (criterion_cat[i - 1] > criterion_cat[i - 2]) and (
                    criterion_num[i - 1] > criterion_num[i - 2]
                ):
                    print(
                        "The critirion was satisfied after {} iterations".format(i - 1)
                    )
                    return data_prev_step

    return "The criterion was not satisfied after {} iterations".format(i - 1)

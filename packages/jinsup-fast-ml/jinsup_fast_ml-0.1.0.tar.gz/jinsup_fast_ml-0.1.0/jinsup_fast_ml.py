from sklearn.base import TransformerMixin
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pandas as pd
from collections import namedtuple
from lazypredict.Supervised import LazyClassifier
import lightgbm as lgb
import contextlib
import os
import optuna
from xgboost import XGBRegressor, XGBClassifier
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    RandomForestClassifier,
    GradientBoostingClassifier,
)
from typing import Literal,Any
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, classification_report
from datetime import datetime
from optuna.samplers import TPESampler
import joblib

class JinsupFastML:

    # 라벨 인코딩
    @staticmethod
    def all_label_encode(df, cols):
        for col in cols:
            le = LabelEncoder()
            df[col + "_encode"] = le.fit_transform(df[col])

        return df.drop(columns=cols)

    # 원핫 인코딩
    @staticmethod
    def all_one_hot_encode(df, cols, **kwargs):
        return pd.get_dummies(df, columns=cols, dtype=int, **kwargs)

    # 전체 스케일링
    @staticmethod
    def df_to_scaler(df, scaler_cls: type[TransformerMixin], **scaler_kwargs):
        scaler = scaler_cls(**scaler_kwargs)
        df_scaler = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
        return df_scaler

    # IQR을 이용한 특정 칼럼 이상치 제거
    @staticmethod
    def remove_outlier_by_iqr(df, columns):
        df_copy = df.copy()
        mask = pd.Series(True, index=df.index)
        for col in columns:
            Q1 = df_copy[col].quantile(0.25)
            Q3 = df_copy[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            mask &= (df[col] >= lower) & (df[col] <= upper)
        return df[mask]

    # IQR을 이용한 전체 결측치 찾기
    @staticmethod
    def find_outlier_columns(df):
        numeric_cols = df.select_dtypes(include="number").columns
        outlier_cols = []

        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            if ((df[col] < lower) | (df[col] > upper)).any():
                outlier_cols.append(col)

        return outlier_cols

    # 훈련, 테스트 데이터를 split 객체로 묶어서 사용하기
    @staticmethod
    def train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=False, **kwargs
    ):
        Split = namedtuple("Split", "X_train X_test y_train y_test")
        if stratify:
            split = Split(
                *train_test_split(
                    X,
                    y,
                    test_size=test_size,
                    random_state=random_state,
                    stratify=y,
                    **kwargs,
                )
            )
        else:
            split = Split(
                *train_test_split(
                    X, y, test_size=test_size, random_state=random_state, **kwargs
                )
            )

        return split

    # 최고의 모델 찾기 (기본적으로 상위 5개 출력)
    @staticmethod
    def check_best_model(data_split: namedtuple, top_k: int = 5, **kwargs):
        params = {"verbose": 0, "ignore_warnings": True, "custom_metric": None}
        params.update(kwargs)

        lcf_model = LazyClassifier(**params)

        with (
            open(os.devnull, "w") as fnull,
            contextlib.redirect_stdout(fnull),
            contextlib.redirect_stderr(fnull),
        ):
            models, predictions = lcf_model.fit(
                data_split.X_train,
                data_split.X_test,
                data_split.y_train,
                data_split.y_test,
            )

        print(models[:top_k])
    

    
    # Optuna를 이용한 하이퍼 파라미터 튜닝
    @staticmethod
    def optuna_start(split:namedtuple, task: Literal["regression", "classification"] = None):
        if task is None:
            raise ValueError("task 값이 None입니다. 'regression' 또는 'classification' 중 하나를 지정하세요.\n아니면 이진섭에게 문의 주세요")
    
        if task not in ("regression", "classification"):
            raise ValueError(f"지원하지 않는 task 값입니다: {task} \n 아니면 이진섭에게 문의 주세요")
        
        def objective(trial, split:namedtuple):
            model_type = trial.suggest_categorical(
                "model", ["RandomForest", "GradientBoost", "XGBoost"]
            )

            random_state = 42

            if task == "classification":
                if model_type == "RandomForest":
                    model = RandomForestClassifier(
                        n_estimators=trial.suggest_int("n_estimators", 100, 500),
                        max_depth=trial.suggest_int("max_depth", 3, 20),
                        random_state=random_state,
                    )
                elif model_type == "GradientBoost":
                    model = GradientBoostingClassifier(
                        n_estimators=trial.suggest_int("n_estimators", 100, 500),
                        max_depth=trial.suggest_int("max_depth", 3, 20),
                        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
                        random_state=random_state,
                    )
                elif model_type == "XGBoost":
                    model = XGBClassifier(
                        n_estimators=trial.suggest_int("n_estimators", 100, 500),
                        max_depth=trial.suggest_int("max_depth", 3, 40),
                        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
                        random_state=random_state,
                    )
            else:
                if model_type == "RandomForest":
                    model = RandomForestRegressor(
                        n_jobs=-1,
                        n_estimators=trial.suggest_int("n_estimators", 100, 1500),
                        max_depth=trial.suggest_int("max_depth", 3, 40),
                        min_samples_split=trial.suggest_int("min_samples_split", 2, 10),
                        random_state=random_state,
                    )
                elif model_type == "GradientBoost":
                    model = GradientBoostingRegressor(
                        n_iter_no_change=5,
                        n_estimators=trial.suggest_int("n_estimators", 100, 1500),
                        max_depth=trial.suggest_int("max_depth", 3, 40),
                        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
                        random_state=random_state,
                    )
                elif model_type == "XGBoost":
                    model = XGBRegressor(
                        tree_method="auto",
                        n_estimators=trial.suggest_int("n_estimators", 100, 1500),
                        max_depth=trial.suggest_int("max_depth", 3, 40),
                        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
                        subsample=trial.suggest_float("subsample", 0.5, 1.0),
                        random_state=random_state,
                    )

            model.fit(split.X_train, split.y_train)
            y_pred = model.predict(split.X_test)
            return r2_score(split.y_test, y_pred)
        
        study = optuna.create_study(direction="maximize",
                                    sampler=TPESampler(seed=42))
        study.optimize(lambda trial: objective(trial, split), n_trials=50)    
        print("최고의 모델", study.best_params["model"])
        print("최고의 파리미터스", study.best_params)
        print("최고 스코어", study.best_value)

        best_params = study.best_params.copy()
        best_params["task"] = task
        best_params["random_state"] = 42
        return best_params
    
    # Optuna 결과로부터 모델을 빌드하고 평가
    @staticmethod
    def build_model_from_optuna_result(optuna_result:dict[str, Any], split:namedtuple, auto_save=True):
        
        model = optuna_result["model"]
        task = optuna_result.pop("task", None)

        params = {k: v for k, v in optuna_result.items() if k != "model"}
        
        if task == "classification":
            if model == "RandomForest":
                model = RandomForestClassifier(**params)
            elif model == "GradientBoost":
                model = GradientBoostingClassifier(**params)
            elif model == "XGBoost":
                model = XGBClassifier(**params)

        elif task == "regression":
            if model == "RandomForest":
                model = RandomForestRegressor(**params)
            elif model == "GradientBoost":
                model = GradientBoostingRegressor(**params)
            elif model == "XGBoost":
                model = XGBRegressor(**params)
        else:
            raise ValueError(f"지원하지 않는 task 값입니다: {task} \n 아니면 이진섭에게 문의 주세요")
        
        model.fit(split.X_train, split.y_train)
        y_pred = model.predict(split.X_test)

        if task == "regression":
            print(f"MSE:{mean_squared_error(split.y_test, y_pred)}")
            print(f"MAE:{mean_absolute_error(split.y_test, y_pred)}")
            print(f"R2_Score: {r2_score(split.y_test,y_pred)}")
        else:
            print(classification_report(split.y_test, y_pred))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if auto_save:
            joblib.dump(model, f"model_{timestamp}.pkl")
        
        return model
    

    

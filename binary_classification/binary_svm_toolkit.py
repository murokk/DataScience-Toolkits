# Author: Hamza Tazi Bouardi
import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from binary_utils import get_all_metrics_binary


class SVM_Toolkit():
    def __init__(
            self, 
            X_train: pd.DataFrame, 
            X_test: pd.DataFrame, 
            y_train: pd.Series, 
            y_test: pd.Series
    ):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.X_train_scaled = None
        self.X_test_scaled = None
        self.fpr_svm_rbf = None
        self.tpr_svm_rbf = None
        self.threshold_svm_rbf = None
        self.svm_rbf_model_best = None
        self.roc_auc_svm_rbf = None
        self.fpr_svm_linear = None
        self.tpr_svm_linear = None
        self.threshold_svm_linear = None
        self.svm_linear_model_best = None
        self.roc_auc_svm_linear = None
        
    def scale_data(self):
        # Scaling data (speeds up a lot the fitting)
        scaler = StandardScaler()
        scaler.fit(self.X_train)
        self.X_train_scaled = scaler.transform(self.X_train)
        self.X_test_scaled = scaler.transform(self.X_test)

    def svm_toolkit(self):
        self.scale_data()
        self.linear_svm_toolkit()
        self.gaussian_svm_toolkit()

    def linear_svm_toolkit(self):
        # Linear Kernel
        svm_linear_model = SVC(
            kernel="linear",
            random_state=0
        )
        gs_params_svm_linear = {
            "C": np.linspace(0.001, 50, 50),
        }
        gs_cv_obj_svm_linear = GridSearchCV(svm_linear_model, gs_params_svm_linear, cv=3, n_jobs=-1, scoring="roc_auc")
        gs_cv_obj_svm_linear.fit(self.X_train_scaled, self.y_train)
        results_svm_linear = pd.DataFrame(gs_cv_obj_svm_linear.cv_results_)
        dict_best_params_svm_linear = results_svm_linear[results_svm_linear.rank_test_score == 1]["params"].values[0]
        print("Linear SVM \n", dict_best_params_svm_linear)
        self.svm_linear_model_best = SVC(
            kernel="linear",
            C=dict_best_params_svm_linear["C"],
            random_state=0,
            probability=True
        )
        self.svm_linear_model_best.fit(self.X_train_scaled, self.y_train)

        # Predict train and test
        y_pred_train_proba_svm_linear = self.svm_linear_model_best.predict_proba(self.X_train_scaled)[:, 1]
        y_pred_train_svm_linear = self.svm_linear_model_best.predict(self.X_train_scaled)
        y_pred_svm_linear = self.svm_linear_model_best.predict(self.X_test_scaled)
        y_pred_proba_svm_linear = self.svm_linear_model_best.predict_proba(self.X_test_scaled)[:, 1]

        # Generate all useful metrics
        accuracy_train_svm_linear, auc_train_svm_linear, classification_report_train_svm_linear = get_all_metrics_binary(
            self.y_train, y_pred_train_svm_linear, y_pred_train_proba_svm_linear
        )
        accuracy_test_svm_linear, auc_test_svm_linear, classification_report_test_svm_linear = get_all_metrics_binary(
            self.y_test, y_pred_svm_linear, y_pred_proba_svm_linear
        )

        # Scores on train
        print(f"Linear SVM scores on Train:\nAccuracy={accuracy_train_svm_linear} \tAUC={auc_train_svm_linear}" +
              f"\nClassification Report:\n{classification_report_train_svm_linear} ")
        # Scores on test
        print(f"Linear SVM scores on Test:\nAccuracy={accuracy_test_svm_linear} \tAUC={auc_test_svm_linear}" +
              f"\nClassification Report:\n{classification_report_test_svm_linear} ")

        # FPR, TPR and AUC for svm_linear for visualization
        self.fpr_svm_linear, self.tpr_svm_linear, self.threshold_svm_linear = roc_curve(
            self.y_test,
            y_pred_proba_svm_linear
        )
        self.roc_auc_svm_linear = auc(self.fpr_svm_linear, self.tpr_svm_linear)

    def gaussian_svm_toolkit(self):
        # Gaussian Kernel
        svm_rbf_model = SVC(
            kernel="rbf",
            random_state=0
        )
        gs_params_svm_rbf = {
            "C": np.linspace(0.001, 50, 50),
        }
        gs_cv_obj_svm_rbf = GridSearchCV(svm_rbf_model, gs_params_svm_rbf, cv=3, n_jobs=-1, scoring="roc_auc")
        gs_cv_obj_svm_rbf.fit(self.X_train_scaled, self.y_train)
        results_svm_rbf = pd.DataFrame(gs_cv_obj_svm_rbf.cv_results_)
        dict_best_params_svm_rbf = results_svm_rbf[results_svm_rbf.rank_test_score == 1]["params"].values[0]
        print("Gaussian SVM \n", dict_best_params_svm_rbf)
        self.svm_rbf_model_best = SVC(
            kernel="rbf",
            C=dict_best_params_svm_rbf["C"],
            random_state=0,
            probability=True
        )
        self.svm_rbf_model_best.fit(self.X_train_scaled, self.y_train)
        
        # Predict train and test
        y_pred_train_proba_svm_rbf = self.svm_rbf_model_best.predict_proba(self.X_train_scaled)[:, 1]
        y_pred_train_svm_rbf = self.svm_rbf_model_best.predict(self.X_train_scaled)
        y_pred_svm_rbf = self.svm_rbf_model_best.predict(self.X_test_scaled)
        y_pred_proba_svm_rbf = self.svm_rbf_model_best.predict_proba(self.X_test_scaled)[:, 1]

        # Generate all useful metrics
        accuracy_train_svm_rbf, auc_train_svm_rbf, classification_report_train_svm_rbf = get_all_metrics_binary(
            self.y_train, y_pred_train_svm_rbf, y_pred_train_proba_svm_rbf
        )
        accuracy_test_svm_rbf, auc_test_svm_rbf, classification_report_test_svm_rbf = get_all_metrics_binary(
            self.y_test, y_pred_svm_rbf, y_pred_proba_svm_rbf
        )

        # Scores on train
        print(f"rbf SVM scores on Train:\nAccuracy={accuracy_train_svm_rbf} \tAUC={auc_train_svm_rbf}" +
              f"\nClassification Report:\n{classification_report_train_svm_rbf} ")
        # Scores on test
        print(f"rbf SVM scores on Test:\nAccuracy={accuracy_test_svm_rbf} \tAUC={auc_test_svm_rbf}" +
              f"\nClassification Report:\n{classification_report_test_svm_rbf} ")

        # FPR, TPR and AUC for svm_rbf for visualization
        self.fpr_svm_rbf, self.tpr_svm_rbf, self.threshold_svm_rbf = roc_curve(
            self.y_test,
            y_pred_proba_svm_rbf
        )
        self.roc_auc_svm_rbf = auc(self.fpr_svm_rbf, self.tpr_svm_rbf)

import os
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_palette("tab10")

from sklearn.model_selection import train_test_split,GroupKFold,ParameterGrid,GridSearchCV,cross_val_score

from sklearn.metrics import accuracy_score,classification_report,confusion_matrix,roc_auc_score,roc_curve,make_scorer
from sklearn.compose import ColumnTransformer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer,IterativeImputer,KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler,LabelEncoder,OrdinalEncoder,MinMaxScaler

from imblearn.over_sampling import SMOTE, SMOTENC
from imblearn.combine import SMOTEENN, SMOTETomek

import optuna
from skopt import BayesSearchCV


from sklearn.tree import DecisionTreeClassifier,plot_tree
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from catboost import CatBoostClassifier,CatBoostRegressor
from xgboost import XGBClassifier,XGBRegressor
from lightgbm import LGBMClassifier,LGBMRegressor

from functools import partial
from tabulate import tabulate


from sklearn import set_config
set_config(transform_output="default")

def rodar_tudo_sem_outliers(dados,
            alvo,
            proporcaoParaTeste,
            categoricas,
            numericas,
            dicionario_de_modelos,
            modelos_optuna,
            dicionario_de_parametros_para_otimizacao_grid,
            dicionario_de_parametros_para_otimizacao_baysiana,
            nome_do_notebook,ordenadas=None,
            descricao_do_notebook=None):
   
    X_train, X_test, y_train, y_test = separar_treino_e_teste_sem_outiliers(dados=dados, alvo=alvo, proporcaoParaTeste=proporcaoParaTeste,numericas=numericas)

   

    



    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_MICE_random_forest(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        descricao_do_notebook=descricao_do_notebook,
        nome_do_notebook=nome_do_notebook
    )

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_mediana(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        descricao_do_notebook=descricao_do_notebook,
        nome_do_notebook=nome_do_notebook
    )

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_media(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        descricao_do_notebook=descricao_do_notebook,
        nome_do_notebook=nome_do_notebook
    )

    
    

   

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_MICE_random_forest(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        nome_do_notebook=nome_do_notebook,
        descricao_do_notebook=descricao_do_notebook,
        padronizacao=False
    )

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_mediana(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        nome_do_notebook=nome_do_notebook,
        descricao_do_notebook=descricao_do_notebook,
        padronizacao=False
    )

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_media(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        nome_do_notebook=nome_do_notebook,
        descricao_do_notebook=descricao_do_notebook,
        padronizacao=False
    )



def rodar_tudo(
            dados,
            alvo,
            proporcaoParaTeste,
            categoricas,
            numericas,
            dicionario_de_modelos,
            modelos_optuna,
            dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana,
            nome_do_notebook,ordenadas=None,
            descricao_do_notebook=None):
   
    X_train, X_test, y_train, y_test = separar_treino_e_teste(dados=dados, alvo=alvo, proporcaoParaTeste=proporcaoParaTeste)

    


  
    
    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_MICE_random_forest(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        descricao_do_notebook=descricao_do_notebook,
        nome_do_notebook=nome_do_notebook
    )

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_mediana(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        descricao_do_notebook=descricao_do_notebook,
        nome_do_notebook=nome_do_notebook
    )

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_media(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        descricao_do_notebook=descricao_do_notebook,
        nome_do_notebook=nome_do_notebook
    )
  

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_MICE_random_forest(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        nome_do_notebook=nome_do_notebook,
        descricao_do_notebook=descricao_do_notebook,
        padronizacao=False
    )

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_mediana(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        nome_do_notebook=nome_do_notebook,
        descricao_do_notebook=descricao_do_notebook,
        padronizacao=False
    )

    preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_media(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        categoricas=categoricas,
        numericas=numericas,
        ordenadas=ordenadas,
        dicionario_de_modelos=dicionario_de_modelos,
        modelos_optuna=modelos_optuna,
        dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
        nome_do_notebook=nome_do_notebook,
        descricao_do_notebook=descricao_do_notebook,
        padronizacao=False
    )


   

# Funções de preprocessaento 
def preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_MICE_lightboost(X_train,
                                                                                     X_test,
                                                                                     y_train,
                                                                                     y_test,
                                                                                     categoricas,
                                                                                     numericas,                                                                                     
                                                                                     dicionario_de_modelos,
                                                                                     modelos_optuna,
                                                                                     dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,
                                                                                     nome_do_notebook,
                                                                                     ordenadas=None,
                                                                                     nome_da_funcao='preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_MICE_lightboost',
                                                                                     padronizacao=True,
                                                                                     descricao_do_notebook=None
                                                                                     ):

    m_lgbm_classificador=LGBMClassifier()
    m_lgbm_regressao=LGBMRegressor()

    preencher_vazio_numerico=IterativeImputer(estimator = m_lgbm_regressao,max_iter = 10,
                                                              imputation_order = 'descending',
                                                              random_state=108,
                                                              initial_strategy='most_frequent'
                                                              )
    
    X_train[numericas]=preencher_vazio_numerico.fit_transform(X_train[numericas])

    if padronizacao:
        rescalonador=StandardScaler()
        tipo_de_rescalonamento="dados_padronizados"
    else:
        rescalonador=MinMaxScaler()
        tipo_de_rescalonamento='dados_normalizados'


    X_train[numericas]=rescalonador.fit_transform(X_train[numericas])


    preencher_vazio_categorico=IterativeImputer(estimator = m_lgbm_classificador,max_iter = 10,
                                                              imputation_order = 'descending',
                                                              random_state=108,
                                                              initial_strategy='most_frequent'
                                                              )
    X_train[categoricas]=preencher_vazio_categorico.fit_transform(X_train[categoricas])

    #print(X_train.isna().sum())

    X_train[categoricas]=X_train[categoricas].astype('category')

    rebalanceador= SMOTENC(random_state=42,sampling_strategy='minority',categorical_features='auto')
    X_res,y_res=rebalanceador.fit_resample(X_train,y_train)

    one_hot_enconder=OneHotEncoder(drop='first', handle_unknown='ignore',sparse_output=False)

    X_res_encoded = pd.DataFrame(
    one_hot_enconder.fit_transform(X_res[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),
    index=X_res.index
    )


    X_test[numericas]=preencher_vazio_numerico.transform(X_test[numericas])
    X_test[numericas]=rescalonador.transform(X_test[numericas])

    X_test[categoricas]=preencher_vazio_categorico.transform(X_test[categoricas])

    X_test_encoded = pd.DataFrame(
    one_hot_enconder.transform(X_test[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),

    )


    if ordenadas:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True),X_train[ordenadas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True),X_test[ordenadas].reset_index(drop=True)], axis=1)
    else:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True)], axis=1)

    
    comparar_modelos(nome_do_arquivo=f'{nome_do_notebook}_{tipo_de_rescalonamento}_{nome_da_funcao}',
                     dicionario_de_modelos=dicionario_de_modelos,
                     modelos_optuna=modelos_optuna,
                     dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
                     X_teste_final=X_test_final,
                     y_teste_final=y_test,
                     X_treino_final=X_res_final,
                     y_treino_final=y_res,descricao_do_notebook=descricao_do_notebook)
    
def preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_MICE_random_forest(X_train,
                                                                                     X_test,
                                                                                     y_train,
                                                                                     y_test,
                                                                                     categoricas,
                                                                                     numericas,
                                                                                     dicionario_de_modelos,
                                                                                     modelos_optuna,
                                                                                      dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,
                                                                                     nome_do_notebook,
                                                                                     ordenadas=None,
                                                                                     nome_da_funcao='preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_MICE_random_forest',
                                                                                     padronizacao=True,descricao_do_notebook=None
                                                                                     ):
    m_rf_classificador=RandomForestClassifier()
    m_rf_regressao=RandomForestRegressor()

    preencher_vazio_numerico=IterativeImputer(estimator = m_rf_regressao,max_iter = 10,
                                                              imputation_order = 'descending',
                                                              random_state=108,
                                                              initial_strategy='most_frequent'
                                                              )
    X_train[numericas]=preencher_vazio_numerico.fit_transform(X_train[numericas])

    if padronizacao:
        rescalonador=StandardScaler()
        tipo_de_rescalonamento="dados_padronizados"
    else:
        rescalonador=MinMaxScaler()
        tipo_de_rescalonamento='dados_normalizados'

    X_train[numericas]=rescalonador.fit_transform(X_train[numericas])


    preencher_vazio_categorico=IterativeImputer(estimator = m_rf_classificador,max_iter = 10,
                                                              imputation_order = 'descending',
                                                              random_state=108,
                                                              initial_strategy='most_frequent'
                                                              )
    X_train[categoricas]=preencher_vazio_categorico.fit_transform(X_train[categoricas])

    #print(X_train.isna().sum())

    X_train[categoricas]=X_train[categoricas].astype('category')

    rebalanceador= SMOTENC(random_state=42,sampling_strategy='minority',categorical_features='auto')
    X_res,y_res=rebalanceador.fit_resample(X_train,y_train)

    one_hot_enconder=OneHotEncoder(drop='first', handle_unknown='ignore',sparse_output=False)

    X_res_encoded = pd.DataFrame(
    one_hot_enconder.fit_transform(X_res[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),
    index=X_res.index
    )


    X_test[numericas]=preencher_vazio_numerico.transform(X_test[numericas])
    X_test[numericas]=rescalonador.transform(X_test[numericas])

    X_test[categoricas]=preencher_vazio_categorico.transform(X_test[categoricas])

    X_test_encoded = pd.DataFrame(
    one_hot_enconder.transform(X_test[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),

    )


    if ordenadas:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True),X_train[ordenadas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True),X_test[ordenadas].reset_index(drop=True)], axis=1)
    else:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True)], axis=1)

    comparar_modelos(nome_do_arquivo=f'{nome_do_notebook}_{tipo_de_rescalonamento}_{nome_da_funcao}',
                     dicionario_de_modelos=dicionario_de_modelos,
                     modelos_optuna=modelos_optuna,
                     dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
                     X_teste_final=X_test_final,
                     y_teste_final=y_test,
                     X_treino_final=X_res_final,
                     y_treino_final=y_res,descricao_do_notebook=descricao_do_notebook)

def preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_KNN_cinco_distance(X_train,
                                                                                     X_test,
                                                                                     y_train,
                                                                                     y_test,
                                                                                     categoricas,
                                                                                     numericas,                                                                                     
                                                                                     dicionario_de_modelos,
                                                                                     modelos_optuna,
                                                                                      dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,
                                                                                     nome_do_notebook,
                                                                                     ordenadas=None,
                                                                                     nome_da_funcao='preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_KNN_cinco_distance',
                                                                                     padronizacao=True,descricao_do_notebook=None
                                                                                     ):

    preencher_vazio_knn_5_distance=KNNImputer(n_neighbors=5,weights='distance')
    X_train[numericas]=preencher_vazio_knn_5_distance.fit_transform(X_train[numericas])

    if padronizacao:
        rescalonador=StandardScaler()
        tipo_de_rescalonamento="dados_padronizados"
    else:
        rescalonador=MinMaxScaler()
        tipo_de_rescalonamento='dados_normalizados'

    X_train[numericas]=rescalonador.fit_transform(X_train[numericas])


    moda=SimpleImputer(strategy='most_frequent')
    X_train[categoricas]=moda.fit_transform(X_train[categoricas])

    #print(X_train.isna().sum())

    X_train[categoricas]=X_train[categoricas].astype('category')

    rebalanceador= SMOTENC(random_state=42,sampling_strategy='minority',categorical_features='auto')
    X_res,y_res=rebalanceador.fit_resample(X_train,y_train)

    one_hot_enconder=OneHotEncoder(drop='first', handle_unknown='ignore',sparse_output=False)

    X_res_encoded = pd.DataFrame(
    one_hot_enconder.fit_transform(X_res[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),
    index=X_res.index
    )


    X_test[numericas]=preencher_vazio_knn_5_distance.transform(X_test[numericas])
    X_test[numericas]=rescalonador.transform(X_test[numericas])

    X_test[categoricas]=moda.transform(X_test[categoricas])

    X_test_encoded = pd.DataFrame(
    one_hot_enconder.transform(X_test[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),

    )


    if ordenadas:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True),X_train[ordenadas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True),X_test[ordenadas].reset_index(drop=True)], axis=1)
    else:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True)], axis=1)

    comparar_modelos(nome_do_arquivo=f'{nome_do_notebook}_{tipo_de_rescalonamento}_{nome_da_funcao}',
                     dicionario_de_modelos=dicionario_de_modelos,
                     modelos_optuna=modelos_optuna,
                     dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
                     X_teste_final=X_test_final,
                     y_teste_final=y_test,
                     X_treino_final=X_res_final,
                     y_treino_final=y_res,descricao_do_notebook=descricao_do_notebook)

def preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_KNN_dois_distance(X_train,
                                                                                     X_test,
                                                                                     y_train,
                                                                                     y_test,
                                                                                     categoricas,
                                                                                     numericas,
                                                                                     dicionario_de_modelos,
                                                                                     modelos_optuna,
                                                                                      dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,
                                                                                     nome_do_notebook,
                                                                                     ordenadas=None,
                                                                                     nome_da_funcao='preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_KNN_dois_distance',
                                                                                     padronizacao=True,descricao_do_notebook=None
                                                                                     ):

    preencher_vazio_knn_2_distance=KNNImputer(n_neighbors=2,weights='distance')
    X_train[numericas]=preencher_vazio_knn_2_distance.fit_transform(X_train[numericas])

    if padronizacao:
        rescalonador=StandardScaler()
        tipo_de_rescalonamento="dados_padronizados"
    else:
        rescalonador=MinMaxScaler()
        tipo_de_rescalonamento='dados_normalizados'

    X_train[numericas]=rescalonador.fit_transform(X_train[numericas])


    moda=SimpleImputer(strategy='most_frequent')
    X_train[categoricas]=moda.fit_transform(X_train[categoricas])

    #print(X_train.isna().sum())

    X_train[categoricas]=X_train[categoricas].astype('category')

    rebalanceador= SMOTENC(random_state=42,sampling_strategy='minority',categorical_features='auto')
    X_res,y_res=rebalanceador.fit_resample(X_train,y_train)

    one_hot_enconder=OneHotEncoder(drop='first', handle_unknown='ignore',sparse_output=False)

    X_res_encoded = pd.DataFrame(
    one_hot_enconder.fit_transform(X_res[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),
    index=X_res.index
    )


    X_test[numericas]=preencher_vazio_knn_2_distance.transform(X_test[numericas])
    X_test[numericas]=rescalonador.transform(X_test[numericas])

    X_test[categoricas]=moda.transform(X_test[categoricas])

    X_test_encoded = pd.DataFrame(
    one_hot_enconder.transform(X_test[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),

    )


    if ordenadas:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True),X_train[ordenadas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True),X_test[ordenadas].reset_index(drop=True)], axis=1)
    else:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True)], axis=1)


    comparar_modelos(nome_do_arquivo=f'{nome_do_notebook}_{tipo_de_rescalonamento}_{nome_da_funcao}',
                     dicionario_de_modelos=dicionario_de_modelos,
                     modelos_optuna=modelos_optuna,
                     dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
                     X_teste_final=X_test_final,
                     y_teste_final=y_test,
                     X_treino_final=X_res_final,
                     y_treino_final=y_res,descricao_do_notebook=descricao_do_notebook)
def preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_KNN_cinco_uniform(X_train,
                                                                                     X_test,
                                                                                     y_train,
                                                                                     y_test,
                                                                                     categoricas,
                                                                                     numericas,                                                                                  
                                                                                     dicionario_de_modelos,
                                                                                     modelos_optuna,
                                                                                      dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,
                                                                                     nome_do_notebook,
                                                                                     ordenadas=None,
                                                                                     nome_da_funcao='preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_KNN_cinco_uniform(X_train',
                                                                                     padronizacao=True,descricao_do_notebook=None
                                                                                     ):

    preencher_vazio_knn_5_uniform=KNNImputer(n_neighbors=5,weights='uniform')
    X_train[numericas]=preencher_vazio_knn_5_uniform.fit_transform(X_train[numericas])

    if padronizacao:
        rescalonador=StandardScaler()
        tipo_de_rescalonamento="dados_padronizados"
    else:
        rescalonador=MinMaxScaler()
        tipo_de_rescalonamento='dados_normalizados'

    X_train[numericas]=rescalonador.fit_transform(X_train[numericas])


    moda=SimpleImputer(strategy='most_frequent')
    X_train[categoricas]=moda.fit_transform(X_train[categoricas])

    #print(X_train.isna().sum())

    X_train[categoricas]=X_train[categoricas].astype('category')

    rebalanceador= SMOTENC(random_state=42,sampling_strategy='minority',categorical_features='auto')
    X_res,y_res=rebalanceador.fit_resample(X_train,y_train)

    one_hot_enconder=OneHotEncoder(drop='first', handle_unknown='ignore',sparse_output=False)

    X_res_encoded = pd.DataFrame(
    one_hot_enconder.fit_transform(X_res[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),
    index=X_res.index
    )


    X_test[numericas]=preencher_vazio_knn_5_uniform.transform(X_test[numericas])
    X_test[numericas]=rescalonador.transform(X_test[numericas])

    X_test[categoricas]=moda.transform(X_test[categoricas])

    X_test_encoded = pd.DataFrame(
    one_hot_enconder.transform(X_test[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),

    )


    if ordenadas:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True),X_train[ordenadas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True),X_test[ordenadas].reset_index(drop=True)], axis=1)
    else:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True)], axis=1)

    comparar_modelos(nome_do_arquivo=f'{nome_do_notebook}_{tipo_de_rescalonamento}_{nome_da_funcao}',
                     dicionario_de_modelos=dicionario_de_modelos,
                     modelos_optuna=modelos_optuna,
                     dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
                     X_teste_final=X_test_final,
                     y_teste_final=y_test,
                     X_treino_final=X_res_final,
                     y_treino_final=y_res,descricao_do_notebook=descricao_do_notebook)

def preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_KNN_dois_uniform(X_train,
                                                                                     X_test,
                                                                                     y_train,
                                                                                     y_test,
                                                                                     categoricas,
                                                                                     numericas,                                                                                   
                                                                                     dicionario_de_modelos,
                                                                                     modelos_optuna,
                                                                                      dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,
                                                                                     nome_do_notebook,
                                                                                     ordenadas=None,
                                                                                     nome_da_funcao='preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_KNN_dois_uniform',
                                                                                     padronizacao=True,descricao_do_notebook=None):

    preencher_vazio_knn_2_uniform=KNNImputer(n_neighbors=2,weights='uniform')
    X_train[numericas]=preencher_vazio_knn_2_uniform.fit_transform(X_train[numericas])

    if padronizacao:
        rescalonador=StandardScaler()
        tipo_de_rescalonamento="dados_padronizados"
    else:
        rescalonador=MinMaxScaler()
        tipo_de_rescalonamento='dados_normalizados'

    X_train[numericas]=rescalonador.fit_transform(X_train[numericas])


    moda=SimpleImputer(strategy='most_frequent')
    X_train[categoricas]=moda.fit_transform(X_train[categoricas])

    #print(X_train.isna().sum())

    X_train[categoricas]=X_train[categoricas].astype('category')

    rebalanceador= SMOTENC(random_state=42,sampling_strategy='minority',categorical_features='auto')
    X_res,y_res=rebalanceador.fit_resample(X_train,y_train)

    one_hot_enconder=OneHotEncoder(drop='first', handle_unknown='ignore',sparse_output=False)

    X_res_encoded = pd.DataFrame(
    one_hot_enconder.fit_transform(X_res[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),
    index=X_res.index
    )

    

    X_test[numericas]=preencher_vazio_knn_2_uniform.transform(X_test[numericas])
    X_test[numericas]=rescalonador.transform(X_test[numericas])

    X_test[categoricas]=moda.transform(X_test[categoricas])

    X_test_encoded = pd.DataFrame(
    one_hot_enconder.transform(X_test[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),

    )


    if ordenadas:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True),X_train[ordenadas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True),X_test[ordenadas].reset_index(drop=True)], axis=1)
    else:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True)], axis=1)

    comparar_modelos(nome_do_arquivo=f'{nome_do_notebook}_{tipo_de_rescalonamento}_{nome_da_funcao}',
                     dicionario_de_modelos=dicionario_de_modelos,
                     modelos_optuna=modelos_optuna,
                     dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
                     X_teste_final=X_test_final,
                     y_teste_final=y_test,
                     X_treino_final=X_res_final,
                     y_treino_final=y_res,descricao_do_notebook=descricao_do_notebook)

def preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_mediana(X_train,
                                                                                     X_test,
                                                                                     y_train,
                                                                                     y_test,
                                                                                     categoricas,
                                                                                     numericas,                                                                                     
                                                                                     dicionario_de_modelos,
                                                                                     modelos_optuna,
                                                                                      dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,
                                                                                     nome_do_notebook,
                                                                                     ordenadas=None,
                                                                                     nome_da_funcao='preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_mediana',padronizacao=True,descricao_do_notebook=None):

    if padronizacao:
        rescalonador=StandardScaler()
        tipo_de_rescalonamento="dados_padronizados"
    else:
        rescalonador=MinMaxScaler()
        tipo_de_rescalonamento='dados_normalizados'

    X_train[numericas]=rescalonador.fit_transform(X_train[numericas])

    media=SimpleImputer(strategy='median')
    X_train[numericas]=media.fit_transform(X_train[numericas])

    moda=SimpleImputer(strategy='most_frequent')
    X_train[categoricas]=moda.fit_transform(X_train[categoricas])

    #print(X_train.isna().sum())

    X_train[categoricas]=X_train[categoricas].astype('category')



    rebalanceador= SMOTENC(random_state=42,sampling_strategy='minority',categorical_features='auto')
    X_res,y_res=rebalanceador.fit_resample(X_train,y_train)

    one_hot_enconder=OneHotEncoder(drop='first', handle_unknown='ignore',sparse_output=False)

    X_res_encoded = pd.DataFrame(
    one_hot_enconder.fit_transform(X_res[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),
    index=X_res.index
    )


    X_test[numericas]=rescalonador.transform(X_test[numericas])
    X_test[numericas]=media.transform(X_test[numericas])
    X_test[categoricas]=moda.transform(X_test[categoricas])

    X_test_encoded = pd.DataFrame(
    one_hot_enconder.transform(X_test[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),

    )


    if ordenadas:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True),X_train[ordenadas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True),X_test[ordenadas].reset_index(drop=True)], axis=1)
    else:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True)], axis=1)

    comparar_modelos(nome_do_arquivo=f'{nome_do_notebook}_{tipo_de_rescalonamento}_{nome_da_funcao}',
                     dicionario_de_modelos=dicionario_de_modelos,
                     modelos_optuna=modelos_optuna,
                     dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
                     X_teste_final=X_test_final,
                     y_teste_final=y_test,
                     X_treino_final=X_res_final,
                     y_treino_final=y_res,descricao_do_notebook=descricao_do_notebook)

def preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_media(X_train,
                                                                                     X_test,
                                                                                     y_train,
                                                                                     y_test,
                                                                                     categoricas,
                                                                                     numericas,
                                                                                     nome_do_notebook,                                                                                     
                                                                                     dicionario_de_modelos,
                                                                                     modelos_optuna,
                                                                                      dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,
                                                                                     ordenadas=None,
                                                                                     nome_da_funcao="preprocessar_com_rebalanceamento_com_SMOTENC_e_com_preenchimento_com_moda_e_media",
                                                                                     padronizacao=True,descricao_do_notebook=None):
    if padronizacao:
        rescalonador=StandardScaler()
        tipo_de_rescalonamento="dados_padronizados"
    else:
        rescalonador=MinMaxScaler()
        tipo_de_rescalonamento='dados_normalizados'

    X_train[numericas]=rescalonador.fit_transform(X_train[numericas])

    media=SimpleImputer(strategy='mean')
    X_train[numericas]=media.fit_transform(X_train[numericas])

    moda=SimpleImputer(strategy='most_frequent')
    X_train[categoricas]=moda.fit_transform(X_train[categoricas])
    #print(X_train.isna().sum())

    X_train[categoricas]=X_train[categoricas].astype('category')


    rebalanceador= SMOTENC(random_state=42,sampling_strategy='minority',categorical_features='auto')
    X_res,y_res=rebalanceador.fit_resample(X_train,y_train)

    one_hot_enconder=OneHotEncoder(drop='first', handle_unknown='ignore',sparse_output=False)

    X_res_encoded = pd.DataFrame(
    one_hot_enconder.fit_transform(X_res[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),
    index=X_res.index
    )


    X_test[numericas]=rescalonador.transform(X_test[numericas])
    X_test[numericas]=media.transform(X_test[numericas])
    X_test[categoricas]=moda.transform(X_test[categoricas])

    X_test_encoded = pd.DataFrame(
    one_hot_enconder.transform(X_test[categoricas]),
    columns=one_hot_enconder.get_feature_names_out(categoricas),

    )
    if ordenadas:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True),X_train[ordenadas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True),X_test[ordenadas].reset_index(drop=True)], axis=1)
    else:
        X_res_final = pd.concat([X_res_encoded, X_res[numericas].reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_encoded, X_test[numericas].reset_index(drop=True)], axis=1)


    comparar_modelos(nome_do_arquivo=f'{nome_do_notebook}_{tipo_de_rescalonamento}_{nome_da_funcao}',
                     dicionario_de_modelos=dicionario_de_modelos,
                     modelos_optuna=modelos_optuna,
                     dicionario_de_parametros_para_otimizacao_grid=dicionario_de_parametros_para_otimizacao_grid,
        dicionario_de_parametros_para_otimizacao_baysiana=dicionario_de_parametros_para_otimizacao_baysiana,
                     X_teste_final=X_test_final,
                     y_teste_final=y_test,
                     X_treino_final=X_res_final,
                     y_treino_final=y_res,descricao_do_notebook=descricao_do_notebook)

#Funções que compara os modelos
def comparar_modelos(nome_do_arquivo,dicionario_de_modelos,modelos_optuna, dicionario_de_parametros_para_otimizacao_grid,
                                                                                    dicionario_de_parametros_para_otimizacao_baysiana,X_teste_final,y_teste_final,X_treino_final,y_treino_final,descricao_do_notebook=None):
    modelos_optuna=modelos_optuna
    comparativo_sem_otimizacao={}
    comparativo_com_otimizacao_grid={}
    comparativo_com_otimizacao_grid_threshold={}
    comparativo_com_otimizacao_baysiana={}
    comparativo_com_otimizacao_baysiana_threshold={}

    print("\n------Modelos sem Otimização----")
    for t, m in dicionario_de_modelos.items():
        try:
            auc_sem_otimizacao,relatorio_de_metricas = rodar_modelo(modelo=m, X_teste=X_teste_final, y_teste=y_teste_final, X_treino=X_treino_final, y_treino=y_treino_final)
            comparativo_sem_otimizacao[t] = [round(auc_sem_otimizacao, 3),relatorio_de_metricas]
        except Exception as e:
            print(f"Erro ao rodar o modelo {t} sem otimização: {e}")

    print("-----Modelos com Otimização Grid----")
    try:
        melhores_modelos_grid = rodar_modelo_com_otimizacao_grid_resarch(
            modelos=dicionario_de_modelos,
            parametros=dicionario_de_parametros_para_otimizacao_grid,
            X_treinamento=X_treino_final,
            y_treinamento=y_treino_final
        )
        for t, m in melhores_modelos_grid.items():
            try:
                auc_com_otimizacao,relatorio_de_metricas = rodar_modelo(modelo=m, X_teste=X_teste_final, y_teste=y_teste_final, X_treino=X_treino_final, y_treino=y_treino_final)
                comparativo_com_otimizacao_grid[t] = [round(auc_com_otimizacao, 3),relatorio_de_metricas]
            except Exception as e:
                print(f"Erro ao rodar o modelo {t} com otimização Grid: {e}")
    except Exception as e:
        print(f"Erro ao rodar otimização Grid: {e}")

    print("-----Modelos com Otimização Grid e Threshold--------")
    for t, m in melhores_modelos_grid.items():
        try:
            auc_com_threshhold,relatorio_de_metricas, threshold, matriz_de_confusao = rodar_modelo_com_threshold(
                modelo=m,
                X_teste=X_teste_final,
                y_teste=y_teste_final,
                X_treino=X_treino_final,
                y_treino=y_treino_final
                )
            comparativo_com_otimizacao_grid_threshold[t] = {
                'auc': round(auc_com_threshhold, 3),
                'relatorio_de_metricas':relatorio_de_metricas,
                "threshold": threshold,
                "Matriz de confusao": matriz_de_confusao
            }
        except Exception as e:
            print(f"Erro ao rodar threshold para o modelo {t} com Grid: {e}")

    print("Salvar modelo")

    print("-----Modelos com Otimização Bayesiana----")
    try:
        melhores_modelos_baysiana = rodar_modelo_com_otimizacao_grid_resarch(
            modelos=dicionario_de_modelos,
            parametros=dicionario_de_parametros_para_otimizacao_baysiana,
            X_treinamento=X_treino_final,
            y_treinamento=y_treino_final
        )
        for t, m in melhores_modelos_baysiana.items():
            try:
                auc_com_otimizacao,relatorio_de_metricas = rodar_modelo(modelo=m, X_teste=X_teste_final, y_teste=y_teste_final, X_treino=X_treino_final, y_treino=y_treino_final)
                comparativo_com_otimizacao_baysiana[t] = [round(auc_com_otimizacao, 3),relatorio_de_metricas]
            except Exception as e:
                print(f"Erro ao rodar o modelo {t} com otimização Bayesiana: {e}")
    except Exception as e:
        print(f"Erro ao rodar otimização Bayesiana: {e}")

    print("-----Modelos com Otimização Bayesiana e Threshold--------")
    for t, m in melhores_modelos_baysiana.items():
        try:
            auc_com_threshhold,relatorio_de_metricas, threshold, matriz_de_confusao = rodar_modelo_com_threshold(
                modelo=m,
                X_teste=X_teste_final,
                y_teste=y_teste_final,
                X_treino=X_treino_final,
                y_treino=y_treino_final
            )
            comparativo_com_otimizacao_baysiana_threshold[t] = {
                'auc': round(auc_com_threshhold, 3),
                "threshold": threshold,
                "Matriz de confusao": matriz_de_confusao,
                "relatorio_de_metricas":relatorio_de_metricas
            }
        except Exception as e:
            print(f"Erro ao rodar threshold para o modelo {t} com Bayesiana: {e}")

    print("-----Modelos com Otimização Optuna--------")
    try:
        resultado_optuna = rodar_modelo_optuna(X_teste_final=X_teste_final,
                                                y_teste_final=y_teste_final,
                                                X_treino_final=X_treino_final,
                                                 y_treino_final=y_treino_final)
    except Exception as e:
        print(f"Erro ao rodar modelo com Optuna: {e}")

    print("-----Modelos com Otimização Optuna e Threshold--------")
    try:
        resultado_optuna_treshhold= rodar_modelo_optuna_threshold(
            X_teste_final=X_teste_final,
            y_teste_final=y_teste_final,
            X_treino_final=X_treino_final,
            y_treino_final=y_treino_final
        )
    except Exception as e:
        print(f"Erro ao rodar modelo com Optuna e Threshold: {e}")
    print("Salvar modelo")
    salvar_arquivo(nome=nome_do_arquivo,
                   comparativo_com_otimizacao_grid=comparativo_com_otimizacao_grid,
                   comparativo_com_otimizacao_grid_threshold=comparativo_com_otimizacao_grid_threshold,
                   melhores_modelos_grid=melhores_modelos_grid,
                   melhores_modelos_baysiana=melhores_modelos_baysiana,
                   comparativo_sem_otimizacao=comparativo_sem_otimizacao,
                   comparativo_com_otimizacao_baysiana=comparativo_com_otimizacao_baysiana,
                   comparativo_com_otimizacao_baysiana_threshold=comparativo_com_otimizacao_baysiana_threshold,
                   resultado_optuna=resultado_optuna,
                   resultado_optuna_treshhold=resultado_optuna_treshhold,
                   descricao_do_notebook=descricao_do_notebook)
    print('Fim')

# Salvam os arquivos
def verificar_pasta():
  pasta = f"meus_resultados/dia_{datetime.now().strftime('%d-%m-%Y')}"

  if not os.path.exists(pasta):
      os.makedirs(pasta)
      print(f"Pasta '{pasta}' criada.")
  else:
      print(f"Pasta '{pasta}' já existe.")
  return pasta

def salvar_arquivo(nome:str,
                   comparativo_com_otimizacao_grid,
                   comparativo_com_otimizacao_grid_threshold,
                   melhores_modelos_grid,
                   melhores_modelos_baysiana,
                   comparativo_sem_otimizacao,
                   comparativo_com_otimizacao_baysiana,
                   comparativo_com_otimizacao_baysiana_threshold,
                   resultado_optuna,
                   resultado_optuna_treshhold,
                   descricao_do_notebook=None
                   ):
   pasta=verificar_pasta()
   with open(f"{pasta}/modelo_{nome}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",'a') as f:
    f.write(f""" 
    Nome:{nome}\n 
    =====================================================\n
    Descricao do notebook:\n\t{descricao_do_notebook}\n
    =====================================================\n
    Modelos sem otimização
    {tabela_modelos_e_metricas(comparativo_sem_otimizacao)}\n
    =====================================================\n
    Melhores Modelos Grid
    {tabela_com_melhores_modelos(melhores_modelos_grid)}\n
    =====================================================\n
    Modelos  com otimização grid
    {tabela_modelos_e_metricas(comparativo_com_otimizacao_grid)}\n
    =====================================================\n
    Modelos com otimização grid e threshold
    {tabela_com_otimizacao_e_threshold(comparativo_com_otimizacao_grid_threshold)}\n  
    =====================================================\n
    Melhores Modelos Bayes
    {tabela_com_melhores_modelos(melhores_modelos_baysiana)}\n 
    =====================================================\n
    Modelos com otimização baysiana
    {tabela_modelos_e_metricas(comparativo_com_otimizacao_baysiana)}\n
    =====================================================\n
    Modelos com otimização baysiana e threshold 
    {tabela_com_otimizacao_e_threshold(comparativo_com_otimizacao_baysiana_threshold)}\n
    =====================================================\n  
    Resulta Optuna
    {tabela_optuna(resultado_optuna)}\n
    =====================================================\n  
    Resultado Optuna com threshold
    {tabela_com_optuna_e_threshold(resultado_optuna_treshhold)}\n  
    =====================================================\n              
             """)


 

# Funções que rodam o modelo

def rodar_modelo_com_otimizacao_baysiana(*,modelos, parametros,X_treinamento,y_treinamento):
  #print("Otimizar")
  return otimizacao_por_validacao_cruzada_baysiana(modelos=modelos.values(),
                                            nomes=modelos.keys(),
                                            parametros=parametros,
                                            X_treinamento=X_treinamento,
                                            y_treinamento=y_treinamento)

def otimizacao_por_validacao_cruzada_baysiana(modelos, nomes, parametros,X_treinamento,y_treinamento):
  melhores_modelos={}
  for modelo, nome, parametros_mod in zip(modelos, nomes, parametros):
    #print('\n -----------------------------------------------')
    #print('\n Algorítimo: ' + nome +'\n \n')
    #start = time.time()
    grid_search = BayesSearchCV(modelo, search_spaces=parametros_mod, scoring='roc_auc', n_iter=50,cv=10).fit(X_treinamento, y_treinamento)
    #print('Melhor roc_auc :', grid_search.best_score_)
    #print('Melhores parâmetros : ',grid_search.best_params_)
    #print('Melhor estimador : ', grid_search.best_estimator_)
    #print('\n')
    #print('Tempo :', time.time() - start)
    #print('\n')
    melhores_modelos[nome]=grid_search.best_estimator_
  return melhores_modelos


def rodar_modelo_com_otimizacao_grid_resarch(*,modelos, parametros,X_treinamento,y_treinamento):
  return otimizacao_por_validacao_cruzada_grid_research(modelos=modelos.values(),
                                            nomes=modelos.keys(),
                                            parametros=parametros,
                                            X_treinamento=X_treinamento,
                                            y_treinamento=y_treinamento)

def otimizacao_por_validacao_cruzada_grid_research(modelos, nomes, parametros,X_treinamento,y_treinamento):
  melhores_modelos={}
  for modelo, nome, parametros_mod in zip(modelos, nomes, parametros):
    #print('\n -----------------------------------------------')
    #print('\n Algorítimo: ' + nome +'\n \n')
    #start = time.time()
    grid_search = GridSearchCV(modelo, param_grid=parametros_mod, scoring='roc_auc', cv=10).fit(X_treinamento, y_treinamento)
    #print('Melhor roc_auc :', grid_search.best_score_)
    #print('Melhores parâmetros : ',grid_search.best_params_)
    #print('Melhor estimador : ', grid_search.best_estimator_)
    #print('\n')
    #print('Tempo :', time.time() - start)
    #print('\n')
    melhores_modelos[nome]=grid_search.best_estimator_
  return melhores_modelos

def rodar_modelo(*,modelo,X_treino,y_treino,X_teste,y_teste):
  modelo=treinar_modelo(modelo=modelo,caracteristicas_para_treino=X_treino,alvo_para_treino=y_treino)
  predicao=predizer(modelo=modelo,caracteristicas_para_teste=X_teste)
  auc,relatorio_de_metricas= avaliar_modelo(alvo_para_teste=y_teste,
                  predicao=predicao)
  return auc,relatorio_de_metricas

def objective(trial, X_treino_final,y_treino_final):
    modelos_optuna= {
    'Decision Tree': DecisionTreeClassifier,
    'Random Forest': RandomForestClassifier,
    'XGB': XGBClassifier,
    'CatBoost': CatBoostClassifier,
    'LightBoost': LGBMClassifier
    }
    model_name = trial.suggest_categorical('model', list(modelos_optuna.keys()))

    if model_name == 'Decision Tree':
        params = {
            'max_depth': trial.suggest_categorical('dt_max_depth', [3, 5, 10]),
            'min_samples_split': trial.suggest_categorical('dt_min_samples_split', [2, 5]),
            'min_samples_leaf': trial.suggest_categorical('dt_min_samples_leaf', [1, 2]),
            'criterion': trial.suggest_categorical('dt_criterion', ['gini', 'entropy']),
            'random_state': 108
        }

    elif model_name == 'Random Forest':
        max_depth_options = [10]  # Removido None para evitar erro
        params = {
            'n_estimators': trial.suggest_categorical('rf_n_estimators', [100, 200]),
            'max_depth': trial.suggest_categorical('rf_max_depth', max_depth_options),
            'min_samples_split': trial.suggest_categorical('rf_min_samples_split', [2, 5]),
            'min_samples_leaf': trial.suggest_categorical('rf_min_samples_leaf', [1, 2]),
            'random_state': 108
        }

    elif model_name == 'XGB':
        params = {
            'n_estimators': trial.suggest_categorical('xgb_n_estimators', [100, 200]),
            'learning_rate': trial.suggest_categorical('xgb_learning_rate', [0.01, 0.1]),
            'max_depth': trial.suggest_categorical('xgb_max_depth', [3, 6]),
            'random_state': 108,
            'eval_metric': 'logloss'
        }

    elif model_name == 'CatBoost':
        params = {
            'iterations': trial.suggest_categorical('cat_iterations', [100, 200]),
            'depth': trial.suggest_categorical('cat_depth', [4, 6, 10]),
            'learning_rate': trial.suggest_categorical('cat_learning_rate', [0.01, 0.1]),
            'random_seed': 108,
            'silent': True
        }

    elif model_name == 'LightBoost':
        params = {
            'n_estimators': trial.suggest_categorical('lgb_n_estimators', [100, 200]),
            'learning_rate': trial.suggest_categorical('lgb_learning_rate', [0.01, 0.1]),
            'num_leaves': trial.suggest_categorical('lgb_num_leaves', [31, 50]),
            'max_depth': trial.suggest_categorical('lgb_max_depth', [10, -1]),
            'random_state': 108,
            'verbose': -1
        }

    model = modelos_optuna[model_name](**params)
    score = cross_val_score(model, X_treino_final, y_treino_final, cv=3, scoring='roc_auc').mean()
    return score

def rodar_modelo_optuna(X_treino_final,X_teste_final,y_teste_final,y_treino_final):
    study=rodar_optuna(X_treino_final,y_treino_final)
    modelo_optuna,nome_do_modelo,parametros=melhor_modelo_optuna(study=study)
    auc,relatorio_de_metricas=rodar_modelo(modelo=modelo_optuna,X_treino=X_treino_final,X_teste=X_teste_final,y_teste=y_teste_final,y_treino=y_treino_final)
    resultado={'Modelo':f'{nome_do_modelo}:{parametros}', 'AUC':auc, "Relatorio":relatorio_de_metricas}
    return resultado

def rodar_modelo_optuna_threshold(X_treino_final,X_teste_final,y_teste_final,y_treino_final):
    study=rodar_optuna(X_treino_final,y_treino_final)
    modelo_optuna,nome_do_modelo,parametros=melhor_modelo_optuna(study=study)
    auc_com_threshhold,relatorio_de_metricas,threshold,matriz_de_confusao=rodar_modelo_com_threshold(modelo=modelo_optuna,X_treino=X_treino_final,X_teste=X_teste_final,y_teste=y_teste_final,y_treino=y_treino_final)
    resultado={'nome_do_modelo':nome_do_modelo,
               'parametros':parametros,
               'auc':round(auc_com_threshhold,3),
               "threshold":threshold,
               "Matriz de confusao":matriz_de_confusao,'Relatorio de Métricas':relatorio_de_metricas}
    return resultado


def rodar_optuna(X_treino_final,y_treino_final):
    objective_func = partial(objective, X_treino_final=X_treino_final, y_treino_final=y_treino_final)
    study = optuna.create_study(direction='maximize')
    study.optimize(objective_func, n_trials=50)
    print(study.best_trial.params)
    return study

def melhor_modelo_optuna(study):
    melhor_parametro=study.best_trial.params
    nome_do_melhor_modelo=melhor_parametro['model']
    if melhor_parametro['model']== 'Decision Tree':
        params = {
            'max_depth':melhor_parametro['dt_max_depth'],
            'min_samples_split':melhor_parametro['dt_min_samples_split'],
            'min_samples_leaf':melhor_parametro['dt_min_samples_leaf'],
            'criterion':melhor_parametro['dt_criterion'],
        }
        modelo=DecisionTreeClassifier(**params)

    elif melhor_parametro['model']== 'Random Forest':
        params = {
            'n_estimators':melhor_parametro['rf_n_estimators'],
            'max_depth':melhor_parametro['rf_max_depth'],
            'min_samples_split':melhor_parametro['rf_min_samples_split'],
            'min_samples_leaf':melhor_parametro['rf_min_samples_leaf'],
        }
        modelo=RandomForestClassifier(**params)

    elif melhor_parametro['model']== 'XGB':
        params = {
            'n_estimators':melhor_parametro['xgb_n_estimators'],
            'learning_rate':melhor_parametro['xgb_learning_rate'],
            'max_depth':melhor_parametro['xgb_max_depth'],
            'eval_metric': 'logloss'
        }
        modelo=XGBClassifier(**params)

    elif melhor_parametro['model']== 'CatBoost':
        params = {
            'iterations':melhor_parametro['cat_iterations'],
            'depth':melhor_parametro['cat_depth'],
            'learning_rate':melhor_parametro['cat_learning_rate'],
        }
        modelo=CatBoostClassifier(**params)

    elif melhor_parametro['model']== 'LightBoost':
        params = {
            'n_estimators':melhor_parametro['lgb_n_estimators'],
            'learning_rate':melhor_parametro['lgb_learning_rate'],
            'num_leaves':melhor_parametro['lgb_num_leaves'],
            'max_depth':melhor_parametro['lgb_max_depth'],
        }
        modelo=LGBMClassifier(**params)
    return modelo,nome_do_melhor_modelo,params

# Funções que avaliam os modelos 
def avaliar_modelo(*,alvo_para_teste,predicao):
    try:
      auc=roc_auc_score(alvo_para_teste,predicao)
      relatorio_de_metricas=classification_report(alvo_para_teste,predicao)
    except:
      print('Não é possivel realizar ROC-AUC')
    return auc,relatorio_de_metricas

# Predizer
def predizer(*,modelo,caracteristicas_para_teste):
    predicao=modelo.predict(caracteristicas_para_teste)
    return predicao
def predizer_com_probabilidade(*,modelo,caracteristicas_para_teste):
  predicao=modelo.predict_proba(caracteristicas_para_teste)
  return predicao[:,1]


def rodar_modelo_com_threshold(*,modelo,X_treino,y_treino,X_teste,y_teste):
  #print("Treino do modelo")
  modelo=treinar_modelo(modelo=modelo,caracteristicas_para_treino=X_treino,alvo_para_treino=y_treino)
  #print('Predições')
  predicao=predizer_com_probabilidade(modelo=modelo,caracteristicas_para_teste=X_teste)
  #print("Avaliação do modelos")
  predicao,threshold,matriz_de_confusao=aplicar_melhor_threshold(y_teste=y_teste,predicao=predicao)
  auc,relatorio_de_metricas=avaliar_modelo(alvo_para_teste=y_teste,predicao=predicao)
  return auc,relatorio_de_metricas,threshold,matriz_de_confusao

def encontrar_threshold_otimo(*,y_teste, predicao):
    fpr, tpr, thresholds = roc_curve(y_teste, predicao)
    youden_index = tpr - fpr
    idx_melhor = np.argmax(youden_index)
    melhor_threshold = thresholds[idx_melhor]
    #print(f" - Threshold ótimo: {melhor_threshold:.3f}")
    return melhor_threshold

def aplicar_melhor_threshold(*,y_teste, predicao):
    threshold= encontrar_threshold_otimo(y_teste=y_teste, predicao=predicao)
    predicao = (predicao >= threshold).astype(int)
    #print(confusion_matrix(y_teste, predicao))
    return predicao,threshold,confusion_matrix(y_teste, predicao)

def treinar_modelo(*,modelo,caracteristicas_para_treino,alvo_para_treino):
  modelo.fit(caracteristicas_para_treino,alvo_para_treino)
  return modelo

# Funções que treinam o modelos

def treinar_modelo(*,modelo,caracteristicas_para_treino,alvo_para_treino):
  modelo.fit(caracteristicas_para_treino,alvo_para_treino)
  return modelo

def separar_treino_e_teste(*,dados,alvo,proporcaoParaTeste):
  X,y=separar_variaveis_preditoras_e_alvo(dados=dados,alvo=alvo)
  X_train,X_test,y_train,y_test=train_test_split(X, y, test_size=proporcaoParaTeste, random_state=180,stratify=y)
  return X_train,X_test,y_train,y_test

def limitar_outliers_min_max(dados, numericas):
    for coluna in numericas:
        Q1 = dados[coluna].quantile(0.25)
        Q3 = dados[coluna].quantile(0.75)
        IQR = Q3 - Q1

        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR

        dados[coluna] = np.where(
            dados[coluna] < limite_inferior,
            limite_inferior,
            np.where(
                dados[coluna] > limite_superior,
                limite_superior,
                dados[coluna]
            )
        )
    return dados[numericas]

def separar_treino_e_teste_sem_outiliers(*,dados,alvo,proporcaoParaTeste,numericas):
  X,y=separar_variaveis_preditoras_e_alvo(dados=dados,alvo=alvo)
  X_train,X_test,y_train,y_test=train_test_split(X, y, test_size=proporcaoParaTeste, random_state=180,stratify=y)
  X_train[numericas]=limitar_outliers_min_max(X_train,numericas)
  return X_train,X_test,y_train,y_test

def separar_variaveis_preditoras_e_alvo(*, dados,alvo):
  y=dados[alvo]
  X=dados.drop([alvo],axis='columns')
  return X, y

def codificar_variaveis_alvo_em_zero_e_um(*,dados,alvo,controle=1):
  dados.loc[:, alvo] = dados[alvo].apply(lambda x: 0 if x == controle else 1)
  return dados

def tabela_modelos_e_metricas(dicionario):
    tabela=[]
    print('Dicionario abaixo:')
    print(dicionario.items())
    for modelos, metricas in dicionario.items():
        modelo = str(modelos)
        metrica =metricas
        tabela.append([modelo,metrica[0],metrica[1]])
    
    cabecalho=['Modelo','AUC','Relatorio de Métricas']
    tabela_formatada= tabulate(tabela,headers=cabecalho,tablefmt='grid')
    
    return tabela_formatada

def tabela_com_melhores_modelos(dicionario):
    tabela=[]
    for modelo, metrica in dicionario.items():
        modelo = modelo
        metrica =metrica
        tabela.append([modelo,metrica])
    
    cabecalho=['Modelo','Parametros']
    tabela_formatada= tabulate(tabela,headers=cabecalho,tablefmt='grid')
    
    return tabela_formatada

def tabela_com_otimizacao_e_threshold(dicionario):
    tabela = []
    for modelo, valores in dicionario.items():
        auc = valores['auc']
        relatorio=valores['relatorio_de_metricas']
        threshold = valores['threshold']
        vn, fp = valores['Matriz de confusao'][0]
        fn, vp = valores['Matriz de confusao'][1]
        tabela.append([modelo, auc,relatorio, threshold, vp, fn, fp, vn])

    
    cabecalho = ["Modelo", "AUC","Relatorio", "Threshold", "VP", "FN", "FP", "VN"]

    
    tabela_formatada = tabulate(tabela, headers=cabecalho, tablefmt="grid")

    return tabela_formatada

def tabela_optuna(dicionario):
    modelo = dicionario['Modelo']
    metrica =dicionario['AUC']
    relatorio=dicionario['Relatorio']
    
    tabela=[[modelo,metrica,relatorio]]
    
    cabecalho=['Modelo','AUC',"Relatorio"]
    tabela_formatada= tabulate(tabela,headers=cabecalho,tablefmt='grid')
    
    return tabela_formatada

def tabela_com_optuna_e_threshold(dicionario):
    nome_do_modelo= dicionario['nome_do_modelo']
    parametros=dicionario['parametros']
    auc = dicionario['auc']
    relatorio=dicionario['Relatorio de Métricas']
    threshold = dicionario['threshold']
    vn, fp = dicionario['Matriz de confusao'][0]
    fn, vp = dicionario['Matriz de confusao'][1]

    tabela=[[str(nome_do_modelo),str(parametros), str(auc),str(relatorio), str(threshold), str(vp), str(fn), str(fp), str(vn)]]

    
    cabecalho = ["Modelo","Parametros", "AUC","Relatorio", "Threshold", "VP", "FN", "FP", "VN"]

    
    tabela_formatada = tabulate(tabela, headers=cabecalho, tablefmt="grid")

    return tabela_formatada

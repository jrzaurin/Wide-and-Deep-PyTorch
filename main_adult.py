import os
import torch
import pickle
import numpy as np
import pandas as pd

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from pathlib import Path
from torchvision import transforms

from pytorch_widedeep.data_utils.prepare_data import prepare_data

from pytorch_widedeep.models.wide_deep import WideDeep, WideDeepLoader

from pytorch_widedeep.initializers import Normal, Uniform, XavierNormal, XavierUniform
from pytorch_widedeep.optimizers import MultipleOptimizers, Adam, SGD, RAdam
from pytorch_widedeep.lr_schedulers import MultipleLRScheduler, StepLR, MultiStepLR

# -> HERE. CHECK callbacks and metrics. move modules and move on
from pytorch_widedeep.models.callbacks import EarlyStopping, ModelCheckpoint
from pytorch_widedeep.models.metrics import BinaryAccuracy

import pdb

if __name__ == '__main__':

    use_cuda = torch.cuda.is_available()

    wd = pickle.load(open('data/wd_dataset.p', 'rb'))
    model = WideDeep(output_dim=1, wide_dim=wd.wide.shape[1],
        embeddings_input = wd.cat_embeddings_input,
        embeddings_encoding_dict=wd.cat_embeddings_encoding_dict,
        continuous_cols=wd.continuous_cols,
        deep_column_idx=wd.deep_column_idx)

    initializers = {'wide': Normal, 'deepdense':Normal}
    optimizers = {'wide': Adam, 'deepdense':Adam}
    schedulers = {'wide': StepLR(step_size=5), 'deepdense':StepLR(step_size=5)}
    callbacks = [EarlyStopping, ModelCheckpoint(filepath='model_weights/wd_out.pt')]
    metrics = [BinaryAccuracy]

    model.compile(method='logistic', initializers=initializers, optimizers=optimizers,
        lr_schedulers=schedulers, callbacks=callbacks, metrics=metrics)
    model.fit(wd.wide.astype('float32'), wd.deep_dense, wd.target, n_epochs=4, batch_size=256, val_split=0.2)
    preds = model.predict_proba(wd.wide.astype('float32'), wd.deep_dense)
    pdb.set_trace()

    # wd_dataset = pickle.load(open("data/airbnb/wide_deep_data/wd_dataset.p", "rb"))
    # params = dict()
    # params['wide'] = dict(
    #     wide_dim = wd_dataset['train']['wide'].shape[1]
    #     )
    # params['deep_dense'] = dict(
    #     embeddings_input = wd_dataset['cat_embeddings_input'],
    #     embeddings_encoding_dict = wd_dataset['cat_embeddings_encoding_dict'],
    #     continuous_cols = wd_dataset['continuous_cols'],
    #     deep_column_idx = wd_dataset['deep_column_idx'],
    #     hidden_layers = [64,32],
    #     dropout = [0.5]
    #     )
    # params['deep_text'] = dict(
    #     vocab_size = len(wd_dataset['vocab'].itos),
    #     embedding_dim = wd_dataset['word_embeddings_matrix'].shape[1],
    #     hidden_dim = 64,
    #     n_layers = 2,
    #     rnn_dropout = 0.5,
    #     spatial_dropout = 0.1,
    #     padding_idx = 1,
    #     attention = False,
    #     bidirectional = True,
    #     embedding_matrix = wd_dataset['word_embeddings_matrix']
    #     )
    # params['deep_img'] = dict(
    #     pretrained = True,
    #     freeze='all',
    #     )

    # model = WideDeep(output_dim=1, **params)
    # # optimizer={'widedeep': ['Adam', 0.1]}
    # # lr_scheduler = {'widedeep': ['MultiStepLR', [3,5,7], 0.1]}
    # optimizer=dict(
    #     wide=['Adam', 0.1],
    #     deep_dense=['Adam', 0.01],
    #     deep_text=['RMSprop', 0.01,0.1],
    #     deep_img= ['Adam', 0.01]
    #     )
    # lr_scheduler=dict(
    #     wide=['StepLR', 3, 0.1],
    #     deep_dense=['StepLR', 3, 0.1],
    #     deep_text=['MultiStepLR', [3,5,7], 0.1],
    #     deep_img=['MultiStepLR', [3,5,7], 0.1]
    #     )
    # model.compile(method='regression', optimizer=optimizer, lr_scheduler=lr_scheduler)
    # if use_cuda:
    #     model = model.cuda()
    # # # ImageNet metrics
    # # mean=[0.485, 0.456, 0.406] #RGB
    # # std=[0.229, 0.224, 0.225]  #RGB
    # # cv2 reads BGR
    # mean=[0.406, 0.456, 0.485] #BGR
    # std=[0.225, 0.224, 0.229]  #BGR
    # transform  = transforms.Compose([
    #     transforms.ToTensor(),
    #     transforms.Normalize(mean=mean, std=std)
    # ])
    # train_set = WideDeepLoader(wd_dataset['train'], transform, mode='train')
    # valid_set = WideDeepLoader(wd_dataset['valid'], transform, mode='train')
    # test_set = WideDeepLoader(wd_dataset['test'], transform, mode='test')
    # train_loader = torch.utils.data.DataLoader(dataset=train_set,
    #     batch_size=64, num_workers=4, shuffle=True)
    # valid_loader = torch.utils.data.DataLoader(dataset=valid_set,
    #     batch_size=64, num_workers=4, shuffle=True)
    # test_loader = torch.utils.data.DataLoader(dataset=test_set,
    #     batch_size=32,shuffle=False)
    # model.fit(n_epochs=10, train_loader=train_loader, eval_loader=valid_loader)
    # preds = model.predict(test_loader)
    # y = wd_dataset['test']['target']
    # print(np.sqrt(mean_squared_error(y, preds)))
    # # save
    # MODEL_DIR = Path('data/models')
    # if not MODEL_DIR.exists(): os.makedirs(MODEL_DIR)
    # torch.save(model.state_dict(), MODEL_DIR/'widedeep.pkl')

    # load
    # model = WideDeep(1, **params)
    # model.compile(method='regression', optimizer=optimizer, lr_scheduler=lr_scheduler)
    # model.load_state_dict(torch.load('model/widedeep.pkl'))
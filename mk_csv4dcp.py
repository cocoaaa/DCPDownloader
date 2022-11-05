#!/usr/bin/env python
# coding: utf-8
# Creates csv file containing <img_fp>,<label_str> for images downloaded from DCP.
# 
# Usage:
# To generate dcp{n_data}_train.csv and dcp{n_data}_test.csv needed for fastsearch repo, run
# python mk_csv4dcp.py --data_dir ./dcp_images --n_data 10000 --out_dir ./dcp_csv
# 
# To generate csv's using all images filepaths in data_dir, drop argument --n_data:
# python mk_csv4dcp.py --data_dir ./dcp_images  --out_dir ./dcp_csv
#  

import csv
from pathlib import Path
from PIL import Image
import numpy as np
import argparse

def main(args):
    
    # header = ['filepath', 'label']
    # data_dir = Path('/nas/home/haejinso/DCP/outs/'
    # data_dir = Path('/data/hayley-old/DCPDownloader/nbs/outs/')
    data_dir = Path(args.data_dir)
    print_every = 1_000

    c_invalid_names = 0
    c_invalid_formats = 0
    data = []
    for i, img_fp in enumerate(data_dir.iterdir()):
        # if i > 10: #debug
        #     break
        # print(img_fp)
        
        if (i+1)%print_every == 0:
            print(i, end='...', flush=True)
        
        #parse: {vid}_{lat}_{lon}-{descrp}.jpg
        img_bn = img_fp.stem #no suffix
        # vid, lat, lng, descr = img_bn.split('_')
        # print(vid, lat, lng, descr)
        
        img_fp = str(img_fp.absolute())
        
        if img_fp.startswith('"'):
            c_invalid_names += 1
            img_fp = img_fp.strip('"')
            
        try: 
            # img_np = plt.imread(img_fp)
            img_np = np.asarray(Image.open(img_fp))
        except:
            print('cannot read img: ', img_fp)
            c_invalid_formats += 1
            continue
            
        data.append([str(img_fp), img_bn])
        
        
    print(f'count imgs with starts with quote: {c_invalid_names}')
    print(f'count imgs that cannot be read: {c_invalid_formats}')
    print(f'valid imgs: {len(data)}')


    # out_dir = Path('./dcp_csv2')
    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True)
    with open(out_dir/'dcp_all_imgfps.csv', 'w') as f:
        writer = csv.writer(f)
        # write multiple rows
        writer.writerows(data)

    # train, test split
    seed = 123
    np.random.seed(seed) 
    np.random.shuffle(data)  #inplace

    # selec n-data images
    n_data = args.n_data
    if n_data is not None:
        data = data[:n_data]
    else:
        n_data = len(data)

    p_train = 0.7
    n_train = int(n_data * p_train)
    train_data, test_data = data[:n_train], data[n_train:]
    dict_data = {'train': train_data, 
                'test': test_data}
    # write  to file
    # with open('all_imgfps.csv', 'w', encoding='UTF8', newline='') as f:
    for mode, d in dict_data.items():
        with open(out_dir/f'dcp{n_data}_{mode}.csv', 'w') as f:
            writer = csv.writer(f)
            # write multiple rows
            writer.writerows(d)
            print(f'Done writing csv for {mode}: {len(d)}')
            
            
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description="Create csv files of DCP images for train, test sets",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
                                     
    parser.add_argument(
        '--data_dir', type=str, required=True,
        help='Dir containing DCP images'
    )
    parser.add_argument(
        '--n_data', type=int, default=None,
        help='Number of images to use by randomly sampling from images in data_dir. Default: use all images in data_dir.'
    )
    
    parser.add_argument(
        '--out_dir', type=str, required=True,
        help='Output dir to save train and test csv files'
    )
    args = parser.parse_args()
    
    main(args)
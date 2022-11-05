# Downalod images from Degree Confluence Project (DCP)


## How to install package and download images from DCP
Two packages will be needed (beautifulsoup4 and requests):
`conda install -c conda-forge bs4 requests`

Currently `main.py` is set to test run for the first 11 visits.
You could try it first to see if it works: the downloaded images will be saved to outs folder (which will be created if not existing).
If it works, then you can comment out line 119 and uncomment line 122 to download images from all visits

## How to generate train/test csv files of $img_fp, $label_str based on the download images
Once the images are downloaded, you can run:

`python mk_csv4dcp.py --data_dir ./outs  --out_dir ./dcp_csv`

 which will geneate the train and test csv's and save to the dcp_csv folder
 This will use all images in the data_dir.

If you want to test with smaller number of images, you can pass argument to `--n_dat`a which will use `n_data` images in `data_dir`, randomly sampled:

` python mk_csv4dcp.py --data_dir ./outs --n_data 10000 --out_dir ./dcp_csv`



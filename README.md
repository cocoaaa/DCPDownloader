# Downalod images from Degree Confluence Project (DCP)
![dcp-banner](media/dcp_banner.jpeg)

[Degree Confluence Project (DCP)](https://confluence.org/infoconf.php) is a voluntary project to 
"visit each of the lat, lng integer degree intersections in the world, and to take pictures at each
location".
Each report contains images taken at the confluence point, as well as rich narrative on the stories
of people who took the visit.

The first visit posted on the website dates back to 1996. Feb. 20, by Alex Jarrett (project founder)
and Peter Cline  at 43N 72W in New Hampshire, USA.

This repo contains code to parse the html of each visit report and download images and  useful
metadata about the visit, such as lat, lng and text description uploaded from the visitor.


## How to install package and download images from DCP
Two packages will be needed (beautifulsoup4 and requests):
`conda install -c conda-forge bs4 requests`

Currently `main.py` is set to test run for the first 11 visits.
You could try it first to see if it works: the downloaded images will be saved to an output folder, which can be specified as an argument of `--out_dir` (default: `outs`). The output folder will be created if not existing.
If the code works on retrieving and parsing the first 11 visits, then you can comment out line 119 and 122 to download images from _all_ visits

## How to generate train/test csv files of $img_fp, $label_str based on the download images
Once the images are downloaded, you can run:

`python mk_csv4dcp.py --data_dir ./outs  --out_dir ./dcp_csv`

 which will geneate the train and test csv's and save to the dcp_csv folder
 This will use all images in the data_dir.

If you want to test with smaller number of images, you can pass argument to `--n_dat`a which will use `n_data` images in `data_dir`, randomly sampled:

` python mk_csv4dcp.py --data_dir ./outs --n_data 10000 --out_dir ./dcp_csv`



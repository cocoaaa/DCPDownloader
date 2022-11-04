Two packages will be needed (beautifulsoup4 and requests):
`conda install -c conda-forge bs4 requests`

Currently `main.py` is set to test run for the first 11 visits.
You could try it first to see if it works: the downloaded images will be saved to outs folder (which will be created if not existing).
If it works, then you can comment out line 119 and uncomment line 122 to download images from all visits

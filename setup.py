# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '1.0',
    packages     = find_packages(),
    package_data={
        'shop_crawler': ['shop_crawler/spiders/*.csv']
    },
    include_package_data = True,
    data_files = [('csv_file',['shop_crawler/spiders/sample_21site_utf8.csv'])],
    entry_points = {'scrapy': ['settings = shop_crawler.settings']},
    zip_safe=False,
)

import os
from datetime import date

# set up logger
today = date.today()
from pixBoards.log_utils import setup_logger

logger = setup_logger(__name__)

import yaml

from pixBoards.arguments import args


def load_config(yml_path):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


if args.config:
    configFile = args.config
    # print('configfile is ' + configFile)
else:
    configFile = "config.yml"
config = load_config(configFile)

# masterDir = config["masterDir"]

padding = config["padding"]
imgs_per_page = config["page_size"]
# print(f'imgs per page are {imgs_per_page}'  )


class page:
    def __init__(self, page_number, total_pages, images, file_location):
        self.page_number = page_number  # Current page number
        self.images = images  # image list for the page
        self.total_pages = total_pages
        self.file_location = file_location


from math import ceil


class board:
    def __init__(
        self,
        name,
        output_file_loc,
        image_paths,
        # outputDir,
        images_per_page=None,  # deprecated
        paginate=True,
        upload=False,
        dummy_status=False,
        img_list_status=False,
    ):
        self.name = name
        self.image_paths = image_paths
        self.pages = []  # will be storing a list of instances of class, page.
        self.images_per_page = imgs_per_page
        self.output_file_loc = output_file_loc
        self.upload_status = upload
        self.paginate_status = paginate
        self.link_hash_map = {} if self.upload_status else None
        # self.outputDir = outputDir
        # self.subfolders = []
        self.nested_boards = []
        self.dummy_status = dummy_status
        self.img_list_status = img_list_status

    def paginate_board(self):
        total_images = len(self.image_paths)
        # logger.info(f'total images = {total_images}')
        total_pages = ceil(total_images / self.images_per_page)
        output_base = self.output_file_loc
        for i in range(total_pages):

            start = i * self.images_per_page
            end = start + self.images_per_page
            page_images = self.image_paths[start:end]

            # if self.output_file_loc[-5:] == '.html':
            #     file_loc = self.output_file_loc.replace('.html', f'_{(i+1):0{padding}}.html') # padded to 3 digits.
            #     logger.info('output loc has .html')
            # else:
            #     # file_loc = self.output_file_loc + f'_{(i+1):0{padding}}.html'
            #     file_loc = os.path.join(self.output_file_loc, self.name) + f'_{(i+1):0{padding}}.html'
            #     logger.info('output loc doesn\' have .html' + file_loc)
            #     logger.info('board name is ' + self.name)
            file_loc = (
                os.path.join(output_base, self.name) + f"_{(i+1):0{padding}}.html"
            )
            Page = page(
                page_number=i + 1,
                total_pages=total_pages,
                images=page_images,
                file_location=file_loc,
            )
            self.pages.append(Page)
            logger.debug(
                f"Finished with - Board: {self.name}, page {i + 1} of {total_pages}"
            )

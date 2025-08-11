import os
from typing import List, Union
import base64
from functools import reduce
from IPython.display import display, HTML

from bluer_objects import storage, mlflow


def get_image_base64(filename):
    with open(filename, "rb") as f:
        data = f.read()
        return "data:image/gif;base64," + base64.b64encode(data).decode("utf-8")


def imshow(
    list_of_files: Union[
        List[List[str]],
        List[str],
        str,
    ],
    dryrun: bool = False,
):
    if not isinstance(list_of_files, list):
        list_of_files = [list_of_files]
    list_of_files = [(row if isinstance(row, list) else [row]) for row in list_of_files]

    html = "".join(
        ["<table>"]
        + reduce(
            lambda x, y: x + y,
            [
                ["<tr>"]
                + [
                    '<td><img src="{}"></td>'.format(get_image_base64(filename))
                    for filename in row
                ]
                + ["</tr>"]
                for row in list_of_files
            ],
            [],
        )
        + ["</table>"]
    )

    if not dryrun:
        display(HTML(html))


def upload(
    object_name: str,
    public: bool = False,
    zip: bool = False,
) -> bool:
    if not storage.upload(
        object_name=object_name,
        public=public,
        zip=zip,
    ):
        return False

    if public or zip:
        return True

    return mlflow.log_run(object_name)

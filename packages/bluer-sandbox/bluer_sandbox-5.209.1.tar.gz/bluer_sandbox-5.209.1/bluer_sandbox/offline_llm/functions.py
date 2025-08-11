from blueness import module

from bluer_options.env import CYAN, NC
from bluer_objects import file, objects
from bluer_objects.metadata import post_to_object

from bluer_sandbox import NAME
from bluer_sandbox.logger import logger


NAME = module.name(__file__, NAME)


def post_process(object_name: str) -> bool:
    logger.info(f"{NAME}.post_process({object_name})")

    success, prompt = file.load_text(
        objects.path_of(
            object_name=object_name,
            filename="prompt.txt",
        )
    )
    if not success:
        return success
    prompt = [line for line in prompt if line]

    success, output = file.load_text(
        objects.path_of(
            object_name=object_name,
            filename="output.txt",
        )
    )
    if not success:
        return success
    output = [line for line in output if line]

    print("\n".join([CYAN] + output + [NC]))

    return post_to_object(
        object_name,
        "post_process",
        {
            "prompt": prompt,
            "output": output,
        },
    )

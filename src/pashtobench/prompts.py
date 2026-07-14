"""Build the model prompt for each item.

Translation items hold only the source text, so I wrap them with a direction
instruction. For the other tasks the item prompt is already the full prompt.
"""

from pashtobench.schema import Item

_EN_TO_PBT = (
    "Translate the following English text into Pashto. Reply with only the translation.\n\n"
)
_PBT_TO_EN = (
    "Translate the following Pashto text into English. Reply with only the translation.\n\n"
)


def build_prompt(item: Item) -> str:
    if item.task == "translation":
        lead = _EN_TO_PBT if item.direction == "en-pbt" else _PBT_TO_EN
        return lead + item.prompt
    return item.prompt

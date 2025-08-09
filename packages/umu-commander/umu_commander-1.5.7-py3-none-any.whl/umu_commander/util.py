from umu_commander import VERSION
from umu_commander.classes import Element, ExitCode, Group, Value


def strings_to_values(values: list[str]) -> list[Value]:
    return [Value(value) for value in values]


def _selection_set_valid(
    selection_elements: list[Element] | None, selection_groups: list[Group] | None
):
    if (selection_elements is None or len(selection_elements) == 0) and (
        len(selection_groups) == 0
        or all([len(group.elements) == 0 for group in selection_groups])
    ):
        return False
    else:
        return True


def _print_selection_group(
    elements: list[Element], enum_start_idx: int, tab: bool = True
):
    prefix: str = "\t" if tab else ""
    print(
        *[
            f"{prefix}{idx}) {element.value} {element.info}"
            for idx, element in enumerate(elements, start=enum_start_idx)
        ],
        sep="\n",
    )
    print("")


def _translate_index_to_selection(
    selection_index: int,
    selection_elements: list[Element],
    selection_groups: list[Group],
) -> Element:
    len_counter: int = 0

    if selection_elements is not None:
        selection_groups.insert(0, Group(elements=selection_elements))

    for group in selection_groups:
        len_counter += len(group.elements)
        if len_counter > selection_index:
            break

    return Element(
        group.identity, group.elements[selection_index - len_counter].value, ""
    )


def get_selection(
    prompt: str,
    selection_elements: list[Element] | None,
    selection_groups: list[Group] | None,
) -> Element:
    if not _selection_set_valid(selection_elements, selection_groups):
        print("Nothing to select from.")
        exit(ExitCode.INVALID_SELECTION.value)

    if selection_groups is None:
        selection_groups = []

    while True:
        enum_start_idx: int = 1

        print(prompt)

        if selection_elements is not None:
            _print_selection_group(selection_elements, enum_start_idx, tab=False)
            enum_start_idx += len(selection_elements)

        for group_idx, group in enumerate(selection_groups):
            if len(group.elements) == 0:
                continue

            print(group.label)
            _print_selection_group(group.elements, enum_start_idx)

            enum_start_idx += len(group.elements)

        selection_index: str = input("? ")
        print("")
        if selection_index.isdecimal():
            selection_index: int = int(selection_index) - 1
            if enum_start_idx - 1 > selection_index >= 0:
                break

    return _translate_index_to_selection(
        selection_index, selection_elements, selection_groups
    )


def print_help():
    print(
        f"umu-commander {VERSION}",
        "Interactive CLI tool to augment umu-launcher as well as help you manage its Proton versions.",
        "",
        "For details, usage, and more, see the README.md file, or visit https://github.com/Mpaxlamitsounas/umu-commander.",
        sep="\n",
    )

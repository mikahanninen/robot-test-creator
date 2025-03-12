import click
import os
from RPA.Excel.Files import Files

run_types = {
    "tests": {
        "columns": ["test case", "steps", "libraries", "manual steps"],
        "keywords": ["task", "steps"],
        "texts": ["Test Cases"],
    },
    "tasks": {
        "columns": ["task", "steps", "libraries", "manual steps"],
        "keywords": ["task", "steps"],
        "texts": ["Tasks"],
    },
}


def process_arguments(row, tests_text, variables, variable_index):
    """Process arguments from a row and return the argument text and count.

    Args:
        row: The row containing arguments
        tests_text: Current test text being built
        variables: List of variables
        variable_index: Current variable index
    Returns:
        tuple of (modified tests_text, argument_count)
    """
    argument_count = 0
    for idx in range(1, 20):
        ar = f"arg{idx}"
        if ar in row.keys() and row[ar]:
            argument_count += 1
            try:
                converted_list = (
                    str(row[ar]).replace("[", "").replace("]", "").split(",")
                )
                if len(converted_list) > 1:
                    variable_name = f"@{{LIST_{variable_index}}}"
                    variables.append(
                        f"{variable_name}{' '*4}{'    '.join(converted_list)}"
                    )
                    tests_text += f"{' '*4}{variable_name.replace('@', '$')}"
                else:
                    tests_text += f"{' '*4}{row[ar]}"
            except TypeError:
                pass
    return tests_text, argument_count


@click.command()
@click.option("--input_excel", "-i", required=True, help="Excel with test cases")
@click.option(
    "--output_dir", "-o", default=".", help="Output directory for Robot files"
)
@click.option(
    "--no-title-case", "-nt", is_flag=True, help="Disable title case for names"
)
def main(input_excel, output_dir, no_title_case):
    print(f"Title case disabled: {no_title_case}")
    library = Files()
    library.open_workbook(input_excel)
    sheets = library.list_worksheets()

    for sheet in sheets:
        sheet = sheet.strip()
        print(f"\nProcessing sheet: {sheet}")
        testcases = []
        variables = []
        tests_text = ""
        keywords = dict()
        keyword_manual_steps = dict()  # Store manual steps for each keyword
        keyword_manual_args = dict()  # Store arguments for manual steps
        current_keyword = None
        variable_index = 1
        settings_text = f"Documentation  Created from sheet {sheet} of {input_excel}\n"
        table = library.read_worksheet_as_table(name=sheet, header=True)

        # Get all columns first
        first_row = next(table.iter_dicts())
        print(f"Columns in sheet: {list(first_row.keys())}")
        has_manual_steps = "manual steps" in first_row
        has_libraries = "libraries" in first_row
        run_type = "tests" if "test case" in first_row else "tasks"
        print(f"Sheet has manual steps column: {has_manual_steps}")
        print(f"Sheet has libraries column: {has_libraries}")
        print(f"Sheet run type: {run_type}")

        # Read the table again for processing
        table = library.read_worksheet_as_table(name=sheet, header=True)

        # First pass: collect all libraries to add them at the beginning of settings
        libraries = set()  # Use set to avoid duplicates
        if has_libraries:
            for row in table.iter_dicts():
                if row.get("libraries"):
                    libraries.add(row["libraries"])
            # Add libraries to settings text
            for lib in sorted(libraries):  # Sort for consistent order
                settings_text += f"Library  {lib}\n"

        # Read the table again for the main processing
        table = library.read_worksheet_as_table(name=sheet, header=True)

        for row in table.iter_dicts():
            r_type = run_types[run_type]["columns"][0]
            if row[r_type]:
                testcasename = row[r_type] if no_title_case else row[r_type].title()
                if len(testcases) > 0:
                    tests_text += "\n"
                tests_text += testcasename
                testcases.append(testcasename)
                current_keyword = None
            else:
                if not row["steps"]:
                    # Check if this is a manual step for the current keyword
                    if current_keyword and has_manual_steps and row.get("manual steps"):
                        print(
                            f"Found manual step for {current_keyword}: {row['manual steps']}"
                        )
                        if current_keyword not in keyword_manual_steps:
                            keyword_manual_steps[current_keyword] = []
                            keyword_manual_args[current_keyword] = []

                        # Process arguments for manual steps
                        manual_step_text = row["manual steps"]
                        args_text = ""
                        args_text, arg_count = process_arguments(
                            row, args_text, variables, variable_index
                        )

                        if arg_count > 0:
                            keyword_manual_args[current_keyword].append(
                                args_text.strip()
                            )
                        else:
                            keyword_manual_args[current_keyword].append("")

                        keyword_manual_steps[current_keyword].append(manual_step_text)
                    continue

                keyword_name = (
                    row["steps"] if no_title_case else row["steps"].title()
                ).replace(" ", "_")
                current_keyword = keyword_name
                tests_text += f"{' '*4}{keyword_name.replace('_', ' ')}"

                if keyword_name not in keywords.keys():
                    keywords[keyword_name] = 0

                # Check for manual steps in the same row as the keyword
                if has_manual_steps and row.get("manual steps"):
                    print(
                        f"Found manual step in keyword row for {keyword_name}: {row['manual steps']}"
                    )
                    if keyword_name not in keyword_manual_steps:
                        keyword_manual_steps[keyword_name] = []
                        keyword_manual_args[keyword_name] = []

                    # Process arguments for manual steps in keyword row
                    manual_step_text = row["manual steps"]
                    args_text = ""
                    args_text, arg_count = process_arguments(
                        row, args_text, variables, variable_index
                    )

                    if arg_count > 0:
                        keyword_manual_args[keyword_name].append(args_text.strip())
                    else:
                        keyword_manual_args[keyword_name].append("")

                    keyword_manual_steps[keyword_name].append(manual_step_text)

                # Process regular step arguments
                tests_text, argument_count = process_arguments(
                    row, tests_text, variables, variable_index
                )
                if argument_count > keywords[keyword_name]:
                    keywords[keyword_name] = argument_count
            tests_text += "\n"

        robotfilename = os.path.join(output_dir, f"{sheet}.robot")
        print("Creating Robot file:", robotfilename)
        with open(robotfilename, "w") as robotfile:
            for tc in testcases:
                print(f"\tCreating {r_type}: {tc}")
            robotfile.write("*** Settings ***\n" + settings_text)
            if len(variables) > 0:
                robotfile.write("\n*** Variables ***\n")
                for var in variables:
                    robotfile.write(f"{var}\n")
            if tests_text:
                robotfile.write(
                    f"\n*** {run_types[run_type]['texts'][0]} ***\n{tests_text}"
                )
            print(f"keyword manual steps: {keyword_manual_steps}")
            print(f"keyword manual args: {keyword_manual_args}")
            if len(keywords) > 0:
                robotfile.write("\n*** Keywords ***")
                for kw, val in keywords.items():
                    robotfile.write(f'\n{kw.replace("_", " ")}')
                    if val > 0:
                        robotfile.write(f"\n{' '*4}[Arguments]")
                        for idx in range(1, val + 1):
                            robotfile.write(f"{' '*4}${{arg{idx}}}")
                        robotfile.write("\n")
                        # Add manual steps as comments if they exist
                        if kw in keyword_manual_steps:
                            for i, manual_step in enumerate(keyword_manual_steps[kw]):
                                args = keyword_manual_args[kw][i]
                                if args:
                                    # Format with 4 spaces prefix, 2 spaces between args, and comment at end
                                    formatted_args = args.replace("    ", "  ")
                                    robotfile.write(
                                        f"{' '*4}{manual_step}  {formatted_args}    # manual step\n"
                                    )
                                else:
                                    robotfile.write(
                                        f"{' '*4}{manual_step}    # manual step\n"
                                    )
                        for idx in range(1, val + 1):
                            robotfile.write(f"{' '*4}Log{' '*4}${{arg{idx}}}\n")
                    else:
                        robotfile.write("\n")
                        # Add manual steps as comments if they exist
                        if kw in keyword_manual_steps:
                            for i, manual_step in enumerate(keyword_manual_steps[kw]):
                                args = keyword_manual_args[kw][i]
                                if args:
                                    # Format with 4 spaces prefix, 2 spaces between args, and comment at end
                                    formatted_args = args.replace("    ", "  ")
                                    robotfile.write(
                                        f"{' '*4}{manual_step}  {formatted_args}    # manual step\n"
                                    )
                                else:
                                    robotfile.write(
                                        f"{' '*4}{manual_step}    # manual step\n"
                                    )
                        else:
                            robotfile.write(f"{' '*4}No Operation\n")


if __name__ == "__main__":
    main()

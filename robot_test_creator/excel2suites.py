import click
from RPA.Excel.Files import Files


@click.command()
@click.option("--input_excel", "-i", required=True, help="Excel with test cases")
def main(input_excel):
    library = Files()
    library.open_workbook(input_excel)
    sheets = library.list_worksheets()

    for sheet in sheets:
        sheet = sheet.strip()
        testcases = []
        variables = []
        tests_text = ""
        keywords = dict()
        variable_index = 1
        settings_text = f"Documentation  Created from sheet {sheet} of {input_excel}\n"
        table = library.read_worksheet_as_table(name=sheet, header=True)
        for row in table.iter_dicts():
            if row["test case"]:
                testcasename = row["test case"].title()
                tests_text += testcasename
                testcases.append(testcasename)
            else:
                keyword_name = row["steps"].title().replace(" ", "_")
                tests_text += f"{' '*4}{keyword_name.replace('_', ' ')}"
                if keyword_name not in keywords.keys():
                    keywords[keyword_name] = 0
                argument_count = 0
                for idx in range(1, 10):
                    ar = f"arg{idx}"
                    if ar in row.keys() and row[ar]:
                        argument_count += 1

                        try:
                            converted_list = (
                                str(row[ar])
                                .replace("[", "")
                                .replace("]", "")
                                .split(",")
                            )
                            if len(converted_list) > 1:
                                variable_name = f"@{{LIST_{variable_index}}}"
                                variables.append(
                                    f"{variable_name}{' '*4}{'    '.join(converted_list)}"
                                )
                                tests_text += (
                                    f"{' '*4}{variable_name.replace('@', '$')}"
                                )
                            else:
                                tests_text += f"{' '*4}{row[ar]}"
                        except TypeError:
                            pass
                if argument_count > keywords[keyword_name]:
                    keywords[keyword_name] = argument_count
            tests_text += "\n"

        robotfilename = f"{sheet}.robot"
        print("Creating Robot file:", robotfilename)
        with open(robotfilename, "w") as robotfile:
            for tc in testcases:
                print("\tCreating Test Case:", tc)
            robotfile.write("*** Settings ***\n" + settings_text)
            if len(variables) > 0:
                robotfile.write("\n*** Variables ***\n")
                for var in variables:
                    robotfile.write(f"{var}\n")
            if tests_text:
                robotfile.write("\n*** Test Cases ***\n" + tests_text)
            if len(keywords) > 0:
                robotfile.write("\n*** Keywords ***\n")
                for kw, val in keywords.items():
                    robotfile.write(kw.replace("_", " "))
                    if val > 0:
                        robotfile.write("\n\t[Arguments]")
                        for idx in range(1, val + 1):
                            robotfile.write(f"{' '*4}${{arg{idx}}}")
                        robotfile.write("\n")
                        for idx in range(1, val + 1):
                            robotfile.write(f"\tLog{' '*4}${{arg{idx}}}\n")
                    else:
                        robotfile.write("\n\tNo Operation\n")


if __name__ == "__main__":
    main()

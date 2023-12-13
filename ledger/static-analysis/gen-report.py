from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import os


class ErrorRecord:
    def __init__(self, id, severity, message, file, line, column):
        self.id = id
        self.severity = severity
        self.message = message
        self.file = file
        self.line = line
        self.column = column


def get_error_list(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    error_list = []

    for error in root.iter('error'):
        id = error.get('id')
        severity = error.get('severity')
        message = error.get('msg')
        location = error.find('location')
        file = location.get('file')
        line = location.get('line')
        column = location.get('col')
        error_list.append(ErrorRecord(id, severity, message, file, line, column))

    return error_list


def get_report_paths(input_dir):
    common_report = os.path.join(input_dir, "common.xml")
    signer_report = os.path.join(input_dir, "signer.xml")
    ui_report = os.path.join(input_dir, "ui.xml")
    tcpsigner_report = os.path.join(input_dir, "tcpsigner.xml")

    if not os.path.isfile(common_report):
        raise Exception(f"File not found: {common_report}")

    if not os.path.isfile(signer_report):
        raise Exception(f"File not found: {signer_report}")

    if not os.path.isfile(ui_report):
        raise Exception(f"File not found: {ui_report}")

    if not os.path.isfile(tcpsigner_report):
        raise Exception(f"File not found: {tcpsigner_report}")

    return [common_report, signer_report, ui_report, tcpsigner_report]


def generate_report(report, cppcheck_report):
    error_list = get_error_list(cppcheck_report)
    if len(error_list) == 0:
        report.write("### No errors found!\n\n")
    else:
        report.write(f"### {len(error_list)} errors:\n\n")
        report.write("| File | Message | Severity |\n")
        report.write("|------|---------|----------|\n")
        for error in error_list:
            report.write(f"| {error.file}:{error.line} |"
                         f" {error.message} |"
                         f" {error.severity} |\n")


def main():
    parser = ArgumentParser(description="Generates a report from cppcheck XML outputs")
    parser.add_argument(
        "-d",
        "--inputDir",
        dest="input_dir",
        help="Directory containing cppcheck XML output files.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="Output file path (Markdown report).",
        required=True,
    )
    options = parser.parse_args()

    try:
        [common_report, signer_report,
         ui_report, tcpsigner_report] = get_report_paths(options.input_dir)

        # If an old report already exists, remove it
        if os.path.exists(options.output_path):
            os.remove(options.output_path)

        # Create and open report file
        with open(options.output_path, "w") as report:
            # Write report title
            report.write("# rsk-powhsm Static Analysis Report\n\n")
            # Write reports for each module
            report.write("## Common\n\n")
            generate_report(report, common_report)
            report.write("****\n")
            report.write("## Signer\n\n")
            generate_report(report, signer_report)
            report.write("****\n")
            report.write("## UI\n\n")
            generate_report(report, ui_report)
            report.write("****\n")
            report.write("## TCPSigner\n\n")
            generate_report(report, tcpsigner_report)

        print(f"Report generated at {options.output_path}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

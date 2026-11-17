import pandas as pd
import csv
from io import StringIO


def xlsx_to_csv(input_file, output_file, delimiter=','):
    """
    Converts an XLSX file containing CSV-like data in a single column
    into a properly structured CSV file.

    Parameters:
        input_file (str): Path to the input XLSX file.
        output_file (str): Path to the output CSV file.
        delimiter (str): Delimiter separating the values (default: ',').
    """

    # Read the Excel file without interpreting the first row as headers
    df = pd.read_excel(input_file, header=None, dtype=str)

    # Extract the first column
    rows = df.iloc[:, 0].dropna()

    # Parse each row as CSV data
    parsed_rows = [
        next(csv.reader([row], delimiter=delimiter))
        for row in rows
    ]

    # Write the resulting structured data to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(parsed_rows)

    print(f"Successfully converted {input_file} to {output_file}")



def analyze_tables(nuclei, cytoplasm, output):
    columns = [
        'patient_record',
        'patient_name',
        'group',
        'exam_date',
        'exam_instance',
        'datetime'
    ]

    number_of_cells = {
        'normal': 0,
        'suspeita': 0
    }

    # Read inputs CSV
    with open(cytoplasm, 'r', newline='', encoding='utf-8') as cytoplasm_file:
        with open(nuclei, 'r', newline='', encoding='utf-8') as nuclei_file:
            nuclei_reader = csv.DictReader(nuclei_file)
            cytoplasm_reader = csv.DictReader(cytoplasm_file)

            # Read the first rows
            nuclei_first_row = next(nuclei_reader, None)
            cytoplasm_first_row = next(cytoplasm_reader, None)

            if (nuclei_first_row is None) or (cytoplasm_first_row is None):
                raise ValueError("One of the input CSV is empty.")

            # Extract the requested fields
            result = {column: nuclei_first_row[column] for column in columns}

            nucleus_pixel_count = 0
            cytoplasm_pixel_count = 0

            for row in nuclei_reader:
                value = row['type'].strip().lower()

                if value in ('intermediaria', 'superficial'):
                    number_of_cells['normal'] += 1

                elif value in ('suspeita'):
                    number_of_cells['suspeita'] += 1

                nucleus_pixel_count += float(row['nucleus_pixel_count'])

            for row in cytoplasm_reader:
                cytoplasm_pixel_count += float(row['cluster_pixel_count'])

            result['number_of_normal_cells'] = number_of_cells['normal']
            result['number_of_suspect_cells'] = number_of_cells['suspeita']

            result['normal_cells_%'] = "{:.2f}".format(number_of_cells['normal']*100 / (number_of_cells['normal'] + number_of_cells['suspeita']))
            result['suspect_cells_%'] = "{:.2f}".format(number_of_cells['suspeita']*100 / (number_of_cells['normal'] + number_of_cells['suspeita']))

            result['mean_nucleus_pixel_count'] = "{:.2f}".format(nucleus_pixel_count / (number_of_cells['normal'] + number_of_cells['suspeita']))
            result['mean_cytoplasm_pixel_count'] = "{:.2f}".format(cytoplasm_pixel_count / (number_of_cells['normal'] + number_of_cells['suspeita']))
            result['cytoplasm_nucleus_ratio'] = "{:.2f}".format(float(result['mean_cytoplasm_pixel_count']) / float(result['mean_nucleus_pixel_count']))


            columns = [
            'patient_record',
            'patient_name',
            'group',
            'exam_date',
            'exam_instance',
            'number_of_normal_cells',
            'number_of_suspect_cells',
            'normal_cells_%',
            'suspect_cells_%',
            'mean_nucleus_pixel_count',
            'mean_cytoplasm_pixel_count',
            'cytoplasm_nucleus_ratio',
            'datetime'
        ]

        # Write output CSV
        with open(output, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=columns)
            writer.writeheader()
            writer.writerow(result)



def main():

    #xlsx_to_csv('nuclei_202611041046.xlsx', 'nuclei_202611041046.csv', delimiter=',')

    analyze_tables(nuclei='nuclei_202611041046.csv',
        cytoplasm='cluster_cytoplasm_anucleate_202611041046.csv',
        output='papanicolau.csv')


if __name__ == "__main__":
    main()
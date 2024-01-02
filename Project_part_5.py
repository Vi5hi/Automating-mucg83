import subprocess
import pandas as pd
import csv
from time import time

start = time()


# To replace D by E from the number
def transform_D_to_E(num):
    numeric_value = float(num.replace("D", "e"))
    return numeric_value


# To find the lowest value of the DIFFT and SHEART
def find_DIFFT_SHEART(output):
    sheart_min = float('inf')
    difft_min = float('inf')
    sheart_index = None
    difft_index = None
    lines = output.strip().split('\n')

    for line in lines:
        if 'SHEART' in line and 'DIFFT' in line:
            header_line = line.split()
            sheart_index = header_line.index('SHEART')
            difft_index = header_line.index('DIFFT')
            continue

        if '***** FTO VERSUS TEMPERATURE ****' in line:
            break

        if sheart_index is not None and difft_index is not None:
            line_values = line.split()
            if len(line_values) > max(sheart_index, difft_index):
                sheart_value = transform_D_to_E(line_values[sheart_index])
                difft_value = transform_D_to_E(line_values[difft_index])
                sheart_min = min(sheart_min, sheart_value)
                difft_min = min(difft_min, difft_value)

    return sheart_min, difft_min


# finding the minimum of NUCLEATION and GROWTH temperature
def highest_of_n_g(output):
    n = find_temperature('NUCLEATION LIMITED BAINITE START TEMP', output)
    g = find_temperature('GROWTH LIMITED BAINITE START TEMPERATURE', output)
    if n:
        nucleation_bainite_start = (find_temperature('NUCLEATION LIMITED BAINITE START TEMP', output).split()[-2])
        updated_n = float(calling(nucleation_bainite_start))
    else:
        updated_n = -100000000
    if g:
        growth_bainite_start = (find_temperature('GROWTH LIMITED BAINITE START TEMPERATURE', output).split()[-2])
        updated_g = float(calling(growth_bainite_start))
    else:
        updated_g = -100000000
    return max(updated_n, updated_g)


# Function to find the martensitic and bainitic start temperatures
def find_temperature(text, x):
    desired_line = None
    lines = x.split('\n')

    for line in lines:
        if text in line:
            desired_line = line
            break
    return desired_line


def calling(temperature):
    if '=' in temperature:
        temp = temperature.replace("=", "")
        return temp
    else:
        return temperature

# Function to input the compositions (Send inputs to the program)
def input_composition(x):

    for number in x.tolist():
        input_data = str(number) + "\n"
        p.stdin.write(input_data.encode())
        p.stdin.flush()


# Function to input the identification number
def input_identification(x):
    input_data = str(x) + "\n"
    p.stdin.write(input_data.encode())
    p.stdin.flush()


# Function to extract a line containing specific text(CTEM = 250)
def find_text(num, output):
    output_lines = output.split('\n')
    desired_line = None
    ctemp_index = None

    for line in output_lines:
        if 'CTEMP' in line:
            header_line = line.split()
            ctemp_index = header_line.index('CTEMP')
            continue

        if ctemp_index is not None and str(num) in line.split()[ctemp_index]:
            desired_line = line
            break

    return desired_line


# Path of the csv data (Compositions)
composition_path = 'D:\\Bharat Stuff\\MTech Project\\last batch\\final_sub_batch_6.csv'
df = pd.read_csv(composition_path)
# df_orig = pd.read_csv(composition_path)
# df = df_orig.drop('Fe', axis=1)
# df.insert(loc=6, column='V', value=0)  # Adding the 0 column in 6th index named as V
# df.insert(loc=10, column='W', value=0)  # Adding the 0 column in 10th index named as W
compositions = df.to_numpy()

# Path of the .exe file (Map Steel)
exe_path = 'D:\\Bharat Stuff\\MTech Project\\mucg83'

rows = compositions.shape[0]
columns = compositions.shape[1]

# Number of compositions for what data will be generated
number_of_compositions = rows
# Print the data for CTEMP
search_CTEMP_for = 250

# Names of the column in the CSV file
column_names = ['C', 'Si', 'Mn', 'Ni', 'Mo', 'Cr', 'V', 'Co', 'Cu', 'Al', 'W', 'Ms','Bs', 'FPRO', 'FPROA',
                'GMAX', 'CTEMP', 'X NUCLEUS', 'FSON', 'XEQ', 'XEQ50', 'FTO', 'XTO', 'VOLF', 'X44', 'XTO400', 'SHEART',
                'DIFFT', 'SHEART_MIN', 'DIFFT_MIN', 'DIFFT_MIN/SHEART_MIN']

# Path of the output CSV file
output_file_path = 'D:\\Bharat Stuff\\MTech Project\\mapsteelfinalbatch\\map_steel_data_batch_6.csv'

# Number of compositions to process in one batch
batch_size = 500

# Initialize a list to store the data points for each batch
batch_data = []

count = 1  # To count the batch number

# Main loop for the iteration of the Map Steel Program and storing data directly into the CSV file
with open(output_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(column_names)  # Write the column names to the CSV file

    for i in range(number_of_compositions):
        comp = compositions[i, :]

        # Open the (Map Steel) program with Popen
        p = subprocess.Popen([exe_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Calling the functions to input the data
        input_identification(i + 1)
        input_composition(comp)

        # Close the program's stdin to indicate no more input
        p.stdin.flush()  # Flush any remaining input data
        p.stdin.close()

        # Get output from the program
        output, error = p.communicate()

        # Decode the output
        output = output.decode()
        # print(output)

        # Here the martensite start temperatures for the different compositions are extracted
        martensite_start_temp = (find_temperature('MARTENSITE START TEMPERATURE', output).split()[-2])
        updated_martensite = float(calling(martensite_start_temp))
        extracted_data = list(comp)  # Initialize extracted_data list with the composition values
        extracted_data.append(updated_martensite)  # Appending the martensite temp value in list
        extracted_data.append(highest_of_n_g(output))  # Appending the highest value of bainitic start temp
        sheart_min, difft_min = find_DIFFT_SHEART(output)  # Extracting the minimum value of DIFFT and SHEART time
        extracted_data.extend(find_text(search_CTEMP_for, output).split())  # Extending the list with the thermodynamic values
        extracted_data.append(sheart_min)  # Appending the minimum SHEART time to the list
        extracted_data.append(difft_min)  # Appending the minimum DIFFT time to the list
        extracted_data.append(round((difft_min / sheart_min), 3))  # Appending the ration of min(DIFFT) and min(SHEART)
        del extracted_data[26]  # Deleting unnecessary value

        for a, element in enumerate(extracted_data):
            modified_data = []
            if isinstance(element, str) and "D" in element:
                modified_data = [
                    float(element.replace("D", "E")) if isinstance(element, str) and 'D' in element else float(element)
                    for
                    element in extracted_data]
                extracted_data = modified_data

        batch_data.append(extracted_data)

        # Write the data to CSV in batches
        if len(batch_data) >= batch_size:
            writer.writerows(batch_data)
            batch_data = []  # Clear the list after writing to CSV
            print(f'Batch {count} printed in CSV.')
            count += 1

    # Write if any remaining data in the batch_data list to CSV
    if batch_data:
        writer.writerows(batch_data)
        print(f'Remaining data also printed in CSV.')
finish = time()
print(f"Time taken by the program: {finish - start} seconds.")

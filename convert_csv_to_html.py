import csv
import os
import sys
import datetime
import json
import urllib.parse

def convert_csv_to_html(csv_file_path, html_file_path, template_path):
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            headers = next(reader) # Get headers
            raw_data = []
            for row in reader:
                raw_data.append(row)

            # Update headers list for internal processing
            if 'Rates(30Years)' in headers:
                rates_column_index = headers.index('Rates(30Years)')
                headers[rates_column_index] = 'Rates' # Rename for consistency

            # Process data to store all rates for each credit union
            processed_credit_unions_data = []
            for row_data in raw_data:
                credit_union_name = row_data[headers.index('CreditUnion')]
                link = row_data[headers.index('Link')]
                rates_raw = row_data[headers.index('Rates')] # Use new header name

                parsed_rates = []
                if rates_raw != "None":
                    for rate_entry in rates_raw.split('|'):
                        parts = rate_entry.rsplit('-', 1) # Split from right, once
                        if len(parts) == 2:
                            loan_type_full = parts[0].strip()
                            rate_str = parts[1].strip()
                            numeric_rate = None
                            try:
                                numeric_rate = float(rate_str.strip('%'))
                            except ValueError:
                                pass

                            # Determine simplified loan type for filtering and display
                            simplified_type = "Conventional"
                            year_term = None
                            if "ARM" in loan_type_full.upper():
                                simplified_type = "ARM"
                            elif "30 Year Fixed" in loan_type_full:
                                year_term = "30 Years"
                            elif "20 Year Fixed" in loan_type_full:
                                year_term = "20 Years"
                            elif "15 Year Fixed" in loan_type_full:
                                year_term = "15 Years"
                            elif "Jumbo 30 Year Fixed" in loan_type_full:
                                simplified_type = "Jumbo"
                                year_term = "30 Years"
                            elif "Jumbo 15 Year Fixed" in loan_type_full:
                                simplified_type = "Jumbo"
                                year_term = "15 Years"

                            parsed_rates.append({
                                'loanTypeFull': loan_type_full,
                                'rateStr': rate_str,
                                'numericRate': numeric_rate,
                                'simplifiedType': simplified_type,
                                'yearTerm': year_term # Will be None for ARM or other types
                            })

                # Determine Overall Best Program and Best Rate based on 30Year and ARM
                best_30_year_rate = None
                best_arm_rate = None
                best_arm_program_full_name = "N/A"

                for rate_info in parsed_rates:
                    # Ignore 15 Year Fixed rates for Overall Best Program and Best Rate
                    if rate_info['yearTerm'] == "15 Years":
                        continue

                    if rate_info['simplifiedType'] == "ARM" and rate_info['numericRate'] is not None:
                        if best_arm_rate is None or rate_info['numericRate'] < best_arm_rate:
                            best_arm_rate = rate_info['numericRate']
                            best_arm_program_full_name = rate_info['loanTypeFull']
                    elif rate_info['yearTerm'] == "30 Years" and rate_info['numericRate'] is not None and rate_info['simplifiedType'] != "Jumbo":
                        if best_30_year_rate is None or rate_info['numericRate'] < best_30_year_rate:
                            best_30_year_rate = rate_info['numericRate']

                overall_best_program = "N/A"
                final_best_rate = "N/A"

                if best_30_year_rate is not None and (best_arm_rate is None or best_30_year_rate <= best_arm_rate):
                    overall_best_program = "30Year"
                    final_best_rate = best_30_year_rate
                elif best_arm_rate is not None:
                    overall_best_program = best_arm_program_full_name
                    final_best_rate = best_arm_rate

                processed_credit_unions_data.append({
                    'CreditUnion': credit_union_name,
                    'Link': link,
                    'Rates': rates_raw, # Use new header name
                    'OverallBestProgram': overall_best_program,
                    'BestRate': final_best_rate,
                    'parsedRates': parsed_rates,
                })
            # Convert processed data to a URL-encoded JSON string for safe embedding in JS
            json_data_for_js_encoded = urllib.parse.quote(json.dumps(processed_credit_unions_data))

        # Read the HTML template file
        with open(template_path, mode='r', encoding='utf-8') as template_file:
            html_template = template_file.read()

        # Get today's date and format it
        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d") # e.g., "2026-03-17"

        # Replace the placeholders in the template with the URL-encoded JSON data and the date
        html_content = html_template.replace('{json_data_for_js_encoded}', json_data_for_js_encoded)
        html_content = html_content.replace('{{ current_date }}', formatted_date)

        with open(html_file_path, mode='w', encoding='utf-8') as outfile:
            outfile.write(html_content)
        print("Successfully converted '{}' to '{}'".format(csv_file_path, html_file_path))
    except FileNotFoundError:
        print("Error: One of the required files (CSV, HTML template) was not found.", file=sys.stderr)
    except Exception as e:
        print("An error occurred: {}".format(e), file=sys.stderr)

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    csv_input_path = os.path.join(script_dir, "mortgage_rates.csv")
    html_output_path = os.path.join(script_dir, "mortgage_rates.html")
    html_template_path = os.path.join(script_dir, "mortgage_rates_base64_template.html")
    
    convert_csv_to_html(csv_input_path, html_output_path, html_template_path)

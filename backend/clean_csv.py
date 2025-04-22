import pandas as pd
import re
import csv

# Function to clean text while preserving multilingual characters
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[!@#$%^&*()_+\-=\[\]{};:"\\\',.<>?/]', '', text)
    return text

# Step 1: Preprocess the existing dataset to fix any formatting issues
existing_file = "faq_data_cleaned.csv"
temp_existing_file = "faq_data_cleaned_temp.csv"

# Check if the existing file exists and has the expected number of rows
expected_existing_rows = 2655  # From the previous successful run
try:
    with open(existing_file, 'r', encoding='utf-8') as infile:
        row_count = sum(1 for row in infile) - 1  # Subtract 1 for the header
    if row_count != expected_existing_rows:
        print(f"Warning: {existing_file} has {row_count} rows, expected {expected_existing_rows}. Skipping existing dataset.")
        existing_df = pd.DataFrame(columns=['text', 'label'])
    else:
        with open(existing_file, 'r', encoding='utf-8') as infile, open(temp_existing_file, 'w', encoding='utf-8', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
            
            # Write the header
            header = next(reader)
            writer.writerow(header)
            
            # Process each row
            row_count = 0
            for row in reader:
                if len(row) == 0 or all(cell.strip() == '' for cell in row):
                    continue
                if len(row) != 2:
                    if len(row) > 2:
                        text = ','.join(row[:-1])
                        label = row[-1]
                        writer.writerow([text, label])
                    else:
                        continue
                else:
                    writer.writerow(row)
                row_count += 1
        print(f"Preprocessed existing dataset with {row_count} rows (excluding header).")
        
        # Load the preprocessed existing dataset
        existing_df = pd.read_csv(temp_existing_file, quoting=csv.QUOTE_ALL)
        print(f"Loaded preprocessed existing dataset with {len(existing_df)} rows.")
except FileNotFoundError:
    print(f"Existing file {existing_file} not found. Starting with an empty dataset.")
    existing_df = pd.DataFrame(columns=['text', 'label'])
except Exception as e:
    print(f"Error loading existing dataset: {e}. Starting with an empty dataset.")
    existing_df = pd.DataFrame(columns=['text', 'label'])

# Step 2: Preprocess the new dataset to fix unescaped commas and encoding issues
new_file = "new_data.csv"
temp_file = "new_data_temp.csv"

# Try different encodings to read the file
encodings = ['utf-8', 'windows-1252', 'iso-8859-1']
new_data_rows = None
for encoding in encodings:
    try:
        with open(new_file, 'r', encoding=encoding) as infile, open(temp_file, 'w', encoding='utf-8', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
            
            # Write the header
            header = next(reader)
            writer.writerow(header)
            
            # Process each row
            for row in reader:
                if len(row) != 2:
                    text = ','.join(row[:-1])
                    label = row[-1]
                    writer.writerow([text, label])
                else:
                    writer.writerow(row)
        print(f"Successfully read {new_file} with {encoding} encoding.")
        break
    except UnicodeDecodeError as e:
        print(f"Failed to read {new_file} with {encoding} encoding: {e}")
        continue
    except Exception as e:
        print(f"Error reading {new_file}: {e}")
        exit(1)
else:
    print(f"Could not read {new_file} with any of the encodings: {encodings}")
    exit(1)

# Step 3: Load the preprocessed new dataset
try:
    new_df = pd.read_csv(temp_file, quoting=csv.QUOTE_ALL, on_bad_lines='warn')
    print(f"Loaded preprocessed new dataset with {len(new_df)} rows.")
except Exception as e:
    print(f"Failed to load preprocessed file: {e}")
    exit(1)

# Step 4: Clean the new dataset
new_df = new_df.dropna()
new_df['text'] = new_df['text'].apply(clean_text)
new_df = new_df.drop_duplicates(subset=['text'], keep='first')
print(f"After cleaning, new dataset has {len(new_df)} rows.")

# Step 5: Merge the datasets
combined_df = pd.concat([existing_df, new_df], ignore_index=True)
combined_df = combined_df.drop_duplicates(subset=['text'], keep='first')
print(f"After merging and removing duplicates, combined dataset has {len(combined_df)} rows.")

# Step 6: Save the combined dataset
output_file = "faq_data_cleaned.csv"
combined_df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
print(f"Combined cleaned data saved to {output_file}")

# Step 7: Check class balance
class_counts = combined_df['label'].value_counts()
print("\nClass distribution in the combined dataset:")
print(class_counts)
print(f"FAQ (label=1) percentage: {class_counts[1] / len(combined_df) * 100:.2f}%")
print(f"Non-FAQ (label=0) percentage: {class_counts[0] / len(combined_df) * 100:.2f}%")
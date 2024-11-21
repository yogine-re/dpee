import os
from file_handler import detect_file_type
from file_handler import extract_text_from_digital_pdf
from file_handler import save_pdf_content_to_dir


def test_detect_file_type(input_directory):
    files = os.listdir(input_directory)

    for file in files:
        file_path = os.path.join(input_directory, file)
        file_type = detect_file_type(file_path)
        print(f"Detected file type of {file}: {file_type}")

def test_extract_text_from_pdf(input_file):
    extracted_content = extract_text_from_digital_pdf(input_file)
    print(extracted_content[3]['images'])

def test_save_pdf_content_to_dir(input_file, output_dir):
    save_pdf_content_to_dir(input_file, output_dir)

def main():
    # detect file types in a directory
    input_dir = "input/16513-Bonnie-Lane"
   # test_detect_file_type(input_dir)

    # extract text from a digital pdf file
    input_file = "input/16513-Bonnie-Lane/10_16513_Bonnie_Lne_Home.pdf"
    #test_extract_text_from_pdf(input_file)

    # save the extracted content to a directory
    output_dir = "output/16513-Bonnie-Lane/10_16513_Bonnie_Lne_Home"
    test_save_pdf_content_to_dir(input_file, output_dir)



if __name__ == "__main__":
    main()
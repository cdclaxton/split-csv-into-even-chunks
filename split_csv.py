import csv
import matplotlib.pyplot as plt
import numpy as np
import os


# Increase the maximum field size to handle large files
csv.field_size_limit(10000000)


def calc_length(s):
    """Calculate the number of characters excluding delimiters and encapsulators."""

    # Preconditions
    assert isinstance(s, list)

    return sum([len(x) for x in s])


def calc_doc_lengths(filepath, delimiter, encapsulator):
    """Calculate the length of the documents."""

    # Preconditions
    assert os.path.exists(filepath), f"File doesn't exist: {filepath}"
    assert isinstance(delimiter, str)
    assert isinstance(encapsulator, str)

    # List of the lengths of each document
    doc_lengths = []

    with open(filepath, 'r', encoding='utf8') as fp:
        reader = csv.reader(fp, delimiter=delimiter, quotechar=encapsulator)

        num_rows_read = 0

        for row in reader:
            doc_lengths.append(calc_length(row))
            num_rows_read += 1

    print(f"Read {num_rows_read} rows from {filepath}")

    return doc_lengths


def spacing_ratio(n):
    """Calculate n-1 even ratios."""

    # Preconditions
    assert n > 1

    return [x/n for x in list(range(1, n))]


def calc_break_points(cum_doc_lengths, num_files):
    """Calculate breaks (row indicies) in the input file."""

    # Preconditions
    assert isinstance(doc_lengths, list)
    assert num_files > 1

    # Total number of characters
    total = cum_doc_lengths[-1]

    return [np.argmin(abs(cum_doc_lengths - r*total)) for r in spacing_ratio(num_files)]


class BatchedCsvWriter:
    def __init__(self, folder, prefix, delimiter, encapsulator, header):

        # Preconditions
        assert os.path.exists(folder)
        assert isinstance(prefix, str)
        assert isinstance(delimiter, str)
        assert encapsulator is None or isinstance(encapsulator, str)
        assert isinstance(header, list)

        self.folder = folder
        self.prefix = prefix
        self.delimiter = delimiter
        self.encapsulator = encapsulator
        self.header = header

        # File pointer
        self.fp = None

        # CSV writer
        self.writer = None

        # Current index of the file
        self.current_index = -1

    def start_new_file(self):
        """Start a new output file."""

        self.current_index += 1

        # Create the filepath
        filepath = os.path.join(
            self.folder, f"{self.prefix}-{self.current_index}.csv")
        print(f"Writing to file: {filepath}")

        # Open the file for writing
        self.fp = open(filepath, 'w', encoding='utf8', newline='')
        self.writer = csv.writer(self.fp)

        # Add the header to the file
        self.add_row(self.header)

    def add_row(self, row):
        """Add a row of data to the output file."""

        # Preconditions
        assert isinstance(row, list)

        # Start a new file if this is the first row
        if self.fp is None:
            self.start_new_file()

        self.writer.writerow(row)

    def close(self):
        """Close the file."""

        if self.fp is not None:
            self.fp.close()


def split(filepath, delimiter, encapsulator, output_folder, prefix, cuts):
    """Split a CSV file into smaller files."""

    # Preconditions
    assert os.path.exists(filepath)
    assert isinstance(delimiter, str)
    assert encapsulator is None or isinstance(encapsulator, str)
    assert os.path.exists(output_folder)
    assert isinstance(prefix, str)
    assert isinstance(cuts, list) and len(cuts) > 0

    with open(filepath, 'r', encoding='utf8') as fp:
        reader = csv.reader(fp, delimiter=delimiter, quotechar=encapsulator)

        # Read the header
        header = next(reader)

        # Initialise the CSV writer
        writer = BatchedCsvWriter(
            output_folder, prefix, delimiter, encapsulator, header)

        num_rows_read = 0

        for row in reader:

            num_rows_read += 1

            # Should a new file be started?
            if num_rows_read in cuts:
                writer.start_new_file()

            writer.add_row(row)

        print(f"Read {num_rows_read} data rows from {filepath}")
        writer.close()


def plot_doc_lengths(doc_lengths):
    """Plot the length of each document as a function of document index."""

    # Preconditions
    assert isinstance(doc_lengths, list)
    assert len(doc_lengths) > 0

    plt.plot(doc_lengths)
    plt.xlabel("Row index")
    plt.ylabel("Number of characters")
    # plt.show()

    plt.savefig("doc_lengths.png")
    plt.show()


def plot_break_points(cum_doc_lengths, cuts):
    """Plot the break points for the files"""

    # Preconditions
    assert isinstance(doc_lengths, list)
    assert len(doc_lengths) > 0
    assert isinstance(cuts, list)
    assert len(cuts) > 0

    plt.plot(cum_doc_lengths, '-g')

    for cut in cuts:
        plt.plot([0, len(cum_doc_lengths)], [
                 cum_doc_lengths[cut], cum_doc_lengths[cut]], '--r')

    plt.xlabel("Row index")
    plt.ylabel("Cumulative total number of characters")

    plt.savefig("break_points.png")
    plt.show()


if __name__ == '__main__':

    # Location of the input CSV file to split
    filepath = r"./data/input.csv"

    # CSV file parameters
    delimiter = ","
    encapsulator = "|"

    # Number of files to split the input file into
    num_files = 4

    # Location of the output (split) files
    output_folder = r"./data/"
    prefix = "split"

    # Calculate the length of each document (row) in the CSV file
    print(f"Calculating the lengths of each row in {filepath} ...")
    doc_lengths = calc_doc_lengths(filepath, delimiter, encapsulator)
    plot_doc_lengths(doc_lengths)

    # Cumulative sum of the document lengths
    # Using int64 to avoid overflow issues
    cum_total = np.cumsum(np.int64(doc_lengths))

    # Calculate the 'break' indices
    cuts = calc_break_points(cum_total, num_files)
    plot_break_points(cum_total, cuts)

    # Split the CSV file
    split(filepath, delimiter, encapsulator, output_folder, prefix, cuts)

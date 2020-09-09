import csv
import numpy as np

from faker import Faker

fake = Faker()


def mixture_of_uniforms(p1, bound1, bound2):
    """Sample from a mixture of uniforms."""

    # Preconditions
    assert 0 <= p1 <= 1
    assert len(bound1) == 2
    assert len(bound2) == 2

    # Mixture from which the sample will be generated
    mixture = np.random.binomial(1, p1)

    if mixture == 0:
        return np.random.randint(*bound1)
    else:
        return np.random.randint(*bound2)


def generate_doc():
    """Generate a synthetic document."""

    num_sentences = mixture_of_uniforms(0.05, [1, 6], [100, 120])

    return [
        fake.name(),
        fake.address(),
        " ".join(fake.sentences(num_sentences))
    ]


def generate_header():
    """Return the header associated with a document."""

    return ["Name", "Address", "Statement"]


def build_data(filepath, delimiter, encapsulator):
    """Generate a CSV file."""

    with open(filepath, 'w', encoding='utf8', newline='') as fp:
        writer = csv.writer(fp, delimiter=delimiter, quotechar=encapsulator)

        # Write the header
        writer.writerow(generate_header())

        for _ in range(num_docs):
            writer.writerow(generate_doc())


def check_data(filepath, delimiter, encapsulator, expected_num_docs):
    """Check the generated CSV file."""

    # Check the data
    num_rows_read = 0
    with open(filepath, 'r', encoding='utf8') as fp:
        reader = csv.reader(fp, delimiter=delimiter, quotechar=encapsulator)

        for row in reader:
            num_rows_read += 1

    print(f"Read {num_rows_read} rows (expected {expected_num_docs + 1})")

    assert expected_num_docs == (num_rows_read - 1)


if __name__ == '__main__':

    # Location of the file to be written by this generator
    filepath = r"./data/input.csv"

    # CSV file parameters
    delimiter = ","
    encapsulator = "|"

    # Number of documents to generate
    num_docs = np.random.randint(500, 700)
    print(f"Generating {num_docs} documents")

    # Generate the data
    print(f"Building data in {filepath}")
    build_data(filepath, delimiter, encapsulator)

    # Check the data
    print(f"Checking data in {filepath}")
    check_data(filepath, delimiter, encapsulator, num_docs)

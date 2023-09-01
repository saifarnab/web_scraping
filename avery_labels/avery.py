from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def generate_presta_labels(data, rows, columns, label_width, label_height, output_filename):
    c = canvas.Canvas(output_filename, pagesize=letter)

    x_margin = 0.3 * inch
    y_margin = 0.3 * inch

    x_gap = 0.1 * inch
    y_gap = 0.1 * inch

    for row in range(rows):
        for col in range(columns):
            if not data:
                break

            x = x_margin + col * (label_width + x_gap)
            y = letter[1] - (y_margin + row * (label_height + y_gap))

            label_text = data.pop(0)
            c.setFont("Helvetica", 8)  # Adjust font and size as needed
            lines = label_text.split('\n')
            y_offset = y
            for line in lines:
                c.drawString(x, y_offset, line)
                y_offset -= 0.2 * inch  # Adjust line spacing as needed

    c.save()

# Example data: Replace this with your own list of label content
label_data = [
    "John Doe\n123 Main St\nCity, State Zip",
    "Jane Smith\n456 Elm St\nTown, State Zip",
    # Add more data entries as needed
]

rows = 5  # Number of label rows on a page
columns = 2  # Number of label columns on a page
label_width = 3.5  # Width of a single label (in inches)
label_height = 1.0  # Height of a single label (in inches)
output_filename = "presta_labels.pdf"  # Output PDF filename

generate_presta_labels(label_data, rows, columns, label_width, label_height, output_filename)

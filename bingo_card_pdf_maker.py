#!/usr/bin/env python3
"""
Bingo Card PDF Generator (Courier font, wider cells, aligned title/instructions)

- Uses Courier font for all text.
- Title is bold Courier.
- Instructions are italic Courier and 4pt smaller than title.
- Title and description span the same width as the card grid.
- Wider cell width (3.7 * inch / 3).
- More spacing between the two cards.
"""

import json
import sys
import argparse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Flowable, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def load_bingo_data(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{json_path}': {e}")
        sys.exit(1)


def validate_bingo_data(data):
    required_positions = [
        "top_left", "top_middle", "top_right",
        "middle_left", "centre", "middle_right",
        "bottom_left", "bottom_middle", "bottom_right"
    ]

    for card_num, card_data in data.items():
        for position in required_positions:
            if position not in card_data or "content" not in card_data[position]:
                raise ValueError(f"Card {card_num} missing required position or content: {position}")


def convert_card_to_grid(card_data):
    return [
        [card_data["top_left"]["content"], card_data["top_middle"]["content"], card_data["top_right"]["content"]],
        [card_data["middle_left"]["content"], card_data["centre"]["content"], card_data["middle_right"]["content"]],
        [card_data["bottom_left"]["content"], card_data["bottom_middle"]["content"], card_data["bottom_right"]["content"]]
    ]


class BingoCardFlowable(Flowable):
    def __init__(self, card_data, width=4.5*inch, height=6.0*inch):
        Flowable.__init__(self)
        self.card_data = card_data
        self.width = width
        self.height = height
        self.cell_width = 3.7 * inch / 3  # wider cells
        self.cell_height = 1.6 * inch

    def draw(self):
        grid_total_width = 3 * self.cell_width

        # Title
        title_style = ParagraphStyle(
            'Title',
            fontName='Courier-Bold',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=6
        )
        title = Paragraph("Meet the Lovely People @ Lulu's B-day", title_style)
        w, h = title.wrap(grid_total_width, self.height)
        title.drawOn(self.canv, 0.1*inch, self.height - h)

        # Instructions (4pts smaller)
        instr_style = ParagraphStyle(
            'Instructions',
            fontName='Courier-Oblique',
            fontSize=9,  # 4 pts smaller than title (16 -> 12)
            alignment=TA_CENTER,
            leading=14,
            spaceAfter=12
        )
        instructions = (
            'Find party-goers who identify with the following descriptions, '
            'and ask them to sign to "stamp" the square. No one can sign '
            'a single card twice! See Lulu after all squares are completed for maybe a prize...'
        )
        instr = Paragraph(instructions, instr_style)
        iw, ih = instr.wrap(grid_total_width, self.height)
        instr.drawOn(self.canv, 0.1*inch, self.height - h - ih - 10)

        # Grid position after title + instructions
        grid_start_y = self.height - h - ih - 0.5*inch
        grid_height = 3 * self.cell_height

        # Grid border
        self.canv.setLineWidth(2)
        self.canv.rect(0.1*inch, grid_start_y - grid_height,
                       grid_total_width, grid_height, stroke=1, fill=0)

        # Grid lines
        self.canv.setLineWidth(1)
        for i in range(1, 3):
            y = grid_start_y - i * self.cell_height
            self.canv.line(0.1*inch, y, 0.1*inch + grid_total_width, y)
        for i in range(1, 3):
            x = 0.1*inch + i * self.cell_width
            self.canv.line(x, grid_start_y, x, grid_start_y - grid_height)

        # Cell content with auto font scaling in Courier
        for row_idx, row in enumerate(self.card_data):
            for col_idx, cell_content in enumerate(row):
                if cell_content and cell_content.strip():
                    x = 0.1*inch + col_idx * self.cell_width
                    y = grid_start_y - (row_idx + 1) * self.cell_height

                    font_size = 10
                    while font_size >= 6:  # shrink text until it fits
                        style = ParagraphStyle(
                            'CardCell',
                            fontName='Courier',
                            fontSize=font_size,
                            leading=font_size + 2,
                            alignment=TA_CENTER
                        )
                        p = Paragraph(cell_content, style)
                        w, h = p.wrap(self.cell_width - 0.1*inch, self.cell_height - 0.1*inch)
                        if h <= self.cell_height - 0.1*inch:
                            break
                        font_size -= 1

                    p.drawOn(self.canv, x + (self.cell_width - w) / 2, y + (self.cell_height - h) / 2)


def create_side_by_side_cards(card1_data, card2_data=None):
    if card2_data is None:
        card2_data = [["", "", ""], ["", "", ""], ["", "", ""]]

    card1_flowable = BingoCardFlowable(card1_data)
    card2_flowable = BingoCardFlowable(card2_data)

    table_data = [[card1_flowable, card2_flowable]]
    # more spacing between cards
    table = Table(table_data, colWidths=[4.7*inch, 4.7*inch], hAlign='CENTER')

    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 30),
        ('RIGHTPADDING', (0, 0), (-1, -1), 30),
    ]))

    return table


def generate_bingo_pdf(json_path, output_path=None):
    bingo_data = load_bingo_data(json_path)
    validate_bingo_data(bingo_data)

    card_grids = [convert_card_to_grid(bingo_data[num]) for num in sorted(bingo_data.keys(), key=lambda x: int(x))]

    if output_path is None:
        output_path = json_path.replace('.json', '_bingo_cards.pdf')

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    story = []
    for i in range(0, len(card_grids), 2):
        card1_data = card_grids[i]
        card2_data = card_grids[i+1] if i+1 < len(card_grids) else None
        story.append(create_side_by_side_cards(card1_data, card2_data))
        if i + 2 < len(card_grids):
            story.append(PageBreak())

    try:
        doc.build(story)
        print(f"Successfully generated PDF: {output_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate PDF bingo cards from JSON data")
    parser.add_argument('json_file', help='Path to JSON file containing bingo card data')
    parser.add_argument('-o', '--output', help='Output PDF filename (optional)')
    args = parser.parse_args()
    generate_bingo_pdf(args.json_file, args.output)


if __name__ == "__main__":
    main()
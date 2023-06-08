from embeds import DATETIME_FORMAT

from PIL import Image, ImageDraw, ImageFont

import nextcord

import io

SIZE = WIDTH, HEIGHT = 1280, 720

FONT_TITLE = ImageFont.truetype(
    font="/usr/local/share/fonts/SegoeUI-VF/Segoe-UI-Variable-Static-Display.ttf",
    size=36
)
FONT_TITLE_BOLD = ImageFont.truetype(
    font="/usr/local/share/fonts/SegoeUI-VF/Segoe-UI-Variable-Static-Display-Bold.ttf",
    size=36
)
FONT_NORMAL = ImageFont.truetype(
    font="/usr/share/fonts/noto/NotoSans-Regular.ttf",
    size=22
)
FONT_NORMAL_BOLD = ImageFont.truetype(
    font="/usr/share/fonts/noto/NotoSans-Bold.ttf",
    size=22
)
FONT_DATA = ImageFont.truetype(
    font="/usr/share/fonts/noto/NotoSansMono-Regular.ttf",
    size=22
)
FONT_DATA_BOLD = ImageFont.truetype(
    font="/usr/share/fonts/noto/NotoSansMono-Bold.ttf",
    size=22
)
FONT_DATA_BIGGER = ImageFont.truetype(
    font="/usr/share/fonts/noto/NotoSansMono-Regular.ttf",
    size=32
)
FONT_DATA_BIGGER_BOLD = ImageFont.truetype(
    font="/usr/share/fonts/noto/NotoSansMono-Bold.ttf",
    size=32
)

TITLE_LOCATION = (25, 15)

GRAPH_MARGIN = 50

PIE_COLOURS = {
    'vote': (0, 48, 73),
    'nonvote': (247, 127, 0),
    'duplicate': (214, 40, 40),
    'late': (234, 226, 183)
}

VOTE_COLOURS = (
    (217, 237, 146),
    (181, 228, 140),
    (153, 217, 140),
    (118, 200, 147),
    (82, 182, 154),
    (52, 160, 164),
    (22, 138, 173),
    (26, 117, 159),
    (30, 96, 145),
    (24, 78, 119)
)

def nextcordise(image, filename, desc, spoiler=True):
    output = io.BytesIO()
    image.save(output, format='PNG')
    output.seek(0)

    return nextcord.File(
        fp=output,
        filename=filename,
        description=desc,
        spoiler=spoiler
    )

def xywh_to_bbox(x, y, w, h):
    return (
        x, y,
        x + w, y + h
    )

def draw_text_aligned(draw, text, bbox, alignment, anchor, offset, font=None, fill='white'):
    text_bbox = font.getbbox(text)

    bbox_wh = (
        bbox[2] - bbox[0],
        bbox[3] - bbox[1]
    )

    draw.text(
        (
            bbox[0] + bbox_wh[0] * alignment[0] - (text_bbox[2] * anchor[0]) + offset[0],
            bbox[1] + bbox_wh[1] * alignment[1] - (text_bbox[3] * anchor[1]) + offset[1],
        ),
        text,
        font=font,
        fill=fill
    )

    return text_bbox
    

def draw_text_segmented(draw, pos, text_segments):
    final_bbox = [pos[0], pos[1], 0, 0]

    for seg in text_segments:
        text = str(seg['text'])
        bbox = seg['font'].getbbox(text)

        if 'bg' in seg:
            draw.rectangle(
                xywh_to_bbox(
                    final_bbox[0],
                    final_bbox[1],
                    bbox[2],
                    bbox[3]
                ),
                fill=seg['bg']
            )

        if 'draw' not in seg or seg['draw']:
            draw.text(
                (
                    pos[0] + final_bbox[2],
                    pos[1]
                ),
                text,
                font=seg['font'],
                fill=seg['fill'] if 'fill' in seg else 'white'
            )

        final_bbox[2] += bbox[2]
        final_bbox[3] = max(bbox[3], final_bbox[3])

    return final_bbox

def stats_graph(stats):
    image = Image.new("RGB", SIZE, color=(0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw title
    draw_text_segmented(
        draw,
        TITLE_LOCATION,
        [
            {
                'text': "Stats, as of ",
                'font': FONT_TITLE
            },
            {
                'text': stats['counted_at'].strftime(DATETIME_FORMAT),
                'font': FONT_TITLE_BOLD
            },
        ]
    )

    pieslice_bbox = xywh_to_bbox(
        TITLE_LOCATION[0] + GRAPH_MARGIN,
        TITLE_LOCATION[1] + FONT_TITLE.getbbox("Stats, as of ")[3] + GRAPH_MARGIN,
        HEIGHT - (TITLE_LOCATION[1] + FONT_TITLE.getbbox("Stats, as of ")[3] + GRAPH_MARGIN) - GRAPH_MARGIN,
        HEIGHT - (TITLE_LOCATION[1] + FONT_TITLE.getbbox("Stats, as of ")[3] + GRAPH_MARGIN) - GRAPH_MARGIN
    )

    angles = (
        360 * (stats['vote_comments'] / stats['total_comments']),
        360 * (stats['non_vote_comments'] / stats['total_comments']),
        360 * (stats['duplicate_comments'] / stats['total_comments']),
        360 * (stats['late_votes'] / stats['total_comments']),
    )

    # Draw comment pie
    draw.pieslice(
        pieslice_bbox,
        -angles[0],
        0,
        fill=PIE_COLOURS['vote']
    )

    draw.pieslice(
        pieslice_bbox,
        0,
        angles[1],
        fill=PIE_COLOURS['nonvote']
    )

    draw.pieslice(
        pieslice_bbox,
        angles[1],
        angles[2] + angles[1],
        fill=PIE_COLOURS['duplicate']
    )

    draw.pieslice(
        pieslice_bbox,
        angles[2] + angles[1],
        angles[3] + angles[2] + angles[1],
        fill=PIE_COLOURS['late']
    )

    draw.ellipse(
        pieslice_bbox,
        width=4
    )

    # Draw legend
    legend_colour_bbox = FONT_DATA.getbbox("__")
    initial_pos = (
        pieslice_bbox[2] + GRAPH_MARGIN,
        pieslice_bbox[3] - (legend_colour_bbox[3] * (1.5 * 4)) + (legend_colour_bbox[3] * 0.5)
    )

    # Valid votes
    bbox = draw_text_segmented(
        draw,
        initial_pos,
        [
            {
                'text': "__",
                'font': FONT_DATA,
                'bg': PIE_COLOURS['vote'],
                'draw': False
            },
            {
                'text': " ",
                'font': FONT_DATA,
                'draw': False
            },
            {
                'text': "Valid vote comments",
                'font': FONT_NORMAL
            }
        ]
    )

    # Non-votes
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5
        ),
        [
            {
                'text': "__",
                'font': FONT_DATA,
                'bg': PIE_COLOURS['nonvote'],
                'draw': False
            },
            {
                'text': " ",
                'font': FONT_DATA,
                'draw': False
            },
            {
                'text': "Non-vote comments",
                'font': FONT_NORMAL
            }
        ]
    )

    # Duplicate votes
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5 * 2
        ),
        [
            {
                'text': "__",
                'font': FONT_DATA,
                'bg': PIE_COLOURS['duplicate'],
                'draw': False
            },
            {
                'text': " ",
                'font': FONT_DATA,
                'draw': False
            },
            {
                'text': "Duplicate votes",
                'font': FONT_NORMAL
            }
        ]
    )

    # Late votes
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5 * 3
        ),
        [
            {
                'text': "__",
                'font': FONT_DATA,
                'bg': PIE_COLOURS['late'],
                'draw': False
            },
            {
                'text': " ",
                'font': FONT_DATA,
                'draw': False
            },
            {
                'text': "Late votes",
                'font': FONT_NORMAL
            }
        ]
    )

    # Draw textual data
    initial_pos = (pieslice_bbox[2] + GRAPH_MARGIN, pieslice_bbox[1])
    line_number = 1
    
    # Total comments
    bbox = draw_text_segmented(
        draw,
        initial_pos,
        [
            {
                'text': "There are ",
                'font': FONT_NORMAL
            },
            {
                'text': stats['total_comments'],
                'font': FONT_DATA_BOLD
            },
            {
                'text': " comments in total.",
                'font': FONT_NORMAL
            }
        ]
    )

    line_number += 1

    # Vote comments
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5 * line_number
        ),
        [
            {
                'text': stats['vote_comments'],
                'font': FONT_DATA_BOLD,
                'fill': PIE_COLOURS['vote']
            },
            {
                'text': " (about ",
                'font': FONT_NORMAL
            },
            {
                'text': str(round(stats['vote_comments'] / stats['total_comments'] * 100, 1)) + "%",
                'font': FONT_DATA_BOLD,
                'fill': PIE_COLOURS['vote']
            },
            {
                'text': ") of them are ",
                'font': FONT_NORMAL
            },
            {
                'text': "votes",
                'font': FONT_NORMAL_BOLD
            },
            {
                'text': ".",
                'font': FONT_NORMAL
            },
        ]
    )

    line_number += 1

    # Non-vote comments
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5 * line_number
        ),
        [
            {
                'text': stats['non_vote_comments'],
                'font': FONT_DATA_BOLD,
                'fill': PIE_COLOURS['nonvote']
            },
            {
                'text': " (about ",
                'font': FONT_NORMAL
            },
            {
                'text': str(round(stats['non_vote_comments'] / stats['total_comments'] * 100, 1)) + "%",
                'font': FONT_DATA_BOLD,
                'fill': PIE_COLOURS['nonvote']
            },
            {
                'text': ") of them are ",
                'font': FONT_NORMAL
            },
            {
                'text': "normal comments",
                'font': FONT_NORMAL_BOLD
            },
            {
                'text': ".",
                'font': FONT_NORMAL
            },
        ]
    )

    line_number += 1

    # Late votes
    if stats['late_votes'] > 0:
        draw_text_segmented(
            draw,
            (
                initial_pos[0],
                initial_pos[1] + bbox[3] * 1.5 * line_number
            ),
            [
                {
                    'text': stats['late_votes'],
                    'font': FONT_DATA_BOLD,
                    'fill': PIE_COLOURS['late']
                },
                {
                    'text': " (about ",
                    'font': FONT_NORMAL
                },
                {
                    'text': str(round(stats['late_votes'] / stats['total_comments'] * 100, 1)) + "%",
                    'font': FONT_DATA_BOLD,
                    'fill': PIE_COLOURS['late']
                },
                {
                    'text': ") of them are ",
                    'font': FONT_NORMAL
                },
                {
                    'text': "late votes",
                    'font': FONT_NORMAL_BOLD
                },
                {
                    'text': ".",
                    'font': FONT_NORMAL
                },
            ]
        )

        line_number += 1

    line_number += 1

    # Duplicate votes
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5 * line_number
        ),
        [
            {
                'text': stats['duplicate_comments'],
                'font': FONT_DATA_BOLD,
                'fill': PIE_COLOURS['duplicate']
            },
            {
                'text': " (about ",
                'font': FONT_NORMAL
            },
            {
                'text': str(round(stats['duplicate_comments'] / stats['total_comments'] * 100, 1)) + "%",
                'font': FONT_DATA_BOLD,
                'fill': PIE_COLOURS['duplicate']
            },
            {
                'text': ") of them are ",
                'font': FONT_NORMAL
            },
            {
                'text': "duplicated votes",
                'font': FONT_NORMAL_BOLD
            },
            {
                'text': ".",
                'font': FONT_NORMAL
            },
        ]
    )

    line_number += 1

    # Duplicate commenters
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5 * line_number
        ),
        [
            {
                'text': stats['duplicate_commenters'],
                'font': FONT_DATA_BOLD,
                'fill': PIE_COLOURS['duplicate']
            },
            {
                'text': " commenters have submitted ",
                'font': FONT_NORMAL
            },
            {
                'text': "duplicated votes",
                'font': FONT_NORMAL_BOLD
            },
            {
                'text': ".",
                'font': FONT_NORMAL
            },
        ]
    )

    line_number += 1

    # Most prolific duplicator
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5 * line_number
        ),
        [

            {
                'text': "The most prolific one is ",
                'font': FONT_NORMAL
            },
            {
                'text': stats['most_prolific_duplicator'],
                'font': FONT_DATA_BOLD
            },
            {
                'text': ",",
                'font': FONT_NORMAL
            },
        ]
    )

    line_number += 1

    # Most prolific duplicator votes
    draw_text_segmented(
        draw,
        (
            initial_pos[0],
            initial_pos[1] + bbox[3] * 1.5 * line_number
        ),
        [

            {
                'text': "who submitted ",
                'font': FONT_NORMAL
            },
            {
                'text': stats['most_prolific_duplicator_votes'],
                'font': FONT_DATA_BOLD,
                'fill': PIE_COLOURS['duplicate']
            },
            {
                'text': " of them.",
                'font': FONT_NORMAL
            },
        ]
    )

    return image


def votes_graph(stats, sort=False):
    image = Image.new("RGB", SIZE, color=(0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw title
    draw_text_segmented(
        draw,
        TITLE_LOCATION,
        [
            {
                'text': "Votes, as of ",
                'font': FONT_TITLE
            },
            {
                'text': stats['counted_at'].strftime(DATETIME_FORMAT),
                'font': FONT_TITLE_BOLD
            },
        ]
    )

    votebox_bbox = (
        WIDTH / 2,
        TITLE_LOCATION[1] + FONT_TITLE.getbbox("Votes, as of ")[3] + GRAPH_MARGIN,
        WIDTH - GRAPH_MARGIN,
        HEIGHT - GRAPH_MARGIN
    )

    # Draw bars
    bar_width = (votebox_bbox[2] - votebox_bbox[0]) / len(stats['votes'])
    max_bar_height = votebox_bbox[3] - votebox_bbox[1]
    max_votes = max(stats['votes'].values())

    vote_items = stats['votes'].items()

    if sort:
        vote_items = sorted(vote_items, key=lambda x: x[1], reverse=True)

    assigned_colours = {}

    for i, (letter, votes) in enumerate(vote_items):
        assigned_colours[letter] = VOTE_COLOURS[i]
        percentage = votes / max_votes

        bar_bbox = (
            votebox_bbox[0] + bar_width * i,
            votebox_bbox[3] - max_bar_height * percentage,
            votebox_bbox[0] + (bar_width * (i + 1)),
            votebox_bbox[3],
        )

        draw.rectangle(
            bar_bbox,
            fill=VOTE_COLOURS[i]
        )

        # Draw line
        draw.line(
            (
                votebox_bbox[0] + bar_width * i,
                votebox_bbox[3] - max_bar_height * percentage,
                votebox_bbox[2],
                votebox_bbox[3] - max_bar_height * percentage,
            ),
            fill=(64, 64, 64),
            width=1
        )

        if percentage > 0.5:
            # Draw text below
            bbox = draw_text_aligned(
                draw,
                f"[{letter}]",
                bar_bbox,
                (0.5, 0),
                (0.5, 0),
                (0, 0),
                font=FONT_DATA_BOLD,
                fill='black'
            )

            draw_text_aligned(
                draw,
                str(votes),
                bar_bbox,
                (0.5, 0),
                (0.5, 0),
                (0, bbox[3]),
                font=FONT_DATA_BOLD,
                fill='black'
            )
        else:
            # Draw text above
            bbox = draw_text_aligned(
                draw,
                f"[{letter}]",
                bar_bbox,
                (0.5, 0),
                (0.5, 1),
                (0, -FONT_DATA_BOLD.getbbox(f"[{letter}]")[3] * 0.25),
                font=FONT_DATA_BOLD,
                fill='white'
            )

            bbox = draw_text_aligned(
                draw,
                str(votes),
                bar_bbox,
                (0.5, 0),
                (0.5, 1),
                (0, -FONT_DATA_BOLD.getbbox(f"[{letter}]")[3] * 0.25 - bbox[3]),
                font=FONT_DATA_BOLD,
                fill='white'
            )

    # Draw graph boundaries
    draw.line(
        (
            votebox_bbox[0], votebox_bbox[1],
            votebox_bbox[0], votebox_bbox[3]
        ),
        width=2
    )
    draw.line(
        (
            votebox_bbox[0], votebox_bbox[3],
            votebox_bbox[2], votebox_bbox[3]
        ),
        width=2
    )
    draw.line(
        (
            votebox_bbox[2], votebox_bbox[3],
            votebox_bbox[2], votebox_bbox[1]
        ),
        width=2
    )

    # Draw text
    text_pos = [
        TITLE_LOCATION[0],
        TITLE_LOCATION[1] + FONT_TITLE.getbbox("Votes, as of ")[3] + GRAPH_MARGIN
    ]
    
    for letter, votes in stats['votes'].items():
        bbox = draw_text_segmented(
            draw,
            text_pos,
            [
                {
                    'text': f"[{letter}]",
                    'font': FONT_DATA_BIGGER_BOLD,
                    'fill': assigned_colours[letter]
                },
                {
                    'text': " - ",
                    'font': FONT_DATA_BIGGER
                },
                {
                    'text': str(votes),
                    'font': FONT_DATA_BIGGER_BOLD
                },
                {
                    'text': " (",
                    'font': FONT_DATA_BIGGER
                },
                {
                    'text': str(round(votes / stats['vote_comments'] * 100, 2)) + "%",
                    'font': FONT_DATA_BIGGER_BOLD
                },
                {
                    'text': ")",
                    'font': FONT_DATA_BIGGER
                }
            ]
        )

        text_pos[1] += bbox[3] * 1.5

    return image

# PADI Recreational Dive Planner Implementation
from typing import Tuple, Dict, Optional

# No-Decompression Limits Table (depth in feet : max bottom time in minutes)
no_deco_limits = {
    35: 205,
    40: 140,
    50: 80,
    60: 55,
    70: 40,
    80: 30,
    90: 25,
    100: 20,
    110: 16,
    120: 13,
    130: 10,
    140: 8
}

# Pressure groups A-Z mapped to their numeric index (0-25)
PRESSURE_GROUPS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# No-Decompression Limits Table
pressure_group_table = {
    35: [(10, 'A'), (19, 'B'), (25, 'C'), (29, 'D'), (32, 'E'), (36, 'F'), (40, 'G'), (44, 'H'),
         (48, 'I'), (52, 'J'), (57, 'K'), (62, 'L'), (67, 'M'), (73, 'N'), (79, 'O'), (85, 'P'),
         (92, 'Q'), (100, 'R'), (108, 'S'), (117, 'T'), (127, 'U'), (139, 'V'), (152, 'W'),
         (168, 'X'), (188, 'Y'), (205, 'Z')],
    40: [(9, 'A'), (16, 'B'), (22, 'C'), (25, 'D'), (27, 'E'), (31, 'F'), (34, 'G'), (37, 'H'),
         (40, 'I'), (44, 'J'), (48, 'K'), (51, 'L'), (55, 'M'), (60, 'N'), (64, 'O'), (69, 'P'),
         (74, 'Q'), (79, 'R'), (85, 'S'), (91, 'T'), (97, 'U'), (104, 'V'), (111, 'W'),
         (120, 'X'), (129, 'Y'), (140, 'Z')],
    50: [(7, 'A'), (13, 'B'), (17, 'C'), (19, 'D'), (21, 'E'), (24, 'F'), (26, 'G'), (28, 'H'),
         (31, 'I'), (33, 'J'), (36, 'K'), (38, 'L'), (41, 'M'), (44, 'N'), (47, 'O'), (50, 'P'),
         (53, 'Q'), (57, 'R'), (60, 'S'), (63, 'T'), (67, 'U'), (71, 'V'), (75, 'W'),
         (80, 'X')],
    60: [(6, 'A'), (11, 'B'), (14, 'C'), (16, 'D'), (17, 'E'), (19, 'F'), (21, 'G'), (23, 'H'),
         (25, 'I'), (27, 'J'), (29, 'K'), (31, 'L'), (33, 'M'), (35, 'N'), (37, 'O'), (39, 'P'),
         (42, 'Q'), (44, 'R'), (47, 'S'), (49, 'T'), (52, 'U'), (54, 'V'), (55, 'W')],
    70: [(5, 'A'), (9, 'B'), (12, 'C'), (13, 'D'), (15, 'E'), (16, 'F'), (18, 'G'), (19, 'H'),
         (21, 'I'), (22, 'J'), (24, 'K'), (26, 'L'), (27, 'M'), (29, 'N'), (31, 'O'), (33, 'P'),
         (35, 'Q'), (36, 'R'), (38, 'S'), (40, 'T')],
    80: [(4, 'A'), (8, 'B'), (10, 'C'), (11, 'D'), (13, 'E'), (14, 'F'), (15, 'G'), (17, 'H'),
         (18, 'I'), (19, 'J'), (21, 'K'), (22, 'L'), (23, 'M'), (25, 'N'), (26, 'O'), (28, 'P'),
         (29, 'Q'), (30, 'R')],
    90: [(4, 'A'), (7, 'B'), (9, 'C'), (10, 'D'), (11, 'E'), (12, 'F'), (13, 'G'), (15, 'H'),
         (16, 'I'), (17, 'J'), (18, 'K'), (19, 'L'), (21, 'M'), (22, 'N'), (23, 'O'), (24, 'P'),
         (25, 'Q')],
    100: [(3, 'A'), (6, 'B'), (8, 'C'), (9, 'D'), (10, 'E'), (11, 'F'), (12, 'G'), (13, 'H'),
          (14, 'I'), (15, 'J'), (16, 'K'), (17, 'L'), (18, 'M'), (19, 'N'), (20, 'O')],
    110: [(3, 'A'), (5, 'B'), (7, 'C'), (8, 'D'), (9, 'E'), (10, 'F'), (11, 'G'), (12, 'H'),
          (13, 'I'), (14, 'J'), (15, 'K'), (16, 'L')],
    120: [(3, 'A'), (5, 'B'), (6, 'C'), (7, 'D'), (8, 'E'), (9, 'F'), (10, 'G'), (11, 'H'),
          (12, 'I'), (13, 'J')],
    130: [(3, 'A'), (4, 'B'), (5, 'C'), (6, 'D'), (7, 'E'), (8, 'F'), (9, 'G'), (10, 'H')],
    140: [(3, 'A'), (4, 'B'), (5, 'C'), (6, 'D'), (7, 'E'), (8, 'F')]
}

# Residual Nitrogen Time Table (Table 3)
# Format: (depth, pressure_group): residual_nitrogen_time
rnt_table = {
    (35, 'A'): 10,
    (35, 'B'): 19,
    (35, 'C'): 25,
    (35, 'D'): 29,
    (35, 'E'): 32,
    (35, 'F'): 36,
    (35, 'G'): 40,
    (35, 'H'): 44,
    (35, 'I'): 48,
    (35, 'J'): 52,
    (35, 'K'): 57,
    (35, 'L'): 62,
    (35, 'M'): 67,
    (35, 'N'): 73,
    (35, 'O'): 79,
    (35, 'P'): 85,
    (35, 'Q'): 92,
    (35, 'R'): 100,
    (35, 'S'): 108,
    (35, 'T'): 117,
    (35, 'U'): 127,
    (35, 'V'): 139,
    (35, 'W'): 152,
    (35, 'X'): 168,
    (35, 'Y'): 188,
    (35, 'Z'): 205,

    (40, 'A'): 9,
    (40, 'B'): 16,
    (40, 'C'): 22,
    (40, 'D'): 25,
    (40, 'E'): 27,
    (40, 'F'): 31,
    (40, 'G'): 34,
    (40, 'H'): 37,
    (40, 'I'): 40,
    (40, 'J'): 44,
    (40, 'K'): 48,
    (40, 'L'): 51,
    (40, 'M'): 55,
    (40, 'N'): 60,
    (40, 'O'): 64,
    (40, 'P'): 69,
    (40, 'Q'): 74,
    (40, 'R'): 79,
    (40, 'S'): 85,
    (40, 'T'): 91,
    (40, 'U'): 97,
    (40, 'V'): 104,
    (40, 'W'): 111,
    (40, 'X'): 120,
    (40, 'Y'): 129,
    (40, 'Z'): 140,

    (50, 'A'): 7,
    (50, 'B'): 13,
    (50, 'C'): 17,
    (50, 'D'): 19,
    (50, 'E'): 21,
    (50, 'F'): 24,
    (50, 'G'): 26,
    (50, 'H'): 28,
    (50, 'I'): 31,
    (50, 'J'): 33,
    (50, 'K'): 36,
    (50, 'L'): 38,
    (50, 'M'): 41,
    (50, 'N'): 44,
    (50, 'O'): 47,
    (50, 'P'): 50,
    (50, 'Q'): 53,
    (50, 'R'): 57,
    (50, 'S'): 60,
    (50, 'T'): 63,
    (50, 'U'): 67,
    (50, 'V'): 71,
    (50, 'W'): 75,
    (50, 'X'): 80,

    (60, 'A'): 6,
    (60, 'B'): 11,
    (60, 'C'): 14,
    (60, 'D'): 16,
    (60, 'E'): 17,
    (60, 'F'): 19,
    (60, 'G'): 21,
    (60, 'H'): 23,
    (60, 'I'): 25,
    (60, 'J'): 27,
    (60, 'K'): 29,
    (60, 'L'): 31,
    (60, 'M'): 33,
    (60, 'N'): 35,
    (60, 'O'): 37,
    (60, 'P'): 39,
    (60, 'Q'): 42,
    (60, 'R'): 44,
    (60, 'S'): 47,
    (60, 'T'): 49,
    (60, 'U'): 52,
    (60, 'V'): 54,
    (60, 'W'): 55,

    (70, 'A'): 5,
    (70, 'B'): 9,
    (70, 'C'): 12,
    (70, 'D'): 13,
    (70, 'E'): 15,
    (70, 'F'): 16,
    (70, 'G'): 18,
    (70, 'H'): 19,
    (70, 'I'): 21,
    (70, 'J'): 22,
    (70, 'K'): 24,
    (70, 'L'): 26,
    (70, 'M'): 27,
    (70, 'N'): 29,
    (70, 'O'): 31,
    (70, 'P'): 33,
    (70, 'Q'): 35,
    (70, 'R'): 36,
    (70, 'S'): 38,
    (70, 'T'): 40,

    (80, 'A'): 4,
    (80, 'B'): 8,
    (80, 'C'): 10,
    (80, 'D'): 11,
    (80, 'E'): 13,
    (80, 'F'): 14,
    (80, 'G'): 15,
    (80, 'H'): 17,
    (80, 'I'): 18,
    (80, 'J'): 19,
    (80, 'K'): 21,
    (80, 'L'): 22,
    (80, 'M'): 23,
    (80, 'N'): 25,
    (80, 'O'): 26,
    (80, 'P'): 28,
    (80, 'Q'): 29,
    (80, 'R'): 30,

    (90, 'A'): 4,
    (90, 'B'): 7,
    (90, 'C'): 9,
    (90, 'D'): 10,
    (90, 'E'): 11,
    (90, 'F'): 12,
    (90, 'G'): 13,
    (90, 'H'): 15,
    (90, 'I'): 16,
    (90, 'J'): 17,
    (90, 'K'): 18,
    (90, 'L'): 19,
    (90, 'M'): 21,
    (90, 'N'): 22,
    (90, 'O'): 23,
    (90, 'P'): 24,
    (90, 'Q'): 25,

    (100, 'A'): 3,
    (100, 'B'): 6,
    (100, 'C'): 8,
    (100, 'D'): 9,
    (100, 'E'): 10,
    (100, 'F'): 11,
    (100, 'G'): 12,
    (100, 'H'): 13,
    (100, 'I'): 14,
    (100, 'J'): 15,
    (100, 'K'): 16,
    (100, 'L'): 17,
    (100, 'M'): 18,
    (100, 'N'): 19,
    (100, 'O'): 20,

    (110, 'A'): 3,
    (110, 'B'): 5,
    (110, 'C'): 7,
    (110, 'D'): 8,
    (110, 'E'): 9,
    (110, 'F'): 10,
    (110, 'G'): 11,
    (110, 'H'): 12,
    (110, 'I'): 13,
    (110, 'J'): 14,
    (110, 'K'): 15,
    (110, 'L'): 16,

    (120, 'A'): 3,
    (120, 'B'): 5,
    (120, 'C'): 6,
    (120, 'D'): 7,
    (120, 'E'): 8,
    (120, 'F'): 9,
    (120, 'G'): 10,
    (120, 'H'): 11,
    (120, 'I'): 12,
    (120, 'J'): 13,

    (130, 'A'): 3,
    (130, 'B'): 4,
    (130, 'C'): 5,
    (130, 'D'): 6,
    (130, 'E'): 7,
    (130, 'F'): 8,
    (130, 'G'): 9,
    (130, 'H'): 10,

    (140, 'A'): 3,
    (140, 'B'): 4,
    (140, 'C'): 5,
    (140, 'D'): 6,
    (140, 'E'): 7,
    (140, 'F'): 8
}

# Surface Interval Credit Table (in minutes)
# Format: (old_group, new_group): (min_time, max_time)
surface_interval_table = {
    # Group Z
    ('Z', 'A'): (180, float('inf')),
    ('Z', 'B'): (159, 179),
    ('Z', 'C'): (138, 158),
    ('Z', 'D'): (120, 137),
    ('Z', 'E'): (103, 119),
    ('Z', 'F'): (87, 102),
    ('Z', 'G'): (73, 86),
    ('Z', 'H'): (60, 72),
    ('Z', 'I'): (48, 59),
    ('Z', 'J'): (37, 47),
    ('Z', 'K'): (29, 36),
    ('Z', 'L'): (22, 28),
    ('Z', 'M'): (16, 21),
    ('Z', 'N'): (11, 15),
    ('Z', 'O'): (8, 10),
    ('Z', 'P'): (5, 7),
    ('Z', 'Q'): (4, 4),
    ('Z', 'R'): (3, 3),
    ('Z', 'S'): (2, 2),
    ('Z', 'T'): (1, 1),
    ('Z', 'U'): (0, 0),

    # Group Y
    ('Y', 'A'): (169, float('inf')),
    ('Y', 'B'): (147, 168),
    ('Y', 'C'): (127, 146),
    ('Y', 'D'): (109, 126),
    ('Y', 'E'): (92, 108),
    ('Y', 'F'): (77, 91),
    ('Y', 'G'): (64, 76),
    ('Y', 'H'): (52, 63),
    ('Y', 'I'): (41, 51),
    ('Y', 'J'): (32, 40),
    ('Y', 'K'): (25, 31),
    ('Y', 'L'): (19, 24),
    ('Y', 'M'): (14, 18),
    ('Y', 'N'): (10, 13),
    ('Y', 'O'): (7, 9),
    ('Y', 'P'): (5, 6),
    ('Y', 'Q'): (3, 4),
    ('Y', 'R'): (2, 2),
    ('Y', 'S'): (1, 1),
    ('Y', 'T'): (0, 0),

    # Group X
    ('X', 'A'): (157, float('inf')),
    ('X', 'B'): (136, 156),
    ('X', 'C'): (116, 135),
    ('X', 'D'): (99, 115),
    ('X', 'E'): (83, 98),
    ('X', 'F'): (69, 82),
    ('X', 'G'): (56, 68),
    ('X', 'H'): (45, 55),
    ('X', 'I'): (35, 44),
    ('X', 'J'): (27, 34),
    ('X', 'K'): (21, 26),
    ('X', 'L'): (16, 20),
    ('X', 'M'): (12, 15),
    ('X', 'N'): (9, 11),
    ('X', 'O'): (6, 8),
    ('X', 'P'): (4, 5),
    ('X', 'Q'): (3, 3),
    ('X', 'R'): (2, 2),
    ('X', 'S'): (0, 1),

    # Group W
    ('W', 'A'): (146, float('inf')),
    ('W', 'B'): (125, 145),
    ('W', 'C'): (106, 124),
    ('W', 'D'): (89, 105),
    ('W', 'E'): (74, 88),
    ('W', 'F'): (61, 73),
    ('W', 'G'): (49, 60),
    ('W', 'H'): (39, 48),
    ('W', 'I'): (30, 38),
    ('W', 'J'): (23, 29),
    ('W', 'K'): (18, 22),
    ('W', 'L'): (13, 17),
    ('W', 'M'): (10, 12),
    ('W', 'N'): (7, 9),
    ('W', 'O'): (5, 6),
    ('W', 'P'): (3, 4),
    ('W', 'Q'): (2, 2),
    ('W', 'R'): (0, 1),

    # Group V
    ('V', 'A'): (134, float('inf')),
    ('V', 'B'): (114, 133),
    ('V', 'C'): (95, 113),
    ('V', 'D'): (79, 94),
    ('V', 'E'): (65, 78),
    ('V', 'F'): (53, 64),
    ('V', 'G'): (42, 52),
    ('V', 'H'): (33, 41),
    ('V', 'I'): (25, 32),
    ('V', 'J'): (19, 24),
    ('V', 'K'): (15, 18),
    ('V', 'L'): (11, 14),
    ('V', 'M'): (8, 10),
    ('V', 'N'): (6, 7),
    ('V', 'O'): (4, 5),
    ('V', 'P'): (3, 3),
    ('V', 'Q'): (0, 2),

    # Group U
    ('U', 'A'): (122, float('inf')),
    ('U', 'B'): (103, 121),
    ('U', 'C'): (85, 102),
    ('U', 'D'): (70, 84),
    ('U', 'E'): (56, 69),
    ('U', 'F'): (45, 55),
    ('U', 'G'): (35, 44),
    ('U', 'H'): (27, 34),
    ('U', 'I'): (21, 26),
    ('U', 'J'): (16, 20),
    ('U', 'K'): (12, 15),
    ('U', 'L'): (9, 11),
    ('U', 'M'): (7, 8),
    ('U', 'N'): (5, 6),
    ('U', 'O'): (3, 4),
    ('U', 'P'): (0, 2),

    # Group T
    ('T', 'A'): (111, float('inf')),
    ('T', 'B'): (93, 110),
    ('T', 'C'): (75, 92),
    ('T', 'D'): (61, 74),
    ('T', 'E'): (48, 60),
    ('T', 'F'): (38, 47),
    ('T', 'G'): (29, 37),
    ('T', 'H'): (22, 28),
    ('T', 'I'): (17, 21),
    ('T', 'J'): (13, 16),
    ('T', 'K'): (10, 12),
    ('T', 'L'): (7, 9),
    ('T', 'M'): (5, 6),
    ('T', 'N'): (4, 4),
    ('T', 'O'): (0, 3),

    # Group S
    ('S', 'A'): (100, float('inf')),
    ('S', 'B'): (83, 99),
    ('S', 'C'): (66, 82),
    ('S', 'D'): (53, 65),
    ('S', 'E'): (41, 52),
    ('S', 'F'): (32, 40),
    ('S', 'G'): (24, 31),
    ('S', 'H'): (18, 23),
    ('S', 'I'): (14, 17),
    ('S', 'J'): (11, 13),
    ('S', 'K'): (8, 10),
    ('S', 'L'): (6, 7),
    ('S', 'M'): (4, 5),
    ('S', 'N'): (0, 3),

    # Group R
    ('R', 'A'): (89, float('inf')),
    ('R', 'B'): (73, 88),
    ('R', 'C'): (57, 72),
    ('R', 'D'): (45, 56),
    ('R', 'E'): (35, 44),
    ('R', 'F'): (27, 34),
    ('R', 'G'): (20, 26),
    ('R', 'H'): (15, 19),
    ('R', 'I'): (11, 14),
    ('R', 'J'): (9, 10),
    ('R', 'K'): (7, 8),
    ('R', 'L'): (5, 6),
    ('R', 'M'): (0, 4),

    # Group Q
    ('Q', 'A'): (78, float('inf')),
    ('Q', 'B'): (63, 77),
    ('Q', 'C'): (48, 62),
    ('Q', 'D'): (37, 47),
    ('Q', 'E'): (29, 36),
    ('Q', 'F'): (22, 28),
    ('Q', 'G'): (16, 21),
    ('Q', 'H'): (12, 15),
    ('Q', 'I'): (9, 11),
    ('Q', 'J'): (7, 8),
    ('Q', 'K'): (5, 6),
    ('Q', 'L'): (0, 4),

    # Group P
    ('P', 'A'): (67, float('inf')),
    ('P', 'B'): (54, 66),
    ('P', 'C'): (40, 53),
    ('P', 'D'): (30, 39),
    ('P', 'E'): (23, 29),
    ('P', 'F'): (17, 22),
    ('P', 'G'): (13, 16),
    ('P', 'H'): (10, 12),
    ('P', 'I'): (7, 9),
    ('P', 'J'): (5, 6),
    ('P', 'K'): (0, 4),

    # Group O
    ('O', 'A'): (57, float('inf')),
    ('O', 'B'): (44, 56),
    ('O', 'C'): (32, 43),
    ('O', 'D'): (24, 31),
    ('O', 'E'): (18, 23),
    ('O', 'F'): (13, 17),
    ('O', 'G'): (10, 12),
    ('O', 'H'): (7, 9),
    ('O', 'I'): (5, 6),
    ('O', 'J'): (0, 4),

    # Group N
    ('N', 'A'): (46, float('inf')),
    ('N', 'B'): (35, 45),
    ('N', 'C'): (25, 34),
    ('N', 'D'): (18, 24),
    ('N', 'E'): (13, 17),
    ('N', 'F'): (10, 12),
    ('N', 'G'): (7, 9),
    ('N', 'H'): (5, 6),
    ('N', 'I'): (0, 4),

    # Group M
    ('M', 'A'): (36, float('inf')),
    ('M', 'B'): (26, 35),
    ('M', 'C'): (18, 25),
    ('M', 'D'): (13, 17),
    ('M', 'E'): (9, 12),
    ('M', 'F'): (7, 8),
    ('M', 'G'): (5, 6),
    ('M', 'H'): (0, 4),

    # Group L
    ('L', 'A'): (26, float('inf')),
    ('L', 'B'): (18, 25),
    ('L', 'C'): (12, 17),
    ('L', 'D'): (8, 11),
    ('L', 'E'): (6, 7),
    ('L', 'F'): (4, 5),
    ('L', 'G'): (0, 3),

    # Group K
    ('K', 'A'): (17, float('inf')),
    ('K', 'B'): (11, 16),
    ('K', 'C'): (7, 10),
    ('K', 'D'): (5, 6),
    ('K', 'E'): (3, 4),
    ('K', 'F'): (0, 2),

    # Group J
    ('J', 'A'): (8, float('inf')),
    ('J', 'B'): (5, 7),
    ('J', 'C'): (3, 4),
    ('J', 'D'): (2, 2),
    ('J', 'E'): (0, 1),

    # Group I
    ('I', 'A'): (4, float('inf')),
    ('I', 'B'): (2, 3),
    ('I', 'C'): (1, 1),
    ('I', 'D'): (0, 0),

    # Group H
    ('H', 'A'): (2, float('inf')),
    ('H', 'B'): (1, 1),
    ('H', 'C'): (0, 0),

    # Group G
    ('G', 'A'): (1, float('inf')),
    ('G', 'B'): (0, 0),

    # Group F
    ('F', 'A'): (0, float('inf')),

    # Groups E through A don't need entries as they can only go to A
    ('E', 'A'): (0, float('inf')),
    ('D', 'A'): (0, float('inf')),
    ('C', 'A'): (0, float('inf')),
    ('B', 'A'): (0, float('inf')),
    ('A', 'A'): (0, float('inf'))
}

def get_pressure_group(depth: int, time: int) -> str:
    """Get pressure group letter based on depth and bottom time."""
    if depth not in pressure_group_table:
        return "Invalid depth"
    
    for max_time, group in pressure_group_table[depth]:
        if time <= max_time:
            return group
    return "Exceeds limits"

def get_new_group_after_surface_interval(old_group: str, surface_interval: int) -> str:
    """Get new pressure group after surface interval."""
    for (start, end), (min_time, max_time) in surface_interval_table.items():
        if start == old_group and min_time <= surface_interval <= max_time:
            return end
            
    # If we get here, find the lowest possible group
    # Sort by ending group, from Z to A
    possible_transitions = sorted(
        [(start, end, min_time, max_time) 
         for (start, end), (min_time, max_time) in surface_interval_table.items()
         if start == old_group],
        key=lambda x: PRESSURE_GROUPS.index(x[1]), reverse=True
    )
    
    # Find first transition where surface interval is less than min time
    for _, end, min_time, _ in possible_transitions:
        if surface_interval < min_time:
            continue
        return end
    
    # If surface interval is longer than all intervals, return A
    return 'A'

def get_rnt(pg: str, depth: int) -> int:
    """Get residual nitrogen time for pressure group and planned depth."""
    # First check if this combination exists in the table
    rnt = rnt_table.get((depth, pg), -1)
    if rnt >= 0:
        return rnt
        
    # If not in table, this combination is not allowed
    # This handles cases where the pressure group is too high for the depth
    return 0

def check_ndl(depth: int, tbt: int) -> bool:
    """Check if total bottom time is within no-decompression limits."""
    if depth not in no_deco_limits:
        return False
    return tbt <= no_deco_limits[depth]

def calculate_total_bottom_time(rnt: int, planned_time: int) -> int:
    """Calculate total bottom time (RNT + planned time)."""
    return rnt + planned_time

def validate_repetitive_dive(depth: int, pg: str, planned_time: int) -> bool:
    """Validate if a repetitive dive is safe."""
    rnt = get_rnt(pg, depth)
    tbt = calculate_total_bottom_time(rnt, planned_time)
    return check_ndl(depth, tbt)

def main():
    print("\n=== PADI Dive Planner Calculator ===\n")
    
    # First dive
    while True:
        try:
            depth1 = int(input("Enter first dive depth (ft): "))
            if depth1 in no_deco_limits:
                break
            print(f"Invalid depth. Valid depths are: {list(no_deco_limits.keys())}")
        except ValueError:
            print("Please enter a valid number")

    while True:
        try:
            time1 = int(input("Enter first dive bottom time (min): "))
            if time1 > 0:
                break
            print("Time must be positive")
        except ValueError:
            print("Please enter a valid number")

    pg1 = get_pressure_group(depth1, time1)
    print(f"\nPressure Group after first dive: {pg1}")

    if pg1 == "Exceeds limits":
        print("⚠️ WARNING: First dive exceeds no-decompression limits!")
        return

    # Surface interval
    while True:
        try:
            interval = int(input("\nEnter surface interval (minutes): "))
            if interval >= 10:
                break
            print("Surface interval must be at least 10 minutes")
        except ValueError:
            print("Please enter a valid number")

    pg2 = get_new_group_after_surface_interval(pg1, interval)
    print(f"New Pressure Group after surface interval: {pg2}")

    # Second dive
    while True:
        try:
            depth2 = int(input("\nEnter second dive depth (ft): "))
            if depth2 in no_deco_limits:
                break
            print(f"Invalid depth. Valid depths are: {list(no_deco_limits.keys())}")
        except ValueError:
            print("Please enter a valid number")

    while True:
        try:
            planned_time2 = int(input("Enter second dive planned bottom time (min): "))
            if planned_time2 > 0:
                break
            print("Time must be positive")
        except ValueError:
            print("Please enter a valid number")

    if not validate_repetitive_dive(depth2, pg2, planned_time2):
        print("⚠️ WARNING: Second dive exceeds no-decompression limits!")
        return

    while True:
        try:
            abtime2 = int(input("Enter second dive actual bottom time (min): "))
            if abtime2 > 0:
                break
            print("Time must be positive")
        except ValueError:
            print("Please enter a valid number")

    rnt = get_rnt(pg2, depth2)
    print(f"Residual Nitrogen Time: {rnt} min")

    tbt = calculate_total_bottom_time(rnt, abtime2)
    print(f"\nTotal Bottom Time: {tbt} min")

    if check_ndl(depth2, tbt):
        print("✅ Second dive is within no-decompression limits.")
    else:
        print("⚠️ WARNING: Second dive exceeds no-decompression limits!")

if __name__ == "__main__":
    main()

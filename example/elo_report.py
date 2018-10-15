import sqlite3

BETA = 200
K = 200
#: The actual score for win.
WIN = 1.
#: The actual score for draw.
DRAW = 0.5
#: The actual score for loss.
LOSS = 0.


def expect(rating, other_rating, beta=BETA):
    """The "E" function in Elo. It calculates the expected score of the
    first rating by the second rating.
    """
    # http://www.chess-mind.com/en/elo-system
    diff = float(other_rating) - float(rating)
    f_factor = 2 * beta  # rating disparity
    return 1. / (1 + 10 ** (diff / f_factor))


def adjust(rating, series):
    """Calculates the adjustment value."""
    return sum(score - expect(rating, other_rating)
               for score, other_rating in series)


def rate(rating, series, k):
    """Calculates new ratings by the game result series."""
    new_rating = float(rating) + k * adjust(rating, series)
    return new_rating


def rate_1vs1(rating1, rating2, k=K, drawn=False):
        scores = (DRAW, DRAW) if drawn else (WIN, LOSS)
        return (rate(rating1, [(scores[0], rating2)], k),
                rate(rating2, [(scores[1], rating1)], k))


SQL_SELECT_IMAGES_ALL = '''
SELECT *
  FROM images
'''

SQL_SELECT_MATCHES_ALL = '''
SELECT *
  FROM matches
 ORDER BY match_id
'''

conn = sqlite3.connect('example/image-echelon.db')
conn.row_factory = sqlite3.Row

c = conn.cursor()

images = {}
for row in c.execute(SQL_SELECT_IMAGES_ALL):
    images[row['image_id']] = {'name': row['name'], 'rating': 1200.0, 'wins': 0, 'losses': 0}

c.close()

c = conn.cursor()

K_DEF = 10
K_STEPS = [
    {'K': 200.0, 'TOTAL': 1200},
    {'K': 175.0, 'TOTAL': 1600},
    {'K': 150.0, 'TOTAL': 2000},
    {'K': 125.0, 'TOTAL': 2400},
    {'K': 100.0, 'TOTAL': 2800},
    {'K': 75.0, 'TOTAL': 4000},
    {'K': 50.0, 'TOTAL': 5200},
    {'K': 25.0, 'TOTAL': 3600},
    {'K': 10.0, 'TOTAL': -1},

]


def get_k(num):
    if len(K_STEPS) == 0:
        return K_DEF

    k = K_STEPS[0]['K']
    for step in K_STEPS:
        k = step['K']
        if num <= step['TOTAL']:
            break

    return k


current_k = get_k(1)

for row in c.execute(SQL_SELECT_MATCHES_ALL):
    if current_k != get_k(row['match_id']):
        current_k = get_k(row['match_id'])

    new_ratings = rate_1vs1(images[row['winner_id']]['rating'], images[row['loser_id']]['rating'], 10)
    images[row['winner_id']]['rating'] = new_ratings[0]
    images[row['winner_id']]['wins'] = images[row['winner_id']]['wins'] + 1
    images[row['loser_id']]['rating'] = new_ratings[1]
    images[row['loser_id']]['losses'] = images[row['loser_id']]['losses'] + 1

conn.commit()
conn.close()

new_images = sorted(images.items(), key=lambda x: x[1]['rating'], reverse=True)

for i in new_images[:10]:
    print(i)

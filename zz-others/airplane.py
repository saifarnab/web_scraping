def seat_passengers(seats_arrangements, passengers):
    print(seats_arrangements)
    for row in seats_arrangements:
        for column in row:
            print(column)


def make_seats(seats_arrangements):
    for row in seats_arrangements:
        print(row)


def run():
    seats_arrangements = [[3, 2], [4, 3], [2, 3], [3, 4]]
    passengers = 30
    make_seats(seats_arrangements)


run()

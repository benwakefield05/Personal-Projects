"""
Tests for Milestone 1 Game Logic
"""

import pytest
import os

from strands import Pos, Strand, Board, StrandsGame
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step

# 0
def test_inheritance():
    """
    Test that Pos, Strand, Board, and StrandsGame inherits 
    from the corresponding base classes.
    """
    # Check that Pos is a subclass of PosBase
    assert issubclass(Pos, PosBase)
    # same
    assert issubclass(Strand, StrandBase)
    assert issubclass(Board, BoardBase)
    assert issubclass(StrandsGame, StrandsGameBase)


# 1
def test_pos_take_step():
    """
    Test a position plus a step in each neighboring direction.
    """
    # Example starting position
    p = Pos(3, 3)
    
    # We'll check each of the 8 directions

    expected_moves = {
        Step("n"):  (2, 3),
        Step("s"):  (4, 3),
        Step("e"):  (3, 4),
        Step("w"):  (3, 2),
        Step("ne"): (2, 4),
        Step("nw"): (2, 2),
        Step("se"): (4, 4),
        Step("sw"): (4, 2),
    }
    
    # check, for each possible step, that it is updating the position
    # to the right place
    for step_str, (r, c) in expected_moves.items():
        new_pos = p.take_step(step_str)
        assert new_pos.r == r
        assert new_pos.c == c


# 2
def test_pos_step_to_success():
    """
    For the same position values used in the previous test,
    check the eight corresponding calls to the pos_step_to method.
    """
    start = Pos(3, 3)
    # We'll define the eight neighbors
    neighbors = {
        (2, 3): Step("n"),
        (4, 3): Step("s"),
        (3, 4): Step("e"),
        (3, 2): Step("w"),
        (2, 4): Step("ne"),
        (2, 2): Step("nw"),
        (4, 4): Step("se"),
        (4, 2): Step("sw"),
    }
    # check, for each of the eight neighbors, 
    # that the method step_to is valid
    for (r, c), expected_step in neighbors.items():
        neighbor_pos = Pos(r, c)
        actual_step = start.step_to(neighbor_pos)
        assert actual_step == expected_step


# 3
def test_pos_step_to_failure():
    """
    Check that, when calling the method on several
    pairs of positions which are two steps away 
    from each other, that the method raises an exception.

    Ditto above for a couple pairs of positions which
    are three steps away from each other.
    """
    p = Pos(3, 3)
    # Positions that are 2 steps away (horizontally, vertically, or diagonally)
    two_steps_positions = [
        Pos(3, 5),  
        Pos(1, 3),  
        Pos(1, 1),  
        Pos(5, 3),  
    ]
    # Also positions that are 3 steps away
    three_steps_positions = [
        Pos(3, 6),
        Pos(0, 3),
        Pos(6, 6),
    ]
    
    # merge the two lists for tests
    for bad_pos in two_steps_positions + three_steps_positions:
        try:
            p.step_to(bad_pos)      # This should raise ValueError
            assert False            # It's wrong when it doesn't raise ValueError
        except ValueError:
            # Good. We expect ValueError
            pass

# 4
def test_strand_positions_straight_cardinal():
    """
    Create four strands, one in each cardinal direction, 
    each with length at least 4 steps, and check that the positions
    method returns the appropriate results.
    """
    # easiest way to write a test would be repeating cardinal
    # direction 4 times
    # have to assume that this board is large enough though
    north_steps = [Step("n")] * 4
    strand_north = Strand(Pos(5, 5), north_steps)
    
    # Similarly for south, east, west
    south_steps = [Step("s")] * 4
    strand_south = Strand(Pos(5, 5), south_steps)
    
    east_steps = [Step("e")] * 4
    strand_east = Strand(Pos(5, 5), east_steps)
    
    west_steps = [Step("w")] * 4
    strand_west = Strand(Pos(5, 5), west_steps)

    # Now check the positions list for each:

    pos_list_n = strand_north.positions()
    assert len(pos_list_n) == 5  # Start + 4 steps
    assert pos_list_n[0].r == 5 and pos_list_n[0].c == 5
    # if the last position is at the right place,
    # the method should be valid
    assert pos_list_n[-1].r == 1 and pos_list_n[-1].c == 5
    
    # same for south, east and west
    pos_list_s = strand_south.positions()
    assert len(pos_list_s) == 5
    # skip the check for first position. Done in North
    assert pos_list_s[-1].r == 9 and pos_list_s[-1].c == 5
    
    pos_list_e = strand_east.positions()
    assert len(pos_list_e) == 5
    assert pos_list_e[-1].r == 5 and pos_list_e[-1].c == 9
    
    pos_list_w = strand_west.positions()
    assert len(pos_list_w) == 5
    assert pos_list_w[-1].r == 5 and pos_list_w[-1].c == 1


# 4 
# in Milestone 1 instruction this method was also labelled
# as 4. Not sure if it's intentional
def test_strand_positions_straight_intercardinal():
    '''
    Ditto previous, but for the intercardinal directions.
    '''
    # everything's the same
    # also have to assume a board that is large enough
    ne_steps = [Step("ne")] * 4
    strand_ne = Strand(Pos(5, 5), ne_steps)
    pos_list_ne = strand_ne.positions()
    # final position should be (1, 9)
    assert pos_list_ne[-1].r == 1
    assert pos_list_ne[-1].c == 9

    nw_steps = [Step("nw")] * 4
    strand_nw = Strand(Pos(5, 5), nw_steps)
    pos_list_nw = strand_nw.positions()
    assert pos_list_nw[-1].r == 1
    assert pos_list_nw[-1].c == 1

    se_steps = [Step("se")] * 4
    strand_se = Strand(Pos(5, 5), se_steps)
    pos_list_se = strand_se.positions()
    assert pos_list_se[-1].r == 9
    assert pos_list_se[-1].c == 9

    sw_steps = [Step("sw")] * 4
    strand_sw = Strand(Pos(5, 5), sw_steps)
    pos_list_sw = strand_sw.positions()
    assert pos_list_sw[-1].r == 9
    assert pos_list_sw[-1].c == 1


# 5
def test_strand_positions_long():
    """
    Create a strand which includes at least one step in each 
    of the eight directions but does not ever (or every) cross
    itself. Check that positions and is_folded return the
    expected results.

    Ditto for a second long strand which does cross itself.
    Check that positions and is_folded return the expected results.
    """
    # non-crossing strand
    # one step in each direction
    steps_no_cross = [
        Step("n"), Step("ne"), Step("e"), Step("se"), Step("s"), 
        Step("sw"), Step("w"), Step("nw")
    ]
    strand_no_cross = Strand(Pos(5, 5), steps_no_cross)
    # positions() should produce a list of length 9
    pos_list = strand_no_cross.positions()
    assert len(pos_list) == 9
    assert strand_no_cross.is_folded() == False

    # crossing strand
    steps_cross = [
        Step("n"), Step("n"), Step("e"), Step("se"), 
        Step("n"), Step("sw")  
    ]
    strand_cross = Strand(Pos(5, 5), steps_cross)
    # positions() => length 8
    pos_list2 = strand_cross.positions()
    assert len(pos_list2) == 7
    assert strand_cross.is_folded() == True

# 6
def test_load_game_a_good_roast_file():
    """
    Pick a game file boards/G.txt that includes an 8x6 board
    (i.e. the “official” size), and throughly check that all 
    of the following methods return the intended data: theme,
    num_rows, num_cols, and answers.
    """
    # pick one with official size
    filename = "boards/a-good-roast.txt"
    game = StrandsGame(filename)

    # Check board size
    assert game.board().num_rows() == 8
    assert game.board().num_cols() == 6

    # check theme
    assert game.theme().lower() == "a good roast"

    # check answers
    ans = game.answers()
    assert len(ans) == 8
    actual = []
    for string, other in ans:
        actual.append(string)
    expected = [
        "howl", "roar", "laugh", "cackle",
        "giggle", "shriek", "chuckle", "crackingup"
    ]
    assert actual == expected

# 7
def test_load_game_a_good_roast_variations():
    """
    For the same game file as in the previous test, 
    test that a list[str] corresponding to the contents 
    of boards/G.txt can also be used to correctly initialize
    the same game.
    
    This test should also exercise enough additional string
    variations from the version in boards/G.txt, in order to
    check the allowed differences in whitespace and capitalization
    do not affect the results of loading the game.
    """

    with open("boards/a-good-roast.txt") as f:
        lines = f.readlines()
    # strip trailing spaces and 
    varied = [line.rstrip() + "\n" for line in lines]
    # add the title to the front
    title = "A good roast\n"
    varied[0] = title
    
    # should be able to construct the game in this new way
    game = StrandsGame(varied)

    # copy the set of assertions from 6
    # see if it really recreates the game
    assert game.board().num_rows() == 8
    assert game.board().num_cols() == 6
    ans = game.answers()
    assert len(ans) == 8
    actual = []
    for string, other in ans:
        actual.append(string)
    expected = [
        "howl", "roar", "laugh", "cackle",
        "giggle", "shriek", "chuckle", "crackingup"
    ]
    assert actual == expected


# 8

def test_load_game_a_good_roast_invalid():
    """
    For the same game is in the previous tests, test several
    variations that make the game file invalid (e.g. missing 
    board letters, answer strands that do not match the expected 
    word, answers that do not span the board, etc.), and check 
    that load_game raises a ValueError in each case.

    To help your team debug the game logic, it is a good 
    idea to provide detailed string messages with these errors. 
    However, your tests should check simply for the presence of 
    a ValueError but should not rely on its string arguments.

    You can factor these multiple tests either as a single test, 
    or as multiple tests with additional suffixes to distinguish 
    them, or as a single parameterized test using 
    @pytest.mark.parametrize.
    """

    lines_missing_row = [
        "A good roast\n", "\n",
        "G L P L K C\n",
        "G E U E U R\n",
        # missed one line
        "K L N C O A\n",
        "C C I R L U\n",
        "A S K C H G\n",
        "E K H A L W\n",
        "I R C R O H\n", "\n",
        "HOWL 8 6  w ne w\n",
    ]

    lines_bad_coord = [
        "A good roast\n", "\n",
        "G L P L K C\n", "G E U E U R\n", "G I E G H A\n",
        "K L N C O A\n", "C C I R L U\n", "A S K C H G\n",
        "E K H A L W\n", "I R C R O H\n", "\n",
        "HOWL 9 9  w ne w\n",        # this start is outside the board
    ]

    # wrong path
    lines_bad_word = [
        "A good roast\n", "\n",
        "G L P L K C\n", "G E U E U R\n", "G I E G H A\n",
        "K L N C O A\n", "C C I R L U\n", "A S K C H G\n",
        "E K H A L W\n", "I R C R O H\n", "\n",
        "HOWL 8 6  e e e e\n",       # this path is invalid
    ]

    # put the bad cases in one list
    broken_cases = [lines_missing_row, lines_bad_coord, lines_bad_word]

    for i, bad_lines in enumerate(broken_cases):
        try:
            # similar format with previous
            StrandsGame(bad_lines)
            assert False, f"Case {i} should have raised ValueError"
        except ValueError:
            # this is expected 
            pass

# 9
def test_play_game_a_good_roast_once():
    """
    For the same game, test a sequence a moves involving only 
    submitting theme words in the correct order.

    Check several important expected results at different 
    points in the sequence.
    """

    game = StrandsGame("boards/a-good-roast.txt")

    # the answers method should return all answers in the right sequence
    for word, strand in game.answers():
        result = game.submit_strand(strand)
        # if strings or False appear in output,
        # it's already found or not in the right sequence
        assert result == (word, True)

    # final check that all answers are found
    assert game.game_over()


# 10
def test_play_game_a_good_roast_twice():
    """
    Ditto above, but with moves in a different order.
    """
    game = StrandsGame("boards/a-good-roast.txt")
    answers = game.answers()

    # just design an arbitrary order
    # for instance, submit even number answers first
    for i in range(0, len(answers), 2):
        w, s = answers[i]
        assert game.submit_strand(s) == (w, True)
    
    for i in range(1, len(answers), 2):
        w, s = answers[i]
        assert game.submit_strand(s) == (w, True)

    assert game.game_over()

# 11
def test_pla_game_a_good_roast_three_times():
    """
    Ditto above, but including some moves that submit 
    some non-theme words and some already found words.
    """
    game = StrandsGame("boards/a-good-roast.txt")
    word0, strand0 = game.answers()[0]

    # submit a non-theme word
    random = Strand(Pos(0, 0), [Step("e")])
    assert game.submit_strand(random) == "Too short" or game.submit_strand(random) == "Not in word list" or game.submit_strand(random) == "Not a theme word"

    # submit a correct one
    assert game.submit_strand(strand0) == (word0, True)

    # right after this, submit the same one
    assert game.submit_strand(strand0) == "Already found"


# 12
def test_play_game_a_good_roast_more():
    """
    Ditto above, but including hints in the sequence
    in a way that triggers each of the potential 
    scenarios involving use_hint.

    Will cover every possible outcome. First: (i,False)
    Second: (i,True), Third: "use your hint"

    And clear the hint once it's discovered
    """
    game = StrandsGame("boards/a-good-roast.txt")

    # directly add the hint_counter to the threshold
    game.meter_hint = game.hint_threshold()

    h1 = game.use_hint()
    # first should return (i, False)
    assert isinstance(h1, tuple) and h1[1] is False

    game.meter_hint = game.hint_threshold()
    h2 = game.use_hint()
    # second time should return (i, True)
    assert h2 == (h1[0], True)

    game.meter_hint = game.hint_threshold()
    h3 = game.use_hint()
    # third time should return the string
    assert h3 == "Use your current hint"

    # locate the corresponding hint and submit it
    hint_index = h1[0]
    word, strand = game.answers()[hint_index]
    game.submit_strand(strand)

    # the new hint should target at a different answer
    if not game.game_over():
        h4 = game.use_hint()
        assert h4[0] != hint_index


"""
Milestone 2
"""
# 13
def test_is_not_cyclic():
    """
    Define four acyclic strands with different lengths
    and shapes, and check that is_cyclic returns the 
    ppropriate answer.
    """
    # define four routes that are not cyclic
    # they are all different in length
    strands = [
        Strand(Pos(0, 0), [Step("e"), Step("e")]),
        Strand(Pos(3, 3), [Step("nw"), Step("n"), Step("e")]),
        Strand(Pos(2, 2), [Step("s"), Step("sw"), Step("w"), Step("nw")]),
        Strand(Pos(1, 1), [Step("n"), Step("e"), Step("se"), Step("s"), Step("sw")])
    ]

    # for each strand, assert that it's not cyclic
    for strand in strands:
        assert not strand.is_cyclic()

# 14
def test_is_cyclic():
    """Define four cyclic strands with different lengths
    and shapes, and check that is_cyclic returns the 
    appropriate answer.
    """
    # first 2 strands are cyclic with different shape
    # the third is in the shape of line
    # fourth is a bigger loop.
    # I assume this satisfies the requirement of
    # different lengths and shapes
    strands = [
        Strand(Pos(1, 1), [Step("e"), Step("s"), Step("w"), Step("n")]),
        Strand(Pos(0, 0), [Step("se"), Step("ne"), Step("nw"), Step("sw")]),
        Strand(Pos(4, 4), [Step("w"), Step("w"), Step("e"), Step("e")]),
        Strand(Pos(2, 2), [Step("n"), Step("ne"), Step("e"),
                          Step("se"), Step("s"), Step("sw"),
                          Step("w"), Step("nw")]),
    ]
    for st in strands:
        assert st.is_cyclic()

# 15
# this is testing two different games with overlapping strand
# so I will use parameterized tests
Strand
@pytest.mark.parametrize(
    "filename, word, strand_pairs",
    [
        (
            "boards/free-for-all.txt",
            "tote",
            [
                Strand(Pos(0, 0), [Step("se"), Step("w"), Step("ne")]),
                Strand(Pos(1, 0), [Step("e"), Step("nw"), Step("e")])
            ],  # both strands present Tote, with same letters and different routes
        ),
        (
            "boards/counter-offers.txt",      
            "espresso",
            # e n e s s e n
            [
                Strand(Pos(4, 2), [Step("e"), Step("n"), Step("e"), 
                                   Step("s"), Step("s"), Step("e"), Step("n")]),
                Strand(Pos(4, 2), [Step("e"), Step("n"), Step("e"), 
                                   Step("s"), Step("se"), Step("w"), Step("ne")])
            ],
        )
    ]
)

# 15
def test_overlapping(filename, word, strand_pairs):
    """
    Pick a game and a theme word which has ambiguous 
    strands, meaning that more than one strand can be drawn 
    through the same letters for that word. In the specification, 
    we call such strands overlapping. Check that each of the 
    overlapping strands can be successfully played to find 
    that theme word.

    Pick a second game and theme word with overlapping 
    strands, and check that both can be successfully played.
    """
    # for each parametrized case,
    game = StrandsGame(filename)
    for strand in strand_pairs:
        # submit the two strands, and see if they both could be
        # succesfully played
        result = game.submit_strand(strand)
        assert result == (word, True)

# 16
def test_load_game_best_in_class_file():
    """
    Analogous to test 6, for a different game best_in_class
    """
    # copy everything from 6
    game = StrandsGame("boards/best-in-class.txt")

    assert game.board().num_rows() == 8
    assert game.board().num_cols() == 6

    assert game.theme().lower() == "best in class"

    ans = game.answers()
    assert len(ans) == 8
    actual = []
    for string, other in ans:
        actual.append(string)
    expected = [
        "eyes", "hair", "smile", "couple",
        "athlete", "dressed", "friends", "yearbook"
    ]
    assert actual == expected

# 17
def test_load_game_best_in_class_variations():
    # same
    with open("boards/best-in-class.txt") as f:
        lines = f.readlines()
    varied = [line.rstrip() + "\n" for line in lines]

    title = "Best in class\n"
    varied[0] = title
    
    game = StrandsGame(varied)


    assert game.board().num_rows() == 8
    assert game.board().num_cols() == 6
    ans = game.answers()
    assert len(ans) == 8
    actual = []
    for string, other in ans:
        actual.append(string)
    expected = [
        "eyes", "hair", "smile", "couple",
        "athlete", "dressed", "friends", "yearbook"
    ]
    assert actual == expected

# 18

def test_load_game_best_in_class_invalid():
    

    lines_missing_row = [
        "Best in class\n", "\n",
        "L E K R E D\n", 
        "H T O D S E\n",
        "T E O R I S\n", 
        "A I M B S A\n",
        "L S R N D H\n", 
        "E U A E I E\n",
        "P O E R S Y\n", 
        "\n",  # miss final line
        "eyes 6 6  s s nw\n",
    ]

    lines_bad_coord = [
        "Best in class\n", "\n",
        "L E K R E D\n", 
        "H T O D S E\n",
        "T E O R I S\n", 
        "A I M B S A\n",
        "L S R N D H\n", 
        "E U A E I E\n",
        "P O E R S Y\n", 
        "L E C Y F E\n",
        "\n",
        "eyes 9 9  s s nw\n",        # this start is outside the board
    ]

    # wrong path
    lines_bad_word = [
        "Best in class\n", "\n",
        "L E K R E D\n", 
        "H T O D S E\n",
        "T E O R I S\n", 
        "A I M B S A\n",
        "L S R N D H\n", 
        "E U A E I E\n",
        "P O E R S Y\n", 
        "L E C Y F E\n",
        "\n",
        "eyes 6 6  s s w\n",# this path is invalid
    ]

    broken_cases = [lines_missing_row, lines_bad_coord, lines_bad_word]

    for i, bad_lines in enumerate(broken_cases):
        try:
            StrandsGame(bad_lines)
            assert False, f"Case {i} should have raised ValueError"
        except ValueError:
            # this is expected 
            pass


# 19
def test_play_game_best_in_class_once():
    # same with test 9
    game = StrandsGame("boards/best-in-class.txt")

    for word, strand in game.answers():
        result = game.submit_strand(strand)
        assert result == (word, True)

    assert game.game_over()

# 20
def test_play_game_best_in_class_twice():
    # same with 10
    game = StrandsGame("boards/best-in-class.txt")
    answers = game.answers()

    for i in range(0, len(answers), 2):
        w, s = answers[i]
        assert game.submit_strand(s) == (w, True)
    
    for i in range(1, len(answers), 2):
        w, s = answers[i]
        assert game.submit_strand(s) == (w, True)

    assert game.game_over()

# 21
def test_play_game_best_in_class_three_times():
    # same with 11
    game = StrandsGame("boards/best-in-class.txt")
    word0, strand0 = game.answers()[0]

    # submit a non-theme word
    random = Strand(Pos(0, 0), [Step("e")])
    assert game.submit_strand(random) == "Too short" or game.submit_strand(random) == "Not in word list" or game.submit_strand(random) == "Not a theme word"

    # submit a correct one
    assert game.submit_strand(strand0) == (word0, True)

    # right after this, submit the same one
    assert game.submit_strand(strand0) == "Already found"

# 22
def test_play_game_best_in_class_more():
    # same with 12
    game = StrandsGame("boards/best-in-class.txt")

    game.meter_hint = game.threshold_hint

    h1 = game.use_hint()
    # first should return (i, False)
    assert isinstance(h1, tuple) and h1[1] is False

    game.meter_hint = game.threshold_hint
    h2 = game.use_hint()
    # second time should return (i, True)
    assert h2 == (h1[0], True)

    h3 = game.use_hint()
    # third time should return the string
    assert h3 == "Use your current hint"

    # locate the corresponding hint and submit it
    hint_index = h1[0]
    word, strand = game.answers()[hint_index]
    game.submit_strand(strand)

    # the new hint should target at a different answer
    if not game.game_over():
        h4 = game.use_hint()
        assert h4[0] != hint_index

# 23
def test_valid_game_files():
    """
    Check that each of the game files in the boards/ 
    directory is valid.
    """

    board_dir = "boards"

    txt_files = []

    # extract all filenames in boards/
    for fname in os.listdir(board_dir):
        full_path = os.path.join(board_dir, fname)
        txt_files.append(full_path)

    for path in txt_files:
        StrandsGame(path)


# 24
def test_play_game_buzzing_in_hints_0():
    game = StrandsGame("boards/buzzing-in.txt", hint_threshold=0)
    for counter in range(4):
        hint = game.use_hint()
        # expect a hint tuple
        assert isinstance(hint, tuple)

        i, b = hint
        # first hint should be False
        assert b == False

        hint = game.use_hint()
        i, b = hint
        # second hint should be true
        assert b == True

        word, strand = game.answers()[i]
        result = game.submit_strand(strand)
        assert result == (word, True)
    # non None at least 4 times
    assert len(game.found_strands()) == 4

# 25
def test_play_game_buzzing_in_hints_1():
    game = StrandsGame("boards/buzzing-in.txt", hint_threshold=1)
    non_theme_strands = [
        Strand(Pos(7,0), [Step("e"), Step("e"), Step("e")]),  # SWOT
        Strand(Pos(5,2), [Step("e"), Step("e"), Step("s")]),  # SHOW
        Strand(Pos(7,1), [Step("e"), Step("nw"), Step("n")]),  # WORD
        Strand(Pos(1,0), [Step("e"), Step("e"), Step("ne"), Step("se")])  # DREAM
    ]
    for non_theme_strand in non_theme_strands:
        # first non-theme word
        result = game.submit_strand(non_theme_strand)
        assert isinstance(result, tuple) and result[1] == False
        # first use_hint call
        hint = game.use_hint()
        i, b = hint
        assert b == False, "First hint should be (index, False)"

        # simulate second non-theme word
        game.meter_hint += 1  # manual increment to ensure meter_hint >= 1
        # second use_hint call
        hint = game.use_hint()
        i, b = hint
        # Second hint should be true
        assert b == True
        word, strand = game.answers()[i]
        result = game.submit_strand(strand)
        assert result == (word, True)
    assert len(game.found_strands()) == 4

# 26
def test_play_game_counter_offers_hints_0():
    # the same with 24
    game = StrandsGame("boards/counter-offers.txt", hint_threshold=0)
    for counter in range(4):
        hint = game.use_hint()
        # expect a hint tuple
        assert isinstance(hint, tuple)

        i, b = hint
        # first hint should be False
        assert b == False

        hint = game.use_hint()
        i, b = hint
        # second hint should be true
        assert b == True

        word, strand = game.answers()[i]
        result = game.submit_strand(strand)
        assert result == (word, True)
    # non None at least 4 times
    assert len(game.found_strands()) == 4

# 27
def test_play_game_counter_offers_hints_1():
    game = StrandsGame("boards/counter-offers.txt", hint_threshold=1)
    # Define four distinct "non-theme" strands
    # (the code may or may not recognize these as actual dictionary words)
    non_theme_strands = [
        Strand(Pos(0,1), [Step("s"), Step("s"), Step("e")]),  # "WHEN"
        Strand(Pos(1,0), [Step("e"), Step("s"), Step("s"), Step("se")]),  # "CHEAP"
        Strand(Pos(7,2), [Step("e"), Step("e"), Step("e")]),  # "RISE"
        Strand(Pos(7,0), [Step("e"), Step("e"), Step("n"), Step("e"), Step("ne")]),  # "STRESS"
    ]

    for non_theme_strand in non_theme_strands:
        # Submit the first non-theme word
        result = game.submit_strand(non_theme_strand)

        # "Not a valid word" is the output for word not in dictionary
        if isinstance(result, str):
            # if it's a string, assume it's "Not a valid word"
            assert result == "Not a valid word"
        else:
            # otherwise, we check that it's recognized but not theme
            word, is_theme = result
            assert not is_theme

        # test the hint logic as before

        hint = game.use_hint()
        assert isinstance(hint, tuple)
        i, b = hint
        assert b == False

        game.meter_hint += 1

        hint = game.use_hint()
        i, b = hint
        assert b is True

        word, strand = game.answers()[i]
        result = game.submit_strand(strand)
        assert result == (word, True)

    assert len(game.found_strands()) == 4
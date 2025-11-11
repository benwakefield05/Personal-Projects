-to run the game simply type python3 src/tui.py 
and a random game will be generated to play.
Use:
123
456
789
to move around the board, press q to quit the game, enter to enter a letter
and enter twice to enter a strand. Press h to get a hint after the threashold
has been met

-run the following command in the TUI
    $python3 src/tui.py --title_screen
-this will give a title screen before the game begins
-see run_title_screen, title_screen and title_screen_event_loop functions in
 src/tui.py for implimentation

 -run the following command in the TUI
    $python3 src/tui.py --special
-this will give a special breakfast board with a special art board
-see ArtTUISpecial is src/art_tui and the command line in src/tui to see
implimentation
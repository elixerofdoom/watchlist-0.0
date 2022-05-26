# A watchlist organizer in PySimpleGUI
import json
from typing import Tuple
import PySimpleGUI as sg
from classes import Movie
import imdb_api as imdb

def create_window(title, used_layout, display_values= '') -> sg.Window:
    """ Layouts are stored locally else an Error message occurs
    when reusing a layout while creating a new window.
    """
    sg.theme('DarkGrey1')
    sg.set_options(font= font) 

    main_layout = [
        [
            sg.Menu(menu_def)
        ],
        [  # Row 1
            sg.Text(
                'watchlist organizer',
                justification='center',
                expand_x=True,
                key='TEXT',)
        ],
        [  # Row 2 
            sg.Table( # not watched
                values= table_content_not_watched,
                headings= headings_not_watched,
                text_color= 'Black',
                def_col_width= 30,
                row_height= 20,
                num_rows= 20,
                background_color= 'grey',
                display_row_numbers= True,
                auto_size_columns= False,
                right_click_menu= right_click_menu_1,
                justification= 'right',
                key= '-WATCHLIST_TABLE-'
                ),
            sg.Table( # watched
                values= table_content_watched,
                headings= headings_watched,
                text_color= 'Black',
                def_col_width= 30,
                row_height= 20,
                num_rows= 20,
                background_color= 'grey',
                display_row_numbers= True,
                auto_size_columns= False,
                right_click_menu= right_click_menu_2,
                justification= 'right',
                key= '-WATCHED_LIST_TABLE-'
                ),
        ], 
        [   # Row 3
            sg.Push(),
            sg.Button(
                button_text= 'exit', 
                key= '-EXIT-')
        ],
    ]
    
    input_popup = [
        [sg.Radio('Show', "RAD1"), sg.Radio('Movie', "RAD1")], 
        [sg.Input(key='-INPUT-')],
        [sg.Button('Cancel'), sg.Push(), sg.Button('Submit')]]

    display_results = [
        [sg.Table(
            values= display_values,
            headings= 'results')]

    ]


    layouts = {
        'main': main_layout,
        'popup': input_popup,
        'display': display_results
        }

    return sg.Window(title, layouts[used_layout], finalize=True)

def load_json() -> dict[list[dict], list[dict]]:
    with open('database.json') as f:
        return  json.load(f)

def save_to_json(data) -> None:
    with open('database.json', 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

def create_movie_objects(database) -> None:
    """fills the 2 lists watchlist/watched_list with Movie Objects respectively"""
    for item in database['watchlist']:
        m = Movie(
            title= item['title'],
            id= item['id'],
            description= item['description'],
            image= item['image'],
        )
        watchlist.append(m)
    for item in database['watched_list']:
        m = Movie(
            title= item['title'],
            id= item['id'],
            description= item['description'],
            image= item['image'],
        )
        if item.get('watched date') != None: # some items in watched_list dont have a 'watched date'
            m.set_watched_date(item['watched date'])
        watched_list.append(m)

def show_details():
    pass

def update_tables() -> None:
    global table_content_not_watched, table_content_watched
    table_content_not_watched = []
    table_content_watched = []
    for movie in watchlist:
        table_content_not_watched.append([movie.title])
    for movie in watched_list:
        table_content_watched.append([movie.title])

def move_movie(remove_from, put_in, indx) -> None:
    m = remove_from.pop(indx)
    put_in.append(m)
    
def get_input(popup: sg.Window) -> Tuple[str, str]:
    """Tuple first value is search type and the second value is search title"""
    while True:
        event, values = popup.read()
        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            popup.close()
            return
        if event == 'Submit':
            if values['-INPUT-'] == '':
                continue
            if values[0] == False and values[1] == False:
                print('both radio')
                continue
            break
        print(event, values)
    
    popup.close()
    if values[0] == True:
        return 'SearchShow', values['-INPUT-']
    else:
        return 'SearchMovie', values['-INPUT-']

def fetch_imdb_data(search_type, search_title) -> list:
    responseObj = imdb.get_respObj(search_title, search_type)
    search_results = responseObj.json()
    return search_results['results']

def display_results(win: sg.Window):
    while True:
        event, values = win.read()
        if event == sg.WINDOW_CLOSED:
            win.close()
            return


def main() -> None:
    """Main Function where all the logic is"""
    database = load_json()
    create_movie_objects(database)
    update_tables()
    window = create_window('Movie Organizer', 'main')

    while True:
        # main window loop
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == '-EXIT-':
            break
        
        if event == 'Add':
            search_ipt = get_input(create_window('Search', 'popup'))
            if search_ipt == None:
                continue
            search_results = fetch_imdb_data(search_ipt[0], search_ipt[1])
            display_win = create_window('Results', 'display', [search_results])


        if event == 'Move':
            if values['-WATCHLIST_TABLE-'] == []:
                continue
            move_movie(watchlist, watched_list, values['-WATCHLIST_TABLE-'][0])
            update_tables()
            window['-WATCHLIST_TABLE-'].update(table_content_not_watched)
            window['-WATCHED_LIST_TABLE-'].update(table_content_watched)

        if event == 'Move Back':
            if values['-WATCHED_LIST_TABLE-'] == []:
                continue
            move_movie(watched_list, watchlist, values['-WATCHED_LIST_TABLE-'][0])
            window['-WATCHLIST_TABLE-'].update(table_content_not_watched)
            window['-WATCHED_LIST_TABLE-'].update(table_content_watched)

        if event == 'Remove':
            pass
        
        if event == 'Details':
            show_details()

        print(event, values)

    window.close()


# variables
font= ('Ariel, 12')

menu_def = [['File', ['Add']],
            ['Help', ['right click on item for drop down menu']]]  

right_click_menu_1 = ['rc_menu',
    ['Move', 'Details', '---', 'Remove']]

right_click_menu_2 = ['rc_menu',
    ['Move Back', 'Details']]

table_content_watched = [] # 2d array
table_content_not_watched = [] # 2d array

watchlist : list[Movie] = []
watched_list : list[Movie]= []
search_results = ''

headings_watched = ['watched']
headings_not_watched = ['not watched']


if __name__ == '__main__':
    main()

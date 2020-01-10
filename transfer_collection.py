from gmusicapi import Mobileclient
import spotipy
import spotipy.util as util

def add_search_string(tracks, search_strings):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        search_strings.append(track['artists'][0]['name'] + ' ' + track['name'])


client_id = 'your client id here'
client_secret='your secret client id here'
redirect_uri='http://localhost:4002'

username = input('Enter your account name/email: ')
token = util.prompt_for_user_token(username, 'user-library-read playlist-read-private', client_id, client_secret, redirect_uri)

playlist_name = input('Enter destination playlist name: ')

search_strings = []
if token:
    sp = spotipy.Spotify(auth=token)
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        print(f'PLAYLIST ', playlist['name'])
        print('  total tracks', playlist['tracks']['total'])

    playlist_to_transfer_name = input('Input name of playlist you want to transfer (if you want export saved songs - type \'saved\'): ')

    playlist_to_transfer = next((x for x in playlists['items'] if x['name'] == playlist_to_transfer_name), None)
    page_length = 20
    page = 0
    if playlist_to_transfer_name == 'saved':
        while True:
            results = sp.current_user_saved_tracks(page_length, page * page_length)
            add_search_string(results, search_strings)
            if len(results['items']) != page_length:
                break
            else:
                page += 1
    elif playlist_to_transfer == None:
            print("Can't find playlist ", playlist_to_transfer_name)
            exit(0)
    else:
        print("Playlist ", playlist_to_transfer_name)
        playlist = sp.user_playlist(username, playlist_to_transfer['id'], fields="tracks,next")
        tracks = playlist['tracks']
        add_search_string(tracks, search_strings)
        while tracks['next']:
            tracks = sp.next(tracks)
            add_search_string(tracks, search_strings)
else:
    print("Can't get token for", username)

print(f'Detected {len(search_strings)} songs to transfer.')

mm = Mobileclient()
mm.perform_oauth() 
mm.oauth_login(Mobileclient.FROM_MAC_ADDRESS)
playlist_id = mm.create_playlist(playlist_name)

print(f'Playlist \'{playlist_name}\' created.')
found_songs = 0
for row in search_strings:
    print(f'\t Searching \'{row}\'.')

    search_result = mm.search(row)
    songs = search_result.get('song_hits')

    song_id = None
    if len(songs) > 0:
        song_id = songs[0].get('track').get('storeId')
        found_songs += 1
    else:
        print('Song not found.')
        continue

    mm.add_songs_to_playlist(playlist_id, song_id)

print(f'Imported {found_songs} songs.')
